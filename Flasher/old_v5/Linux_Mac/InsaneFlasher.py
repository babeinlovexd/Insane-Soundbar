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

FIRMWARE_URL = "https://raw.githubusercontent.com/babeinlovexd/Insane-Sound-System/main/Firmware/insane_bl_v5.ino.merged.bin"
GITHUB_URL = "https://github.com/babeinlovexd"
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
        self.title("Insane Sound System V5 - Official Hub")
        self.geometry("780x850") 
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

        self.title_label = ctk.CTkLabel(self.header_frame, text="Insane Sound System V5", font=("Roboto", 26, "bold"), text_color="#ffffff")
        self.title_label.grid(row=0, column=1, sticky="sw")
        
        # --- STATUS PUNKT (NEBEN DEM TITEL) ---
        self.status_dot = ctk.CTkLabel(self.header_frame, text="●", font=("Roboto", 20), text_color="#444444")
        self.status_dot.grid(row=0, column=2, padx=(10, 0), sticky="sw")
        
        self.author_link = ctk.CTkLabel(self.header_frame, text="by BabeinlovexD ", font=("Roboto", 14, "italic"), text_color="#3b8ed0", cursor="hand2")
        self.author_link.grid(row=1, column=1, sticky="nw")
        self.author_link.bind("<Button-1>", lambda e: webbrowser.open(GITHUB_URL))

        self.main_area = ctk.CTkFrame(self, fg_color="transparent")
        self.main_area.pack(fill="both", expand=True, padx=30)

        # ---------------------------------------------------------
        # 1. Card: SYSTEM AUSWAHL
        # ---------------------------------------------------------
        self.card_dev = ctk.CTkFrame(self.main_area, fg_color="#242424", corner_radius=10)
        self.card_dev.pack(pady=5, fill="x")

        # Container für Dropdown + Buttons nebeneinander
        dev_ctrl_frame = ctk.CTkFrame(self.card_dev, fg_color="transparent")
        dev_ctrl_frame.pack(pady=15, padx=20, fill="x")

        self.device_dropdown = ctk.CTkOptionMenu(dev_ctrl_frame, values=["Suche läuft..."], state="disabled", height=35,
                                                fg_color="#1a1a1a", button_color="#333333", button_hover_color="#444444", command=self.on_device_select)
        self.device_dropdown.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # 1. Favoriten Button (Outline-Style mit Text)
        self.fav_btn = ctk.CTkButton(
            dev_ctrl_frame, text="⭐ Merken", width=95, height=32, 
            fg_color="transparent", border_width=1, border_color="#f1c40f", 
            hover_color="#333333", text_color="#f1c40f", font=("Roboto", 13, "bold"), 
            command=self.save_favorite
        )
        self.fav_btn.pack(side="left", padx=(0, 5)) 

        # 2. Favorit Löschen Button (Outline-Style mit Text)
        self.del_fav_btn = ctk.CTkButton(
            dev_ctrl_frame, text="✖ Löschen", width=95, height=32, 
            fg_color="transparent", border_width=1, border_color="#c0392b", 
            hover_color="#333333", text_color="#c0392b", font=("Roboto", 13, "bold"), 
            command=self.delete_favorite
        )
        self.del_fav_btn.pack(side="left", padx=(0, 20)) 

        # 3. Reboot Button (Outline-Style mit Text)
        self.restart_btn = ctk.CTkButton(
            dev_ctrl_frame, text="⚡ Reset", width=95, height=32, 
            fg_color="transparent", border_width=1, border_color="#e67e22", 
            hover_color="#333333", text_color="#e67e22", font=("Roboto", 13, "bold"), 
            command=self.restart_bluetooth
        )
        self.restart_btn.pack(side="left", padx=(0, 5))

        # ---------------------------------------------------------
        # 2. Card: LIVE TELEMETRY DASHBOARD
        # ---------------------------------------------------------
        self.card_dash = ctk.CTkFrame(self.main_area, fg_color="#242424", corner_radius=10)
        self.card_dash.pack(pady=10, fill="x")

        dash_top = ctk.CTkFrame(self.card_dash, fg_color="transparent")
        dash_top.pack(fill="x", padx=20, pady=(15, 0))

        ctk.CTkLabel(dash_top, text="LIVE SYSTEM MONITOR", font=("Roboto", 12, "bold"), text_color="#666666").pack(side="left")

        self.info_grid = ctk.CTkFrame(self.card_dash, fg_color="#1a1a1a", corner_radius=10)
        self.info_grid.pack(pady=15, padx=20, fill="x")
        
        # Grid konfigurieren, damit die Spalten gleich breit sind
        self.info_grid.columnconfigure((0, 1, 2), weight=1)

        # Funktion zum schnellen Erstellen der Datenfelder inkl. optionaler Progressbar
        def create_stat(row, col, label_text, is_temp=False):
            lbl = ctk.CTkLabel(self.info_grid, text=label_text, font=("Roboto", 11, "bold"), text_color="#888888")
            lbl.grid(row=row*2, column=col, sticky="w", padx=15, pady=(10, 0))
            
            if is_temp:
                # Extra Container für Wert + Balken
                container = ctk.CTkFrame(self.info_grid, fg_color="transparent")
                container.grid(row=row*2+1, column=col, sticky="ew", padx=15, pady=(0, 10))
                
                val = ctk.CTkLabel(container, text="-", font=("Roboto", 14, "bold"), text_color="#ffffff")
                val.pack(anchor="w")
                
                bar = ctk.CTkProgressBar(container, height=6, fg_color="#333333")
                bar.set(0)
                bar.pack(fill="x", pady=(4, 0))
                return val, bar # Gibt Label UND Balken zurück
            else:
                val = ctk.CTkLabel(self.info_grid, text="-", font=("Roboto", 14, "bold"), text_color="#ffffff")
                val.grid(row=row*2+1, column=col, sticky="w", padx=15, pady=(0, 10))
                return val

        # Reihe 1: Hauptsystem
        self.val_src = create_stat(0, 0, "AUDIO QUELLE")
        self.val_amp = create_stat(0, 1, "VERSTÄRKER")
        self.val_turbo = create_stat(0, 2, "TURBO MODE")

        # Reihe 2: Temperaturen (mit is_temp=True)
        self.val_temp_amp = create_stat(1, 0, "TEMP VERSTÄRKER", is_temp=True)
        self.val_temp_esp = create_stat(1, 1, "TEMP ESP32", is_temp=True)
        self.val_temp_pwr = create_stat(1, 2, "TEMP POWER", is_temp=True)

        # Reihe 3: Medien Metadaten
        self.val_bl_stat = create_stat(2, 0, "MEDIA STATUS")
        self.val_bl_song = create_stat(2, 1, "MEDIA TITEL")
        self.val_bl_art = create_stat(2, 2, "MEDIA INTERPRET")

        # Reihe 4: System
        self.val_fan = create_stat(3, 0, "LÜFTER")
        self.val_wifi = create_stat(3, 1, "WLAN SIGNAL")
        self.val_bl_ver = create_stat(3, 2, "FIRMWARE VER") 

        # ---------------------------------------------------------
        # 3. Card: BLUETOOTH FIRMWARE UPDATE
        # ---------------------------------------------------------
        self.card_flash = ctk.CTkFrame(self.main_area, fg_color="#242424", corner_radius=10)
        self.card_flash.pack(pady=5, fill="x")

        self.sec_2 = ctk.CTkLabel(self.card_flash, text="OTA UPDATE (WROOM CHIP)", font=("Roboto", 12, "bold"), text_color="#666666")
        self.sec_2.pack(pady=(15, 5), padx=20, anchor="w")

        self.fw_frame = ctk.CTkFrame(self.card_flash, fg_color="transparent")
        self.fw_frame.pack(pady=5, padx=20, fill="x")

        self.fw_label = ctk.CTkLabel(self.fw_frame, text="Prüfe Firmware Status...", font=("Roboto", 14), text_color="#ffffff")
        self.fw_label.pack(side="left")

        self.status_label = ctk.CTkLabel(self.card_flash, text="Bereit.", font=("Roboto", 13), text_color="#888888")
        self.status_label.pack(pady=(10, 5))

        self.flash_btn = ctk.CTkButton(self.card_flash, text="FLASHVORGANG STARTEN", state="disabled", fg_color="#7a1a1a", hover_color="#9b1b1b", height=45, font=("Roboto", 16, "bold"), command=self.start_flash_thread)
        self.flash_btn.pack(pady=(5, 20), padx=20, fill="x")

        # --- FOOTER (COPYRIGHT & CREDITS) ---
        self.footer_label = ctk.CTkLabel(
            self, 
            text="© 2026 BabeinlovexD | Powered by esptool (GPLv2)", 
            font=("Roboto", 10), 
            text_color="#555555"
        )
        self.footer_label.pack(side="bottom", pady=(0, 10))
        
        self.sync_timer = None

        # Favoriten laden und Scan starten (Deine bestehenden Zeilen)
        self.load_favorites()
        self.start_scan()

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
            # Wir nutzen deinen in YAML definierten bl_normal_start Button!
            # Hinweis: Die Web-API erwartet die object_id aus dem Namen "WROOM Normal starten"
            requests.post(f"http://{ip}/button/WROOM Normal starten/press", timeout=3)
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

    def _fetch_api_data(self, ip):
        def get_state(domain, object_id):
            try:
                url = f"http://{ip}/{domain}/{object_id}"
                r = requests.get(url, timeout=2).json() # Timeout auf 2s verkürzt
                return r.get("state", "N/A")
            except: return "Offline"

        # Daten abrufen (ESPHome generiert URLs aus dem 'name' der Komponente)
        src = get_state("switch", "Audio Quelle (Intern)")
        amp = get_state("switch", "Verstärker Power")
        turbo = get_state("switch", "Insane Turbo Mode")
        t_amp = get_state("sensor", "Temp Verstärker")
        t_esp = get_state("sensor", "Temp ESP32 Umgebung")
        t_pwr = get_state("sensor", "Temp Spannungsregler")
        bl_stat = get_state("text_sensor", "Wiedergabe Status")
        bl_song = get_state("text_sensor", "Aktueller Titel")
        bl_art = get_state("text_sensor", "Aktueller Interpret")
        fan = get_state("fan", "Gehäuse Lüfter")
        wifi = get_state("sensor", "WLAN Signal")
        bl_version = get_state("text_sensor", "BL Firmware Version") # Version holen

        import time
        current_time = time.time()

        # Check GitHub version only occasionally to avoid rate limiting
        if current_time - self.last_update_check > UPDATE_CHECK_INTERVAL:
            self.last_update_check = current_time
            try:
                VERSION_URL = "https://raw.githubusercontent.com/babeinlovexd/Insane-Sound-System/main/Firmware/version.txt"
                self.online_version = requests.get(VERSION_URL, timeout=3).text.strip()
            except:
                self.online_version = None

        # UI Update triggern (jetzt mit bl_version als Argument)
        self.after(0, self._update_dashboard_ui, src, amp, turbo, t_amp, t_esp, t_pwr, bl_stat, bl_song, bl_art, fan, wifi, bl_version)
        # Versions-Check für den Button
        self.after(0, lambda: self.check_for_updates(bl_version))

    def _update_dashboard_ui(self, src, amp, turbo, t_amp, t_esp, t_pwr, bl_stat, bl_song, bl_art, fan, wifi, bl_version):
        def set_val(lbl, text, color="#ffffff"):
            lbl.configure(text=str(text), text_color=color)

        # PRÜFUNG: Ist das System online?
        is_online = src != "Offline" and wifi != "Offline"
        
        # Status-Punkt im Header aktualisieren
        if is_online:
            self.status_dot.configure(text_color="#2ecc71") # Grün
        else:
            self.status_dot.configure(text_color="#e74c3c") # Rot

        # Reihe 1 bis 3 (unverändert)...
        set_val(self.val_src, "WLAN (S3)" if src == "ON" else ("Bluetooth" if src == "OFF" else src), "#2ecc71" if src == "ON" else "#3498db")
        set_val(self.val_amp, "Aktiv 🔊" if amp == "ON" else ("Standby 💤" if amp == "OFF" else amp), "#2ecc71" if amp == "ON" else "#f39c12")
        set_val(self.val_turbo, "🔥 INSANE" if turbo == "ON" else "Normal", "#e74c3c" if turbo == "ON" else "#888888")

        # Reihe 2: Temperaturen mit Balken
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
        update_temp_ui(self.val_temp_pwr, *parse_temp(t_pwr))

        # Reihe 3: Bluetooth
        set_val(self.val_bl_stat, bl_stat, "#3498db" if bl_stat == "Wiedergabe" else "#ffffff")
        set_val(self.val_bl_song, bl_song)
        set_val(self.val_bl_art, bl_art)

        # Reihe 4: System (Jetzt mit Version!)
        set_val(self.val_fan, "AN" if fan == "ON" else ("AUS" if fan == "OFF" else fan), "#3498db" if fan == "ON" else "#888888")
        set_val(self.val_wifi, f"{wifi} dBm" if wifi != "Offline" else wifi)
        set_val(self.val_bl_ver, bl_version) # Firmware Version anzeigen

        self.is_fetching = False
        
        # DAS HERZSTÜCK: Automatischer Re-Sync nach 1 Sekunde (und Timer-ID speichern!)
        self.sync_timer = self.after(1000, self.sync_live_data)

    # --- FLASHING FUNKTIONEN ---
    def start_download_thread(self):
        self.download_btn.configure(state="disabled", text="Lädt...")
        self.fw_label.configure(text="GitHub Server...")
        threading.Thread(target=self.download_firmware, daemon=True).start()

    def start_flash_thread(self):
        threading.Thread(target=self.run_flash, daemon=True).start()

    def run_flash(self):
        ip = self.dropdown_mapping.get(self.device_dropdown.get())
        if not ip: return
        
        self.after(0, lambda: self.flash_btn.configure(state="disabled", text="LADE FIRMWARE..."))
        
        try:
            # --- SCHRITT 0: FIRMWARE DOWNLOADEN ---
            self.after(0, lambda: self.status_label.configure(text="Schritt 0: Lade Firmware von GitHub...", text_color="orange"))
            r = requests.get(FIRMWARE_URL, timeout=15)
            r.raise_for_status()
            with open(get_firmware_path(), "wb") as f: 
                f.write(r.content)

            # --- SCHRITT 1: WROOM IN DEN BOOTLOADER ZWINGEN ---
            self.after(0, lambda: self.flash_btn.configure(text="FLASHING..."))
            self.after(0, lambda: self.status_label.configure(text="Schritt 1: Setze WROOM in Flash-Modus...", text_color="orange"))
            requests.post(f"http://{ip}/button/WROOM in Flash-Modus setzen/press", timeout=5)
            
            import time
            time.sleep(2) 
            
            # --- SCHRITT 2: ESPTOOL ALS MODUL STARTEN ---
            self.after(0, lambda: self.status_label.configure(text="Schritt 2: Flashe Firmware (Bitte warten)...", text_color="orange"))
            
            command_args = [
                "--port", f"socket://{ip}:8888",
                "--baud", "115200",
                "write_flash", "0x0", get_firmware_path()
            ]
            
            def gui_update(msg):
                text = f"Flashing: {msg.split('...')[0]}..." if "..." in msg else msg
                self.after(0, lambda: self.status_label.configure(text=text))

            redirector = ConsoleRedirector(gui_update)
            with contextlib.redirect_stdout(redirector):
                esptool.main(command_args)

            # --- SCHRITT 3: WROOM NORMAL NEUSTARTEN ---
            self.after(0, lambda: self.status_label.configure(text="Schritt 3: WROOM Neustart...", text_color="orange"))
            requests.post(f"http://{ip}/button/WROOM Normal starten/press", timeout=5)
            
            self.after(0, lambda: self.status_label.configure(text="🚀 Update 100% erfolgreich!", text_color="#2ecc71"))
            self.after(0, lambda: messagebox.showinfo("Insane Sound System", "Der WROOM-Chip wurde erfolgreich geflasht und startet neu!"))

        except requests.exceptions.RequestException as e:
            self.after(0, lambda: self.status_label.configure(text="❌ Netzwerk/Download Fehler", text_color="red"))
            self.after(0, lambda e=e: messagebox.showerror("Netzwerk Fehler", f"Verbindungsproblem:\n{e}"))
            
        except SystemExit as e:
            if e.code != 0:
                self.after(0, lambda: self.status_label.configure(text="❌ Fehler beim Flashen!", text_color="red"))
                self.after(0, lambda: messagebox.showerror("Flash Fail", "Flashen durch esptool abgebrochen."))
                
        except Exception as e:
            self.after(0, lambda: self.status_label.configure(text="❌ Fehler!", text_color="red"))
            self.after(0, lambda e=e: messagebox.showerror("Fehler", f"Vorgang abgebrochen:\n{e}"))
            
        finally:
            self.after(0, lambda: self.flash_btn.configure(state="normal", text="UPDATE JETZT INSTALLIEREN"))
            
    def check_for_updates(self, local_version):
        try:
            # 1. Beide Versionen von unsichtbaren Zeichen bereinigen!
            online_version = str(self.online_version).replace("v", "").replace("V", "").replace("\x00", "").strip() if self.online_version else None
            clean_local = str(local_version).replace("v", "").replace("V", "").replace("\r", "").replace("\n", "").replace("\x00", "").strip()
            
            if not online_version:
                raise Exception("Keine Online-Version verfügbar")
            
            # 2. Logik & UI Update
            if clean_local == "N/A" or clean_local == "Offline" or clean_local == "0.0":
                self.fw_label.configure(text=f"WROOM Version: Unbekannt (Offline?)", text_color="#888888")
                self.flash_btn.configure(state="normal", text="FIRMWARE FLASHEN", fg_color="#7a1a1a")
            
            elif online_version != clean_local:
                self.fw_label.configure(text=f"⚠️ Update verfügbar! (Box: {clean_local} -> Neu: {online_version})", text_color="#f39c12")
                self.flash_btn.configure(state="normal", text="UPDATE JETZT INSTALLIEREN", fg_color="#e74c3c")
            
            else:
                self.fw_label.configure(text=f"✅ WROOM ist aktuell (Version {clean_local})", text_color="#2ecc71")
                # Optional: Button deaktivieren, wenn alles aktuell ist (Schutz vor unnötigem Flashen)
                self.flash_btn.configure(state="disabled", text="KEIN UPDATE NÖTIG", fg_color="#333333")
                
        except Exception:
            self.fw_label.configure(text=f"Box: {str(local_version).strip()} | GitHub: Offline", text_color="#888888")

if __name__ == "__main__":
    app = InsaneFlasher()
    app.mainloop()
