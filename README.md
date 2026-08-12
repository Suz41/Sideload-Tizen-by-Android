# Sideloading Apps in Samsung Tizen TV by Android (No PC, No Pendrive, No Tizen Studio, No Certificates, No Licensing) (Just use some brain)

A complete step-by-step tutorial to sideload Tizen application packages (`.wgt` files) onto your Samsung Smart TV using **only Termux on your Android phone** over local Wi-Fi.

---

## 🗺️ Process Flowchart

```mermaid
flowchart TD
    Start([Start Sideloading]) --> TVDev[1. Enable Developer Mode on Samsung TV]
    TVDev --> TVHost[2. Set Host IP to Phone Hotspot IP & Restart TV]
    TVHost --> TermuxKey[3. Generate & Sync RSA Keys in Termux]
    TermuxKey --> Connect[4. Connect adb connect TV_IP:26101]
    Connect --> InstallPy[5. Run install.py Script in Termux]
    InstallPy --> Stream[6. Stream .wgt App Package to TV Share Path]
    Stream --> Register[7. TV Installs & Registers .wgt Package]
    Register --> Launch[8. App Automatically Launches on TV Screen]
    Launch --> End([Complete])
    
    style Start fill:#22c55e,stroke:#fff,stroke-width:2px,color:#fff
    style End fill:#22c55e,stroke:#fff,stroke-width:2px,color:#fff
    style InstallPy fill:#6366f1,stroke:#fff,stroke-width:2px,color:#fff
```

---

## 🌟 Key Features
* 📱 **No PC / Laptop Required:** Everything is performed directly inside Termux on your mobile phone.
* 💾 **No USB Pendrives:** Apps are streamed directly to the TV over your local network.
* 📦 **No Tizen Studio SDK:** Bypasses downloading and configuring gigabytes of developer tooling.
* 🔑 **No Certificates or Licensing signatures:** Install any prebuilt `.wgt` file without author or distributor signature errors.
* 🚀 **Zero File Footprint (Optional):** Run the installation script directly over the internet without saving it to your phone storage!

---

## 📋 Prerequisites (One-Time Setup in Termux)

If you haven't installed Python or ADB yet inside Termux, run this command:

```bash
pkg update && pkg install python android-tools -y
```

---

## 📺 Step 1: Configure Developer Mode on Samsung TV

1. Open the **Smart Hub** (Home menu) on your TV and navigate to the **Apps** panel.
2. Using your physical TV remote control, press the numeric sequence **`12345`**.
3. A developer menu pop-up will appear. Toggle **Developer Mode** to **ON**.
4. Identify your **Phone's Wi-Fi / Hotspot IP Address** (e.g., `10.187.217.60`) and enter it in the **Host IP** field.
5. Click **OK** or **Submit**.
6. **Reboot the TV:** Hold the remote Power button down for 5 seconds until the TV turns off and turns back on displaying the Samsung logo. (This opens Port `26101`).
7. Go to TV Network Settings and write down your **TV IP Address** (e.g., `10.187.217.145`).

---

## 🔐 Step 2: Set Up Termux on Your Phone

Open **Termux** on your Android phone and copy-paste these commands:

### 1. Set Up Security Permissions (Just Copy & Paste)
Copy and paste this line into Termux and press **Enter**. (This lets your TV trust your phone):
```bash
mkdir -p ~/.android ~/.tizen && [ -f ~/.tizen/sdbkey ] || adb keygen ~/.tizen/sdbkey 2>/dev/null; cp ~/.tizen/sdbkey ~/.android/adbkey && cp ~/.tizen/sdbkey.pub ~/.android/adbkey.pub
```

### 2. Download and Run the Installer Script
Choose **one** of the following methods to run the installer:

* **Method A (No Saving - Run directly from the internet):**
  Stream and run the script on the fly without keeping the script file:
  ```bash
  curl -sL https://raw.githubusercontent.com/Suz41/Sideload-Tizen-by-Android/main/install.py | python3 - <file.wgt> <AppID>
  ```
  *(Example: `curl -sL https://raw.githubusercontent.com/Suz41/Sideload-Tizen-by-Android/main/install.py | python3 - Jellyfin.wgt Jellyfin`)*

* **Method B (Download & Save to phone):**
  Download the file first to your phone:
  ```bash
  curl -L -o install.py https://raw.githubusercontent.com/Suz41/Sideload-Tizen-by-Android/main/install.py
  ```
  Then run the saved script:
  ```bash
  python3 install.py <file.wgt> <AppID>
  ```

---

## 📋 App Identifiers Catalog

| Application | File Name | AppID / Package Name |
| :--- | :--- | :--- |
| **Jellyfin TV** | `Jellyfin.wgt` | `Jellyfin` |
| **TizenBrew (YouTube Ad-free)** | `TizenBrew.wgt` | `xvvl3S1bvH.TizenBrewStandalone` |
| **VLC TV** | `vlctv.wgt` | `VLCTV` |

---

## 🛠️ Troubleshooting Tips

* **ADB Status Unauthorized:** If `adb devices` shows your TV as `unauthorized`, double-check that your phone's Wi-Fi hotspot IP is set correctly as the **Host IP** in the TV Developer menu, and that you rebooted your TV by holding the power button.
* **Connection Timeout:** Ensure both your TV and Android phone are connected to the exact same Wi-Fi subnet.
