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
    - Apps -> Press 1 2 3 4 5 on remote
    - Turn Developer Mode -> ON
    - Host IP -> Enter: 192.168.1.5
    - Hold TV Power button 5s to restart TV

 2. FIND TV IP ON TV:
    - Settings -> General -> Network -> Network Status
========================================================
```

### 2. Live Interactive Dashboard
```text
╭──────────────────────────────────────────────────────────────╮
│  SAMSUNG TIZEN SIDELOAD MANAGER   v2.5.0                     │
├──────────────────────────────────────────────────────────────┤
│  STATUS     : [ONLINE]  192.168.1.100:26101                  │
│  PHONE IP   : 192.168.1.5 (Wi-Fi)                            │
│  VERSION    : v2.5.0 (Latest) [OK]                           │
│  TV MODEL   : Samsung QLED 4K (Tizen 6.5)                    │
│  DEV MODE   : [ON] (Host: 192.168.1.5) [MATCH OK]            │
│  ON PHONE   : 18 Packages Ready (.wgt / .tpk files)          │
│  ON TV      : 2 Apps Installed (User 5001 sandbox)           │
├──────────────────────────────────────────────────────────────┤
│  QUICK SETUP GUIDE:                                          │
│  1. TV Apps -> Remote: 1 2 3 4 5 -> Dev Mode [ON]            │
│  2. In 'Host PC IP', enter   -> 192.168.1.5                  │
│  3. Cold reboot TV (Hold Remote Power for 5s)                │
╰──────────────────────────────────────────────────────────────╯

╭── [SIDELOAD & PACKAGES] ──────────────────────────────────────╮
│  [1] Sideload Local Package  (18 ready on phone)              │
│  [2] Community App Store    (TizenBrew, Gaming, 50+ apps)     │
│  [s] Streaming Suite Hub    (Jellyfin OG, Litefin, Moonfin)   │
│  [3] App & Package Hub      (2 on TV, 18 on phone)            │
│  [4] Uninstall App from TV                                    │
├── [DIAGNOSTICS & TV TOOLS] ───────────────────────────────────┤
│  [5] TV Health & Diagnostic Monitor                           │
│  [6] TV Remote Cold Reboot Instructions                       │
│  [7] Change / Auto-Scan TV IP Address                         │
├── [SYSTEM] ───────────────────────────────────────────────────┤
│  [u] Check for Updates       (Auto-restart)                   │
│  [r] Refresh Dashboard                                        │
│  [0] Exit                                                     │
╰───────────────────────────────────────────────────────────────╯
```

### 3. Pre-Signed Community App Store
```text
=== Pre-signed Community App Store ===

--- Framework ---
 [ 1] TizenBrew (Homebrew App Store & Module Runner)

--- Streaming Suite & Media ---
 >> Jellyfin Official & Mod Builds:
  [ 2] Jellyfin TV (OSA) [AVPlay 4K HDR]
  [ 3] Jellyfin TV (OG - Official Stable Vanilla) [Recommended]
  [ 4] Jellyfin TV (GrayFix - Letterbox Black Bar Fix)
  [ 5] Jellyfin TV (OblongIcon - Modern Rectangular Tile)
  [ 6] Jellyfin TV (Secondary Instance - Dual Server)
  [ 7] Jellyfin TV (Legacy - Tizen 2.4-4.0)

 >> Litefin High-Performance Client:
  [ 8] Litefin TV (Normal - Stable)
  [ 9] Litefin TV (Modern - Fast ES6 WebView)
  [10] Litefin TV (Normal - Oblong Icon)
  [11] Litefin TV (Legacy - Tizen 3-4)
  [12] Litefin TV (Ultra-Legacy - Tizen 2.4)
  [13] Litefin TV (Ultra-Legacy NoService - Security Bypass)

 >> Moonfin Remote-First AVPlay Client:
  [14] Moonfin TV (Regular - AVPlay 4K HDR & Moonbase)
  [15] Moonfin TV (Oblong Icon)
  [16] Moonfin TV (Legacy - Tizen 3-4)

 >> Pelagica Client:
  [17] Pelagica TV (Modern Jellyfin Client)

 >> Video & Live Streaming:
  [18] TizenTube (Ad-free YouTube + SponsorBlock)
  [19] Stremio TV (Community App)
  [20] SmartTV Twitch (Ad-free Twitch Client)

--- Media ---
 [21] VLC Media Player (Native Video Player)

--- Gaming ---
 [22] Moonlight TV (4K PC Game Streaming)
 [23] Chiaki (PlayStation 4/5 Remote Play)
 [24] Doom (Classic Doom Port)
 [25] GameBoy Emulator

--- Utilities ---
 [26] AirTizen (Apple AirPlay Receiver)
 [27] FCastReceiver (Open Chromecast Alternative)
 [28] Tailscale (Mesh VPN Client - Native TPK)
 [29] iperf3 (Network Speed Tester)

 [30] Browse All Community Apps (50+ Packages Live Archive)...
