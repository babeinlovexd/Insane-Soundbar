# Security Policy

## Reporting a Vulnerability

Please do not report security vulnerabilities through public GitHub issues. Public disclosure can put other users at risk before a patch is available.

Instead, please report them using GitHub's **"Private vulnerability reporting"** feature in this repository, or contact the maintainer directly. 

Please include the following information in your report:
* The type of issue (e.g., authentication bypass, buffer overflow, cross-site scripting).
* The specific location (e.g., Python App, ESPHome YAML, DSP C-Code, or hardware interface).
* Step-by-step instructions to safely reproduce the issue.
* The potential impact or risk level.

You should receive a response within 48 hours acknowledging receipt of the vulnerability report.

## Handling of ESPHome Secrets

This project relies on ESPHome for the Master MCU integration. It is critical to maintain strict operational security regarding network and device access. 

**Never commit your `secrets.yaml` file to a public repository.** Ensure that your local configuration properly defines and protects the following keys in a strictly unversioned `secrets.yaml` file:
* API encryption keys
* OTA (Over-The-Air) passwords
* Wi-Fi SSIDs
* Wi-Fi passwords
* AP (Access Point) passwords

If you accidentally push these credentials to a public branch, consider them compromised. Immediately change the passwords on your router/devices and remove the sensitive data from your git history.

## Scope

This security policy applies to:
* The cross-platform Python App (Insane Control Center).
* The ESPHome integration and network communications.
* The DSP firmware and OTA update mechanisms.
* Bluetooth pairing and transmission security.
