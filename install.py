import socket
import struct
import os
import sys

tv_ip = "10.187.217.145"

# Default to Jellyfin if no arguments are provided
local_wgt = sys.argv[1] if len(sys.argv) > 1 else "Jellyfin.wgt"
app_id = sys.argv[2] if len(sys.argv) > 2 else "Jellyfin"
remote_wgt = f"/home/owner/share/tmp/sdk_tools/tmp/{local_wgt}"

print(f"Targeting: {local_wgt} (App ID: {app_id})")

if not os.path.exists(local_wgt):
    print(f"Error: {local_wgt} not found! Please download it first or place it in this folder.")
    sys.exit(1)

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
print("Connecting to Samsung TV...")
s = socket.socket()
s.settimeout(30.0)
s.connect((tv_ip, 26101))
s.sendall(struct.pack("<4sIIIII", b"CNXN", 0x01000000, 65536, 7, sum(b"host::\x00")&0xffffffff, 0x4e584e43^0xffffffff) + b"host::\x00")
recv_pkt(s)

print("Opening file transfer channel...")
service = b"sync:\x00"
s.sendall(struct.pack("<4sIIIII", b"OPEN", 1, 0, len(service), sum(service)&0xffffffff, 0x4e45504f^0xffffffff) + service)
cmd, r_id, l_id, p = recv_pkt(s)

print(f"Streaming {local_wgt} to TV...")
dest = remote_wgt.encode() + b",33279"
send_pld = struct.pack("<4sI", b"SEND", len(dest)) + dest
s.sendall(struct.pack("<4sIIIII", b"WRTE", 1, r_id, len(send_pld), sum(send_pld)&0xffffffff, 0x45545257^0xffffffff) + send_pld)
recv_pkt(s)

file_size = os.path.getsize(local_wgt)
bytes_sent = 0

with open(local_wgt, "rb") as f:
    while True:
        blk = b""
        while len(blk) < 32768:
            chunk = f.read(4000)
            if not chunk: break
            blk += struct.pack("<4sI", b"DATA", len(chunk)) + chunk
        if not blk: break
        s.sendall(struct.pack("<4sIIIII", b"WRTE", 1, r_id, len(blk), sum(blk)&0xffffffff, 0x45545257^0xffffffff) + blk)
        bytes_sent += len(blk)
        # Simple progress logger
        print(f"Uploading: {int((bytes_sent/file_size)*100)}%...", end="\r")
        cmd, a0, a1, p = recv_pkt(s)
        if cmd == b"WRTE":
            s.sendall(struct.pack("<4sIIIII", b"OKAY", 1, r_id, 0, 0, 0x47414b4f^0xffffffff))

done_pld = struct.pack("<4sI", b"DONE", int(os.path.getmtime(local_wgt)))
s.sendall(struct.pack("<4sIIIII", b"WRTE", 1, r_id, len(done_pld), sum(done_pld)&0xffffffff, 0x45545257^0xffffffff) + done_pld)
recv_pkt(s)
s.close()
print("\nFile upload complete.")

# 2. Trigger Installation & Launch
print("Installing app on TV...")
run_shell(f"0 vd_appinstall {app_id} {remote_wgt}")
run_shell(f"0 pkgcmd -i -t wgt -p {remote_wgt}")
print("Launching app on TV...")
run_shell(f"0 app_launcher -s {app_id}")
print("SUCCESS: Installation Complete!")
