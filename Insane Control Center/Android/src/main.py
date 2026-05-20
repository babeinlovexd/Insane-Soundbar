import flet as ft
import socket
import threading
import requests
import urllib.parse
import os
import re
import time
import asyncio
import json
import warnings
from zeroconf import ServiceBrowser, Zeroconf

# Suppress Flet deprecation warnings due to client/server version mismatch
warnings.simplefilter("ignore", DeprecationWarning)

GITHUB_URL = "https://github.com/babeinlovexd/Insane-Soundbar"

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

async def main(page: ft.Page):
    # --- persistent storage ---
    prefs = page.shared_preferences
    
    # --- Fenster-Setup ---
    page.title = "Insane Control Center"
    page.theme_mode = ft.ThemeMode.DARK
    page.window.width = 800
    page.window.height = 700
    page.bgcolor = "#0d1117"
    page.scroll = "auto"
    
    page.update()
    
    # Wait a moment for SharedPreferences control to be registered on the client side
    await asyncio.sleep(0.5)
    
    # --- Variablen ---
    scanned_devices = {}
    favorite_devices = {} # Will be loaded later
    dropdown_mapping = {}
    
    session = requests.Session()
    is_fetching = False
    log_running = False
    current_log_ip = None
    browser: ServiceBrowser | None = None
    # --- UI Helper & Callbacks ---
    async def show_snackbar(message, is_error=False):
        page.snack_bar = ft.SnackBar(ft.Text(str(message)), bgcolor="red" if is_error else "green")
        page.snack_bar.open = True

    async def log(msg):
        if 'log_box' in locals() or 'log_box' in globals():
            log_box.value = (log_box.value or "") + str(msg) + "\n"
            page.update()

    async def _update_dropdown():
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
                await sync_live_data()
            elif current not in vals:
                base_current = str(current).replace(" ⭐", "")
                if f"{base_current} ⭐" in vals:
                    device_dropdown.value = f"{base_current} ⭐"
                elif base_current in vals:
                    device_dropdown.value = base_current
                else:
                    device_dropdown.value = vals[0]
                    await sync_live_data()
        page.update()

    async def add_device_to_ui(name, ip):
        base_name = f"{name} ({ip})"
        scanned_devices[base_name] = ip
        await _update_dropdown()

    async def save_favorite(_e):
        current = device_dropdown.value
        if current and current != "Suche läuft...":
            base_name = current.replace(" ⭐", "")
            ip = dropdown_mapping.get(current)
            if ip:
                favorite_devices[base_name] = ip
                await prefs.set("iss_favorites", json.dumps(favorite_devices))
                await show_snackbar(f"{base_name} wurde gespeichert!")
                await _update_dropdown()

    async def delete_favorite(_e):
        current = device_dropdown.value
        if current and current != "Suche läuft...":
            base_name = current.replace(" ⭐", "")
            if base_name in favorite_devices:
                del favorite_devices[base_name]
                await prefs.set("iss_favorites", json.dumps(favorite_devices))
                await _update_dropdown()

    async def sync_live_data():
        nonlocal is_fetching, current_log_ip
        if is_fetching: return
        ip = dropdown_mapping.get(device_dropdown.value)
        if not ip: return
        is_fetching = True
        threading.Thread(target=_fetch_api_data, args=(ip,), daemon=True).start()
        if current_log_ip != ip:
            current_log_ip = ip
            await start_log_stream(ip)

    async def on_device_select(_e):
        await sync_live_data()

    async def start_scan(_e=None):
        nonlocal browser
        scanned_devices.clear()
        if not favorite_devices:
            device_dropdown.options = [ft.dropdown.Option("Suche läuft...")]
            device_dropdown.disabled = True
            device_dropdown.value = "Suche läuft..."
        else:
            await _update_dropdown()
        if browser:
            try:
                browser.cancel()
            except Exception:
                pass
        browser = ServiceBrowser(zeroconf, "_esphomelib._tcp.local.", DeviceListener(lambda n, i: page.run_task(add_device_to_ui, n, i)))
        await show_snackbar("Netzwerk Scan gestartet...", is_error=False)

    async def restart_bluetooth(_e):
        ip = dropdown_mapping.get(device_dropdown.value)
        if not ip: return
        encoded_btn = urllib.parse.quote("Normal Boot: Bluetooth (ESP32)")
        threading.Thread(target=lambda: session.post(f"http://{ip}/button/{encoded_btn}/press", timeout=3), daemon=True).start()
        await show_snackbar("⚡ Bluetooth-Chip (BT_RX) wird neugestartet!", is_error=False)

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

    async def start_log_stream(ip):
        nonlocal log_running
        log_running = False
        await asyncio.sleep(0.5)
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
                            clean_log = ansi_escape.sub('', str(raw_log))
                            page.run_task(log, clean_log)
        except Exception as e:
            if log_running: page.run_task(log, f"Log-Verbindung getrennt: {e}")


    async def _update_dashboard_ui(src, sys_status, t_esp, t_dsp, fault, wifi, bt_conn, sub_conn):
        is_online = src != "Offline" and wifi != "Offline"
        status_dot.color = "#3fb950" if is_online else "#e74c3c"
        val_src.value = src
        val_src.color = "#3498db"
        val_sys.value = sys_status.upper() if sys_status != "Offline" else "N/A"
        val_sys.color = "#2ecc71" if sys_status == "ON" else "#888888"
        val_wifi.value = f"{wifi} dBm" if wifi != "Offline" else str(wifi)
        def parse_temp(val):
            try: return float(val), f"{val} °C"
            except Exception: return 0.0, str(val)
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
            except Exception: return "Offline"
        src = get_state("text_sensor", "Active Input")
        sys_status = get_state("light", "Soundbar Status")
        t_esp = get_state("sensor", "Master Temperature")
        t_dsp = get_state("sensor", "DSP Temperature")
        fault = get_state("binary_sensor", "Verstärker Überlastung (Fault)")
        wifi = get_state("sensor", "WLAN Signal")
        bt_conn = get_state("text_sensor", "BT Version")
        sub_conn = get_state("text_sensor", "SUB Version")
        page.run_task(_update_dashboard_ui, src, sys_status, t_esp, t_dsp, fault, wifi, bt_conn, sub_conn)
        nonlocal is_fetching
        is_fetching = False

    async def periodic_sync():
        while True:
            try:
                if hasattr(page, 'session_id') and page.session_id:
                    await sync_live_data()
            except Exception:
                pass
            await asyncio.sleep(1)


    def apply_preset(preset):
        settings = {}
        if preset == "kino":
            settings = {
                "EQ 100 Hz (Bass)": 14,
                "EQ 300 Hz (Low-Mid)": 10,
                "EQ 1 kHz (Mid)": 10,
                "EQ 3 kHz (High-Mid)": 12,
                "EQ 8 kHz (Treble)": 12,
                "Sub Trim": 14,
                "Clear Voice": True
            }
        elif preset == "musik":
            settings = {
                "EQ 100 Hz (Bass)": 12,
                "EQ 300 Hz (Low-Mid)": 10,
                "EQ 1 kHz (Mid)": 10,
                "EQ 3 kHz (High-Mid)": 11,
                "EQ 8 kHz (Treble)": 11,
                "Sub Trim": 12,
                "Clear Voice": False
            }
        elif preset == "gaming":
            settings = {
                "EQ 100 Hz (Bass)": 15,
                "EQ 300 Hz (Low-Mid)": 11,
                "EQ 1 kHz (Mid)": 9,
                "EQ 3 kHz (High-Mid)": 12,
                "EQ 8 kHz (Treble)": 13,
                "Sub Trim": 15,
                "Clear Voice": True
            }
        elif preset == "flat":
            settings = {
                "EQ 100 Hz (Bass)": 10,
                "EQ 300 Hz (Low-Mid)": 10,
                "EQ 1 kHz (Mid)": 10,
                "EQ 3 kHz (High-Mid)": 10,
                "EQ 8 kHz (Treble)": 10,
                "Sub Trim": 10,
                "Clear Voice": False
            }

        for k, v in settings.items():
            if type(v) == bool:
                send_switch_value(k, v)
                if k == "Clear Voice":
                    switch_clear_voice.value = v
            else:
                send_number_value(k, v)
                if k in sliders_refs:
                    sliders_refs[k].value = v
        page.update()


    sliders_refs = {}

    def create_live_slider(label_text, from_val, to_val, steps, entity_name, color, init_val=None):
        val_lbl = ft.Text(str(init_val) if init_val is not None else str(from_val), size=12, weight="bold")
        def on_change(e):
            val_lbl.value = str(int(e.control.value)); page.update()
            send_number_value(entity_name, e.control.value)
        sl = ft.Slider(min=from_val, max=to_val, divisions=steps, value=init_val or from_val, on_change=on_change, active_color=color)
        sliders_refs[entity_name] = sl
        return ft.Column([ft.Row([ft.Text(label_text, size=12, weight="bold"), val_lbl], alignment=ft.MainAxisAlignment.SPACE_BETWEEN), sl])

    # --- UI Definitions ---
    # FilePickers for Backup/Restore
    async def save_backup_result(e):
        if not e.path: return
        settings = {
            "EQ 100 Hz (Bass)": int(sliders_refs.get("EQ 100 Hz (Bass)").value) if "EQ 100 Hz (Bass)" in sliders_refs else 10,
            "EQ 300 Hz (Low-Mid)": int(sliders_refs.get("EQ 300 Hz (Low-Mid)").value) if "EQ 300 Hz (Low-Mid)" in sliders_refs else 10,
            "EQ 1 kHz (Mid)": int(sliders_refs.get("EQ 1 kHz (Mid)").value) if "EQ 1 kHz (Mid)" in sliders_refs else 10,
            "EQ 3 kHz (High-Mid)": int(sliders_refs.get("EQ 3 kHz (High-Mid)").value) if "EQ 3 kHz (High-Mid)" in sliders_refs else 10,
            "EQ 8 kHz (Treble)": int(sliders_refs.get("EQ 8 kHz (Treble)").value) if "EQ 8 kHz (Treble)" in sliders_refs else 10,
            "Sub Trim": int(sliders_refs.get("Sub Trim").value) if "Sub Trim" in sliders_refs else 10,
            "Mid Trim": int(sliders_refs.get("Mid Trim").value) if "Mid Trim" in sliders_refs else 10,
            "High Trim": int(sliders_refs.get("High Trim").value) if "High Trim" in sliders_refs else 10,
            "Sub LP Crossover": int(sliders_refs.get("Sub LP Crossover").value) if "Sub LP Crossover" in sliders_refs else 120,
            "Sat HP Crossover": int(sliders_refs.get("Sat HP Crossover").value) if "Sat HP Crossover" in sliders_refs else 95,
            "Mid LP Crossover": int(sliders_refs.get("Mid LP Crossover").value) if "Mid LP Crossover" in sliders_refs else 3500,
            "High HP Crossover": int(sliders_refs.get("High HP Crossover").value) if "High HP Crossover" in sliders_refs else 3500
        }
        import json
        with open(e.path, "w") as f:
            json.dump(settings, f, indent=4)
        await show_snackbar("Backup gespeichert!")

    async def pick_restore_result(e):
        if not e.files or len(e.files) == 0: return
        try:
            import json
            with open(e.files[0].path, "r") as f:
                settings = json.load(f)
            for k, v in settings.items():
                send_number_value(k, v)
                if k in sliders_refs:
                    sliders_refs[k].value = v
            page.update()
            await show_snackbar("Einstellungen wiederhergestellt!")
        except Exception as ex:
            await show_snackbar(f"Fehler: {ex}", is_error=True)

    save_file_dialog = ft.FilePicker(); save_file_dialog.on_result = save_backup_result
    pick_file_dialog = ft.FilePicker(); pick_file_dialog.on_result = pick_restore_result
    page.overlay.extend([save_file_dialog, pick_file_dialog])

    status_dot = ft.Text("●", size=20, color="#444444")
    device_dropdown = ft.Dropdown(
        options=[ft.dropdown.Option("Suche läuft...")],
        value="Suche läuft...",
        disabled=True, expand=True, on_select=on_device_select
    )
    
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


    log_box = ft.TextField(multiline=True, read_only=True, expand=True, text_size=12, min_lines=20, max_lines=20, bgcolor="#0d1117", border_color="transparent")

    input_dropdown = ft.Dropdown(options=[ft.dropdown.Option(v) for v in ["Toslink", "Aux", "Bluetooth", "WLAN"]], on_select=lambda e: send_select_value("Input Source", e.control.value))
    ir_dropdown = ft.Dropdown(options=[ft.dropdown.Option(v) for v in ["None", "Vol+", "Vol-", "Mute", "Input Next"]], on_select=lambda e: send_select_value("IR Learn Target", e.control.value))
    switch_night_mode = ft.Switch(label="Night Mode (DRC)", value=False, on_change=lambda e: send_switch_value("Night Mode (DRC)", e.control.value), active_color="#f1c40f")
    switch_clear_voice = ft.Switch(label="Clear Voice", value=False, on_change=lambda e: send_switch_value("Clear Voice", e.control.value), active_color="#f1c40f")

    tabs = ft.Tabs(
        selected_index=0, animation_duration=300, expand=True,
        length=5,
        content=ft.Column(
            expand=True,
            controls=[
                ft.TabBar(
                    tabs=[
                        ft.Tab(label="Steuerung"),
                        ft.Tab(label="DSP"),
                        ft.Tab(label="Telemetrie"),
                        ft.Tab(label="Log"),
                        ft.Tab(label="Info"),
                    ]
                ),
                ft.TabBarView(
                    expand=True,
                    controls=[
                        ft.ListView(expand=True, spacing=10, padding=20, controls=[
                            ft.Text("Quick Presets", size=20, weight="bold", color="#1abc9c"),
                            ft.Row([
                                ft.Button("Kino", bgcolor="#1abc9c", color="white", on_click=lambda e: apply_preset("kino")),
                                ft.Button("Musik", bgcolor="#1abc9c", color="white", on_click=lambda e: apply_preset("musik")),
                                ft.Button("Gaming", bgcolor="#1abc9c", color="white", on_click=lambda e: apply_preset("gaming")),
                                ft.Button("Flat", bgcolor="#1abc9c", color="white", on_click=lambda e: apply_preset("flat")),
                            ], wrap=True),
                            ft.Text("System", size=20, weight="bold", color="#2f81f7"),
                            ft.Text("Input Source"), input_dropdown,
                            ft.Row([
                                ft.Button("Pair Subwoofer", bgcolor="#e67e22", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Pair Subwoofer')}/press")),
                                ft.Button("Master Restart", bgcolor="#8e44ad", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Master Restart')}/press")),
                            ]),
                            ft.Text("Infrarot (IR)", size=20, weight="bold", color="#2f81f7"),
                            ft.Text("IR Learn Target"), ir_dropdown,
                            ft.Row([
                                ft.Button("IR Learn", bgcolor="#3498db", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Start IR Learn')}/press")),
                                ft.Button("Clear IR", bgcolor="#c0392b", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Alle IR-Codes löschen')}/press")),
                            ]),
                            ft.Text("Bluetooth Media Controls", size=20, weight="bold", color="#9b59b6"),
                            ft.Row([
                                ft.Button("⏮ Prev", bgcolor="#8e44ad", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Media Prev')}/press")),
                                ft.Button("▶ Play", bgcolor="#8e44ad", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Media Play')}/press")),
                                ft.Button("⏸ Pause", bgcolor="#8e44ad", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Media Pause')}/press")),
                                ft.Button("⏭ Next", bgcolor="#8e44ad", color="white", on_click=lambda e: send_action(f"button/{urllib.parse.quote('Media Next')}/press")),
                            ], wrap=True),
                            ft.Text("Audio Verbesserungen", size=18, weight="bold", color="#f1c40f"),
                            ft.Row([switch_night_mode, switch_clear_voice]),
                            ft.Text("Allgemein", size=18, weight="bold", color="#3fb950"),
                            create_live_slider("Master Volume (0-100)", 0, 100, 100, "Master Volume", "#2ecc71", 50),
                            create_live_slider("OLED Brightness (0-100)", 0, 100, 100, "OLED Brightness", "#3498db", 100),
                        ]),
                        ft.ListView(expand=True, spacing=10, padding=20, controls=[
                            ft.Text("Frequenzweichen (Crossovers)", size=18, weight="bold", color="#d29922"),
                            ft.Row([
                                ft.Button("Backup Settings", on_click=lambda _: save_file_dialog.save_file(allowed_extensions=["json"])),
                                ft.Button("Restore Settings", on_click=lambda _: pick_file_dialog.pick_files(allowed_extensions=["json"])),
                            ]),
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
                        ]),
                        ft.Container(bgcolor="#0d1117", border_radius=10, padding=20, content=ft.Column([
                            ft.Row([tele_col1_1, tele_col1_2, tele_col1_3], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([tele_col2_1, tele_col2_2, tele_col2_3], alignment=ft.MainAxisAlignment.SPACE_BETWEEN),
                            ft.Row([tele_col3_1, tele_col3_2], alignment=ft.MainAxisAlignment.START),
                        ], spacing=20)),
                        log_box,
                        ft.Column([
                            ft.Text("Insane Control Center", size=24, weight="bold"),
                            ft.Text("Version 1.0.0", size=14, color="#8b949e"),
                            ft.Button("GitHub Repository", on_click=lambda e: page.launch_url(GITHUB_URL)),
                            ft.Text("Powered by Open Source Tools:", size=12, weight="bold"),
                            ft.TextButton("esptool.py", on_click=lambda e: page.launch_url("https://github.com/espressif/esptool")),
                            ft.TextButton("Flet", on_click=lambda e: page.launch_url("https://flet.dev/"))
                        ], alignment=ft.MainAxisAlignment.CENTER, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                    ]
                )
            ]
        )
    )

    page.add(
        ft.Row([ft.Text("Insane Control Center", size=26, weight="bold", color="#c9d1d9"), status_dot], alignment=ft.MainAxisAlignment.START),
        ft.Container(
            bgcolor="#161b22", border=ft.Border(ft.BorderSide(1, "#30363d"), ft.BorderSide(1, "#30363d"), ft.BorderSide(1, "#30363d"), ft.BorderSide(1, "#30363d")), border_radius=10, padding=20,
            content=ft.Row([
                device_dropdown,
                ft.Button("⭐ Merken", on_click=save_favorite, bgcolor="transparent", color="#e3b341"),
                ft.Button("🔄 Scan", on_click=start_scan, bgcolor="transparent", color="#2ecc71"),
                ft.Button("✖ Löschen", on_click=delete_favorite, bgcolor="transparent", color="#c0392b")
            ])
        ),
        tabs
    )
    page.update()

    # --- Start Logic ---
    page.run_task(periodic_sync)
    zeroconf = Zeroconf()
    
    # Final Delay and loading
    await asyncio.sleep(1.0)
    try:
        raw_favs = await prefs.get("iss_favorites")
        if raw_favs:
            loaded_favs = json.loads(raw_favs)
            favorite_devices.update(loaded_favs)
    except Exception:
        pass
        
    await _update_dropdown()
    await start_scan(None)

if __name__ == "__main__":
    ft.run(main)
