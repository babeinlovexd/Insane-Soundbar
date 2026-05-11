import os
import subprocess
import shutil
import sys
import time

def robust_clean(path):
    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except PermissionError:
            time.sleep(1) 
            shutil.rmtree(path, ignore_errors=True)

def build_insane_flasher():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    script_name = "InsaneFlasher.py"
    exe_name = "InsaneFlasher"
    icon_file = "logo.ico"
    png_file = "logo.png"

    print(f"--- Starte Build-Prozess für {exe_name} ---")
    print(f"Arbeitsverzeichnis: {os.getcwd()}")

    robust_clean("build")
    robust_clean("dist")

    required_files = [script_name, icon_file, png_file]
    for f in required_files:
        if not os.path.exists(f):
            print(f"\n❌ FEHLER: Datei '{f}' wurde nicht gefunden!")
            input("\nDrücke Enter zum Beenden...")
            return

    cmd = [
        "py", "-m", "PyInstaller",
        "-y",               
        "--noconsole",
        "--onefile",
        f"--name={exe_name}",
        f"--icon={icon_file}",
        f"--add-data={png_file}{os.pathsep}.",
        f"--add-data={icon_file}{os.pathsep}.",
        "--hidden-import=serial.urlhandler.protocol_socket",
        "--collect-data=esptool",
        script_name
    ]

    try:
        print("🏗️  Kompiliere... (Das kann einen Moment dauern)")
        subprocess.check_call(cmd)
        print("\n✅ BUILD ERFOLGREICH!")
        print(f"Deine Datei findest du im Ordner: {os.path.abspath('dist')}")
        
        robust_clean("build")
        spec_file = f"{exe_name}.spec"
        if os.path.exists(spec_file): 
            os.remove(spec_file)
        print("🧹 Temporäre Build-Dateien wurden entfernt.")

    except subprocess.CalledProcessError:
        print("\n❌ FEHLER: PyInstaller ist fehlgeschlagen.")
    except Exception as e:
        print(f"\n❌ Unerwarteter Fehler: {e}")

    input("\nFertig! Drücke Enter zum Beenden...")

if __name__ == "__main__":
    build_insane_flasher()