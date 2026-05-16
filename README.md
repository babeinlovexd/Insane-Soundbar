<div align="center">

# 🔊 Insane Soundbar

Vier ESP32-Kerne und ein RP2354-Hardware-DSP für verlustfreien Klang und volle Smart-Home-Integration.**

---

<a href="https://github.com/babeinlovexd/insane-soundbar/releases"><img src="https://img.shields.io/github/v/release/babeinlovexd/insane-soundbar?style=for-the-badge&color=2ecc71" alt="Latest Release"></a>
<img src="https://img.shields.io/badge/Hardware-V0.0.0-f39c12?style=for-the-badge&logo=pcb" alt="Hardware Version">
<img src="https://img.shields.io/badge/Status-BETA-ff9800?style=for-the-badge&logo=test-tube" alt="Status: Beta">
<img src="https://img.shields.io/badge/Updates-OTA_Ready-4caf50?style=for-the-badge&logo=wi-fi" alt="OTA Ready">

---

<img src="https://img.shields.io/badge/ESPHome-Native-03A9F4?style=for-the-badge&logo=esphome" alt="ESPHome">
<img src="https://img.shields.io/badge/Home_Assistant-Ready-41BDF5?style=for-the-badge&logo=home-assistant" alt="Home Assistant">
<img src="https://img.shields.io/badge/Language-C%2B%2B_%7C_C_%7C_YAML-00599C?style=for-the-badge&logo=c%2B%2B" alt="Languages">
<img src="https://img.shields.io/badge/PlatformIO-Build_System-F6822A?style=for-the-badge&logo=platformio&logoColor=white" alt="PlatformIO">

---

<img src="https://img.shields.io/badge/Main_Brain-ESP32--S3_(N16R8)-E7352C?style=for-the-badge&logo=espressif" alt="Main: ESP32-S3 (N16R8)">
<img src="https://img.shields.io/badge/DSP-RP2354A-FF69B4?style=for-the-badge&logo=raspberrypi" alt="DSP: RP2354A">
<img src="https://img.shields.io/badge/BT_Radio-WROOM--32U_(N4)-34495E?style=for-the-badge&logo=espressif" alt="BT: WROOM-32U (N4)">
<br>
<img src="https://img.shields.io/badge/SUB_TX-WROOM--32U_(N4)-34495E?style=for-the-badge&logo=espressif" alt="Sub TX: WROOM-32U (N4)">
<img src="https://img.shields.io/badge/SUB_RX-WROOM--32U_(N4)-34495E?style=for-the-badge&logo=espressif" alt="Sub RX: WROOM-32U (N4)">

---

