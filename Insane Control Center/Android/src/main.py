import flet as ft
import socket
import threading
import requests
import json
import urllib.parse
import os
import re
import time
import sys
import webbrowser
from zeroconf import ServiceBrowser, Zeroconf
import esptool
import io
import contextlib

GITHUB_API_LATEST = "https://api.github.com/repos/babeinlovexd/Insane-Sound-System/releases/latest"
GITHUB_URL = "https://github.com/babeinlovexd/Insane-Soundbar"
GITHUB_AUTHOR_URL = "https://github.com/babeinlovexd"
UPDATE_CHECK_INTERVAL = 3600

class ConsoleRedirector(io.StringIO):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.buffer = ""

    def write(self, string):
        self.buffer += string
        if '\r' in self.buffer or '\n' in self.buffer:
            lines = self.buffer.replace('\r', '\n').split('\n')
            for line in lines[:-1]:
                if "Writing at" in line:
                    self.callback(line.strip())
            self.buffer = lines[-1]

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

def main(page: ft.Page):
    # --- Fenster-Setup ---
    page.title = "Insane Control Center"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 800
    page.window.height = 700
    page.bgcolor = "#0d1117"
    page.scroll = "auto"
    
    # --- Variablen ---
    scanned_devices = {}
    favorite_devices = page.client_storage.get("iss_favorites") or {}
    dropdown_mapping = {}
    
    session = requests.Session()
    is_fetching = False
    log_running = False
    current_log_ip = None
    
    online_version = None
    last_update_check = 0
    github_assets = []

    # --- UI Helper & Callbacks ---
    def show_snackbar(message, is_error=False):
        page.snack_bar = ft.SnackBar(ft.Text(message), bgcolor="red" if is_error else "green")
        page.snack_bar.open = True
        page.update()

    def _update_dropdown():
        current = device_dropdown.value
        dropdown_mapping.clear()

        for name, ip in favorite_devices.items():
            dropdown_mapping[f"{name} ⭐"] = ip

        for name, ip in scanned_devices.items():
            if name not in favorite_devices:
                dropdown_mapping[name] = ip

        vals = list(dropdown_mapping.keys())

        if vals:
            device_dropdown.options = [ft.dropdown.Option(v) for v in vals]
            device_dropdown.disabled = False

            if current == "Suche läuft...":
                device_dropdown.value = vals[0]
                sync_live_data()
            elif current not in vals:
                base_current = str(current).replace(" ⭐", "")
                if f"{base_current} ⭐" in vals:
                    device_dropdown.value = f"{base_current} ⭐"
                elif base_current in vals:
                    device_dropdown.value = base_current
                else:
                    device_dropdown.value = vals[0]
                    sync_live_data()
        page.update()

    def add_device_to_ui(name, ip):
        base_name = f"{name} ({ip})"
        scanned_devices[base_name] = ip
        _update_dropdown()

    def save_favorite(e):
        current = device_dropdown.value
        if current and current != "Suche läuft...":
            base_name = current.replace(" ⭐", "")
            ip = dropdown_mapping.get(current)
            if ip:
                favorite_devices[base_name] = ip
                page.client_storage.set("iss_favorites", favorite_devices)
                show_snackbar(f"{base_name} wurde gespeichert!")
                _update_dropdown()

    def delete_favorite(e):
        current = device_dropdown.value
        if current and current != "Suche läuft...":
            base_name = current.replace(" ⭐", "")
            if base_name in favorite_devices:
                del favorite_devices[base_name]
                page.client_storage.set("iss_favorites", favorite_devices)
                _update_dropdown()

    def on_device_select(e):
        sync_live_data()

    # --- Header & Systemauswahl ---
    status_dot = ft.Text("●", size=20, color="#444444")
    
    device_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("Suche läuft...")],
        value="Suche läuft...",
        disabled=True,
        expand=True,
        on_change=on_device_select
    )

    page.add(
        ft.Row([
            ft.Text("Insane Control Center", size=26, weight="bold", color="#c9d1d9"),
            status_dot
        ], alignment=ft.MainAxisAlignment.START),
        
        ft.Container(
            bgcolor="#161b22",
            border=ft.border.all(1, "#30363d"),
            border_radius=10,
            padding=20,
            content=ft.Row([
                device_dropdown,
                ft.ElevatedButton("⭐ Merken", on_click=save_favorite, bgcolor="transparent", color="#e3b341"),
                ft.ElevatedButton("✖ Löschen", on_click=delete_favorite, bgcolor="transparent", color="#c0392b")
            ])
        )
    )

    # --- Telemetrie Helper ---
    def create_stat(label_text, is_temp=False):
        lbl = ft.Text(label_text, size=11, weight="bold", color="#8b949e")
        val = ft.Text("-", size=14, weight="bold", color="#c9d1d9")
        if is_temp:
            pbar = ft.ProgressBar(value=0, height=6, color="#21262d", bgcolor="#21262d")
            return ft.Column([lbl, val, pbar]), val, pbar
        return ft.Column([lbl, val]), val

    tele_col1_1, val_src = create_stat("ACTIVE INPUT")
    tele_col1_2, val_sys = create_stat("SOUNDBAR STATUS")
    tele_col1_3, val_wifi = create_stat("WLAN SIGNAL")
    
    tele_col2_1, val_temp_esp, pb_temp_esp = create_stat("MASTER TEMP", is_temp=True)
    tele_col2_2, val_temp_dsp, pb_temp_dsp = create_stat("DSP TEMP", is_temp=True)
    tele_col2_3, val_amp_stat = create_stat("AMP FAULT")
    
    tele_col3_1, val_sub_conn = create_stat("SUB CONN")
    tele_col3_2, val_bl_conn = create_stat("BT CONN")

    # --- Updates Helper ---
    btrx_fw_label = ft.Text("Aktuelle Version: [N/A]", size=13)
    btrx_status = ft.Text("Bereit.", size=12, color="#8b949e")
    btrx_flash_btn = ft.ElevatedButton("BT_RX UPDATE", bgcolor="#7a1a1a", color="white", on_click=lambda e: start_flash_thread("btrx"))
    
    subtx_fw_label = ft.Text("Aktuelle Version: [N/A]", size=13)
    subtx_status = ft.Text("Bereit.", size=12, color="#8b949e")
    subtx_flash_btn = ft.ElevatedButton("SUB_TX UPDATE", bgcolor="#7a1a1a", color="white", on_click=lambda e: start_flash_thread("subtx"))
    
    rp_fw_label = ft.Text("Aktuelle Version: [N/A]", size=13)
    rp_status = ft.Text("Bereit.", size=12, color="#8b949e")
    rp_flash_btn = ft.ElevatedButton("RP2354 UPDATE", bgcolor="#7a1a1a", color="white", on_click=lambda e: start_flash_thread("rp2354"))
    
    flash_progress = ft.ProgressBar(value=0, height=15, visible=False)

    # --- Log Helper ---
    log_box = ft.TextField(multiline=True, read_only=True, expand=True, text_size=12, min_lines=20, max_lines=20, bgcolor="#0d1117", border_color="transparent")
    
    def log(msg):
        log_box.value = (log_box.value or "") + msg + "\n"
        page.update()
        
    def start_log_stream(ip):
        nonlocal log_running
        log_running = False
        time.sleep(0.5)
        log_box.value = f"--- Verbinde mit Live-Log von {ip} ---\n"
        page.update()
        log_running = True
        threading.Thread(target=_log_stream_task, args=(ip,), daemon=True).start()

    def _log_stream_task(ip):
        ansi_escape = re.compile(r'\x1b\[[0-9;]*[mK]')
        url = f"http://{ip}/events"
        try:
            with session.get(url, stream=True, timeout=5) as r:
                for line in r.iter_lines(decode_unicode=True):
                    if not log_running: break
                    if line:
                        if line.startswith("event: log"): continue
                        if line.startswith("data: "):
                            raw_log = line[6:]
                            clean_log = ansi_escape.sub('', raw_log)
                            log(clean_log)
        except Exception as e:
            if log_running: log(f"Log-Verbindung getrennt: {e}")

    # --- Control Backend ---
    def send_action(endpoint):
        ip = dropdown_mapping.get(device_dropdown.value)
        if ip: threading.Thread(target=lambda: session.post(f"http://{ip}/{endpoint}", timeout=2), daemon=True).start()

    def send_number_value(entity_name, value):
        ip = dropdown_mapping.get(device_dropdown.value)
        if ip:
            encoded_name = urllib.parse.quote(entity_name)
            threading.Thread(target=lambda: session.post(f"http://{ip}/number/{encoded_name}/set?value={int(value)}", timeout=2), daemon=True).start()

    def send_select_value(entity_name, value):
        ip = dropdown_mapping.get(device_dropdown.value)
        if ip:
            encoded_name = urllib.parse.quote(entity_name)
            encoded_val = urllib.parse.quote(value)
            threading.Thread(target=lambda: session.post(f"http://{ip}/select/{encoded_name}/set?option={encoded_val}", timeout=2), daemon=True).start()

    def send_switch_value(entity_name, state):
        ip = dropdown_mapping.get(device_dropdown.value)
        if ip:
            encoded_name = urllib.parse.quote(entity_name)
            action = "turn_on" if state else "turn_off"
            threading.Thread(target=lambda: session.post(f"http://{ip}/switch/{encoded_name}/{action}", timeout=2), daemon=True).start()

    def create_live_slider(label_text, from_val, to_val, steps, entity_name, color, init_val=None):
        val_lbl = ft.Text(str(init_val) if init_val is not None else str(from_val), size=12, weight="bold")
        def on_change(e):
            val_lbl.value = str(int(e.control.value))
            page.update()
            send_number_value(entity_name, e.control.value)
        sl = ft.Slider(min=from_val, max=to_val, divisions=steps, value=init_val or from_val, on_change=on_change, active_color=color)
        return ft.Column([
            ft.Row([ft.Text(label_text, size=12, weight="bold"), val_lbl], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
            sl
        ])

    input_dropdown = ft.Dropdown(options=[ft.dropdown.Option(v) for v in ["Toslink", "Aux", "Bluetooth", "WLAN"]], on_change=lambda e: send_select_value("Input Source", e.control.value))
    ir_dropdown = ft.Dropdown(options=[ft.dropdown.Option(v) for v in ["None", "Vol+", "Vol-", "Mute", "Input Next"]], on_change=lambda e: send_select_value("IR Learn Target", e.control.value))
    switch_night_mode = ft.Switch(label="Night Mode (DRC)", value=False, on_change=lambda e: send_switch_value("Night Mode (DRC)", e.control.value), active_color="#f1c40f")
    switch_clear_voice = ft.Switch(label="Clear Voice", value=False, on_change=lambda e: send_switch_value("Clear Voice", e.control.value), active_color="#f1c40f")

    # --- Live Sync Logic ---
    def check_for_updates(btrx_version, subtx_version, rp_version):
        btrx_fw_label.value = f"Aktuelle Version: [{btrx_version}]" if btrx_version not in ["N/A", "Offline"] else f"Aktuelle Version: Offline"
        subtx_fw_label.value = f"Aktuelle Version: [{subtx_version}]" if subtx_version not in ["N/A", "Offline"] else f"Aktuelle Version: Offline"
        rp_fw_label.value = f"Aktuelle Version: [{rp_version}]" if rp_version not in ["N/A", "Offline"] else f"Aktuelle Version: Offline"
        
        if online_version:
            if btrx_version != online_version and btrx_version != "Offline":
                btrx_flash_btn.bgcolor = "#e74c3c"
                btrx_flash_btn.text = "BT_RX UPDATE INSTALLIEREN"
            else:
                btrx_flash_btn.bgcolor = "#7a1a1a"
                btrx_flash_btn.text = "BT_RX UPDATE"
                
            if subtx_version != online_version and subtx_version != "Offline":
                subtx_flash_btn.bgcolor = "#e74c3c"
                subtx_flash_btn.text = "SUB_TX UPDATE INSTALLIEREN"
            else:
                subtx_flash_btn.bgcolor = "#7a1a1a"
                subtx_flash_btn.text = "SUB_TX UPDATE"
                
            if rp_version != online_version and rp_version != "Offline":
                rp_flash_btn.bgcolor = "#e74c3c"
                rp_flash_btn.text = "RP2354 UPDATE INSTALLIEREN"
            else:
                rp_flash_btn.bgcolor = "#7a1a1a"
                rp_flash_btn.text = "RP2354 UPDATE"

    def _update_dashboard_ui(src, sys_status, t_esp, t_dsp, fault, wifi, bt_conn, sub_conn):
        is_online = src != "Offline" and wifi != "Offline"
        status_dot.color = "#3fb950" if is_online else "#e74c3c"
        
        val_src.value = src
        val_src.color = "#3498db"
        val_sys.value = sys_status.upper() if sys_status != "Offline" else "N/A"
        val_sys.color = "#2ecc71" if sys_status == "ON" else "#888888"
        val_wifi.value = f"{wifi} dBm" if wifi != "Offline" else str(wifi)
        
        def parse_temp(val):
            try: return float(val), f"{val} °C"
            except: return 0.0, str(val)

        def update_temp_ui(val_lbl, pbar, temp_val, temp_str):
            val_lbl.value = temp_str
            val_lbl.color = "#e74c3c" if temp_val > 50 else "#ffffff"
            progress = max(0.0, min(1.0, (temp_val - 20) / 60))
            pbar.value = progress
            if temp_val >= 60: pbar.color = "#e74c3c"
            elif temp_val >= 45: pbar.color = "#f39c12"
            else: pbar.color = "#2ecc71"

        update_temp_ui(val_temp_esp, pb_temp_esp, *parse_temp(t_esp))
        update_temp_ui(val_temp_dsp, pb_temp_dsp, *parse_temp(t_dsp))
        
        val_amp_stat.value = "FAULT" if fault == "ON" else "OK"
        val_amp_stat.color = "#e74c3c" if fault == "ON" else "#2ecc71"
        
        is_bt_conn = bt_conn not in ["Offline", "N/A"]
        val_bl_conn.value = "VERBUNDEN" if is_bt_conn else "GETRENNT"
        val_bl_conn.color = "#3498db" if is_bt_conn else "#888888"
        
        is_sub_conn = sub_conn not in ["Offline", "N/A"]
        val_sub_conn.value = "VERBUNDEN" if is_sub_conn else "GETRENNT"
        val_sub_conn.color = "#e67e22" if is_sub_conn else "#888888"

        page.update()

    def _fetch_api_data(ip):
        def get_state(domain, entity_name):
            try:
                encoded_name = urllib.parse.quote(entity_name)
                url = f"http://{ip}/{domain}/{encoded_name}"
                r = session.get(url, timeout=2).json()
                return r.get("state", "N/A")
            except: return "Offline"

        src = get_state("text_sensor", "Active Input")
        sys_status = get_state("light", "Soundbar Status")
        t_esp = get_state("sensor", "Master Temperature")
        t_dsp = get_state("sensor", "DSP Temperature")
        fault = get_state("binary_sensor", "Verstärker Überlastung (Fault)")
        wifi = get_state("sensor", "WLAN Signal")
        btrx_version = get_state("text_sensor", "BT Version")
        subtx_version = get_state("text_sensor", "SUB Version")
        rp_version = get_state("text_sensor", "DSP Version")
        
        bt_conn = btrx_version
        sub_conn = subtx_version

        nonlocal last_update_check, online_version, github_assets
        current_time = time.time()
        if current_time - last_update_check > UPDATE_CHECK_INTERVAL:
            last_update_check = current_time
            try:
                release_info = requests.get(GITHUB_API_LATEST, timeout=3).json()
                online_version = release_info.get("tag_name", "2.1.0.0")
                github_assets = release_info.get("assets", [])
            except:
                online_version = None

        _update_dashboard_ui(src, sys_status, t_esp, t_dsp, fault, wifi, bt_conn, sub_conn)
        check_for_updates(btrx_version, subtx_version, rp_version)
        page.update()

        nonlocal is_fetching
        is_fetching = False

    def sync_live_data():
        nonlocal is_fetching, current_log_ip
        if is_fetching: return
        ip = dropdown_mapping.get(device_dropdown.value)
        if not ip: return
            
        is_fetching = True
        threading.Thread(target=_fetch_api_data, args=(ip,), daemon=True).start()
        
        if current_log_ip != ip:
            current_log_ip = ip
            start_log_stream(ip)

    def periodic_sync():
        while True:
            if page.session_id:
                sync_live_data()
            time.sleep(1)
            
    threading.Thread(target=periodic_sync, daemon=True).start()

    # --- Flashing Logic ---
    def start_flash_thread(target):
        threading.Thread(target=run_flash, args=(target,), daemon=True).start()

    def run_flash(target):
        ip = dropdown_mapping.get(device_dropdown.value)
        if not ip: return

        if target == "btrx":
            btn, status_lbl = btrx_flash_btn, btrx_status
        elif target == "subtx":
            btn, status_lbl = subtx_flash_btn, subtx_status
        else:
            btn, status_lbl = rp_flash_btn, rp_status

        def update_ui(): page.update()

        btn.disabled = True
        btn.text = "LADE FIRMWARE..."
        flash_progress.visible = True
        flash_progress.value = 0.0
        status_lbl.value = "Schritt 0: Lade Firmware von GitHub..."
        status_lbl.color = "orange"
        update_ui()

        try:
            download_url = None
            if github_assets:
                for asset in github_assets:
                    if target.lower() in asset['name'].lower():
                        download_url = asset['browser_download_url']
                        break

            if not download_url:
                if target == "btrx": download_url = "https://raw.githubusercontent.com/babeinlovexd/Insane-Sound-System/main/Firmware/Bluetooth/firmware.bin"
                elif target == "subtx": download_url = "https://raw.githubusercontent.com/babeinlovexd/Insane-Sound-System/main/Firmware/SUB_TX/firmware.bin"
                else: download_url = "https://raw.githubusercontent.com/babeinlovexd/Insane-Sound-System/main/Firmware/DSP/firmware.bin"

            r = requests.get(download_url, timeout=15)
            r.raise_for_status()
            
            # Save firmware locally via standard Python temp dir logic, since we can't reliably predict Android internal structure via typical os module methods without Flet's helpers. 
            fw_path = os.path.join(os.path.expanduser('~'), "latest_firmware.bin") 
            with open(fw_path, "wb") as f:
                f.write(r.content)

            btn.text = "FLASHING..."
            update_ui()

            if target in ["btrx", "subtx"]:
                target_name_ui = "BT_RX" if target == "btrx" else "SUB_TX"
                port = 8083 if target == "btrx" else 8082
                button_encoded = urllib.parse.quote("Flash Mode: Bluetooth (ESP32)" if target == "btrx" else "Flash Mode: Sub-TX (ESP32)")

                status_lbl.value = f"Schritt 1: Setze {target_name_ui} in Flash-Modus..."
                update_ui()
                session.post(f"http://{ip}/button/{button_encoded}/press", timeout=5)
                time.sleep(2)

                status_lbl.value = f"Schritt 2: Flashe {target_name_ui} Firmware..."
                update_ui()

                command_args = [
                    "--port", f"socket://{ip}:{port}",
                    "--baud", "115200",
                    "write_flash", "0x10000", fw_path
                ]

                def gui_update(msg):
                    text = f"Flashing: {msg.split('...')[0]}..." if "..." in msg else msg
                    status_lbl.value = text
                    log(msg)
                    if "(" in msg and "%" in msg:
                        try:
                            pct_str = msg.split("(")[1].split("%")[0].strip()
                            flash_progress.value = float(pct_str) / 100.0
                        except: pass
                    update_ui()

                redirector = ConsoleRedirector(gui_update)
                with contextlib.redirect_stdout(redirector):
                    esptool.main(command_args)

                status_lbl.value = f"Schritt 3: {target_name_ui} Neustart..."
                update_ui()
                encoded_btn = urllib.parse.quote("Normal Boot: Bluetooth (ESP32)" if target == "btrx" else "Normal Boot: Sub-TX (ESP32)")
                session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=5)

            elif target == "rp2354":
                status_lbl.value = "Schritt 1: Setze RP2354 in Flash-Modus..."
                update_ui()
                encoded_btn = urllib.parse.quote("Flash Mode: DSP (RP2354)")
                session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=5)
                time.sleep(2)

                status_lbl.value = "Schritt 2: Flashe RP2354 Firmware..."
                update_ui()

                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(15)
                    s.connect((ip, 8081))

                    with open(fw_path, 'rb') as f:
                        fw_data = f.read()

                    file_size = len(fw_data)

                    status_lbl.value = "Schritt 2: Sende RP2354 Knock Sequence..."
                    update_ui()
                    s.sendall(bytes([0x56, 0xff, 0x8b, 0xe4]))
                    s.sendall(b'n')
                    resp = s.recv(1)
                    if resp != b'n':
                        s.sendall(bytes([0x56, 0xff, 0x8b, 0xe4]))
                        s.sendall(b'n')
                        resp = s.recv(1)
                        if resp != b'n':
                            raise Exception("RP2354 UART Bootloader antwortet nicht auf Knock.")

                    status_lbl.value = "Schritt 3: Flashe 32-Byte Blöcke..."
                    update_ui()

                    sent = 0
                    last_pct_sent = -1

                    for i in range(0, file_size, 32):
                        chunk = fw_data[i:i+32]
                        if len(chunk) < 32:
                            chunk += bytes([0x00] * (32 - len(chunk)))

                        s.sendall(b'w')
                        s.sendall(chunk)
                        resp = s.recv(1)
                        if resp != b'w':
                            raise Exception(f"RP2354 Schreibfehler bei Offset {i}")

                        sent += len(chunk)
                        pct = min(sent / file_size, 1.0)
                        if int(pct * 100) > last_pct_sent:
                            flash_progress.value = pct
                            status_lbl.value = f"Flashing: {int(pct*100)}%"
                            update_ui()
                            last_pct_sent = int(pct * 100)

                    status_lbl.value = "Schritt 4: Starte RP2354 Firmware..."
                    update_ui()
                    s.sendall(b'x')
                    try: s.recv(1)
                    except socket.timeout: pass

                status_lbl.value = "Schritt 3: RP2354 geflasht. Reboot."
                update_ui()
                encoded_btn = urllib.parse.quote("Normal Boot: DSP (RP2354)")
                session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=5)

            status_lbl.value = "🚀 Update 100% erfolgreich!"
            status_lbl.color = "#3fb950"
            show_snackbar(f"{target.upper()} wurde erfolgreich aktualisiert!")

        except Exception as e:
            status_lbl.value = f"❌ Flashen fehlgeschlagen: {e}"
            status_lbl.color = "red"
            log(f"Fehler: {e}")
        finally:
            btn.disabled = False
            btn.text = f"{target.upper()} UPDATE"
            flash_progress.visible = False
            update_ui()

    # --- UI Tabs Setup ---
    tabs = ft.Tabs(
        selected_index=0,
        animation_duration=300,
        tabs=[
            ft.Tab(
                text="Steuerung",
                content=ft.ListView(
                    expand=True, spacing=10, padding=20,
                    controls=[
                        ft.Text("System", size=20, weight="bold", color="#2f81f7"),
                        ft.Text("Input Source"), input_dropdown,
                        ft.Row([
                            ft.ElevatedButton("Pair Subwoofer", bgcolor="#e67e22", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Pair Subwoofer')}/press")),
                            ft.ElevatedButton("Master Restart", bgcolor="#8e44ad", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Master Restart')}/press")),
                        ]),
                        
                        ft.Text("Infrarot (IR)", size=20, weight="bold", color="#2f81f7"),
                        ft.Text("IR Learn Target"), ir_dropdown,
                        ft.Row([
                            ft.ElevatedButton("IR Learn", bgcolor="#3498db", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Start IR Learn')}/press")),
                            ft.ElevatedButton("Clear IR", bgcolor="#c0392b", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Alle IR-Codes löschen')}/press")),
                        ]),
                        
                        ft.Text("Audio Verbesserungen", size=18, weight="bold", color="#f1c40f"),
                        ft.Row([switch_night_mode, switch_clear_voice]),
                        
                        ft.Text("Allgemein", size=18, weight="bold", color="#3fb950"),
                        create_live_slider("Master Volume (0-100)", 0, 100, 100, "Master Volume", "#2ecc71", 50),
                        create_live_slider("OLED Brightness (0-100)", 0, 100, 100, "OLED Brightness", "#3498db", 100),
                    ]
                )
            ),
            ft.Tab(
                text="DSP",
                content=ft.ListView(
                    expand=True, spacing=10, padding=20,
                    controls=[
                        ft.Text("Frequenzweichen (Crossovers)", size=18, weight="bold", color="#d29922"),
                        create_live_slider("Sub LP Crossover", 50, 255, 205, "Sub LP Crossover", "#e67e22", 120),
                        create_live_slider("Sat HP Crossover", 50, 255, 205, "Sat HP Crossover", "#e67e22", 95),
                        create_live_slider("Mid LP Crossover", 500, 10000, 95, "Mid LP Crossover", "#e67e22", 3500),
                        create_live_slider("High HP Crossover", 500, 10000, 95, "High HP Crossover", "#e67e22", 3500),
                        
                        ft.Text("Equalizer", size=18, weight="bold", color="#e3b341"),
                        create_live_slider("Sub Trim", 0, 20, 20, "Sub Trim", "#f1c40f", 10),
                        create_live_slider("Mid Trim", 0, 20, 20, "Mid Trim", "#f1c40f", 10),
                        create_live_slider("High Trim", 0, 20, 20, "High Trim", "#f1c40f", 4),
                        
                        create_live_slider("EQ 100 Hz (Bass)", 0, 20, 20, "EQ 100 Hz (Bass)", "#f1c40f", 10),
                        create_live_slider("EQ 300 Hz (Low-Mid)", 0, 20, 20, "EQ 300 Hz (Low-Mid)", "#f1c40f", 10),
                        create_live_slider("EQ 1 kHz (Mid)", 0, 20, 20, "EQ 1 kHz (Mid)", "#f1c40f", 10),
                        create_live_slider("EQ 3 kHz (High-Mid)", 0, 20, 20, "EQ 3 kHz (High-Mid)", "#f1c40f", 10),
                        create_live_slider("EQ 8 kHz (Treble)", 0, 20, 20, "EQ 8 kHz (Treble)", "#f1c40f", 10),
                    ]
                )
            ),
            ft.Tab(
                text="Telemetrie",
                content=ft.Container(
                    bgcolor="#0d1117", border_radius=10, padding=20,
                    content=ft.Column([
                        ft.Row([tele_col1_1, tele_col1_2, tele_col1_3], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([tele_col2_1, tele_col2_2, tele_col2_3], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                        ft.Row([tele_col3_1, tele_col3_2], alignment=ft.MainAxisAlignment.START),
                    ], spacing=20)
                )
            ),
            ft.Tab(
                text="Updates",
                content=ft.ListView(
                    expand=True, spacing=10, padding=20,
                    controls=[
                        flash_progress,
                        ft.Container(
                            bgcolor="#161b22", border=ft.border.all(1, "#30363d"), border_radius=10, padding=20,
                            content=ft.Column([
                                ft.Text("ESP32 (BT_RX / BLUETOOTH)", size=14, weight="bold", color="#2f81f7"),
                                btrx_fw_label, btrx_status, btrx_flash_btn
                            ])
                        ),
                        ft.Container(
                            bgcolor="#161b22", border=ft.border.all(1, "#30363d"), border_radius=10, padding=20,
                            content=ft.Column([
                                ft.Text("ESP32 (SUB_TX / SUBWOOFER)", size=14, weight="bold", color="#3fb950"),
                                subtx_fw_label, subtx_status, subtx_flash_btn
                            ])
                        ),
                        ft.Container(
                            bgcolor="#161b22", border=ft.border.all(1, "#30363d"), border_radius=10, padding=20,
                            content=ft.Column([
                                ft.Text("RP2354A (DSP)", size=14, weight="bold", color="#d29922"),
                                rp_fw_label, rp_status, rp_flash_btn
                            ])
                        )
                    ]
                )
            ),
            ft.Tab(text="Log", content=log_box),
            ft.Tab(
                text="Info",
                content=ft.Column([
                    ft.Text("Insane Control Center", size=24, weight="bold"),
                    ft.Text("Version 1.0.0", size=14, color="#8b949e"),
                    ft.ElevatedButton("GitHub Repository", on_click=lambda e: page.launch_url(GITHUB_URL)),
                    ft.Text("Powered by Open Source Tools:", size=12, weight="bold"),
                    ft.TextButton("esptool.py", on_click=lambda e: page.launch_url("https://github.com/espressif/esptool")),
                    ft.TextButton("Flet", on_click=lambda e: page.launch_url("https://flet.dev/"))
                ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
            )
        ],
        expand=True
    )
    
    page.add(tabs)
    page.update()

    # --- Start ZeroConf Scan ---
    zeroconf = Zeroconf()
    if not favorite_devices:
        device_dropdown.options = [ft.dropdown.Option("Suche läuft...")]
        device_dropdown.disabled = True
        device_dropdown.value = "Suche läuft..."
    else:
        _update_dropdown()
    ServiceBrowser(zeroconf, "_esphomelib._tcp.local.", DeviceListener(add_device_to_ui))

if __name__ == "__main__":
    ft.app(target=main)