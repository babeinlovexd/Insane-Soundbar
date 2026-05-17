# Contributing to the Insane Soundbar Project

Welcome! Thank you for your interest in contributing to the **Insane Soundbar** project. Whether you want to fix bugs, implement new software features, optimize the hardware layout, or improve the documentation – any help is greatly appreciated!

Since this project combines complex custom hardware with cross-platform software/firmware, there are a few guidelines to ensure high code and manufacturing quality.

---

## 1. License Agreement (Important!)

By submitting a contribution (Pull Request), you agree that your changes will be published under the existing project licenses:
* **Hardware (Schematics, Layouts, 3D Models):** Licensed under **CC BY-NC-SA 4.0** (Attribution-NonCommercial-ShareAlike).
* **Software & Firmware (C/C++, Python, YAML):** Licensed under the **MIT License**.

---

## 2. How Can I Contribute?

### Reporting Bugs (Issues)
If you find a bug in the Python app, encounter problems with ESPHome, or notice an error in the PCB layout:
1. Check if an open issue already exists for the topic.
2. Use the appropriate issue templates and describe the error as precisely as possible (including logs, hardware revision, OS version).

### Submitting Changes (Pull Requests)
1. Fork the repository and create a descriptive feature branch (e.g., `feature/audio-eq-profiles` or `fix/sub-rx-timeout`).
2. Make your changes, ensuring clean code and clean routing.
3. Create a Pull Request (PR) against the `main` branch of the main project. Briefly describe what you changed and why.

---

## 3. Hardware Contribution Guidelines (EDA / KiCad)

This project utilizes extremely tight tolerances to ensure signal integrity and ultra-compact EMI-compliant loops (e.g., for the internal switching regulator of the RP2354).
* **No unverified changes to the SMPS layout:** The layout of the internal buck converter strictly follows the Raspberry Pi reference design (including the 0.1 mm clearance and reduced 0402 pads). Any changes here must be verified via laboratory measurements.
* **DRC (Design Rule Check):** Every PCB modification must pass the DRC without errors (0 errors, 0 warnings) using the specified manufacturing tolerances.
* **Interactive BOM:** If components or footprints are changed, ensure the interactive HTML BOM (`iBOM`) is regenerated. (Note: Generated HTML files in the `iBOM/` folder are excluded from GitHub's language statistics via `.gitattributes`).

---

## 4. Software & Firmware Guidelines

* **Firmware (ESP32-S3 Master / ESPHome):** Extensions to the YAML configurations or custom components must run stably and must not block the native API for Home Assistant.
* **DSP Code (RP2354):** Audio processing, I2S routing, and filter coefficients must be highly time-critical and deterministically optimized. Document any mathematical filter changes extensively.
* **Control Center (Python App):** Ensure cross-platform compatibility (Android, Windows, Linux). Code should adhere to PEP 8 where possible.
* **No incomplete code fragments:** Only submit code that compiles without errors.

---

## 5. Documentation

Good documentation is just as important as good code! If you add features, please also update:
* The main `README.md`.
* The Mermaid architecture diagram (if the signal or data flow changes).

Thank you again for your support in developing the ultimate soundbar!