<img src="https://img.shields.io/badge/Amps_Bar-2x_TPA3118D2-002C77?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTMwLDEwIGgxNSB2MjAgaDE1IHYxNSBoLTE1IHYzMCBjMCw1IDMsNSA3LDUgaDggdjE1IGgtMTAgYy0xNSwwIC0yMCwtOCAtMjAsLTIwIHYtMzAgaC0xMCB2LTE1IGgxMCB6Ii8+PGNpcmNsZSBjeD0iNzUiIGN5PSIyMCIgcj0iMTAiIGZpbGw9IndoaXRlIi8+PHJlY3QgeD0iNjcuNSIgeT0iMzUiIHdpZHRoPSIxNSIgaGVpZ2h0PSI2MCIgZmlsbD0id2hpdGUiLz48L3N2Zz4=&logoColor=white" alt="Amps Bar">
<img src="https://img.shields.io/badge/Amp_Sub-1x_TPA3116D2-002C77?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTMwLDEwIGgxNSB2MjAgaDE1IHYxNSBoLTE1IHYzMCBjMCw1IDMsNSA3LDUgaDggdjE1IGgtMTAgYy0xNSwwIC0yMCwtOCAtMjAsLTIwIHYtMzAgaC0xMCB2LTE1IGgxMCB6Ii8+PGNpcmNsZSBjeD0iNzUiIGN5PSIyMCIgcj0iMTAiIGZpbGw9IndoaXRlIi8+PHJlY3QgeD0iNjcuNSIgeT0iMzUiIHdpZHRoPSIxNSIgaGVpZ2h0PSI2MCIgZmlsbD0id2hpdGUiLz48L3N2Zz4=&logoColor=white" alt="Amp Sub">
<img src="https://img.shields.io/badge/ADC-PCM1808-16a085?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTMwLDEwIGgxNSB2MjAgaDE1IHYxNSBoLTE1IHYzMCBjMCw1IDMsNSA3LDUgaDggdjE1IGgtMTAgYy0xNSwwIC0yMCwtOCAtMjAsLTIwIHYtMzAgaC0xMCB2LTE1IGgxMCB6Ii8+PGNpcmNsZSBjeD0iNzUiIGN5PSIyMCIgcj0iMTAiIGZpbGw9IndoaXRlIi8+PHJlY3QgeD0iNjcuNSIgeT0iMzUiIHdpZHRoPSIxNSIgaGVpZ2h0PSI2MCIgZmlsbD0id2hpdGUiLz48L3N2Zz4=&logoColor=white" alt="ADC: PCM1808">
<img src="https://img.shields.io/badge/DACs-3x_PCM5102A-27ae60?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTMwLDEwIGgxNSB2MjAgaDE1IHYxNSBoLTE1IHYzMCBjMCw1IDMsNSA3LDUgaDggdjE1IGgtMTAgYy0xNSwwIC0yMCwtOCAtMjAsLTIwIHYtMzAgaC0xMCB2LTE1IGgxMCB6Ii8+PGNpcmNsZSBjeD0iNzUiIGN5PSIyMCIgcj0iMTAiIGZpbGw9IndoaXRlIi8+PHJlY3QgeD0iNjcuNSIgeT0iMzUiIHdpZHRoPSIxNSIgaGVpZ2h0PSI2MCIgZmlsbD0id2hpdGUiLz48L3N2Zz4=&logoColor=white" alt="DACs: PCM5102A">
<br>
<img src="https://img.shields.io/badge/Sub-Dayton_MX6--22-8e44ad?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cG9seWdvbiBmaWxsPSJ3aGl0ZSIgcG9pbnRzPSIyMCwzNSA0NSwzNSA3NSwxMCA3NSw5MCA0NSw2NSAyMCw2NSIvPjwvc3ZnPg==&logoColor=white" alt="Subwoofer">
<img src="https://img.shields.io/badge/Passive-Dayton_DSA215--PR-7f8c8d?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cG9seWdvbiBmaWxsPSJ3aGl0ZSIgcG9pbnRzPSIyMCwzNSA0NSwzNSA3NSwxMCA3NSw5MCA0NSw2NSAyMCw2NSIvPjwvc3ZnPg==&logoColor=white" alt="Passive Radiator">
<img src="https://img.shields.io/badge/Mid-Dayton_ND91--8-d35400?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cG9seWdvbiBmaWxsPSJ3aGl0ZSIgcG9pbnRzPSIyMCwzNSA0NSwzNSA3NSwxMCA3NSw5MCA0NSw2NSAyMCw2NSIvPjwvc3ZnPg==&logoColor=white" alt="Midwoofer">
<img src="https://img.shields.io/badge/High-Dayton_ND16FA--6-f39c12?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cG9seWdvbiBmaWxsPSJ3aGl0ZSIgcG9pbnRzPSIyMCwzNSA0NSwzNSA3NSwxMCA3NSw5MCA0NSw2NSAyMCw2NSIvPjwvc3ZnPg==&logoColor=white" alt="Tweeter">

---

<img src="https://img.shields.io/badge/Espressif-MCUs-E7352C?style=for-the-badge&logo=espressif&logoColor=white" alt="Espressif">
<img src="https://img.shields.io/badge/Raspberry_Pi-DSP-C51A4A?style=for-the-badge&logo=raspberrypi&logoColor=white" alt="Raspberry Pi">
<img src="https://img.shields.io/badge/Texas_Instruments-Audio_ICs-CC0000?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAxMDAgMTAwIj48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTMwLDEwIGgxNSB2MjAgaDE1IHYxNSBoLTE1IHYzMCBjMCw1IDMsNSA3LDUgaDggdjE1IGgtMTAgYy0xNSwwIC0yMCwtOCAtMjAsLTIwIHYtMzAgaC0xMCB2LTE1IGgxMCB6Ii8+PGNpcmNsZSBjeD0iNzUiIGN5PSIyMCIgcj0iMTAiIGZpbGw9IndoaXRlIi8+PHJlY3QgeD0iNjcuNSIgeT0iMzUiIHdpZHRoPSIxNSIgaGVpZ2h0PSI2MCIgZmlsbD0id2hpdGUiLz48L3N2Zz4=&logoColor=white" alt="TI">
<img src="https://img.shields.io/badge/JLCPCB-PCB-005082?style=for-the-badge&logo=easyeda&logoColor=white" alt="JLCPCB">

