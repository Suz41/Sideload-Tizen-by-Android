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

## 🔐 Step 2: Initialize Cryptographic Keys in Termux

Open **Termux** on your phone, copy and paste this one-liner to generate and sync Tizen authorization keys to your local ADB path:

```bash
mkdir -p ~/.android ~/.tizen && adb keygen ~/.tizen/sdbkey 2>/dev/null && cp ~/.tizen/sdbkey ~/.android/adbkey && cp ~/.tizen/sdbkey.pub ~/.android/adbkey.pub
```

---

## 🚀 Step 3: Setup the Sideload Python Script

Save the following Python code as **`install.py`** in your Termux home directory:

```python
import socket
import struct
import os
import sys

tv_ip = "10.187.217.145" # Replace with your TV IP Address
local_wgt = sys.argv[1]   # e.g., "Jellyfin.wgt"
app_id = sys.argv[2]      # e.g., "Jellyfin"
remote_wgt = f"/home/owner/share/tmp/sdk_tools/tmp/{local_wgt}"

def recv_exact(s, n):
    buf = b""
    while len(buf) < n:
        chunk = s.recv(n - len(buf))
        if not chunk: break
        buf += chunk
    return buf

def recv_pkt(s):
    hdr = recv_exact(s, 24)
    if len(hdr) < 24: return None, 0, 0, b""
    cmd, a0, a1, length, crc, magic = struct.unpack("<4sIIIII", hdr)
    p = recv_exact(s, length) if length > 0 else b""
    return cmd, a0, a1, p

def run_shell(cmd_str):
    s = socket.socket()
    s.settimeout(10.0)
    s.connect((tv_ip, 26101))
    s.sendall(struct.pack("<4sIIIII", b"CNXN", 0x01000000, 65536, 7, sum(b"host::\x00")&0xffffffff, 0x4e584e43^0xffffffff) + b"host::\x00")
    s.recv(1024)
    service = f"shell:{cmd_str}\x00".encode()
    s.sendall(struct.pack("<4sIIIII", b"OPEN", 1, 0, len(service), sum(service)&0xffffffff, 0x4e45504f^0xffffffff) + service)
    s.recv(1024)
    out = b""
    try:
        while True:
            c, a0, a1, p = recv_pkt(s)
            if not c or c == b"CLSE": break
            if p: out += p
    except Exception: pass
    s.close()
    return out.decode(errors="ignore")

# 1. Stream File over SDB Sync Socket
s = socket.socket()
s.settimeout(30.0)
s.connect((tv_ip, 26101))
s.sendall(struct.pack("<4sIIIII", b"CNXN", 0x01000000, 65536, 7, sum(b"host::\x00")&0xffffffff, 0x4e584e43^0xffffffff) + b"host::\x00")
recv_pkt(s)

service = b"sync:\x00"
s.sendall(struct.pack("<4sIIIII", b"OPEN", 1, 0, len(service), sum(service)&0xffffffff, 0x4e45504f^0xffffffff) + service)
cmd, r_id, l_id, p = recv_pkt(s)

dest = remote_wgt.encode() + b",33279"
send_pld = struct.pack("<4sI", b"SEND", len(dest)) + dest
s.sendall(struct.pack("<4sIIIII", b"WRTE", 1, r_id, len(send_pld), sum(send_pld)&0xffffffff, 0x45545257^0xffffffff) + send_pld)
recv_pkt(s)

with open(local_wgt, "rb") as f:
    while True:
        blk = b""
        while len(blk) < 32768:
            chunk = f.read(4000)
            if not chunk: break
            blk += struct.pack("<4sI", b"DATA", len(chunk)) + chunk
        if not blk: break
        s.sendall(struct.pack("<4sIIIII", b"WRTE", 1, r_id, len(blk), sum(blk)&0xffffffff, 0x45545257^0xffffffff) + blk)
        cmd, a0, a1, p = recv_pkt(s)
        if cmd == b"WRTE":
            s.sendall(struct.pack("<4sIIIII", b"OKAY", 1, r_id, 0, 0, 0x47414b4f^0xffffffff))

done_pld = struct.pack("<4sI", b"DONE", int(os.path.getmtime(local_wgt)))
s.sendall(struct.pack("<4sIIIII", b"WRTE", 1, r_id, len(done_pld), sum(done_pld)&0xffffffff, 0x45545257^0xffffffff) + done_pld)
recv_pkt(s)
s.close()

# 2. Trigger Installation & Launch
run_shell(f"0 vd_appinstall {app_id} {remote_wgt}")
run_shell(f"0 pkgcmd -i -t wgt -p {remote_wgt}")
run_shell(f"0 app_launcher -s {app_id}")
print(f"SUCCESS: {local_wgt} installed!")
```

---

## 🏃 Step 4: Run Installation Commands

Download any `.wgt` package file to Termux. Then connect to your TV and install it:

1. **Connect to the TV:**
   ```bash
   adb connect <TV_IP_ADDRESS>:26101
   ```
2. **Execute installation script:**
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
