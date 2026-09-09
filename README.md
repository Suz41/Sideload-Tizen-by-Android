# Sideloading Apps in Samsung Tizen TV by Android (No PC, No USB, No Tizen Studio)

Sideload Tizen application packages (`.wgt` and `.tpk` files) onto a Samsung Smart TV directly from **Termux on Android** without a PC, USB drive, or Tizen Studio SDK.

---

## Quick Start (Single Command)

Open Termux on your phone and run:

```bash
cd ~/Sideload-Tizen-by-Android && ./setup.sh
```

*(If cloning for the first time: `git clone https://github.com/Suz41/Sideload-Tizen-by-Android.git && cd Sideload-Tizen-by-Android && ./setup.sh`)*

The script will automatically:
1. Check and silently install any missing tools (`python`, `adb`, `curl`).
2. Generate all required ADB/Tizen authorization keys.
3. Create your dedicated folder: **`Internal Storage -> Download -> Samsung-T-Sideload`**.
4. Show your phone's IP and launch the interactive TV Manager!

---

## 1-Minute TV Setup

1. Open **Apps** on your Samsung TV.
2. Press **`1 2 3 4 5`** on your remote to open Developer Mode.
3. Turn **Developer Mode** to **ON**.
4. Set **Host IP** to your phone's IP (displayed clearly by `./setup.sh`).
5. **Reboot the TV:** Hold your remote's **Power** button for 5 seconds until the TV restarts.

---


---

## Interface Preview

<div align="center">

### 1. Setup & TV Network Instructions
```text
========================================================
          Samsung Tizen TV Sideload Setup               
========================================================

Put your .wgt / .tpk files in File Manager at:
    Internal Storage -> Download -> Samsung-T-Sideload

YOUR PHONE IP : 192.168.1.5

 1. ON YOUR SAMSUNG TV:
    • Apps -> Press 1 2 3 4 5 on remote
    • Turn Developer Mode -> ON
    • Host IP -> Enter: 192.168.1.5
    • Hold TV Power button 5s to restart TV

 2. FIND TV IP ON TV:
    • Settings -> General -> Network -> Network Status
========================================================
```

### 2. Live Interactive Dashboard
```text
============================================================
           Tizen Sideload Manager (Termux TUI)          
============================================================
 Version  : v2.0.0 [Up-to-date]
 Status   : [ONLINE]
 TV IP    : 10.253.229.145:26101
 Model    : Samsung QLED 4K (Tizen 6.5)
 Storage  : 2.8G free of 4.0G (30% used)
 DUID     : 123456789ABCDEF...
------------------------------------------------------------
 [1]  Sideload a Local .wgt / .tpk file
 [2]  Download & Sideload Pre-signed Apps
 [3]   Change TV IP Address (Auto-Scan Subnet)
 [4]  Show Installed Apps on TV
 [5]   Uninstall an App from TV
 [r]  Refresh (Re-scan files & TV status)
 [6]  Exit
============================================================
```

### 3. Pre-Signed Community App Store
```text
=== Pre-signed Community App Store ===

--- Framework ---
 [ 1] TizenBrew (Homebrew App Store & Module Runner)

--- Streaming ---
 [ 2] TizenTube (Ad-free YouTube + SponsorBlock)
 [ 3] Jellyfin TV (Home Media Server Client)
 [ 4] Stremio TV (Community App)
 [ 5] SmartTV Twitch (Ad-free Twitch Client)

--- Media ---
 [ 6] VLC Media Player (Native Video Player)

--- Gaming ---
 [ 7] Moonlight TV (4K PC Game Streaming)
 [ 8] Chiaki (PlayStation 4/5 Remote Play)
 [ 9] Doom (Classic Doom Port)
 [10] GameBoy Emulator

--- Utilities ---
 [11] AirTizen (Apple AirPlay Receiver)
 [12] FCastReceiver (Open Chromecast Alternative)
 [13] Tailscale (Mesh VPN Client - Native TPK)
 [14] iperf3 (Network Speed Tester)

 [15] Browse All Community Apps (50+ Packages Live Archive)...

Select app [1-15] or 0 to cancel: 
```

### 4. Real-Time Streaming & Installation
```text
Connecting to Samsung TV...
Opening file transfer channel...
Streaming TizenBrew.wgt to TV...
Uploading: [] 82% (2.4 MB/s)
 File transfer complete.

Installing app on TV...
Launching app on TV...

 SUCCESS: App installed and launched on TV!
```

</div>

## Interactive Manager Features

```text
============================================================
           Tizen Sideload Manager (Termux TUI)          
============================================================
 Status   : [ONLINE]
 TV IP    : 10.253.229.145:26101
 Model    : Samsung Smart TV (Tizen 6.5)
 DUID     : 123456789ABCDEF...
------------------------------------------------------------
 [1]  Sideload a Local .wgt file
 [2]  Download & Sideload Pre-signed Apps
 [3]   Change TV IP Address (Auto-Scan Subnet)
 [4]  Show Installed Apps on TV
 [5]   Uninstall an App from TV
 [r]  Refresh (Re-scan files & TV status)
 [6]  Exit
============================================================
```