---

<a href="https://github.com/babeinlovexd/insane-soundbar/actions/workflows/esphome-check.yml"><img src="https://img.shields.io/github/actions/workflow/status/babeinlovexd/insane-soundbar/esphome-check.yml?style=for-the-badge&logo=esphome&logoColor=white&label=MAIN_YAML" alt="Main YAML Status"></a>
<a href="https://github.com/babeinlovexd/insane-soundbar/actions/workflows/build-dsp.yml"><img src="https://img.shields.io/github/actions/workflow/status/babeinlovexd/insane-soundbar/build-dsp.yml?style=for-the-badge&logo=raspberrypi&logoColor=white&label=DSP" alt="DSP Build"></a>
<br>
<a href="https://github.com/babeinlovexd/insane-soundbar/actions/workflows/build-icc.yml"><img src="https://img.shields.io/github/actions/workflow/status/babeinlovexd/insane-soundbar/build-icc.yml?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCA0NDggNTEyIj48cGF0aCBmaWxsPSJ3aGl0ZSIgZD0iTTAgOTMuN2wxODMuNi0yNS4zdjE3Ny40SDBWOTMuN3ptMjIzIDE4NHYxOTIuMWwyMjUgMzFWMjc3LjdIMjIzem0yMjUtMjQ1LjlMMjIzIDB2MTgxLjhoMjI1VjMxLjhaTTAgMjc3Ljd2MTQ5LjVsMTgzLjYgMjUuM1YyNzcuN0gweiIvPjwvc3ZnPg==&label=ICC_EXE" alt="ICC Build"></a>
<a href="https://github.com/babeinlovexd/insane-soundbar/actions/workflows/build-apk.yml"><img src="https://img.shields.io/github/actions/workflow/status/babeinlovexd/insane-soundbar/build-apk.yml?style=for-the-badge&logo=android&logoColor=white&label=ICC_APK" alt="ICC APK Build"></a>
<br>
<a href="https://github.com/babeinlovexd/insane-soundbar/actions/workflows/build-bluetooth.yml"><img src="https://img.shields.io/github/actions/workflow/status/babeinlovexd/insane-soundbar/build-bluetooth.yml?style=for-the-badge&logo=espressif&logoColor=white&label=BT" alt="BT Build"></a>
<a href="https://github.com/babeinlovexd/insane-soundbar/actions/workflows/build-sub-tx.yml"><img src="https://img.shields.io/github/actions/workflow/status/babeinlovexd/insane-soundbar/build-sub-tx.yml?style=for-the-badge&logo=espressif&logoColor=white&label=SUB_TX" alt="Sub TX Build"></a>
<a href="https://github.com/babeinlovexd/insane-soundbar/actions/workflows/build-sub-rx.yml"><img src="https://img.shields.io/github/actions/workflow/status/babeinlovexd/insane-soundbar/build-sub-rx.yml?style=for-the-badge&logo=espressif&logoColor=white&label=SUB_RX" alt="Sub RX Build"></a>

---

<img src="https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey?style=for-the-badge&logo=creative-commons" alt="License: CC BY-NC-SA 4.0">

---

## ⚖️ Lizenz
Dieses komplette Projekt (Hardware und Software) steht unter der [CC BY-NC-SA 4.0 Lizenz](https://creativecommons.org/licenses/by-nc-sa/4.0/). 
Das bedeutet: Nachbauen und Anpassen für private Zwecke ist ausdrücklich erwünscht, jede kommerzielle Nutzung oder der Verkauf sind strikt verboten!

---

## ☕ Support dieses Projekts
**Insane Soundbar** hat extrem viel Zeit, Nerven und Kaffee gekostet. Wenn dir das System gefällt und du meine Arbeit unterstützen möchtest, freue ich mich riesig über einen virtuellen Kaffee!

<a href="https://www.paypal.me/babeinlovexd">
  <img src="https://img.shields.io/badge/Donate-PayPal-blue.svg?style=for-the-badge&logo=paypal" alt="Donate mit PayPal">
</a>

Jeder Cent fließt direkt in die Entwicklung von ISB und neue Prototypen! 🚀

---

## 👨‍💻 Entwickelt von

| [<img src="https://avatars.githubusercontent.com/u/43302033?v=4" width="100"><br><sub>**BabeinlovexD**</sub>](https://github.com/babeinlovexd) |
| :---: |

---

</div>
