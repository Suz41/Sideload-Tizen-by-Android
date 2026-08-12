# 📺 Samsung Tizen TV App Sideloading Guide (from Termux)

This guide explains how to sideload `.wgt` applications onto a Samsung Smart TV directly from **Termux on Android** over a Wi-Fi hotspot, without a PC or USB drive.

---

## 📡 1. Network & TV Setup

1. **Get TV IP Address:** Look up your TV's IP address under the TV's Network Status menu (e.g., `10.187.217.145`).
2. **Get Phone Hotspot IP:** In Termux, verify your phone's IP interface address (e.g., `10.187.217.60`).
3. **Turn on TV Developer Mode:**
   * Go to **Smart Hub / Apps** panel.
   * On your TV remote, enter the PIN code sequence **`12345`**.
   * Toggle **Developer Mode** to **ON**.
   * Set the **Host IP** field to your phone's hotspot IP address (e.g., `10.187.217.60`).
   * **Reboot the TV:** Hold the Power button on the remote for 5 seconds until the TV turns off and turns back on displaying the Samsung logo. This opens **Port `26101`** on the TV.

---

## 🔐 2. Cryptographic RSA Key Sync

Because Samsung SDB connects using the ADB wire protocol, you must copy your Tizen keys to your Android ADB location to authenticate properly from Termux:

```bash
# Generate keys if they do not exist
mkdir -p ~/.android ~/.tizen
adb keygen ~/.tizen/sdbkey 2>/dev/null

# Sync Tizen keys to Android tools location
cp ~/.tizen/sdbkey ~/.android/adbkey
cp ~/.tizen/sdbkey.pub ~/.android/adbkey.pub
```

---

## 🚀 3. Sideloading Script (`install.py`)

Save the following Python code as `install.py` in your Termux home directory. This script acts as a custom SDB client, streaming the `.wgt` archive directly over a socket connection to your TV, bypassing the need for x86_64 PC binaries.

```python
import socket
import struct
import os
import sys

tv_ip = "10.187.217.145"
local_wgt = sys.argv[1] # e.g. "Jellyfin.wgt"
app_id = sys.argv[2]   # e.g. "Jellyfin"
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

# 1. Connect & Push File over SDB Sync Socket
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

# 2. Trigger Installation & Launch on TV
run_shell(f"0 vd_appinstall {app_id} {remote_wgt}")
run_shell(f"0 pkgcmd -i -t wgt -p {remote_wgt}")
run_shell(f"0 app_launcher -s {app_id}")
print(f"SUCCESS: {local_wgt} installed and launched on TV!")
```

---

## 📲 4. Commands to Connect and Run

1. Open Termux on your phone.
2. Establish the connection:
   ```bash
   adb connect 10.187.217.145:26101
   ```
3. Run the installer script:
   ```bash
   python3 install.py <file.wgt> <AppID>
   ```

* **Example for Jellyfin:** `python3 install.py Jellyfin.wgt Jellyfin`
* **Example for TizenBrew:** `python3 install.py TizenBrew.wgt xvvl3S1bvH.TizenBrewStandalone`
* **Example for VLC TV:** `python3 install.py vlctv.wgt VLCTV`