### Key Highlights:
* **Auto-Folder Scanning:** Place any downloaded `.wgt` or `.tpk` file into `Internal Storage -> Download -> Samsung-T-Sideload` on your phone. The script finds and validates it automatically!
* **Full Dual-Format Support (.wgt & .tpk):** Supports both web apps (`.wgt`) and native high-performance binaries (`.tpk`) with manifest parsing.
* **Live TV Dashboard:** Displays TV online status, TV Model Name, Tizen OS version, hardware DUID, and **Available TV Storage Space** (`df -h`).
* **Live OS Compatibility Checker:** The App Store compares your TV's Tizen version against each app's requirements and tags them with `[Compatible]` or `[Incompatible]`.
* **Auto TV Discovery:** Automatically scans your local Wi-Fi subnet across all 254 addresses to find your TV's SDB port (`26101`) in seconds.
* **1-Click Community App Store:** Download and install 14+ popular pre-signed apps, plus an instant live directory browser with access to **50+ community packages** (IPTV players, KickTV, retro emulators, security camera feeds, and utilities).
* **Smart Ranked Uninstaller:** Queries TV package activity and sorts apps from **Least Used to Frequently Used**, making it easy to free up space.
* **Integrated Auto-Updater:** Press `[u]` inside the menu or run `./setup.sh` to automatically pull updates from GitHub.
* **Every-Step Error Explainer:** If any step fails (Wi-Fi, signature, permissions, or storage), it prints a clear diagnostic explaining what happened and provides an exact 1-2-3 fix.

---

## Security & Privacy

* **100% Local Execution:** The script runs entirely on your phone. It never logs, tracks, or shares any data, TV tokens, keys, or files with external servers.
* **Direct Network Stream:** Uses raw Python sockets straight to your TV's SDB port (`26101`).
* **Developer Mode Safety:** Only keep Developer Mode active on secure, trusted home Wi-Fi networks.

---

## Author

* **[Suz41](https://github.com/Suz41):** Developer of this direct Android-to-TV Tizen sideloading workflow.

## Acknowledgments & Upstream Credits

Every application available in the 1-click community store was created, ported, or maintained by incredible open-source developers. Full credit goes to:

* **[reisxd](https://github.com/reisxd):** Creator of **TizenBrew** (standalone homebrew loader & package signer) and **TizenTube** (ad-free TV YouTube framework).
* **[Apps2Samsung](https://github.com/Apps2Samsung):** For maintaining community package repository builds, automated signing actions, and hosting distribution mirrors.
* **[Jellyfin Project](https://jellyfin.org/):** For the native Jellyfin TV client and open-source media ecosystem.
* **[Stremio](https://www.stremio.com/):** For the official and community Tizen smart TV streaming application port.
* **[VideoLAN (VLC)](https://www.videolan.org/):** For the VLC media engine and [PatrickSt1991](https://github.com/PatrickSt1991) for the VLC Tizen TV port.
* **[fgl27](https://github.com/fgl27):** For **SmartTV_Twitch**, the open-source ad-free Twitch client for Tizen.
* **[Moonlight Stream](https://moonlight-stream.org/):** For NVIDIA GameStream/Sunshine PC game streaming protocol, and [brightcraft](https://github.com/brightcraft) / [OneLiberty](https://github.com/OneLiberty) for the Tizen ports.
* **[Chiaki-ng](https://github.com/streetpea/chiaki-ng):** For PlayStation 4/5 Remote Play client, and [Trent407](https://github.com/Trent407) for the Tizen TV package.
* **[dos-ise](https://github.com/dos-ise):** For porting classic **Doom** and **GameBoy Emulator** natively to Samsung Tizen OS.
* **[MrHumanRebel](https://github.com/MrHumanRebel):** For **AirTizen**, bringing Apple AirPlay support to Samsung TVs.
* **[FUTO](https://futo.org/):** For **FCastReceiver**, an open-source wireless casting alternative to Chromecast.
* **[Tailscale](https://tailscale.com/):** For the mesh VPN protocol, and [PatrickSt1991](https://github.com/PatrickSt1991) for packaging native Tizen TPK binaries.
* **[Dmitry Maksakov](https://github.com/DmitryMaksakov):** For **iperf3-TV**, enabling direct network throughput testing on Tizen.
* **[Termux Project](https://termux.dev/):** For providing the powerful Linux environment on Android that makes PC-less sideloading a reality.

---

## Disclaimer & Risk Disclosure

* **Educational & Personal Use Only:** This tool is provided solely for personal educational use, developer testing, and sideloading open-source, community-developed home media software onto your own hardware.
* **Third-Party Applications:** The installer script is 100% open-source, local, and transparent. However, the applications and packages you choose to download and sideload (`.wgt` / `.tpk` files) are created and distributed by independent third parties. The author of this repository assumes no responsibility or liability for third-party package stability, performance, or potential security implications.
* **Network & Device Responsibility:** Enabling Developer Mode opens your TV's debugging port (`26101`) to your local network. It should only be enabled on trusted private home networks. The user assumes full technical understanding and responsibility when operating their hardware in Developer Mode.
* **Trademarks:** Samsung, Tizen, Android, Termux, and all related brand names, logos, and trademarks belong to their respective owners and are used here solely for descriptive and identification purposes.
* **AI Assistance:** Portions of the tooling, documentation, automated scripts, and error diagnostics were developed and refined with the assistance of artificial intelligence (Google Gemini / Antigravity pair-programming).
