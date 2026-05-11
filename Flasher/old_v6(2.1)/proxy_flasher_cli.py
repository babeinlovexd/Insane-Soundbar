import sys
import time
import argparse
import logging
import requests
import subprocess
import os
import socket
from zeroconf import ServiceBrowser, Zeroconf

# Simulating finding the S3 via zeroconf (from V5 concept)
class MyListener:
    def remove_service(self, zeroconf, type, name):
        pass

    def add_service(self, zeroconf, type, name):
        info = zeroconf.get_service_info(type, name)
        if info:
            print(f"Found Insane Audio S3 at {info.parsed_addresses()[0]}")

def setup_s3_proxy(ip, target_chip):
    """
    Tells the S3 over API to put the target chip into flash mode.
    """
    print(f"[{ip}] Telling S3 to put {target_chip} into flash mode...")
    
    button_id = "wroom_flash_mode" if target_chip == "wroom" else "rp2354_flash_mode"
    url = f"http://{ip}/button/{button_id}/press"
    try:
        response = requests.post(url, timeout=5)
        response.raise_for_status()
        print(f"  -> Target {target_chip} is in flash mode.")
        time.sleep(2)
    except Exception as e:
        print(f"Failed to communicate with S3 proxy API: {e}")
        sys.exit(1)

def flash_chip(ip, target_chip, firmware_path):
    print(f"Starting flash process for {target_chip} using file {firmware_path}...")
    
    if not os.path.exists(firmware_path):
        print(f"Error: Firmware file {firmware_path} not found.")
        sys.exit(1)

    # Determine port based on target (WROOM = 6666, RP2354 = 6667)
    target_port = 6666 if target_chip == "wroom" else 6667
    port = f"socket://{ip}:{target_port}"
    print(f"Connecting to virtual serial port at {port}")

    if target_chip == "wroom":
        # Call standard esptool.py over the network serial port
        cmd = [
            sys.executable, "-m", "esptool",
            "--port", port,
            "--baud", "115200",
            "write_flash", "0x10000", firmware_path
        ]
        
        try:
            print(f"Executing: {' '.join(cmd)}")
            subprocess.run(cmd, check=True)
            print(f"SUCCESS: Successfully flashed {target_chip}.")
        except subprocess.CalledProcessError as e:
            print(f"Flashing failed: {e}")
            sys.exit(1)
            
    elif target_chip == "rp2354":
        print("\n[NOTE] RP2354 Proxy Flashing via UART:")
        print(f"The S3 has opened a TCP bridge to the RP2354 UART on {port}.")
        
        # Native RP2040/RP2350 ROMs only support UF2 over USB mass storage.
        # To automate serial flashing over this network proxy, the RP2354 MUST be running
        # a custom 3rd-party serial bootloader (like picoboot or a generic XMODEM/raw dump loader).
        # We automate the payload delivery by streaming the raw compiled binary over the TCP socket.
        
        print(f"\n[ATTENTION] Native RP2354s do NOT support serial proxy flashing out of the box.")
        print("You MUST have installed a custom serial bootloader ROM on the RP2354.")
        print(f"Streaming raw firmware binary payload to custom serial bootloader...")
        
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(15)
                s.connect((ip, target_port))
                
                # We assume a raw binary stream protocol is supported by the custom bootloader
                with open(firmware_path, 'rb') as f:
                    while chunk := f.read(1024):
                        s.sendall(chunk)
                        
            print(f"SUCCESS: Streamed firmware {firmware_path} to {target_chip}.")
            print(f"If the DSP does not reboot, your bootloader may require a specific start/stop sequence.")
            
        except Exception as e:
            print(f"Flashing failed: {e}")
            sys.exit(1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="InsaneFlasher V6 - Proxy Flasher")
    parser.add_argument("--target", choices=["wroom", "rp2354"], required=True, help="Target chip to flash")
    parser.add_argument("--file", required=True, help="Path to firmware binary")
    parser.add_argument("--ip", required=False, help="IP of ESP32-S3 (optional, will use zeroconf if omitted)")
    
    args = parser.parse_args()
    
    ip = args.ip
    if not ip:
        print("Searching for S3 Master via ZeroConf...")
        zeroconf = Zeroconf()
        listener = MyListener()
        # ESPHome publishes services under _esphomelib._tcp.local.
        browser = ServiceBrowser(zeroconf, "_esphomelib._tcp.local.", listener)
        time.sleep(3)
        zeroconf.close()
        
        # We assume the listener populates a global or we just extract the IP.
        # Since MyListener in this script just prints the IP, we will implement
        # a simple blocking search here:
        
        class IPFinder:
            def __init__(self):
                self.found_ip = None
            def remove_service(self, zeroconf, type, name): pass
            def add_service(self, zeroconf, type, name):
                global found_ip
                info = zeroconf.get_service_info(type, name)
                if info and "insane" in name.lower():
                    self.found_ip = info.parsed_addresses()[0]

        ip_finder = IPFinder()
        zc = Zeroconf()
        browser = ServiceBrowser(zc, "_esphomelib._tcp.local.", ip_finder)
        time.sleep(3)
        zc.close()

        if ip_finder.found_ip:
            ip = ip_finder.found_ip
            print(f"Found S3 at {ip}")
        else:
            print("Could not find S3 via ZeroConf. Please provide --ip manually.")
            sys.exit(1)
        
    setup_s3_proxy(ip, args.target)
    flash_chip(ip, args.target, args.file)
    
    if args.target == "wroom":
        print(f"[{ip}] Rebooting WROOM normally...")
        try:
            requests.post(f"http://{ip}/button/wroom_normal_boot/press", timeout=5)
        except Exception as e:
            print(f"Failed to trigger normal boot: {e}")
            
    print("Done.")
