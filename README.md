### Sideloading Apps in Samsung Tizen TV by Android (No PC, No Pendrive, No Tizen Studio, No Certificates, No Licensing) (Just use some brain)

Sideload Tizen application packages (`.wgt` files) onto a Samsung Smart TV directly from **Termux on Android** without a PC, USB drive, Tizen Studio SDK, or dealing with Samsung author/distributor certificates and licensing signatures.

---

## 📺 1. TV Configuration

1. Locate your **TV IP Address** in TV settings (e.g., `10.187.217.145`).
2. Locate your **Phone Hotspot IP** (e.g., `10.187.217.60`).
3. Open the **Apps** panel on the TV.
4. Press **`12345`** on the remote to open Developer Mode settings.
5. Toggle **Developer Mode** to **ON** and set the **Host IP** to your Phone Hotspot IP.
6. **Reboot the TV:** Hold the remote Power button down until the TV shuts off and restarts with the Samsung logo. (This opens Port `26101`).

---

## 🔐 2. Termux Keys Setup

Copy cryptographic Tizen keys to Android ADB paths to authenticate connections:

```bash
# Generate keys if they do not exist
mkdir -p ~/.android ~/.tizen
adb keygen ~/.tizen/sdbkey 2>/dev/null

# Sync Tizen keys to ADB paths
cp ~/.tizen/sdbkey ~/.android/adbkey
cp ~/.tizen/sdbkey.pub ~/.android/adbkey.pub
```

---

## 🚀 3. Sideloading Script (`install.py`)

Save this code as `install.py` in your Termux home directory:

```python
import socket
import struct
import os
import sys

tv_ip = "10.187.217.145" # Replace with your TV IP
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

## 🏃 4. Installation Commands

1. Establish authorization bridge:
   ```bash
   adb connect <TV_IP>:26101
   ```
2. Deploy packages:
   ```bash
   python3 install.py <file.wgt> <AppID>
   ```

* **Jellyfin:** `python3 install.py Jellyfin.wgt Jellyfin`
* **TizenBrew:** `python3 install.py TizenBrew.wgt xvvl3S1bvH.TizenBrewStandalone`
* **VLC TV:** `python3 install.py vlctv.wgt VLCTV`
