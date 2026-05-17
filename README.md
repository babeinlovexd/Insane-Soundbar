<div align="center">

# 🔊 Insane Soundbar

Four ESP32-Cores and an RP2354A-Hardware-DPS for lossless audio and full smart home intergation.

---

<a href="https://github.com/babeinlovexd/insane-soundbar/releases"><img src="https://img.shields.io/github/v/release/babeinlovexd/insane-soundbar?style=for-the-badge&color=2ecc71" alt="Latest Release"></a>
<img src="https://img.shields.io/badge/Hardware-V1.0.0-green?style=for-the-badge&logo=pcb" alt="Hardware Version">
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

<a href="LICENSE.md#1-hardware-schematics--documentation"><img src="https://img.shields.io/badge/Hardware-CC%20BY--NC--SA%204.0-blue?style=for-the-badge&logo=creative-commons&logoColor=white" alt="Hardware License: CC BY-NC-SA 4.0"></a>
<a href="LICENSE.md#2-software--firmware-source-code"><img src="https://img.shields.io/badge/Software-MIT-blue?style=for-the-badge&logo=github&logoColor=white" alt="Software License: MIT"></a>

---

```mermaid
graph TD
    %% Styling Definitionen
    classDef appStyle fill:#d35400,stroke:#fff,stroke-width:2px,color:#fff;
    classDef haStyle fill:#41BDF5,stroke:#fff,stroke-width:2px,color:#fff;
    classDef espStyle fill:#34495E,stroke:#fff,stroke-width:2px,color:#fff;
    classDef piStyle fill:#8A2BE2,stroke:#fff,stroke-width:2px,color:#fff;
    classDef hardwareStyle fill:#7F8C8D,stroke:#fff,stroke-width:1px,color:#fff;
    classDef chassisStyle fill:#2C3E50,stroke:#fff,stroke-width:1px,color:#fff,stroke-dasharray: 5 5;

    %% --- LAYER 1: CONTROL INLETS ---
    subgraph Layer_Control [1. Control & Smart Home]
        App[Insane Control Center<br/>Python App]:::appStyle
        HA[Home Assistant<br/>ESPHome Native API]:::haStyle
    end

    %% --- LAYER 2: SYSTEM ORCHESTRATION ---
    subgraph Layer_Master [2. System Master]
        Master[Master MCU<br/>ESP32-S3]:::espStyle
    end

    %% --- LAYER 3: AUDIO INPUT SOURCES ---
    subgraph Layer_Inputs [3. Audio Inputs]
        BTRX[Bluetooth Receiver<br/>ESP32]:::espStyle
        AuxIn[AUX In<br/>3.5mm Klinke]:::hardwareStyle
        ADC_Aux[AUX ADC<br/>PCM1808]:::hardwareStyle
        TosIn[Toslink In<br/>Optisch S/PDIF]:::hardwareStyle
    end

    %% --- LAYER 4: DIGITAL SIGNAL PROCESSING ---
    subgraph Layer_DSP [4. Digital Signal Processing]
        DSP[Audio DSP<br/>RP2354]:::piStyle
    end

    %% --- LAYER 5: AUDIO OUTPUT DISTRIBUTION ---
    subgraph Layer_Outputs [5. Audio Outputs & Transmission]
        DAC_Main[DACs<br/>PCM5102A]:::hardwareStyle
        SUBTX[Subwoofer TX<br/>ESP32]:::espStyle
    end

    %% --- LAYER 6: AMPLIFICATION & WIRELESS RX ---
    subgraph Layer_Amps [6. Amplification & Wireless Sub]
        Amp_Mid[Amp Middle<br/>TPA Class-D]:::hardwareStyle
        Amp_High[Amp High<br/>TPA Class-D]:::hardwareStyle
        SUBRX[Subwoofer RX<br/>ESP32]:::espStyle
        DAC_Sub[DAC<br/>PCM5102A]:::hardwareStyle
        Amp_Sub[Amp Sub<br/>TPA Class-D]:::hardwareStyle
    end

    %% --- LAYER 7: SPEAKER CHASSIS ---
    subgraph Layer_Chassis [7. Acoustic Speakers]
        Chassis_Mid((Dayton<br/>CE70PR-4)):::chassisStyle
        Chassis_High((Dayton<br/>ND25FA-4)):::chassisStyle
        Chassis_Sub((Dayton<br/>DCS205-4)):::chassisStyle
        PR_Sub((Dayton<br/>DSA215-PR)):::chassisStyle
    end

    %% --- INFRASTRUCTURE CONNECTIONS (STRICT FLOW) ---
    
    %% Control Connections
    App <-->|Wi-Fi / TCP| Master
    HA <-->|Wi-Fi| Master

    %% Master Flash & Control Bus (Left & Right Outskirts)
    Master -.->|I2C & UART Flasher| BTRX
    Master -.->|I2C & UART Flasher| DSP
    Master -.->|I2C & UART Flasher| SUBTX

    %% Input Routing to DSP
    Master -->|I2S / WebRadio| DSP
    BTRX -->|I2S Audio| DSP
    AuxIn -->|Analog| ADC_Aux
    ADC_Aux -->|I2S Audio| DSP
    TosIn -->|Digital S/PDIF| DSP

    %% DSP Routing to Outputs
    DSP -->|I2S Mid / High| DAC_Main
    DSP -->|I2S Sub-Channel| SUBTX

    %% Wireless Subwoofer Link
    SUBTX ==>|Wireless Audio Link| SUBRX

    %% Amplification Soundbar
    DAC_Main -->|Analog Left/Right| Amp_Mid
    DAC_Main -->|Analog Left/Right| Amp_High
    Amp_Mid -->|Speaker Wire| Chassis_Mid
    Amp_High -->|Speaker Wire| Chassis_High

    %% Amplification Subwoofer
    SUBRX -->|I2S Audio| DAC_Sub
    DAC_Sub -->|Analog| Amp_Sub
    Amp_Sub -->|Speaker Wire| Chassis_Sub
    Chassis_Sub ---|Acoustic Coupling| PR_Sub

```
    
<img src="Images/steuerrung.png" alt="ISB Platine" width="500">
<img src="Images/dsp.png" alt="ISB Platine" width="500">
<img src="PCB/ISB/3D.png" alt="ISB Platine" width="500">
<img src="PCB/ISB_SUB/3D.png" alt="Subwoofer Platine" width="500">
<img src="PCB/Flashcore/3D.png" alt="Flashcore Platine" width="500">

---

## ☕ Support this project
**Insane Soundbar** took a ton of time, endless caffeine, and a few of my sanity cells. If you love the system and want to support my work, I'd appreciate a virtual coffee.

<a href="https://www.paypal.me/babeinlovexd">
  <img src="https://img.shields.io/badge/Donate-PayPal-blue.svg?style=for-the-badge&logo=paypal" alt="Donate mit PayPal">
</a>

Every cent goes directly toward the ongoing development of ISB and new prototypes. 🚀

---

## 👨‍💻 Entwickelt von

| [<img src="https://avatars.githubusercontent.com/u/43302033?v=4" width="100"><br><sub>**BabeinlovexD**</sub>](https://github.com/babeinlovexd) |
| :---: |

---

</div>
