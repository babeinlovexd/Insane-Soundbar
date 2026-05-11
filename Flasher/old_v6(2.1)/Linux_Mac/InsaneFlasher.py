import customtkinter as ctk
from tkinter import messagebox
import socket
import threading
import requests
import webbrowser
import os
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
    myappid = 'babeinlovexd.insaneflasher.v5' 
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)
except:
    pass

# --- HILFSFUNKTION FÜR DIE .EXE ---
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def get_app_dir():
    # Holt sich den unsichtbaren AppData Ordner und erstellt das Insane-Verzeichnis
    base_dir = os.getenv('APPDATA') if os.name == 'nt' else os.path.expanduser('~')
    app_dir = os.path.join(base_dir, "InsaneFlasher")
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
GITHUB_URL = "https://github.com/babeinlovexd/Insane-Sound-System"
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

class InsaneFlasher(ctk.CTk):
    def __init__(self):
        super().__init__()

        # 1. FENSTER-SETUP
        self.title("Insane Control Center 2.1")
        self.geometry("800x700")
        self.configure(fg_color="#1a1a1a")
        
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
            self.logo_label = ctk.CTkLabel(self.header_frame, text="ISS", font=("Roboto", 40, "bold"), text_color="#3b8ed0", width=80)
            self.logo_label.grid(row=0, column=0, rowspan=2, padx=(0, 20))

        self.title_label = ctk.CTkLabel(self.header_frame, text="Insane Control Center 2.1", font=("Roboto", 26, "bold"), text_color="#ffffff")
        self.title_label.grid(row=0, column=1, sticky="sw")
        
        # --- STATUS PUNKT (NEBEN DEM TITEL) ---
        self.status_dot = ctk.CTkLabel(self.header_frame, text="●", font=("Roboto", 20), text_color="#444444")
        self.status_dot.grid(row=0, column=2, padx=(10, 0), sticky="sw")
        
        self.author_link = ctk.CTkLabel(self.header_frame, text="by BabeinlovexD ", font=("Roboto", 14, "italic"), text_color="#3b8ed0", cursor="hand2")
        self.author_link.grid(row=1, column=1, sticky="nw")
        self.author_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # ---------------------------------------------------------
        # SYSTEM AUSWAHL (Immer sichtbar)
        # ---------------------------------------------------------
        self.dev_ctrl_frame = ctk.CTkFrame(self.main_area, fg_color="#242424", corner_radius=10)
        self.dev_ctrl_frame.pack(pady=(0, 10), fill="x")

        inner_ctrl = ctk.CTkFrame(self.dev_ctrl_frame, fg_color="transparent")
        inner_ctrl.pack(pady=10, padx=20, fill="x")

        self.device_dropdown = ctk.CTkOptionMenu(inner_ctrl, values=["Suche läuft..."], state="disabled", height=35,
                                                fg_color="#1a1a1a", button_color="#333333", button_hover_color="#444444", command=self.on_device_select)
        self.device_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 1. Favoriten Button (Outline-Style mit Text)
        self.fav_btn = ctk.CTkButton(
            inner_ctrl, text="⭐ Merken", width=95, height=32,
            fg_color="transparent", border_width=1, border_color="#f1c40f", 
            hover_color="#333333", text_color="#f1c40f", font=("Roboto", 13, "bold"), 
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
            hover_color="#333333", text_color="#e67e22", font=("Roboto", 13, "bold"), 
            command=self.restart_bluetooth
        )
        self.restart_btn.pack(side="left", padx=(0, 5))

        # ---------------------------------------------------------
        # TABS EINRICHTEN
        # ---------------------------------------------------------
        self.tabview = ctk.CTkTabview(self.main_area, segmented_button_selected_color="#3b8ed0")
        self.tabview.pack(fill="both", expand=True)

        self.tab_ctrl = self.tabview.add("🕹️ Steuerung")
        self.tab_tele = self.tabview.add("📊 Telemetrie")
        self.tab_upd = self.tabview.add("⚡ Updates")
        self.tab_log = self.tabview.add("📝 Log")
        self.tab_info = self.tabview.add("ℹ️ Credits & Links")

        self.setup_tab_ctrl()
        self.setup_tab_tele()
        self.setup_tab_upd()
        self.setup_tab_log()
        self.setup_tab_info()

        # --- FOOTER ---
        self.footer_label = ctk.CTkLabel(
            self,
            text="© 2026 BabeinlovexD | Triple-Brain Architecture Hub",
            font=("Roboto", 10),
            text_color="#555555"
        )
        self.footer_label.pack(side="bottom", pady=(0, 10))

        self.sync_timer = None

        # Favoriten laden und Scan starten (Deine bestehenden Zeilen)
        self.load_favorites()
        self.start_scan()

    def setup_tab_tele(self):
        self.info_grid = ctk.CTkFrame(self.tab_tele, fg_color="#1a1a1a", corner_radius=10)
        self.info_grid.pack(pady=15, padx=20, fill="both", expand=True)
        self.info_grid.columnconfigure((0, 1, 2), weight=1)

        def create_stat(row, col, label_text, is_temp=False):
            lbl = ctk.CTkLabel(self.info_grid, text=label_text, font=("Roboto", 11, "bold"), text_color="#888888")
            lbl.grid(row=row*2, column=col, sticky="w", padx=15, pady=(10, 0))
            if is_temp:
                container = ctk.CTkFrame(self.info_grid, fg_color="transparent")
                container.grid(row=row*2+1, column=col, sticky="ew", padx=15, pady=(0, 10))
                val = ctk.CTkLabel(container, text="-", font=("Roboto", 14, "bold"), text_color="#ffffff")
                val.pack(anchor="w")
                bar = ctk.CTkProgressBar(container, height=6, fg_color="#333333")
                bar.set(0)
                bar.pack(fill="x", pady=(4, 0))
                return val, bar
            else:
                val = ctk.CTkLabel(self.info_grid, text="-", font=("Roboto", 14, "bold"), text_color="#ffffff")
                val.grid(row=row*2+1, column=col, sticky="w", padx=15, pady=(0, 10))
                return val

        self.val_src = create_stat(0, 0, "AUDIO QUELLE")
        self.val_sys = create_stat(0, 1, "SYSTEM STATUS")
        self.val_wifi = create_stat(0, 2, "WLAN SIGNAL")

        self.val_temp_amp = create_stat(1, 0, "TEMP VERSTÄRKER", is_temp=True)
        self.val_temp_esp = create_stat(1, 1, "TEMP ESP32", is_temp=True)
        self.val_temp_dsp = create_stat(1, 2, "TEMP DSP", is_temp=True)

        self.val_bl_stat = create_stat(2, 0, "MEDIA STATUS")
        self.val_bl_song = create_stat(2, 1, "MEDIA TITEL")
        self.val_bl_art = create_stat(2, 2, "MEDIA INTERPRET")

        self.val_fan = create_stat(3, 0, "LÜFTER SPEED")
        self.val_amp_stat = create_stat(3, 1, "AMP FAULT")
        self.val_bl_conn = create_stat(3, 2, "BT CONN")

    def setup_tab_upd(self):
        self.sec_wroom = ctk.CTkFrame(self.tab_upd, fg_color="#242424", corner_radius=10)
        self.sec_wroom.pack(pady=10, padx=20, fill="x")

        wroom_top = ctk.CTkFrame(self.sec_wroom, fg_color="transparent")
        wroom_top.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(wroom_top, text="WROOM-32D (BLUETOOTH)", font=("Roboto", 14, "bold"), text_color="#3b8ed0").pack(side="left")

        self.wroom_fw_label = ctk.CTkLabel(self.sec_wroom, text="Aktuelle Version: [N/A]", font=("Roboto", 13))
        self.wroom_fw_label.pack(pady=5)

        self.wroom_status = ctk.CTkLabel(self.sec_wroom, text="Bereit.", font=("Roboto", 12), text_color="#888888")
        self.wroom_status.pack(pady=(0, 10))

        self.wroom_flash_btn = ctk.CTkButton(
            self.sec_wroom, text="WROOM UPDATE", fg_color="#7a1a1a", hover_color="#9b1b1b", height=40, font=("Roboto", 14, "bold"),
            command=lambda: self.start_flash_thread("wroom")
        )
        self.wroom_flash_btn.pack(pady=(0, 15), padx=20, fill="x")

        self.sec_rp = ctk.CTkFrame(self.tab_upd, fg_color="#242424", corner_radius=10)
        self.sec_rp.pack(pady=10, padx=20, fill="x")

        rp_top = ctk.CTkFrame(self.sec_rp, fg_color="transparent")
        rp_top.pack(fill="x", padx=15, pady=10)
        ctk.CTkLabel(rp_top, text="RP2354A (DSP)", font=("Roboto", 14, "bold"), text_color="#e67e22").pack(side="left")

        self.rp_fw_label = ctk.CTkLabel(self.sec_rp, text="Aktuelle Version: [N/A]", font=("Roboto", 13))
        self.rp_fw_label.pack(pady=5)

        self.rp_status = ctk.CTkLabel(self.sec_rp, text="Bereit.", font=("Roboto", 12), text_color="#888888")
        self.rp_status.pack(pady=(0, 10))

        self.rp_flash_btn = ctk.CTkButton(
            self.sec_rp, text="RP2354 UPDATE", fg_color="#7a1a1a", hover_color="#9b1b1b", height=40, font=("Roboto", 14, "bold"),
            command=lambda: self.start_flash_thread("rp2354")
        )
        self.rp_flash_btn.pack(pady=(0, 15), padx=20, fill="x")

        # Globaler Fortschrittsbalken für Flash Vorgänge (Initial unsichtbar)
        self.flash_progress = ctk.CTkProgressBar(self.tab_upd, height=15, fg_color="#333333", progress_color="#3b8ed0")
        self.flash_progress.set(0)

    def setup_tab_log(self):
        self.log_box = ctk.CTkTextbox(self.tab_log, width=700, height=400, font=("Consolas", 12), state="disabled", fg_color="#1a1a1a")
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
        ctk.CTkLabel(info_frame, text="Version 0.1.0\nTriple-Brain Architecture Hub", font=("Roboto", 14), text_color="#aaaaaa", justify="center").pack(pady=5)

        btn = ctk.CTkButton(info_frame, text="GitHub Repository", fg_color="#333333", height=40, command=lambda: webbrowser.open(GITHUB_URL))
        btn.pack(pady=20)

    def setup_tab_ctrl(self):
        # Scrollable Frame für Steuerung + DSP Regler
        scroll_frame = ctk.CTkScrollableFrame(self.tab_ctrl, fg_color="transparent")
        scroll_frame.pack(fill="both", expand=True)

        # --- MEDIA PLAYER ---
        ctk.CTkLabel(scroll_frame, text="Media Player", font=("Roboto", 20, "bold"), text_color="#3b8ed0").pack(pady=(10, 10))

        btn_row = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        btn_row.pack(pady=10)

        encoded_prev = urllib.parse.quote("BL Vorheriger Titel")
        encoded_play = urllib.parse.quote("BL Play-Pause")
        encoded_next = urllib.parse.quote("BL Nächster Titel")

        ctk.CTkButton(btn_row, text="⏮ Zurück", width=110, height=45, corner_radius=20, fg_color="#333333", hover_color="#444444", command=lambda: self.send_action(f"button/{encoded_prev}/press")).pack(side="left", padx=15)
        ctk.CTkButton(btn_row, text="⏯ Play / Pause", width=160, height=60, corner_radius=30, fg_color="#3b8ed0", hover_color="#2980b9", font=("Roboto", 16, "bold"), command=lambda: self.send_action(f"button/{encoded_play}/press")).pack(side="left", padx=15)
        ctk.CTkButton(btn_row, text="Weiter ⏭", width=110, height=45, corner_radius=20, fg_color="#333333", hover_color="#444444", command=lambda: self.send_action(f"button/{encoded_next}/press")).pack(side="left", padx=15)

        # --- BLUETOOTH VOLUME ---
        vol_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        vol_frame.pack(pady=(20, 30), fill="x", padx=40)
        ctk.CTkLabel(vol_frame, text="Bluetooth Lautstärke", font=("Roboto", 14)).pack(pady=(0, 10))
        self.vol_slider = ctk.CTkSlider(vol_frame, from_=0, to=100, button_color="#3b8ed0", button_hover_color="#2980b9", command=self.send_volume)
        self.vol_slider.pack(fill="x")

        # --- SUBWOOFER DSP ---
        ctk.CTkLabel(scroll_frame, text="2.1 Subwoofer DSP", font=("Roboto", 18, "bold"), text_color="#e67e22").pack(pady=(10, 10))

        sub_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        sub_frame.pack(pady=5, fill="x", padx=40)

        ctk.CTkLabel(sub_frame, text="Crossover Frequenz (40-200 Hz)", font=("Roboto", 12)).pack(pady=(0, 5))
        self.cross_slider = ctk.CTkSlider(sub_frame, from_=40, to=200, number_of_steps=32, button_color="#e67e22", button_hover_color="#d35400", command=lambda val: self.send_dsp_value("Subwoofer Crossover Frequenz", val))
        self.cross_slider.set(80)
        self.cross_slider.pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(sub_frame, text="Bass EQ Gain (0-10)", font=("Roboto", 12)).pack(pady=(0, 5))
        self.sub_eq_slider = ctk.CTkSlider(sub_frame, from_=0, to=10, number_of_steps=10, button_color="#e67e22", button_hover_color="#d35400", command=lambda val: self.send_dsp_value("Subwoofer Bass EQ", val))
        self.sub_eq_slider.set(0)
        self.sub_eq_slider.pack(fill="x", pady=(0, 10))

        # --- STEREO 5-BAND EQ ---
        ctk.CTkLabel(scroll_frame, text="Front Stereo 5-Band EQ", font=("Roboto", 18, "bold"), text_color="#2ecc71").pack(pady=(20, 10))

        eq_frame = ctk.CTkFrame(scroll_frame, fg_color="transparent")
        eq_frame.pack(pady=5, fill="x", padx=40)

        bands = [
            ("Band 1 (60Hz)", "Front EQ Band 1 (60Hz)"),
            ("Band 2 (230Hz)", "Front EQ Band 2 (230Hz)"),
            ("Band 3 (910Hz)", "Front EQ Band 3 (910Hz)"),
            ("Band 4 (3.6kHz)", "Front EQ Band 4 (3.6kHz)"),
            ("Band 5 (14kHz)", "Front EQ Band 5 (14kHz)")
        ]

        self.eq_sliders = []
        for label, entity in bands:
            ctk.CTkLabel(eq_frame, text=label, font=("Roboto", 12)).pack(pady=(5, 0))
            slider = ctk.CTkSlider(eq_frame, from_=-10, to=10, number_of_steps=20, button_color="#2ecc71", button_hover_color="#27ae60", command=lambda val, e=entity: self.send_dsp_value(e, val))
            slider.set(0)
            slider.pack(fill="x", pady=(0, 5))
            self.eq_sliders.append(slider)

    def send_action(self, endpoint):
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return
        threading.Thread(target=lambda: self.session.post(f"http://{ip}/{endpoint}", timeout=2), daemon=True).start()

    def send_volume(self, value):
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return
        # Nutze den exakten Entity Name mit URL-Encoding statt Objekt-ID
        encoded_name = urllib.parse.quote("Bluetooth Lautstärke")
        threading.Thread(target=lambda: self.session.post(f"http://{ip}/number/{encoded_name}/set?value={int(value)}", timeout=2), daemon=True).start()

    def send_dsp_value(self, entity_name, value):
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return
        encoded_name = urllib.parse.quote(entity_name)
        threading.Thread(target=lambda: self.session.post(f"http://{ip}/number/{encoded_name}/set?value={int(value)}", timeout=2), daemon=True).start()

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
        # Zwingt den S3, den EN-Pin des WROOMs auf LOW und wieder HIGH zu ziehen
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return
        
        try:
            # Wir nutzen deinen in YAML definierten WROOM Normal Boot Button!
            encoded_btn = urllib.parse.quote("WROOM Normal Boot")
            self.session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=3)
            messagebox.showinfo("Hardware Reset", "⚡ Befehl gesendet!\nDer S3 startet den Bluetooth-Chip (WROOM) jetzt hart neu.")
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
        src = get_state("text_sensor", "Active Audio Source")
        sys_status = get_state("text_sensor", "Insane System Status")
        t_amp = get_state("sensor", "Amp Temp (UART)")
        t_esp = get_state("sensor", "ESP Ambient Temperature")
        t_dsp = get_state("sensor", "RP2354 Temp (UART)")
        bl_stat = get_state("text_sensor", "Stream Status")
        bl_song = get_state("text_sensor", "Bluetooth Track")
        bl_art = get_state("text_sensor", "Bluetooth Artist")
        fan = get_state("sensor", "Fan Speed")
        fault = get_state("binary_sensor", "Amp Fault")
        wifi = get_state("sensor", "WLAN Signal")
        bl_version = get_state("text", "bl_firmware_version")
        rp_version = get_state("text", "rp2354_firmware_version")
        bt_conn = get_state("binary_sensor", "bluetooth_connected")

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

        self.after(0, self._update_dashboard_ui, src, sys_status, t_amp, t_esp, t_dsp, bl_stat, bl_song, bl_art, fan, fault, wifi, bt_conn, bl_version, rp_version)
        self.after(0, lambda: self.check_for_updates(bl_version, rp_version))

    def _update_dashboard_ui(self, src, sys_status, t_amp, t_esp, t_dsp, bl_stat, bl_song, bl_art, fan, fault, wifi, bt_conn, bl_version, rp_version):
        def set_val(lbl, text, color="#ffffff"):
            lbl.configure(text=str(text), text_color=color)

        is_online = src != "Offline" and wifi != "Offline"
        
        if is_online:
            self.status_dot.configure(text_color="#2ecc71")
        else:
            self.status_dot.configure(text_color="#e74c3c")

        set_val(self.val_src, src, "#2ecc71" if "WLAN" in src else "#3498db")
        set_val(self.val_sys, sys_status.upper(), "#2ecc71" if sys_status == "ok" else "#e74c3c")
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

        update_temp_ui(self.val_temp_amp, *parse_temp(t_amp))
        update_temp_ui(self.val_temp_esp, *parse_temp(t_esp))
        update_temp_ui(self.val_temp_dsp, *parse_temp(t_dsp))

        set_val(self.val_bl_stat, bl_stat, "#3498db" if bl_stat == "playing" else "#ffffff")
        set_val(self.val_bl_song, bl_song)
        set_val(self.val_bl_art, bl_art)

        set_val(self.val_fan, f"{fan}%" if fan != "Offline" else fan, "#3498db" if fan != "0" else "#888888")
        set_val(self.val_amp_stat, "FAULT" if fault == "ON" else "OK", "#e74c3c" if fault == "ON" else "#2ecc71")
        set_val(self.val_bl_conn, "VERBUNDEN" if bt_conn == "ON" else "GETRENNT", "#3498db" if bt_conn == "ON" else "#888888")

        self.is_fetching = False
        
        self.sync_timer = self.after(1000, self.sync_live_data)

    # --- FLASHING FUNKTIONEN ---
    def start_flash_thread(self, target):
        threading.Thread(target=self.run_flash, args=(target,), daemon=True).start()

    def run_flash(self, target):
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return

        btn = self.wroom_flash_btn if target == "wroom" else self.rp_flash_btn
        status_lbl = self.wroom_status if target == "wroom" else self.rp_status
        
        self.after(0, lambda: btn.configure(state="disabled", text="LADE FIRMWARE..."))
        
        try:
            self.after(0, lambda: self.flash_progress.pack(pady=10, padx=20, fill="x"))
            self.after(0, lambda: self.flash_progress.set(0.0))

            self.after(0, lambda: status_lbl.configure(text="Schritt 0: Lade Firmware von GitHub...", text_color="orange"))

            download_url = None
            if hasattr(self, 'github_assets') and self.github_assets:
                # Try to find target specific binary in the release assets
                for asset in self.github_assets:
                    if target.lower() in asset['name'].lower():
                        download_url = asset['browser_download_url']
                        break

            if not download_url:
                # Fallback static URLs if release API fails or no match
                if target == "wroom":
                    download_url = "https://raw.githubusercontent.com/babeinlovexd/Insane-Sound-System/main/Firmware/WROOM32D/firmware.bin"
                else:
                    download_url = "https://raw.githubusercontent.com/babeinlovexd/Insane-Sound-System/main/Firmware/RP2354A/firmware.bin"

            r = requests.get(download_url, timeout=15)
            r.raise_for_status()
            with open(get_firmware_path(), "wb") as f:
                f.write(r.content)

            self.after(0, lambda: btn.configure(text="FLASHING..."))
            
            if target == "wroom":
                self.after(0, lambda: status_lbl.configure(text="Schritt 1: Setze WROOM in Flash-Modus...", text_color="orange"))
                encoded_btn = urllib.parse.quote("WROOM Flash Mode")
                self.session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=5)

                import time
                time.sleep(2)

                self.after(0, lambda: status_lbl.configure(text="Schritt 2: Flashe WROOM Firmware...", text_color="orange"))

                command_args = [
                    "--port", f"socket://{ip}:6666",
                    "--baud", "115200",
                    "write_flash", "0x10000", get_firmware_path()
                ]

                def gui_update(msg):
                    text = f"Flashing: {msg.split('...')[0]}..." if "..." in msg else msg
                    self.after(0, lambda: status_lbl.configure(text=text))
                    self.log(msg)
                    # Extract percentage if possible
                    if "(" in msg and "%" in msg:
                        try:
                            pct_str = msg.split("(")[1].split("%")[0].strip()
                            pct = float(pct_str) / 100.0
                            self.after(0, lambda: self.flash_progress.set(pct))
                        except: pass

                redirector = ConsoleRedirector(gui_update)
                with contextlib.redirect_stdout(redirector):
                    esptool.main(command_args)

                self.after(0, lambda: status_lbl.configure(text="Schritt 3: WROOM Neustart...", text_color="orange"))
                encoded_btn = urllib.parse.quote("WROOM Normal Boot")
                self.session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=5)

                # INJECTION: Post version to ESPHome template text sensor
                if self.online_version:
                    self.after(0, lambda: status_lbl.configure(text="Schritt 4: Version Injection...", text_color="orange"))
                    encoded_txt = urllib.parse.quote("BL Firmware Version")
                    try: self.session.post(f"http://{ip}/text/{encoded_txt}/set?value={self.online_version}", timeout=3)
                    except: pass

            elif target == "rp2354":
                self.after(0, lambda: status_lbl.configure(text="Schritt 1: Setze RP2354 in Flash-Modus...", text_color="orange"))
                encoded_btn = urllib.parse.quote("RP2354 Flash Mode")
                self.session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=5)

                import time
                time.sleep(2)

                self.after(0, lambda: status_lbl.configure(text="Schritt 2: Flashe RP2354 Firmware...", text_color="orange"))

                # Raw TCP stream to custom serial bootloader on port 6667
                import socket
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(15)
                    s.connect((ip, 6667))
                    file_size = os.path.getsize(get_firmware_path())
                    sent = 0
                    last_pct_sent = -1
                    with open(get_firmware_path(), 'rb') as f:
                        while chunk := f.read(8192):
                            s.sendall(chunk)
                            sent += len(chunk)
                            pct = sent / file_size
                            # Optimization: only update UI if progress percentage changed by at least 1%
                            if int(pct * 100) > last_pct_sent or sent == file_size:
                                self.after(0, lambda p=pct: self.flash_progress.set(p))
                                self.after(0, lambda p=pct: status_lbl.configure(text=f"Flashing: {int(p*100)}%"))
                                last_pct_sent = int(pct * 100)

                self.after(0, lambda: status_lbl.configure(text="Schritt 3: RP2354 geflasht. Reboot.", text_color="orange"))
                encoded_btn = urllib.parse.quote("RP2354 Normal Boot")
                self.session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=5)

                # INJECTION: Post version to ESPHome template text sensor
                if self.online_version:
                    self.after(0, lambda: status_lbl.configure(text="Schritt 4: Version Injection...", text_color="orange"))
                    encoded_txt = urllib.parse.quote("RP2354 Firmware Version")
                    try: self.session.post(f"http://{ip}/text/{encoded_txt}/set?value={self.online_version}", timeout=3)
                    except: pass
            
            self.after(0, lambda: status_lbl.configure(text="🚀 Update 100% erfolgreich!", text_color="#2ecc71"))
            self.after(0, lambda: messagebox.showinfo("Update", f"{target.upper()} wurde erfolgreich aktualisiert!"))

        except requests.exceptions.RequestException as e:
            self.after(0, lambda: status_lbl.configure(text="❌ Netzwerk Fehler", text_color="red"))
            self.log(str(e))
        except SystemExit as e:
            if e.code != 0:
                self.after(0, lambda: status_lbl.configure(text="❌ Fehler beim Flashen!", text_color="red"))
        except Exception as e:
            self.after(0, lambda: status_lbl.configure(text="❌ Fehler!", text_color="red"))
            self.log(str(e))
        finally:
            self.after(0, lambda: btn.configure(state="normal", text=f"{target.upper()} UPDATE"))
            self.after(0, lambda: self.flash_progress.pack_forget())
            
    def check_for_updates(self, bl_version, rp_version):
        if bl_version == "N/A" or bl_version == "Offline":
            self.wroom_fw_label.configure(text="Aktuelle Version: Offline", text_color="#888888")
        else:
            self.wroom_fw_label.configure(text=f"Aktuelle Version: [{bl_version}]", text_color="#ffffff")

        if rp_version == "N/A" or rp_version == "Offline":
            self.rp_fw_label.configure(text="Aktuelle Version: Offline", text_color="#888888")
        else:
            self.rp_fw_label.configure(text=f"Aktuelle Version: [{rp_version}]", text_color="#ffffff")

        if self.online_version:
            if bl_version != self.online_version and bl_version != "Offline":
                self.wroom_flash_btn.configure(fg_color="#e74c3c", text="WROOM UPDATE INSTALLIEREN")
            else:
                self.wroom_flash_btn.configure(fg_color="#7a1a1a", text="WROOM UPDATE")
            
            if rp_version != self.online_version and rp_version != "Offline":
                self.rp_flash_btn.configure(fg_color="#e74c3c", text="RP2354 UPDATE INSTALLIEREN")
            else:
                self.rp_flash_btn.configure(fg_color="#7a1a1a", text="RP2354 UPDATE")

if __name__ == "__main__":
    app = InsaneFlasher()
    app.mainloop()