```

#### Community Apps Guide & Recommendations

| App | Category | Use Case & Key Difference | Status |
| :--- | :--- | :--- | :--- |
| **TizenBrew** | Framework | Mod loader & package runner. Run community plugins right from your TV remote. | Essential |
| **Jellyfin TV (OG)** | Streaming | Vanilla official stable upstream web client build. Pure original release. | **[Recommended]** Official Original |
| **Jellyfin TV (OSA)** | Streaming | Direct 4K HDR playback using native Samsung **AVPlay** hardware + Smart Hub ribbon preview. | AVPlay Video Engine |
| **Jellyfin TV (GrayFix)** | Streaming | Fixes washed-out gray letterbox bars on widescreen movies. | Letterbox Fix |
| **Jellyfin TV (OblongIcon)** | Streaming | Wide rectangular tile for newer Samsung TV home bars. | Modern UI |
| **Jellyfin TV (Secondary)** | Streaming | Alternate App ID allowing two Jellyfin apps installed side-by-side. | Dual Server Setup |
| **Jellyfin TV (Legacy)** | Streaming | v10.8.z build for older 2015-2017 Samsung TVs (Tizen 2.4 / 3.0 / 4.0). | Older TVs |
| **Litefin TV (Normal)** | Streaming | Ultra-responsive, lightweight Jellyfin client with AVPlay backend and ASS/PGS subtitle support. | High-Performance |
| **Litefin TV (Modern)** | Streaming | ES6+ build optimized for faster execution on modern Tizen 6.0+ WebViews. | Modern WebViews |
| **Litefin TV (Oblong)** | Streaming | Stable Litefin build packaged with wide rectangular home-screen tile. | Modern UI |
| **Litefin TV (Legacy)** | Streaming | Backward-compatible Litefin build tailored for Tizen 3.0 and 4.0 chipsets. | Older TVs |
| **Litefin TV (Ultra-Legacy)** | Streaming | Polyfilled build for vintage 2015-2016 Tizen 2.4 Samsung Smart TVs. | Legacy Hardware |
| **Litefin TV (NoService)** | Streaming | Stripped background service to bypass TV security policies and installation error -14. | Security Workaround |
| **Moonfin TV (Regular)** | Streaming | Premium remote-first Jellyfin client with AVPlay hardware pipeline, lossless audio passthrough, and Moonbase sync. | Remote-First AVPlay |
| **Moonfin TV (Oblong)** | Streaming | Moonfin TV client packaged with modern horizontal oblong launcher icon. | Modern UI |
| **Moonfin TV (Legacy)** | Streaming | Moonfin build adapted for older Tizen 3.0 & 4.0 Samsung TVs. | Older TVs |
| **Pelagica TV** | Streaming | Sleek, modern client for Jellyfin with responsive UI, multi-server support, and fast browsing. | Multi-Server Client |
| **TizenTube** | Streaming | Ad-free YouTube with SponsorBlock, Return Dislike, and 4K HDR support. | Ad-Free YouTube |
| **Stremio TV** | Streaming | Torrent & Real-Debrid streaming media aggregator. | For Debrid |
| **SmartTV Twitch** | Streaming | Ad-free Twitch client with BTTV / 7TV / FFZ chat emotes and custom sidebar. | Ad-Free Twitch |
| **VLC Media Player** | Media | Native media player for USB flash drives and local SMB/DLNA network shares. | Media Player |
| **Moonlight TV** | Gaming | 4K 60/120fps low-latency PC game streaming via NVIDIA Sunshine/GameStream. | PC Gamers |
| **Chiaki** | Gaming | PlayStation 4 & PlayStation 5 Remote Play client with controller support. | PS4/PS5 Remote |
| **Doom** | Gaming | Classic 1993 Doom game running natively on the TV processor. | Retro Gaming |
| **GameBoy Emulator** | Gaming | GameBoy & GBC retro emulator with Bluetooth gamepad support. | Retro Gaming |
| **AirTizen** | Utilities | Apple AirPlay receiver for Samsung TVs without native AirPlay 2. | AirPlay Receiver |
| **FCastReceiver** | Utilities | Open-source Chromecast alternative to cast media from phone without Google services. | Wireless Casting |
| **Tailscale** | Utilities | Native TPK mesh VPN (WireGuard) to access your home server securely from anywhere. | WireGuard Mesh VPN |
| **iperf3** | Utilities | Direct network bandwidth tester to diagnose Wi-Fi / Ethernet streaming speeds. | Bandwidth Tester |

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
* **1-Click Community App Store & Dedicated Streaming Suite:** Download and install 29+ popular pre-signed apps with a dedicated Streaming Hub featuring Jellyfin (Pure OG & OSA), the complete Litefin family (6 builds), Moonfin AVPlay suite, and Pelagica TV, plus an instant live directory browser with access to **50+ community packages** (IPTV players, KickTV, retro emulators, security camera feeds, and utilities).
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
* **[MoazSalem](https://github.com/MoazSalem):** For **Litefin**, the high-performance, lightweight Jellyfin client for Tizen & webOS with AVPlay backend and native ASS subtitle rendering.
* **[Moonfin-Client](https://github.com/Moonfin-Client):** For **Moonfin Smart-TV**, the remote-first AVPlay hardware-accelerated Jellyfin client with lossless audio and Moonbase sync.
* **[PelagicaApp](https://github.com/PelagicaApp):** For **Pelagica**, the modern responsive web & TV client for Jellyfin.
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
