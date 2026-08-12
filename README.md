# Sideload Tizen by Android

> Sideload Tizen applications (`.wgt`) onto Samsung Smart TVs directly from Termux on Android. No PC, USB drives, or Tizen Studio SDK required.

[![Platform](https://img.shields.io/badge/Platform-Tizen%205.5%20%7C%206.0%20%7C%206.5-blue.svg)](#)
[![Host](https://img.shields.io/badge/Host-Android%20%28Termux%29-green.svg)](#)
[![License](https://img.shields.io/badge/License-MIT-purple.svg)](#)

---

## 🗺️ Process Flow

```mermaid
flowchart LR
    A[1. Enable TV Dev Mode] --> B[2. Sync RSA keys]
    B --> C[3. Connect over Wi-Fi]
    C --> D[4. Stream & install]
```

---

## 🌟 Key Features

* **PC-Less Deployment:** Run the entire process inside Termux on your phone.
* **Direct Network Stream:** Files are transferred directly over Wi-Fi (no USB drives).
* **Zero Studio Dependency:** Bypasses Tizen Studio SDK and Samsung's certificate/signing manager.
* **Streamlined Installer:** Built-in default configuration targets Jellyfin TV installation in a single click.

---

## 🔒 Security Best Practices & Warnings

* **Network Security:** Developer Mode opens SDB port `26101` on your local network. Only enable this on secure, trusted home Wi-Fi networks. Never use public or untrusted Wi-Fi.
* **Sideloading Risk (Third-Party Apps):** Downloading and installing `.wgt` application files from unverified third-party websites can pose significant security risks. Only sideload files from official developer sources (like the official Jellyfin GitHub repository) or trusted community-vetted release channels.
* **Tizen OS vs Generic Android Boxes:** Samsung Smart TVs run Tizen OS. While safer than generic Android TV boxes, keeping TV firmware updated is always recommended.
* **Safe Script Execution:** For maximum security, we recommend downloading, inspecting, and then executing the script locally (**Method A** below) rather than piping directly from the internet.

---

## 📋 Prerequisites

Install Python and ADB tools inside Termux:
```bash
pkg update && pkg install python android-tools -y
```

---

## 📺 1. TV Setup

1. Open **Apps** on your Samsung TV.
2. Press **`12345`** on your remote control to open Developer settings.
3. Turn **Developer Mode** to **ON** and set the **Host IP** to your phone's Hotspot IP address.
4. **Reboot the TV:** Hold the remote Power button down for 5 seconds until the TV restarts.
5. Note the **TV IP Address** from Network Settings.

---

## 🔐 2. Termux Setup

Sync your cryptographic Tizen keys to ADB paths inside Termux:

```bash
mkdir -p ~/.android ~/.tizen && [ -f ~/.tizen/sdbkey ] || adb keygen ~/.tizen/sdbkey 2>/dev/null; cp ~/.tizen/sdbkey ~/.android/adbkey && cp ~/.tizen/sdbkey.pub ~/.android/adbkey.pub
```

---

## 🚀 3. Sideloading Apps

### Connect to your TV:
```bash
adb connect <TV_IP_ADDRESS>:26101
```

### Download the Installer Script (Recommended):
Choose **one** of the following methods to run the installer:

* **Method A: Download, Inspect & Run (Recommended & Secure):**
  Download the installer file locally to inspect the code first:
  ```bash
  curl -L -o install.py https://raw.githubusercontent.com/Suz41/Sideload-Tizen-by-Android/main/install.py
  ```
  Then execute the script:
  ```bash
  python3 install.py
  ```

* **Method B: Pipe execution (Shortcut):**
  Stream and run the script on the fly:
  ```bash
  curl -sL https://raw.githubusercontent.com/Suz41/Sideload-Tizen-by-Android/main/install.py | python3 -
  ```

### Install other apps:
Pass the file name and AppID as arguments:
```bash
python3 install.py <file.wgt> <AppID>
```

| Application | Download Command | Package / AppID |
| :--- | :--- | :--- |
| **🍿 Jellyfin TV** | `curl -L -o Jellyfin.wgt https://github.com/Apps2Samsung/tizen-community-packages/raw/main/Jellyfin.wgt` | `Jellyfin` (Default) |
| **🎬 VLC TV** | `curl -L -o vlctv.wgt https://github.com/Apps2Samsung/tizen-community-packages/raw/main/vlctv.wgt` | `VLCTV` |
| **🍺 TizenBrew** | `curl -L -o TizenBrew.wgt https://github.com/reisxd/TizenBrew/releases/latest/download/TizenBrewStandalone.wgt` | `xvvl3S1bvH.TizenBrewStandalone` |

---

## 👤 Developed by

* **[Suz41](https://github.com/Suz41):** Developer of this direct Termux-to-TV sideloading project workflow.

## 🤝 Acknowledgments

* **[Jellyfin Project](https://jellyfin.org/):** For the open-source media ecosystem.
* **[Apps2Samsung](https://github.com/Apps2Samsung):** For compiled package distribution.
* **[TizenBrew](https://github.com/reisxd/TizenBrew):** For standalone YouTube framework development.
