## Description

Please include a summary of the change, which issue is fixed (if applicable), and the relevant motivation or context. 

Fixes # (issue number)

## Type of Change

Please mark the options that are relevant:

- [ ] **Bug Fix** (non-breaking change which fixes an issue)
- [ ] **New Feature** (non-breaking change which adds functionality)
- [ ] **Hardware / PCB Optimization** (modifications to KiCad schematics, layouts, or footprints)
- [ ] **Breaking Change** (fix or feature that would cause existing functionality to not work as expected)
- [ ] **Documentation Update** (changes to README, guides, or comments)

## Affected Components

- [ ] **Insane Control Center** (Cross-platform Python App)
- [ ] **Master MCU** (ESP32-S3 / ESPHome configurations)
- [ ] **Audio DSP** (RP2354 / C++ firmware / Audio Filters)
- [ ] **Wireless Sub Link** (Subwoofer TX/RX ESP32 modules)
- [ ] **Hardware Design** (KiCad schematics, routing, or enclosure 3D models)

## Checklist

Before submitting this Pull Request, please ensure you have completed the following steps:

### For All Submissions:
- [ ] My code/design follows the project's style and contribution guidelines (`CONTRIBUTING.md`).
- [ ] I have performed a self-review of my own work.
- [ ] I have commented my code or documented the hardware changes, particularly in hard-to-understand areas.
- [ ] My changes generate no new warnings or build errors.

### For Hardware / PCB Changes (KiCad):
- [ ] The design successfully passes the **Design Rule Check (DRC)** with 0 errors and 0 warnings.
- [ ] No critical modifications were made to the ultra-compact **RP2354 SMPS/Buck Converter layout** without prior lab verification.
- [ ] The Interactive BOM (`iBOM`) has been updated and regenerated if footprints or components were altered.

### For Software / Firmware Changes:
- [ ] The firmware compiles successfully without breaking existing ESPHome native API bindings.
- [ ] Time-critical DSP functions on the RP2354 have been tested for deterministic execution.
- [ ] I have verified that no sensitive credentials (Wi-Fi, tokens, API keys) are exposed in the code.

## Verification & Testing

Please describe the tests that you ran to verify your changes. Provide instructions so we can reproduce. Please also list any relevant details for your test configuration.

- **Test Configuration:** (e.g., HW Revision v1.0, ESPHome v2026.x, Android/Windows version)
- **Proof of Concept:** (Attach screenshots, log outputs, oscilloscope/analyzer traces, or audio measurement graphs if applicable)
