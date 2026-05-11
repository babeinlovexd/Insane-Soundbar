import customtkinter as ctk
from tkinter import messagebox
import socket
import threading
import requests
import webbrowser
import os
import re
import sys
import urllib.parse
import subprocess
import esptool
import serial.urlhandler.protocol_socket
import io
import contextlib
import json
from PIL import Image
from zeroconf import ServiceBrowser, Zeroconf
import ctypes

try:
    myappid = 'babeinlovexd.insanecontrolcenter.v1'
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# --- HILFSFUNKTION FÜR DIE .EXE ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def get_app_dir():
    # Holt sich den unsichtbaren AppData Ordner und erstellt das Insane-Verzeichnis
    base_dir = os.getenv('APPDATA') if os.name == 'nt' else os.path.expanduser('~')
    app_dir = os.path.join(base_dir, "InsaneControlCenter")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    return app_dir

def get_config_path():
    return os.path.join(get_app_dir(), "iss_favorites.json")

def get_firmware_path():
    return os.path.join(get_app_dir(), "latest_firmware.bin")

# --- GLOBALE STYLES ---
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

# Default URLs; dynamically resolved via GitHub API where possible.
GITHUB_API_LATEST = "https://api.github.com/repos/babeinlovexd/Insane-Sound-System/releases/latest"
GITHUB_URL = "https://github.com/babeinlovexd/Insane-Soundbar"
GITHUB_AUTHOR_URL = "https://github.com/babeinlovexd"
UPDATE_CHECK_INTERVAL = 3600 # Sekunden

class DeviceListener:
    def __init__(self, callback):
        self.callback = callback
    def add_service(self, zc, type_, name):
        info = zc.get_service_info(type_, name)
        if info and info.parsed_addresses():
            clean_name = name.split('.')[0]
            if "insane" in clean_name.lower():
                ip = info.parsed_addresses()[0]
                self.callback(clean_name, ip)
    def remove_service(self, zc, type_, name): pass
    def update_service(self, zc, type_, name): pass

class ConsoleRedirector(io.StringIO):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        # esptool nutzt \r für die Prozentanzeige, \n für normale Zeilen
        if '\r' in self.buffer or '\n' in self.buffer:
            lines = self.buffer.replace('\r', '\n').split('\n')
            for line in lines[:-1]:
                if "Writing at" in line:
                    self.callback(line.strip())
            self.buffer = lines[-1]

class InsaneControlCenter(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. FENSTER-SETUP
        self.title("Insane Control Center")
        self.geometry("800x700")
        self.configure(fg_color="#0d1117")

        try:
            icon_p = resource_path("logo.ico")
            self.iconbitmap(icon_p)
        except Exception as e:
            print(f"Icon konnte nicht geladen werden: {e}")

        self.scanned_devices = {}   # Alle per WLAN gefundenen Boxen
        self.favorite_devices = {}  # Deine gespeicherten Favoriten
        self.dropdown_mapping = {}
        self.zeroconf = Zeroconf()
        self.is_fetching = False
        self.log_thread = None
        self.log_running = False

        # Keep-Alive Session für die API-Requests (Vermeidet Socket-Erschöpfung auf dem ESP)
        self.session = requests.Session()

        self.online_version = None
        self.last_update_check = 0

        # --- HEADER ---
        self.header_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.header_frame.pack(pady=(20, 10), padx=40, fill="x")

        try:
            logo_path = resource_path("logo.png")
            logo_image = ctk.CTkImage(light_image=Image.open(logo_path), dark_image=Image.open(logo_path), size=(80, 80))
            self.logo_label = ctk.CTkLabel(self.header_frame, image=logo_image, text="")
            self.logo_label.grid(row=0, column=0, rowspan=2, padx=(0, 20))
        except:
            self.logo_label = ctk.CTkLabel(self.header_frame, text="ISS", font=("Roboto", 40, "bold"), text_color="#2f81f7", width=80)
            self.logo_label.grid(row=0, column=0, rowspan=2, padx=(0, 20))

        self.title_label = ctk.CTkLabel(self.header_frame, text="Insane Control Center", font=("Roboto", 26, "bold"), text_color="#c9d1d9")
        self.title_label.grid(row=0, column=1, sticky="sw")

        # --- STATUS PUNKT (NEBEN DEM TITEL) ---
        self.status_dot = ctk.CTkLabel(self.header_frame, text="●", font=("Roboto", 20), text_color="#444444")
        self.status_dot.grid(row=0, column=2, padx=(10, 0), sticky="sw")

        self.author_link = ctk.CTkLabel(self.header_frame, text="by BabeinlovexD ", font=("Roboto", 14, "italic"), text_color="#2f81f7", cursor="hand2")
        self.author_link.grid(row=1, column=1, sticky="nw")
        self.author_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_AUTHOR_URL))

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # ---------------------------------------------------------
        # SYSTEM AUSWAHL (Immer sichtbar)
        # ---------------------------------------------------------
        self.dev_ctrl_frame = ctk.CTkFrame(self.header_frame, fg_color="#161b22", border_width=1, border_color="#30363d", corner_radius=10)
        self.dev_ctrl_frame.grid(row=2, column=0, columnspan=3, pady=(20, 0), sticky="ew")

        inner_ctrl = ctk.CTkFrame(self.dev_ctrl_frame, fg_color="transparent")
        inner_ctrl.pack(pady=10, padx=20, fill="x")

        self.device_dropdown = ctk.CTkOptionMenu(inner_ctrl, values=["Suche läuft..."], state="disabled", height=35,
                                                fg_color="#0d1117", button_color="#21262d", button_hover_color="#30363d", command=self.on_device_select)
        self.device_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 1. Favoriten Button (Outline-Style mit Text)
        self.fav_btn = ctk.CTkButton(
            inner_ctrl, text="⭐ Merken", width=95, height=32,
            fg_color="transparent", border_width=1, border_color="#f1c40f",
            hover_color="#333333", text_color="#e3b341", font=("Roboto", 13, "bold"),
            command=self.save_favorite
        )
        self.fav_btn.pack(side="left", padx=(0, 5))

        self.del_fav_btn = ctk.CTkButton(
            inner_ctrl, text="✖ Löschen", width=95, height=32,
            fg_color="transparent", border_width=1, border_color="#c0392b",
            hover_color="#333333", text_color="#c0392b", font=("Roboto", 13, "bold"),
            command=self.delete_favorite
        )
        self.del_fav_btn.pack(side="left", padx=(0, 20))

        self.restart_btn = ctk.CTkButton(
            inner_ctrl, text="⚡ System Reset", width=120, height=32,
            fg_color="transparent", border_width=1, border_color="#e67e22",
            hover_color="#333333", text_color="#d29922", font=("Roboto", 13, "bold"),
            command=self.restart_bluetooth
        )
        self.restart_btn.pack(side="left", padx=(0, 5))

        # ---------------------------------------------------------
        # TABS EINRICHTEN
        # ---------------------------------------------------------
        self.tabview = ctk.CTkTabview(self.main_area, segmented_button_selected_color="#2f81f7", segmented_button_fg_color="#161b22", segmented_button_unselected_color="#161b22", segmented_button_unselected_hover_color="#30363d", fg_color="transparent")
        self.tabview.pack(fill="both", expand=True)

        self.tab_ctrl = self.tabview.add(" 🕹️ Steuerung ")
        self.tab_tele = self.tabview.add(" 📊 Telemetrie ")
        self.tab_upd = self.tabview.add(" ⚡ Updates ")
        self.tab_log = self.tabview.add(" 📝 Log ")
        self.tab_info = self.tabview.add(" ℹ️ Credits & Links ")

        self.setup_tab_ctrl()
        self.setup_tab_tele()
        self.setup_tab_upd()
        self.setup_tab_log()
        self.setup_tab_info()

        # --- FOOTER ---
        self.footer_label = ctk.CTkLabel(
            self,
            text="© 2026 BabeinlovexD",
            font=("Roboto", 10),
            text_color="#555555"
        )
        self.footer_label.pack(side="bottom", pady=(0, 10))

        self.sync_timer = None

        # Favoriten laden und Scan starten (Deine bestehenden Zeilen)
        self.load_favorites()
        self.start_scan()

    def setup_tab_tele(self):
        self.info_grid = ctk.CTkFrame(self.tab_tele, fg_color="#0d1117", corner_radius=10)
        self.info_grid.pack(pady=15, padx=20, fill="both", expand=True)
        self.info_grid.columnconfigure((0, 1, 2), weight=1)

        def create_stat(row, col, label_text, is_temp=False):
            lbl = ctk.CTkLabel(self.info_grid, text=label_text, font=("Roboto", 11, "bold"), text_color="#8b949e")
            lbl.grid(row=row*2, column=col, sticky="w", padx=15, pady=(10, 0))
            if is_temp:
                container = ctk.CTkFrame(self.info_grid, fg_color="transparent")
                container.grid(row=row*2+1, column=col, sticky="ew", padx=15, pady=(0, 10))
                val = ctk.CTkLabel(container, text="-", font=("Roboto", 14, "bold"), text_color="#c9d1d9")
                val.pack(anchor="w")
                bar = ctk.CTkProgressBar(container, height=6, fg_color="#21262d")
                bar.set(0)
                bar.pack(fill="x", pady=(4, 0))
                return val, bar
            else:
                val = ctk.CTkLabel(self.info_grid, text="-", font=("Roboto", 14, "bold"), text_color="#c9d1d9")
                val.grid(row=row*2+1, column=col, sticky="w", padx=15, pady=(0, 10))
                return val

        self.val_src = create_stat(0, 0, "ACTIVE INPUT")
        self.val_sys = create_stat(0, 1, "SOUNDBAR STATUS")
        self.val_wifi = create_stat(0, 2, "WLAN SIGNAL")

        self.val_temp_esp = create_stat(1, 0, "MASTER TEMP", is_temp=True)
        self.val_temp_dsp = create_stat(1, 1, "DSP TEMP", is_temp=True)
        self.val_amp_stat = create_stat(1, 2, "AMP FAULT")

        self.val_sub_conn = create_stat(2, 0, "SUB CONN")
        self.val_bl_conn = create_stat(2, 1, "BT CONN")
        self.val_dummy = create_stat(2, 2, "")

    def setup_tab_upd(self):
        # Mache den ganzen Updates Tab scrollbar
        self.upd_scroll = ctk.CTkScrollableFrame(self.tab_upd, fg_color="transparent")
        self.upd_scroll.pack(fill="both", expand=True)

        # Bluetooth / BT_RX (ESP32)
        self.sec_btrx = ctk.CTkFrame(self.upd_scroll, fg_color="#161b22", border_width=1, border_color="#30363d", corner_radius=10)
        self.sec_btrx.pack(pady=10, padx=20, fill="x")

        btrx_top = ctk.CTkFrame(self.sec_btrx, fg_color="transparent")
        btrx_top.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(btrx_top, text="ESP32 (BT_RX / BLUETOOTH)", font=("Roboto", 14, "bold"), text_color="#2f81f7").pack(side="left")

        self.btrx_fw_label = ctk.CTkLabel(self.sec_btrx, text="Aktuelle Version: [N/A]", font=("Roboto", 13))
        self.btrx_fw_label.pack(pady=5)

        self.btrx_status = ctk.CTkLabel(self.sec_btrx, text="Bereit.", font=("Roboto", 12), text_color="#8b949e")
        self.btrx_status.pack(pady=(0, 10))

        self.btrx_flash_btn = ctk.CTkButton(
            self.sec_btrx, text="BT_RX UPDATE", fg_color="#7a1a1a", hover_color="#9b1b1b", height=40, font=("Roboto", 14, "bold"),
            command=lambda: self.start_flash_thread("btrx")
        )
        self.btrx_flash_btn.pack(pady=(0, 15), padx=20, fill="x")

        # Subwoofer / SUB_TX (ESP32)
        self.sec_subtx = ctk.CTkFrame(self.upd_scroll, fg_color="#161b22", border_width=1, border_color="#30363d", corner_radius=10)
        self.sec_subtx.pack(pady=10, padx=20, fill="x")

        subtx_top = ctk.CTkFrame(self.sec_subtx, fg_color="transparent")
        subtx_top.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(subtx_top, text="ESP32 (SUB_TX / SUBWOOFER)", font=("Roboto", 14, "bold"), text_color="#3fb950").pack(side="left")

        self.subtx_fw_label = ctk.CTkLabel(self.sec_subtx, text="Aktuelle Version: [N/A]", font=("Roboto", 13))
        self.subtx_fw_label.pack(pady=5)

        self.subtx_status = ctk.CTkLabel(self.sec_subtx, text="Bereit.", font=("Roboto", 12), text_color="#8b949e")
        self.subtx_status.pack(pady=(0, 10))

        self.subtx_flash_btn = ctk.CTkButton(
            self.sec_subtx, text="SUB_TX UPDATE", fg_color="#7a1a1a", hover_color="#9b1b1b", height=40, font=("Roboto", 14, "bold"),
            command=lambda: self.start_flash_thread("subtx")
        )
        self.subtx_flash_btn.pack(pady=(0, 15), padx=20, fill="x")

        # DSP (RP2354)
        self.sec_rp = ctk.CTkFrame(self.upd_scroll, fg_color="#161b22", border_width=1, border_color="#30363d", corner_radius=10)
        self.sec_rp.pack(pady=10, padx=20, fill="x")


        rp_top = ctk.CTkFrame(self.sec_rp, fg_color="transparent")
        rp_top.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(rp_top, text="RP2354A (DSP)", font=("Roboto", 14, "bold"), text_color="#d29922").pack(side="left")

        self.rp_fw_label = ctk.CTkLabel(self.sec_rp, text="Aktuelle Version: [N/A]", font=("Roboto", 13))
        self.rp_fw_label.pack(pady=5)

        self.rp_status = ctk.CTkLabel(self.sec_rp, text="Bereit.", font=("Roboto", 12), text_color="#8b949e")
        self.rp_status.pack(pady=(0, 10))

        self.rp_flash_btn = ctk.CTkButton(
            self.sec_rp, text="RP2354 UPDATE", fg_color="#7a1a1a", hover_color="#9b1b1b", height=40, font=("Roboto", 14, "bold"),
            command=lambda: self.start_flash_thread("rp2354")
        )
        self.rp_flash_btn.pack(pady=(0, 15), padx=20, fill="x")

        # Globaler Fortschrittsbalken für Flash Vorgänge (Initial unsichtbar)
        self.flash_progress = ctk.CTkProgressBar(self.upd_scroll, height=15, fg_color="#21262d", progress_color="#3b8ed0")
        self.flash_progress.set(0)

    def setup_tab_log(self):
        self.log_box = ctk.CTkTextbox(self.tab_log, width=700, height=400, font=("Consolas", 12), state="disabled", fg_color="#0d1117")
        self.log_box.pack(pady=20, padx=20, fill="both", expand=True)

    def log(self, msg):
        self.log_box.configure(state="normal")
        self.log_box.insert("end", msg + "\n")
        self.log_box.see("end")
        self.log_box.configure(state="disabled")

    def start_log_stream(self, ip):
        self.log_running = False # Stoppe alten Thread falls existent
        if self.log_thread and self.log_thread.is_alive():
            self.log_thread.join(timeout=1)

        self.log_box.configure(state="normal")
        self.log_box.delete("0.0", "end")
        self.log_box.insert("0.0", f"--- Verbinde mit Live-Log von {ip} ---\n")
        self.log_box.configure(state="disabled")

        self.log_running = True
        self.log_thread = threading.Thread(target=self._log_stream_task, args=(ip,), daemon=True)
        self.log_thread.start()

    def _log_stream_task(self, ip):
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
        url = f"http://{ip}/events"
        try:
            with self.session.get(url, stream=True, timeout=5) as r:
                for line in r.iter_lines(decode_unicode=True):
                    if not self.log_running:
                        break
                    if line:
                        if line.startswith("event: log"):
                            continue
                        if line.startswith("data: "):
                            raw_log = line[6:]
                            clean_log = ansi_escape.sub('', raw_log)
                            self.after(0, self.log, clean_log)
        except Exception as e:
            if self.log_running:
                self.after(0, self.log, f"Log-Verbindung getrennt: {e}")

    def setup_tab_info(self):
        info_frame = ctk.CTkFrame(self.tab_info, fg_color="transparent")
        info_frame.pack(pady=50)

        try:
            logo_path = resource_path("logo.png")
            logo_image = ctk.CTkImage(light_image=Image.open(logo_path), dark_image=Image.open(logo_path), size=(150, 150))
            ctk.CTkLabel(info_frame, image=logo_image, text="").pack(pady=10)
        except: pass

        ctk.CTkLabel(info_frame, text="Insane Control Center", font=("Roboto", 24, "bold")).pack(pady=10)
        ctk.CTkLabel(info_frame, text="Version 1.0.0", font=("Roboto", 14), text_color="#8b949e", justify="center").pack(pady=5)


        btn = ctk.CTkButton(info_frame, text="GitHub Repository", fg_color="#21262d", height=40, command=lambda: webbrowser.open(GITHUB_URL))
        btn.pack(pady=20)

        tools_frame = ctk.CTkFrame(info_frame, fg_color="transparent")
        tools_frame.pack(pady=10)
        ctk.CTkLabel(tools_frame, text="Powered by Open Source Tools:", font=("Roboto", 12, "bold")).pack(pady=5)

        btn_esptool = ctk.CTkButton(tools_frame, text="esptool.py", fg_color="transparent", text_color="#2f81f7", hover_color="#30363d", command=lambda: webbrowser.open("https://github.com/espressif/esptool"))
        btn_esptool.pack()

        btn_ctk = ctk.CTkButton(tools_frame, text="CustomTkinter", fg_color="transparent", text_color="#2f81f7", hover_color="#30363d", command=lambda: webbrowser.open("https://customtkinter.tomschimansky.com/"))
        btn_ctk.pack()

    def setup_tab_ctrl(self):
        scroll_frame = ctk.CTkScrollableFrame(self.tab_ctrl, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)

        # --- SYSTEM STEUERUNG ---
        ctk.CTkLabel(scroll_frame, text="System", font=("Roboto", 20, "bold"), text_color="#2f81f7").pack(pady=(10, 10))

        sys_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        sys_frame.pack(pady=5, fill="x", padx=40)

        ctk.CTkLabel(sys_frame, text="Input Source", font=("Roboto", 14)).pack(pady=(0, 5))
        self.input_dropdown = ctk.CTkOptionMenu(sys_frame, values=["Toslink", "Aux", "Bluetooth", "WLAN"], command=lambda val: self.send_select_value("Input Source", val))
        self.input_dropdown.pack(fill="x", pady=(0, 15))
        ctk.CTkLabel(sys_frame, text="IR Learn Target", font=("Roboto", 14)).pack(pady=(0, 5))
        self.ir_dropdown = ctk.CTkOptionMenu(sys_frame, values=["None", "Vol+", "Vol-", "Mute", "Input Next"], command=lambda val: self.send_select_value("IR Learn Target", val))
        self.ir_dropdown.pack(fill="x", pady=(0, 15))

        btn_row = ctk.CTkFrame(sys_frame, fg_color="transparent")
        btn_row.pack(pady=10)

        encoded_pair = __import__('urllib').parse.quote("Pair Subwoofer")
        ctk.CTkButton(btn_row, text="🔊 Pair Subwoofer", width=140, height=45, corner_radius=20, fg_color="#e67e22", hover_color="#d35400", command=lambda: self.send_action(f"button/{encoded_pair}/press")).pack(side="left", padx=15)

        encoded_clear_ir = __import__('urllib').parse.quote("Alle IR-Codes löschen")
        ctk.CTkButton(btn_row, text="🗑 Clear IR", width=140, height=45, corner_radius=20, fg_color="#c0392b", hover_color="#922b21", command=lambda: self.send_action(f"button/{encoded_clear_ir}/press")).pack(side="left", padx=15)

        encoded_learn = __import__('urllib').parse.quote("Start IR Learn")
        ctk.CTkButton(btn_row, text="🎯 IR Learn", width=140, height=45, corner_radius=20, fg_color="#3498db", hover_color="#2980b9", command=lambda: self.send_action(f"button/{encoded_learn}/press")).pack(side="left", padx=15)

        # Helper to create slider with live value label
        def create_live_slider(parent, title, from_val, to_val, steps, entity_name, color, hover, init_val=None):
            container = ctk.CTkFrame(parent, fg_color="transparent")
            container.pack(fill="x", pady=(0, 15))

            top_bar = ctk.CTkFrame(container, fg_color="transparent")
            top_bar.pack(fill="x")

            lbl_title = ctk.CTkLabel(top_bar, text=title, font=("Roboto", 12))
            lbl_title.pack(side="left")

            lbl_val = ctk.CTkLabel(top_bar, text=str(init_val if init_val is not None else from_val), font=("Roboto", 12, "bold"))
            lbl_val.pack(side="right")

            # Store timer ID as an attribute of the slider object
            timer_holder = {"id": None}

            def on_slider_change(val):
                lbl_val.configure(text=str(int(val)))

                if timer_holder["id"] is not None:
                    self.after_cancel(timer_holder["id"])

                timer_holder["id"] = self.after(200, lambda: self.send_number_value(entity_name, val))

            slider = ctk.CTkSlider(container, from_=from_val, to=to_val, number_of_steps=steps, button_color=color, button_hover_color=hover, command=on_slider_change)
            if init_val is not None:
                slider.set(init_val)
            slider.pack(fill="x", pady=(5, 0))
            return slider

        # --- VOLUME & BRIGHTNESS ---
        ctk.CTkLabel(scroll_frame, text="Allgemein", font=("Roboto", 18, "bold"), text_color="#3fb950").pack(pady=(20, 10))
        gen_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        gen_frame.pack(pady=5, fill="x", padx=40)

        self.vol_slider = create_live_slider(gen_frame, "Master Volume (0-100)", 0, 100, 100, "Master Volume", "#2ecc71", "#27ae60", 50)
        self.bright_slider = create_live_slider(gen_frame, "OLED Brightness (0-100)", 0, 100, 100, "OLED Brightness", "#3498db", "#2980b9", 100)

        # --- CROSSOVERS ---
        ctk.CTkLabel(scroll_frame, text="Frequenzweichen (Crossovers)", font=("Roboto", 18, "bold"), text_color="#d29922").pack(pady=(20, 10))
        cross_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        cross_frame.pack(pady=5, fill="x", padx=40)

        self.sub_lp = create_live_slider(cross_frame, "Sub LP Crossover", 50, 255, 205, "Sub LP Crossover", "#e67e22", "#d35400", 120)
        self.sat_hp = create_live_slider(cross_frame, "Sat HP Crossover", 50, 255, 205, "Sat HP Crossover", "#e67e22", "#d35400", 95)
        self.mid_lp = create_live_slider(cross_frame, "Mid LP Crossover", 500, 10000, 95, "Mid LP Crossover", "#e67e22", "#d35400", 3500)
        self.high_hp = create_live_slider(cross_frame, "High HP Crossover", 500, 10000, 95, "High HP Crossover", "#e67e22", "#d35400", 3500)

        # --- EQ ---
        ctk.CTkLabel(scroll_frame, text="Equalizer", font=("Roboto", 18, "bold"), text_color="#e3b341").pack(pady=(20, 10))
        eq_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        eq_frame.pack(pady=5, fill="x", padx=40)

        self.sub_trim = create_live_slider(eq_frame, "Sub Trim", 0, 20, 20, "Sub Trim", "#f1c40f", "#f39c12", 10)

        bands = [
            ("EQ Band 1 (60Hz)", "EQ Band 1"),
            ("EQ Band 2 (230Hz)", "EQ Band 2"),
            ("EQ Band 3 (910Hz)", "EQ Band 3"),
            ("EQ Band 4 (3.6kHz)", "EQ Band 4"),
            ("EQ Band 5 (14kHz)", "EQ Band 5")
        ]

        self.eq_sliders = []
        for label, entity in bands:
            sl = create_live_slider(eq_frame, label, 0, 20, 20, entity, "#f1c40f", "#f39c12", 10)
            self.eq_sliders.append(sl)

    def send_action(self, endpoint):
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return
        import threading
        threading.Thread(target=lambda: self.session.post(f"http://{ip}/{endpoint}", timeout=2), daemon=True).start()

    def send_number_value(self, entity_name, value):
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return
        import urllib.parse
        encoded_name = urllib.parse.quote(entity_name)
        import threading
        threading.Thread(target=lambda: self.session.post(f"http://{ip}/number/{encoded_name}/set?value={int(value)}", timeout=2), daemon=True).start()

    def send_select_value(self, entity_name, value):
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return
        import urllib.parse
        encoded_name = urllib.parse.quote(entity_name)
        encoded_val = urllib.parse.quote(value)
        import threading
        threading.Thread(target=lambda: self.session.post(f"http://{ip}/select/{encoded_name}/set?option={encoded_val}", timeout=2), daemon=True).start()

    # --- LOGIK FUNKTIONEN ---
    def add_device_to_ui(self, name, ip):
        base_name = f"{name} ({ip})"
        self.scanned_devices[base_name] = ip
        self.after(0, self._update_dropdown)

    def _update_dropdown(self):
        current = self.device_dropdown.get()
        self.dropdown_mapping.clear()

        # 1. Favoriten hinzufügen (bekommen den Stern)
        for name, ip in self.favorite_devices.items():
            self.dropdown_mapping[f"{name} ⭐"] = ip

        # 2. Gescannte Boxen hinzufügen (die noch kein Favorit sind)
        for name, ip in self.scanned_devices.items():
            if name not in self.favorite_devices:
                self.dropdown_mapping[name] = ip

        vals = list(self.dropdown_mapping.keys())

        if vals:
            self.device_dropdown.configure(values=vals, state="normal")

            # Intelligente Auswahl: Verliert nicht den Fokus, wenn ein Stern dazu kommt/weggeht
            if current == "Suche läuft...":
                self.device_dropdown.set(vals[0])
                self.sync_live_data()
            elif current not in vals:
                base_current = current.replace(" ⭐", "")
                if f"{base_current} ⭐" in vals:
                    self.device_dropdown.set(f"{base_current} ⭐")
                elif base_current in vals:
                    self.device_dropdown.set(base_current)
                else:
                    self.device_dropdown.set(vals[0])
                    self.sync_live_data()

    def load_favorites(self):
        config_file = get_config_path()
        if os.path.exists(config_file):
            try:
                with open(config_file, "r") as f:
                    self.favorite_devices = json.load(f)
                self._update_dropdown()
            except: pass

    def save_favorite(self):
        current = self.device_dropdown.get()
        if current and current != "Suche läuft...":
            base_name = current.replace(" ⭐", "") # Falls er schon einen Stern hat, abschneiden
            ip = self.dropdown_mapping.get(current)

            if ip:
                self.favorite_devices[base_name] = ip
                try:
                    with open(get_config_path(), "w") as f:
                        json.dump(self.favorite_devices, f)
                    messagebox.showinfo("Favorit", f"{base_name} wurde gespeichert!")
                    self._update_dropdown() # Aktualisiert sofort das Dropdown (Stern taucht auf)
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Speichern:\n{e}")

    def delete_favorite(self):
        current = self.device_dropdown.get()
        if current and current != "Suche läuft...":
            base_name = current.replace(" ⭐", "")

            if base_name in self.favorite_devices:
                del self.favorite_devices[base_name]
                try:
                    with open(get_config_path(), "w") as f:
                        json.dump(self.favorite_devices, f)
                    self._update_dropdown() # Aktualisiert das Dropdown (Stern verschwindet, Box bleibt)
                except Exception as e:
                    messagebox.showerror("Fehler", f"Fehler beim Löschen:\n{e}")

    def on_device_select(self, choice):
        self.sync_live_data()

    def start_scan(self):
        self.scanned_devices.clear() # <--- WICHTIG: Alter Name geändert!

        # Nur auf "Suche läuft..." setzen und sperren, wenn wir KEINE Favoriten haben
        if not self.favorite_devices:
            self.device_dropdown.configure(values=["Suche läuft..."], state="disabled")
            self.device_dropdown.set("Suche läuft...")

        ServiceBrowser(self.zeroconf, "_esphomelib._tcp.local.", DeviceListener(self.add_device_to_ui))

    def restart_bluetooth(self):
        # Zwingt den S3, den EN-Pin des Bluetooth-Chips auf LOW und wieder HIGH zu ziehen
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return

        try:
            # Wir nutzen deinen in YAML definierten Normal Boot: Bluetooth (ESP32) Button!
            encoded_btn = urllib.parse.quote("Normal Boot: Bluetooth (ESP32)")
            self.session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=3)
            messagebox.showinfo("Hardware Reset", "⚡ Befehl gesendet!\nDer S3 startet den Bluetooth-Chip (BT_RX) jetzt hart neu.")
        except Exception as e:
            messagebox.showerror("Netzwerk Fehler", f"Konnte den Neustart-Befehl nicht senden:\n{e}")
    # --- TELEMETRY DASHBOARD FUNKTIONEN ---

    def sync_live_data(self):
        # ---Alten Timer abbrechen, falls wir die Box im Dropdown wechseln ---
        if hasattr(self, 'sync_timer') and self.sync_timer:
            self.after_cancel(self.sync_timer)
            self.sync_timer = None

        if self.is_fetching: return
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip:
            # Falls keine Box gewählt ist, in 2 Sek nochmal schauen (Timer-ID speichern!)
            self.sync_timer = self.after(2000, self.sync_live_data)
            return
        self.is_fetching = True
        threading.Thread(target=self._fetch_api_data, args=(ip,), daemon=True).start()
        # FIX: Log-Stream nur starten, wenn sich die IP geändert hat
        if getattr(self, 'current_log_ip', None) != ip:
            self.current_log_ip = ip
            self.start_log_stream(ip)

    def _fetch_api_data(self, ip):
        def get_state(domain, entity_name):
            try:
                # Nutze urllib.parse.quote für ESPHome 2026.x Deprecated URL Warnungen
                encoded_name = urllib.parse.quote(entity_name)
                url = f"http://{ip}/{domain}/{encoded_name}"
                # Nutze die self.session (Requests) für Keep-Alive
                r = self.session.get(url, timeout=2).json()
                return r.get("state", "N/A")
            except: return "Offline"

        # Daten abrufen (Exakte Namen aus dem YAML anstelle von Objekt-IDs)
        src = get_state("text_sensor", "Active Input")
        sys_status = get_state("light", "Soundbar Status")
        t_esp = get_state("sensor", "Master Temperature")
        t_dsp = get_state("sensor", "DSP Temperature")
        fault = get_state("binary_sensor", "Verstärker Überlastung (Fault)")
        wifi = get_state("sensor", "WLAN Signal")
        btrx_version = get_state("text_sensor", "BT Version")
        subtx_version = get_state("text_sensor", "SUB Version")
        rp_version = get_state("text_sensor", "DSP Version")
        # For BT Conn and SUB Conn, they are inferred from version presence or specific binary_sensors if they exist
        # We know "subwoofer_connected" might be a binary sensor from previous step, but let's check BT as well.
        # Actually, if we don't know, we can fall back to checking if the version string is present!
        bt_conn = get_state("text_sensor", "BT Version")
        sub_conn = get_state("text_sensor", "SUB Version")

        import time
        current_time = time.time()

        # Check GitHub version only occasionally to avoid rate limiting
        if current_time - self.last_update_check > UPDATE_CHECK_INTERVAL:
            self.last_update_check = current_time
            try:
                # Fetch latest release info
                release_info = requests.get(GITHUB_API_LATEST, timeout=3).json()
                self.online_version = release_info.get("tag_name", "2.1.0.0")
                # Look for specific assets if you like, else we will fall back to static logic for now.
                self.github_assets = release_info.get("assets", [])
            except:
                self.online_version = None

        self.after(0, self._update_dashboard_ui, src, sys_status, t_esp, t_dsp, fault, wifi, bt_conn, sub_conn)
        self.after(0, lambda: self.check_for_updates(btrx_version, subtx_version, rp_version))

    def _update_dashboard_ui(self, src, sys_status, t_esp, t_dsp, fault, wifi, bt_conn, sub_conn):
        def set_val(lbl, text, color="#ffffff"):
            if lbl != self.val_dummy:
                lbl.configure(text=str(text), text_color=color)

        is_online = src != "Offline" and wifi != "Offline"

        if is_online:
            self.status_dot.configure(text_color="#3fb950")
        else:
            self.status_dot.configure(text_color="#e74c3c")

        set_val(self.val_src, src, "#3498db")
        set_val(self.val_sys, sys_status.upper() if sys_status != "Offline" else "N/A", "#2ecc71" if sys_status == "ON" else "#888888")
        set_val(self.val_wifi, f"{wifi} dBm" if wifi != "Offline" else wifi)

        def parse_temp(val):
            try: return float(val), f"{val} °C"
            except: return 0.0, str(val)

        def update_temp_ui(ui_elements, temp_val, temp_str):
            val_lbl, pbar = ui_elements
            val_lbl.configure(text=temp_str, text_color="#e74c3c" if temp_val > 50 else "#ffffff")
            progress = max(0.0, min(1.0, (temp_val - 20) / 60))
            pbar.set(progress)
            if temp_val >= 60: pbar.configure(progress_color="#e74c3c")
            elif temp_val >= 45: pbar.configure(progress_color="#f39c12")
            else: pbar.configure(progress_color="#2ecc71")

        update_temp_ui(self.val_temp_esp, *parse_temp(t_esp))
        update_temp_ui(self.val_temp_dsp, *parse_temp(t_dsp))

        set_val(self.val_amp_stat, "FAULT" if fault == "ON" else "OK", "#e74c3c" if fault == "ON" else "#2ecc71")

        is_bt_conn = bt_conn != "Offline" and bt_conn != "N/A"
        set_val(self.val_bl_conn, "VERBUNDEN" if is_bt_conn else "GETRENNT", "#3498db" if is_bt_conn else "#888888")

        is_sub_conn = sub_conn != "Offline" and sub_conn != "N/A"
        set_val(self.val_sub_conn, "VERBUNDEN" if is_sub_conn else "GETRENNT", "#e67e22" if is_sub_conn else "#888888")


        self.is_fetching = False

        self.sync_timer = self.after(1000, self.sync_live_data)

    # --- FLASHING FUNKTIONEN ---
    def start_flash_thread(self, target):
        threading.Thread(target=self.run_flash, args=(target,), daemon=True).start()

    def run_flash(self, target):
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return

        if target == "btrx":
            btn = self.btrx_flash_btn
            status_lbl = self.btrx_status
        elif target == "subtx":
            btn = self.subtx_flash_btn
            status_lbl = self.subtx_status
        else:
            btn = self.rp_flash_btn
            status_lbl = self.rp_status

        self.after(0, lambda: btn.configure(state="disabled", text="LADE FIRMWARE..."))

        try:
            self.after(0, lambda: self.flash_progress.pack(pady=10, padx=20, fill="x"))
            self.after(0, lambda: self.flash_progress.set(0.0))

            self.after(0, lambda: status_lbl.configure(text="Schritt 0: Lade Firmware von GitHub...", text_color="orange"))

            download_url = None
            if hasattr(self, 'github_assets') and self.github_assets:
                for asset in self.github_assets:
                    if target.lower() in asset['name'].lower():
                        download_url = asset['browser_download_url']
                        break

            if not download_url:
                if target == "btrx":
                    download_url = "https://raw.githubusercontent.com/babeinlovexd/Insane-Sound-System/main/Firmware/Bluetooth/firmware.bin"
                elif target == "subtx":
                    download_url = "https://raw.githubusercontent.com/babeinlovexd/Insane-Sound-System/main/Firmware/SUB_TX/firmware.bin"
                else:
                    download_url = "https://raw.githubusercontent.com/babeinlovexd/Insane-Sound-System/main/Firmware/DSP/firmware.bin"

            r = requests.get(download_url, timeout=15)
            r.raise_for_status()
            with open(get_firmware_path(), "wb") as f:
                f.write(r.content)

            self.after(0, lambda: btn.configure(text="FLASHING..."))

            if target == "btrx" or target == "subtx":
                target_name_ui = "BT_RX" if target == "btrx" else "SUB_TX"
                port = 8083 if target == "btrx" else 8082
                button_encoded = urllib.parse.quote("Flash Mode: Bluetooth (ESP32)" if target == "btrx" else "Flash Mode: Sub-TX (ESP32)")

                self.after(0, lambda: status_lbl.configure(text=f"Schritt 1: Setze {target_name_ui} in Flash-Modus...", text_color="orange"))
                self.session.post(f"http://{ip}/button/{button_encoded}/press", timeout=5)

                import time
                time.sleep(2)

                self.after(0, lambda: status_lbl.configure(text=f"Schritt 2: Flashe {target_name_ui} Firmware...", text_color="orange"))

                command_args = [
                    "--port", f"socket://{ip}:{port}",
                    "--baud", "115200",
                    "write_flash", "0x10000", get_firmware_path()
                ]

                def gui_update(msg):
                    text = f"Flashing: {msg.split('...')[0]}..." if "..." in msg else msg
                    self.after(0, lambda: status_lbl.configure(text=text))
                    self.after(0, self.log, msg)
                    if "(" in msg and "%" in msg:
                        try:
                            pct_str = msg.split("(")[1].split("%")[0].strip()
                            pct = float(pct_str) / 100.0
                            self.after(0, lambda: self.flash_progress.set(pct))
                        except: pass

                redirector = ConsoleRedirector(gui_update)
                with contextlib.redirect_stdout(redirector):
                    esptool.main(command_args)

                self.after(0, lambda: status_lbl.configure(text=f"Schritt 3: {target_name_ui} Neustart...", text_color="orange"))
                encoded_btn = urllib.parse.quote("Normal Boot: Bluetooth (ESP32)" if target == "btrx" else "Normal Boot: Sub-TX (ESP32)")
                self.session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=5)

            elif target == "rp2354":
                self.after(0, lambda: status_lbl.configure(text="Schritt 1: Setze RP2354 in Flash-Modus...", text_color="orange"))
                encoded_btn = urllib.parse.quote("Flash Mode: DSP (RP2354)")
                self.session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=5)

                import time
                time.sleep(2)

                self.after(0, lambda: status_lbl.configure(text="Schritt 2: Flashe RP2354 Firmware...", text_color="orange"))

                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(15)
                    s.connect((ip, 8081))

                    with open(get_firmware_path(), 'rb') as f:
                        fw_data = f.read()

                    file_size = len(fw_data)

                    self.after(0, lambda: status_lbl.configure(text="Schritt 2: Sende RP2354 Knock Sequence...", text_color="orange"))
                    # Knock sequence: 0x56, 0xff, 0x8b, 0xe4
                    s.sendall(bytes([0x56, 0xff, 0x8b, 0xe4]))

                    # NOP test to ensure interface is awake
                    s.sendall(b'n')
                    resp = s.recv(1)
                    if resp != b'n':
                        s.sendall(bytes([0x56, 0xff, 0x8b, 0xe4]))
                        s.sendall(b'n')
                        resp = s.recv(1)
                        if resp != b'n':
                            raise Exception("RP2354 UART Bootloader antwortet nicht auf Knock.")

                    self.after(0, lambda: status_lbl.configure(text="Schritt 3: Flashe 32-Byte Blöcke...", text_color="orange"))

                    sent = 0
                    last_pct_sent = -1

                    for i in range(0, file_size, 32):
                        chunk = fw_data[i:i+32]
                        if len(chunk) < 32:
                            # padding with 0x00
                            chunk += bytes([0x00] * (32 - len(chunk)))

                        s.sendall(b'w')
                        s.sendall(chunk)

                        resp = s.recv(1)
                        if resp != b'w':
                            raise Exception(f"RP2354 Schreibfehler bei Offset {i}")

                        sent += len(chunk)
                        pct = min(sent / file_size, 1.0)

                        if int(pct * 100) > last_pct_sent:
                            self.after(0, lambda p=pct: self.flash_progress.set(p))
                            self.after(0, lambda p=pct: status_lbl.configure(text=f"Flashing: {int(p*100)}%"))
                            last_pct_sent = int(pct * 100)

                    self.after(0, lambda: status_lbl.configure(text="Schritt 4: Starte RP2354 Firmware...", text_color="orange"))
                    # Send execute command
                    s.sendall(b'x')
                    try:
                        s.recv(1) # wait for echo
                    except socket.timeout:
                        pass # Ignore timeout on final echo because reboot happens instantly

                self.after(0, lambda: status_lbl.configure(text="Schritt 3: RP2354 geflasht. Reboot.", text_color="orange"))
                encoded_btn = urllib.parse.quote("Normal Boot: DSP (RP2354)")
                self.session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=5)

            self.after(0, lambda: status_lbl.configure(text="🚀 Update 100% erfolgreich!", text_color="#3fb950"))
            self.after(0, lambda: messagebox.showinfo("Update", f"{target.upper()} wurde erfolgreich aktualisiert!"))

        except (requests.exceptions.RequestException, socket.error) as e:
            self.after(0, lambda: status_lbl.configure(text="❌ Netzwerk weg / Verbindung fehlgeschlagen!", text_color="red"))
            self.after(0, self.log, f"Verbindungsfehler: {e}")
        except SystemExit as e:
            if e.code != 0:
                self.after(0, lambda: status_lbl.configure(text="❌ Flashen fehlgeschlagen (esptool error)!", text_color="red"))
        except Exception as e:
            self.after(0, lambda err=e: status_lbl.configure(text=f"❌ Flashen fehlgeschlagen: {err}", text_color="red"))
            self.after(0, self.log, f"Fehler: {e}")
        finally:
            self.after(0, lambda: btn.configure(state="normal", text=f"{target.upper()} UPDATE"))
            self.after(0, lambda: self.flash_progress.pack_forget())

    def check_for_updates(self, btrx_version, subtx_version, rp_version):
        if btrx_version == "N/A" or btrx_version == "Offline":
            self.btrx_fw_label.configure(text="Aktuelle Version: Offline", text_color="#8b949e")
        else:
            self.btrx_fw_label.configure(text=f"Aktuelle Version: [{btrx_version}]", text_color="#c9d1d9")

        if subtx_version == "N/A" or subtx_version == "Offline":
            self.subtx_fw_label.configure(text="Aktuelle Version: Offline", text_color="#8b949e")
        else:
            self.subtx_fw_label.configure(text=f"Aktuelle Version: [{subtx_version}]", text_color="#c9d1d9")

        if rp_version == "N/A" or rp_version == "Offline":
            self.rp_fw_label.configure(text="Aktuelle Version: Offline", text_color="#8b949e")
        else:
            self.rp_fw_label.configure(text=f"Aktuelle Version: [{rp_version}]", text_color="#c9d1d9")

        if self.online_version:
            if btrx_version != self.online_version and btrx_version != "Offline":
                self.btrx_flash_btn.configure(fg_color="#e74c3c", text="BT_RX UPDATE INSTALLIEREN")
            else:
                self.btrx_flash_btn.configure(fg_color="#7a1a1a", text="BT_RX UPDATE")

            if subtx_version != self.online_version and subtx_version != "Offline":
                self.subtx_flash_btn.configure(fg_color="#e74c3c", text="SUB_TX UPDATE INSTALLIEREN")
            else:
                self.subtx_flash_btn.configure(fg_color="#7a1a1a", text="SUB_TX UPDATE")

            if rp_version != self.online_version and rp_version != "Offline":
                self.rp_flash_btn.configure(fg_color="#e74c3c", text="RP2354 UPDATE INSTALLIEREN")
            else:
                self.rp_flash_btn.configure(fg_color="#7a1a1a", text="RP2354 UPDATE")


if __name__ == "__main__":
    app = InsaneControlCenter()
    app.mainloop()
