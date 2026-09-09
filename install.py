
def menu_browse_all_upstream(tv_ip):
    """Dynamically fetch and list all 50+ community apps from Apps2Samsung repo."""
    print(f"\n{CYAN}🌐 Fetching complete live community repository catalog...{RESET}")
    api_url = "https://api.github.com/repos/Apps2Samsung/tizen-community-packages/releases/tags/community-611"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    import json
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            assets = [a["name"] for a in data.get("assets", []) if (a["name"].endswith(".wgt") or a["name"].endswith(".tpk")) and not a["name"].startswith("Overscan")]
    except Exception as e:
        print(f"{RED}Could not load live catalog: {e}{RESET}")
        input("\nPress Enter to return...")
        return

    print(f"\n{BOLD}=== Full Community Package Archive ({len(assets)} Apps) ==={RESET}")
    for idx, name in enumerate(assets, 1):
        ext = "TPK" if name.endswith(".tpk") else "WGT"
        print(f" [{str(idx).rjust(2)}] {name.ljust(42)} [{CYAN}{ext}{RESET}]")

    choice = input(f"\nSelect package [1-{len(assets)}] or 0 to cancel: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(assets):
        target_name = assets[int(choice)-1]
        dl_url = f"https://github.com/Apps2Samsung/tizen-community-packages/releases/download/community-611/{target_name}"
        if not os.path.exists(target_name):
            print(f"Downloading {target_name}...")
            try:
                urllib.request.urlretrieve(dl_url, target_name)
                print(f"{GREEN}✔ Download complete!{RESET}")
            except Exception as e:
                print(f"{RED}Download failed: {e}{RESET}")
                input("\nPress Enter to return...")
                return
        stream_and_install_wgt(tv_ip, target_name)
    input("\nPress Enter to continue...")

SCRIPT_VERSION = "2.0.0"

def get_git_update_status():
    """Check if local git repo is up-to-date with remote."""
    try:
        import subprocess
        # Check without blocking for long
        subprocess.run(["git", "fetch", "origin", "main"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        local_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, timeout=1).decode().strip()
        remote_hash = subprocess.check_output(["git", "rev-parse", "origin/main"], stderr=subprocess.DEVNULL, timeout=1).decode().strip()
        if local_hash and remote_hash:
            if local_hash == remote_hash:
                return f"{GREEN}Up-to-date ✔{RESET}"
            else:
                return f"{YELLOW}Update Available ⚡ (Press 'u' to update){RESET}"
    except Exception:
        pass
    return f"{GREEN}Latest ✔{RESET}"



def explain_tv_error(err_str, context="install"):
    """Comprehensive Step-by-Step Error Explainer for every possible failure."""
    err_lower = err_str.lower()
    print(f"\n{YELLOW}╔════════════════════════════════════════════════════════════════════════╗{RESET}")
    print(f"{YELLOW}║ 💡  ERROR DIAGNOSTIC & STEP-BY-STEP SOLUTION                           ║{RESET}")
    print(f"{YELLOW}╚════════════════════════════════════════════════════════════════════════╝{RESET}")

    # STEP 1: CONNECTION / NETWORK FAILURES
    if any(k in err_lower for k in ["connection failed", "cannot connect", "timed out", "errno 111", "refused", "no route"]):
        print(f" {RED}{BOLD}🚨 STAGE: TV Network & Connection Failure{RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" ❓ WHAT YOU DID WRONG:")
        print("    1. Your Phone and TV are NOT on the exact same Wi-Fi or Hotspot.")
        print("    2. Or Developer Mode is NOT active on the TV.")
        print("    3. Or you forgot to reboot the TV after changing Developer Mode.")
        print("    4. Or the TV IP address changed.")
        print("")
        print(f" {GREEN}{BOLD}👉 EXACT STEPS TO FIX IT:{RESET}")
        print("    Step 1: Check Wi-Fi -> Phone and TV must show identical Wi-Fi names.")
        print("    Step 2: On TV Remote -> Open 'Apps' -> Press 1 2 3 4 5.")
        print("    Step 3: Toggle 'Developer Mode' to [ ON ].")
        print("    Step 4: Enter your phone's IP in 'Host IP'.")
        print("    Step 5: Hold TV Remote Power button for 5 sec until TV restarts.")
        print("    Step 6: In this menu, choose Option [3] -> [1] to Auto-Scan your TV.")

    # STEP 2: UNSIGNED PACKAGE (SIGNATURE)
    elif any(k in err_lower for k in ["failed[-11]", "invalid signature", "signature verification", "signature missing"]):
        print(f" {RED}{BOLD}🚨 STAGE: Digital Signature Verification Failed (Error -11){RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" ❓ WHAT YOU DID WRONG:")
        print("    You tried to install an app that has no Samsung Digital Certificate.")
        print("    (Raw builds like NuvioTV.wgt do not have community certificates built-in).")
        print("")
        print(f" {GREEN}{BOLD}👉 EXACT STEPS TO FIX IT:{RESET}")
        print("    Step 1: Go back to the Main Menu and choose Option [2].")
        print("    Step 2: Install 'TizenBrew' (App #1). It has valid certificates.")
        print("    Step 3: Open TizenBrew on your TV screen.")
        print("    Step 4: Inside TizenBrew, select 'Add GitHub Module' and type the app repo.")

    # STEP 3: CERTIFICATE MISMATCH (DUID / AUTHORITY)
    elif any(k in err_lower for k in ["failed[-12]", "author certificate", "duid mismatch"]):
        print(f" {RED}{BOLD}🚨 STAGE: Certificate Authority Mismatch (Error -12){RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" ❓ WHAT YOU DID WRONG:")
        print("    The certificate on this package was created for a different TV device ID (DUID).")
        print("")
        print(f" {GREEN}{BOLD}👉 EXACT STEPS TO FIX IT:{RESET}")
        print("    Step 1: Always install pre-signed packages from Option [2].")
        print("    Step 2: If using custom packages, ensure they use a Public Community Certificate.")

    # STEP 4: PERMISSION / PRIVILEGE ERRORS
    elif any(k in err_lower for k in ["failed[-14]", "privilege", "partner", "platform"]):
        print(f" {RED}{BOLD}🚨 STAGE: Restricted Privilege Level (Error -14){RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" ❓ WHAT YOU DID WRONG:")
        print("    This app requests advanced Samsung Partner/Platform permissions.")
        print("")
        print(f" {GREEN}{BOLD}👉 EXACT STEPS TO FIX IT:{RESET}")
        print("    Step 1: In TV Developer Mode (12345), make sure your phone's IP is set as Host IP.")
        print("    Step 2: Turn off TV, unplug power cable for 10 seconds, plug back in.")

    # STEP 5: STORAGE / DUPLICATE / PACKAGE ERRORS
    elif any(k in err_lower for k in ["failed[-1]", "failed[-4]", "already exists", "duplicate"]):
        print(f" {RED}{BOLD}🚨 STAGE: App Conflict or Storage Error{RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" ❓ WHAT YOU DID WRONG:")
        print("    An older version of this app is already installed or corrupted.")
        print("")
        print(f" {GREEN}{BOLD}👉 EXACT STEPS TO FIX IT:{RESET}")
        print("    Step 1: Go to Main Menu -> Option [5] (Uninstall an App).")
        print("    Step 2: Select the app to remove the older version.")
        print("    Step 3: Re-install the app cleanly.")

    # STEP 6: FILE NOT FOUND
    elif any(k in err_lower for k in ["not found", "no such file"]):
        print(f" {RED}{BOLD}🚨 STAGE: File Missing on Phone Storage{RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" ❓ WHAT YOU DID WRONG:")
        print("    The package was not placed in the correct phone folder.")
        print("")
        print(f" {GREEN}{BOLD}👉 EXACT STEPS TO FIX IT:{RESET}")
        print("    Step 1: Open your phone's File Manager.")
        print("    Step 2: Navigate to: Internal Storage -> Download -> Samsung-T-Sideload")
        print("    Step 3: Paste your .wgt or .tpk file inside that folder.")
        print("    Step 4: Press 'r' in this menu to refresh and find it.")

    else:
        print(f" {RED}{BOLD}🚨 STAGE: General TV System Error{RESET}")
        print(f"    Raw TV Response: {err_str}")
        print("")
        print(f" {GREEN}{BOLD}👉 RECOMMENDED FIX:{RESET}")
        print("    Step 1: Hold Remote Power button for 5 seconds to soft-reboot TV.")
        print("    Step 2: Make sure TV has an active Wi-Fi connection.")
        print("    Step 3: Try again.")

    print(f"{YELLOW}════════════════════════════════════════════════════════════════════════{RESET}\n")

def scan_network_for_tv(phone_ip=None):
    """Scan local subnet on port 26101 to auto-detect Samsung TV."""
    print(f"\n{CYAN}🔍 Scanning local Wi-Fi network for Samsung TV (port 26101)...{RESET}")
    base = None
    if phone_ip and "." in phone_ip and not phone_ip.startswith("127."):
        parts = phone_ip.split(".")
        base = ".".join(parts[:3])
    else:
        saved = get_saved_tv_ip()
        if saved and "." in saved:
            base = ".".join(saved.split(".")[:3])

    if not base:
        base = "192.168.1"

    found_ips = []
    import concurrent.futures

    def test_ip(host):
        s = socket.socket()
        s.settimeout(0.35)
        try:
            if s.connect_ex((host, 26101)) == 0:
                return host
        except Exception:
            pass
        finally:
            s.close()
        return None

    with concurrent.futures.ThreadPoolExecutor(max_workers=50) as executor:
        futures = [executor.submit(test_ip, f"{base}.{i}") for i in range(1, 255)]
        for fut in concurrent.futures.as_completed(futures):
            res = fut.result()
            if res:
                found_ips.append(res)
                print(f"{GREEN}✔ Found TV at: {res}{RESET}")

    if found_ips:
        return found_ips[0]
    print(f"{YELLOW}No TV found on subnet {base}.0/24 (Make sure TV Developer Mode is ON){RESET}")
    return None

#!/usr/bin/env python3
import socket
import struct
import os
import sys
import time
import zipfile
import urllib.request
import xml.etree.ElementTree as ET

CONFIG_FILE = os.path.expanduser("~/.tizen_tv_ip")

# ANSI Color Codes for Clean Terminal Output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"
RESET = "\033[0m"

COMMUNITY_APPS = {
    "1": {"name": "TizenBrew (Homebrew App Store)", "file": "TizenBrew.wgt", "ver": "v2.0.5", "cat": "Framework", "min_tizen": "4.0"},
    "2": {"name": "TizenTube (Ad-free YouTube)", "file": "TizenTube.wgt", "ver": "v0.8.2", "cat": "Streaming", "min_tizen": "4.0"},
    "3": {"name": "Jellyfin TV (Home Media Server)", "file": "Jellyfin.wgt", "ver": "v0.16.2", "cat": "Streaming", "min_tizen": "5.0", "url": "https://github.com/Apps2Samsung/tizen-community-packages/raw/main/Jellyfin.wgt"},
    "4": {"name": "Stremio TV (Community App)", "file": "Stremio-Tizen4.wgt", "ver": "v1.7.0", "cat": "Streaming", "min_tizen": "4.0"},
    "5": {"name": "SmartTV Twitch (Ad-free Twitch)", "file": "SmartTV_Twitch.wgt", "ver": "v1.4.1", "cat": "Streaming", "min_tizen": "5.0"},
    "6": {"name": "VLC Media Player", "file": "VLC-TV.wgt", "ver": "v3.0.18", "cat": "Media", "min_tizen": "5.0"},
    "7": {"name": "Moonlight TV (PC Game Stream 4K)", "file": "Moonlight-Tizen.wgt", "ver": "v1.6.0", "cat": "Gaming", "min_tizen": "5.5"},
    "8": {"name": "Chiaki (PlayStation Remote Play)", "file": "Chiaki-Tizen.wgt", "ver": "v2.2.0", "cat": "Gaming", "min_tizen": "5.5"},
    "9": {"name": "Doom (Classic Doom Port)", "file": "Doom.wgt", "ver": "v1.1", "cat": "Gaming", "min_tizen": "4.0"},
    "10": {"name": "GameBoy Emulator", "file": "GameBoy-Emulator.wgt", "ver": "v1.0", "cat": "Gaming", "min_tizen": "4.0"},
    "11": {"name": "AirTizen (Apple AirPlay)", "file": "AirTizen.wgt", "ver": "v0.3.1", "cat": "Utilities", "min_tizen": "5.5"},
    "12": {"name": "FCastReceiver (Chromecast Alt)", "file": "FCastReceiver.wgt", "ver": "v1.2.0", "cat": "Utilities", "min_tizen": "5.0"},
    "13": {"name": "Tailscale (Mesh VPN Client - TPK)", "file": "Tailscale.tpk", "ver": "v1.78.1", "cat": "Utilities", "min_tizen": "5.0"},
    "14": {"name": "iperf3 (Network Speed Tester)", "file": "iperf3-TV.wgt", "ver": "v3.16", "cat": "Utilities", "min_tizen": "4.0"}
}

def get_saved_tv_ip():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                ip = f.read().strip()
                if ip: return ip
        except Exception: pass
    return "10.253.229.145"

def save_tv_ip(ip):
    try:
        with open(CONFIG_FILE, "w") as f:
            f.write(ip.strip())
    except Exception: pass

def check_tv_online(ip):
    s = socket.socket()
    s.settimeout(1.5)
    try:
        res = s.connect_ex((ip, 26101))
        s.close()
        return res == 0
    except Exception:
        return False

def get_wgt_metadata(wgt_path):
    app_id = None
    is_signed = False
    try:
        with zipfile.ZipFile(wgt_path, "r") as z:
            names = set(z.namelist())
            if "author-signature.xml" in names or "signature1.xml" in names:
                is_signed = True
            # WGT format uses config.xml
            if "config.xml" in names:
                root = ET.fromstring(z.read("config.xml"))
                for elem in root.iter():
                    if elem.tag.endswith("application") and "id" in elem.attrib:
                        app_id = elem.attrib["id"]
                        break
            # TPK format uses tizen-manifest.xml
            elif "tizen-manifest.xml" in names:
                root = ET.fromstring(z.read("tizen-manifest.xml"))
                for elem in root.iter():
                    if (elem.tag.endswith("ui-application") or elem.tag.endswith("service-application")) and "appid" in elem.attrib:
                        app_id = elem.attrib["appid"]
                        break
                    elif "id" in elem.attrib and app_id is None:
                        app_id = elem.attrib["id"]
    except Exception as e:
        print(f"{YELLOW}Warning parsing package: {e}{RESET}")
    return app_id, is_signed

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

def run_tv_shell(tv_ip, cmd_str):
    s = socket.socket()
    s.settimeout(15.0)
    try:
        s.connect((tv_ip, 26101))
    except Exception as e:
        return f"Connection failed: {e}"
    s.sendall(struct.pack("<4sIIIII", b"CNXN", 0x01000000, 65536, 7, sum(b"host::\x00")&0xffffffff, 0x4e584e43^0xffffffff) + b"host::\x00")
    s.recv(1024)
    service = f"shell:{cmd_str}\x00".encode()
    s.sendall(struct.pack("<4sIIIII", b"OPEN", 1, 0, len(service), sum(service)&0xffffffff, 0x4e45504f^0xffffffff) + service)
    cmd, r_id, l_id, p = recv_pkt(s)
    out = b""
    try:
        while True:
            c, a0, a1, p = recv_pkt(s)
            if not c or c == b"CLSE": break
            if p: out += p
            if c == b"WRTE":
                s.sendall(struct.pack("<4sIIIII", b"OKAY", 1, r_id, 0, 0, 0x47414b4f^0xffffffff))
    except Exception: pass
    s.close()
    return out.decode(errors="ignore").strip()

def ensure_adb_connected(tv_ip):
    try:
        import subprocess
        subprocess.run(['adb', 'connect', f'{tv_ip}:26101'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
    except Exception: pass


def get_tv_details(tv_ip):
    """Query TV model name, Tizen version, DUID, and available storage."""
    details = {}
    try:
        raw = run_tv_shell(tv_ip, "0 vconftool -g db/menu/model_name; 0 vconftool -g db/system/tizen_version; 0 vconftool -g db/system/duid; 0 df -h /opt /home/owner")
        lines = [l.strip() for l in raw.splitlines() if l.strip() and not l.startswith("Connection failed")]
        if len(lines) >= 1: details["model"] = lines[0]
        if len(lines) >= 2: details["tizen"] = lines[1]
        if len(lines) >= 3: details["duid"] = lines[2]

        # Parse storage line (look for /opt or /home/owner or root partition)
        for line in lines[3:]:
            parts = line.split()
            if len(parts) >= 6 and (parts[5] in ["/opt", "/home/owner", "/"] or parts[0].startswith("/dev/")):
                # Format: Filesystem Size Used Avail Use% Mounted
                avail = parts[3]
                size = parts[1]
                used_pct = parts[4]
                details["storage"] = f"{avail} free of {size} ({used_pct} used)"
                break
    except Exception:
        pass
    return details

def stream_and_install_wgt(tv_ip, wgt_path, app_id=None):
    ensure_adb_connected(tv_ip)
    if not os.path.exists(wgt_path):
        print(f"{RED}Error: File '{wgt_path}' not found!{RESET}")
        return False

    meta_id, is_signed = get_wgt_metadata(wgt_path)
    final_app_id = app_id or meta_id or "App"

    if not is_signed:
        print(f"\n{YELLOW}======================================================{RESET}")
        print(f"{RED}{BOLD}⚠️  WARNING: UNSIGNED PACKAGE DETECTED!{RESET}")
        print(f"  '{wgt_path}' does not contain author-signature.xml.")
        print(f"  Samsung TV will reject installation with error: failed[-11].")
        print(f"  To use unsigned apps like Nuvio, sideload TizenBrew first.")
        print(f"{YELLOW}======================================================{RESET}")
        confirm = input("Attempt installation anyway? [y/N]: ").strip().lower()
        if confirm != "y":
            return False

    print(f"\n{CYAN}Targeting : {wgt_path}{RESET}")
    print(f"{CYAN}App ID    : {final_app_id}{RESET}")
    print(f"{CYAN}TV IP     : {tv_ip}:26101{RESET}\n")

    remote_wgt = f"/home/owner/share/tmp/sdk_tools/tmp/{os.path.basename(wgt_path)}"

    print("Connecting to Samsung TV...")
    s = socket.socket()
    s.settimeout(15.0)
    try:
        s.connect((tv_ip, 26101))
    except Exception as e:
        print(f"{RED}❌ Cannot connect to TV at {tv_ip}:26101 ({e}){RESET}")
        explain_tv_error(str(e))
        return False

    s.sendall(struct.pack("<4sIIIII", b"CNXN", 0x01000000, 65536, 7, sum(b"host::\x00")&0xffffffff, 0x4e584e43^0xffffffff) + b"host::\x00")
    recv_pkt(s)

    service = b"sync:\x00"
    s.sendall(struct.pack("<4sIIIII", b"OPEN", 1, 0, len(service), sum(service)&0xffffffff, 0x4e45504f^0xffffffff) + service)
    cmd, r_id, l_id, p = recv_pkt(s)

    dest = remote_wgt.encode() + b",33279"
    send_pld = struct.pack("<4sI", b"SEND", len(dest)) + dest
    s.sendall(struct.pack("<4sIIIII", b"WRTE", 1, r_id, len(send_pld), sum(send_pld)&0xffffffff, 0x45545257^0xffffffff) + send_pld)
    recv_pkt(s)

    file_size = os.path.getsize(wgt_path)
    bytes_sent = 0
    start_time = time.time()

    with open(wgt_path, "rb") as f:
        while True:
            blk = b""
            while len(blk) < 32768:
                chunk = f.read(4000)
                if not chunk: break
                blk += struct.pack("<4sI", b"DATA", len(chunk)) + chunk
            if not blk: break
            s.sendall(struct.pack("<4sIIIII", b"WRTE", 1, r_id, len(blk), sum(blk)&0xffffffff, 0x45545257^0xffffffff) + blk)
            bytes_sent += len(blk)
            elapsed = time.time() - start_time
            speed = (bytes_sent / (1024 * 1024)) / (elapsed if elapsed > 0 else 1)
            pct = int((bytes_sent / file_size) * 100)
            bar = ("█" * (pct // 5)).ljust(20, "░")
            print(f"Uploading: [{bar}] {pct}% ({speed:.1f} MB/s)", end="\r")
            cmd, a0, a1, p = recv_pkt(s)
            if cmd == b"WRTE":
                s.sendall(struct.pack("<4sIIIII", b"OKAY", 1, r_id, 0, 0, 0x47414b4f^0xffffffff))

    done_pld = struct.pack("<4sI", b"DONE", int(os.path.getmtime(wgt_path)))
    s.sendall(struct.pack("<4sIIIII", b"WRTE", 1, r_id, len(done_pld), sum(done_pld)&0xffffffff, 0x45545257^0xffffffff) + done_pld)
    recv_pkt(s)
    s.close()
    print(f"\n{GREEN}✔ File transfer complete.{RESET}")

    pkg_type = "tpk" if wgt_path.lower().endswith(".tpk") else "wgt"
    print(f"Installing {pkg_type.upper()} on TV...")
    r1 = run_tv_shell(tv_ip, f"0 vd_appinstall {final_app_id} {remote_wgt}")
    r2 = run_tv_shell(tv_ip, f"0 pkgcmd -i -t {pkg_type} -p {remote_wgt}")

    if r1: print(f"TV Log (vd_appinstall): {r1}")
    if r2: print(f"TV Log (pkgcmd): {r2}")

    print("Launching app on TV...")
    r3 = run_tv_shell(tv_ip, f"0 app_launcher -s {final_app_id}")
    if r3: print(f"TV Log (app_launcher): {r3}")

    if "failed" in (r1 + r2).lower():
        print(f"\n{RED}❌ Installation failed on TV.{RESET}")
        explain_tv_error(r1 + " " + r2)
        return False
    else:
        print(f"\n{GREEN}{BOLD}🎉 SUCCESS: App installed and launched on TV!{RESET}")
        return True

def menu_sideload_local(tv_ip):
    # Scan both current directory and Android phone Downloads folder
    search_dirs = ["/storage/emulated/0/Download/Samsung-T-Sideload", "/sdcard/Download/Samsung-T-Sideload", ".", "/sdcard/Download", os.path.expanduser("~/storage/downloads")]
    found_files = []

    for d in search_dirs:
        if os.path.exists(d):
            try:
                for f in os.listdir(d):
                    if f.endswith(".wgt") or f.endswith(".tpk"):
                        full_p = os.path.join(d, f)
                        if full_p not in [x[0] for x in found_files]:
                            found_files.append((full_p, f, d))
            except Exception:
                pass

    if not found_files:
        print(f"\n{YELLOW}No .wgt or .tpk files found!{RESET}")
        print("Tip: Download any .wgt file in your browser, it will appear here automatically.")
        input("\nPress Enter to return to menu...")
        return

    print(f"\n{BOLD}Found packages on phone:{RESET}")
    for idx, (full_path, fname, origin) in enumerate(found_files, 1):
        _, signed = get_wgt_metadata(full_path)
        status = f"{GREEN}Signed ✔{RESET}" if signed else f"{RED}Unsigned ✖{RESET}"
        loc_str = "Samsung-T-Sideload" if "Samsung-T-Sideload" in origin else ("Downloads" if "Download" in origin else "Current folder")
        print(f" [{idx.rjust(2)}] {fname} ({status}) [{loc_str}]")

    choice = input(f"\nSelect file [1-{len(found_files)}] or 0 to cancel: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(found_files):
        target_path = found_files[int(choice)-1][0]
        stream_and_install_wgt(tv_ip, target_path)
    input("\nPress Enter to continue...")

def menu_download_app(tv_ip):
    tv_info = get_tv_details(tv_ip)
    tv_ver_str = tv_info.get("tizen", "6.0")
    try:
        found = re.findall(r"\d+\.\d+", tv_ver_str)
        tv_ver = float(found[0]) if found else 6.0
    except Exception:
        tv_ver = 6.0

    print(f"\n{BOLD}=== Pre-signed Community App Store ==={RESET}")
    print(f" Connected TV OS: {CYAN}Tizen {tv_ver_str}{RESET}")
    categories = ["Framework", "Streaming", "Media", "Gaming", "Utilities"]
    for cat in categories:
        print(f"\n{CYAN}--- {cat} ---{RESET}")
        for k, v in COMMUNITY_APPS.items():
            if v.get("cat") == cat:
                min_req = float(v.get("min_tizen", "4.0"))
                compat_tag = f"{GREEN}[Compatible ✔]{RESET}" if tv_ver >= min_req else f"{RED}[Incompatible ✖ (Needs Tizen {min_req}+)]{RESET}"
                print(f" [{k.rjust(2)}] {v['name'].ljust(34)} {CYAN}{v.get('ver', '').ljust(8)}{RESET} {compat_tag}")

    print(f"\n [15] {YELLOW}🌐 Browse All Community Apps (50+ Packages Archive)...{RESET}")
    choice = input(f"\nSelect app [1-15] or 0 to cancel: ").strip()
    if choice == "15":
        menu_browse_all_upstream(tv_ip)
        return
    elif choice in COMMUNITY_APPS:
        app = COMMUNITY_APPS[choice]
        min_req = float(app.get("min_tizen", "4.0"))
        if tv_ver < min_req:
            print(f"\n{YELLOW}⚠️  Warning: This app requires Tizen {min_req}+, but your TV is Tizen {tv_ver_str}.{RESET}")
            c_anyway = input("Do you still want to attempt install? [y/N]: ").strip().lower()
            if c_anyway != "y":
                return

        wgt_file = app["file"]
        base_url = "https://github.com/Apps2Samsung/tizen-community-packages/releases/download/community-611/"
        download_url = app.get("url", base_url + wgt_file)

        if not os.path.exists(wgt_file):
            print(f"Downloading {app['name']}...")
            try:
                urllib.request.urlretrieve(download_url, wgt_file)
                print(f"{GREEN}✔ Download complete!{RESET}")
            except Exception as e:
                print(f"{RED}Download failed: {e}{RESET}")
                input("\nPress Enter to return...")
                return
        stream_and_install_wgt(tv_ip, wgt_file, app.get("app_id"))
    input("\nPress Enter to continue...")

def menu_list_installed_apps(tv_ip):
    print(f"\n{CYAN}Querying installed apps from TV...{RESET}")
    res = run_tv_shell(tv_ip, "0 app_launcher --list || 0 pkgcmd -l")
    if not res or "failed" in res.lower() or "connection failed" in res.lower():
        print(f"{RED}Could not retrieve app list from TV ({res}){RESET}")
    else:
        print(f"\n{BOLD}Installed Apps on TV:{RESET}")
        print("-" * 50)
        lines = [l.strip() for l in res.splitlines() if l.strip()]
        for idx, line in enumerate(lines, 1):
            print(f" [{str(idx).rjust(2)}] {line}")
        print("-" * 50)
    input("\nPress Enter to continue...")


def menu_uninstall_app(tv_ip):
    print(f"\n{CYAN}Querying installed packages & usage activity from TV...{RESET}")
    # Query app list and access timestamps of app data directories
    res = run_tv_shell(tv_ip, "0 app_launcher --list || 0 pkgcmd -l")
    time_res = run_tv_shell(tv_ip, "0 ls -lut /opt/usr/apps /home/owner/apps_data 2>/dev/null || true")

    if not res or "failed" in res.lower():
        app_id = input("\\nEnter App ID to uninstall: ").strip()
        if app_id:
            print(f"Uninstalling {app_id}...")
            r = run_tv_shell(tv_ip, f"0 pkgcmd -u -t wgt -q {app_id}; 0 pkgcmd -u -t tpk -q {app_id}")
            print(f"TV Response: {r}")
        input("\\nPress Enter to continue...")
        return

    raw_lines = [l.strip() for l in res.splitlines() if l.strip() and not l.startswith("Connection failed")]
    apps = []
    for l in raw_lines:
        app_clean = l.split()[0] if l.split() else l
        if app_clean not in apps:
            apps.append(app_clean)

    if not apps:
        print(f"{YELLOW}No apps found on TV.{RESET}")
        input("\\nPress Enter to continue...")
        return

    # Parse usage order (least recently used first)
    # ls -lut lists by access time; we reverse or sort so oldest accessed are at the top
    recent_order = []
    for line in time_res.splitlines():
        parts = line.split()
        if parts:
            fname = parts[-1]
            for a in apps:
                if (fname in a or a in fname) and a not in recent_order:
                    recent_order.append(a)

    # Apps not recently opened go to the very top (least used), then sorted by oldest access
    least_used_first = [a for a in apps if a not in recent_order] + list(reversed(recent_order))

    print(f"\n{BOLD}Select app to uninstall (Sorted: Least Used ➔ Frequently Used):{RESET}")
    print("-" * 65)
    for idx, a in enumerate(least_used_first, 1):
        tag = f"{YELLOW}[Least Used]{RESET}" if idx <= max(1, len(least_used_first)//3) else f"{CYAN}[Active]{RESET}"
        print(f" [{str(idx).rjust(2)}] {a.ljust(38)} {tag}")
    print("-" * 65)

    choice = input(f"\\nEnter number [1-{len(least_used_first)}] or 0 to cancel: ").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(least_used_first):
        target_app = least_used_first[int(choice)-1]
        confirm = input(f"{RED}Are you sure you want to uninstall {target_app}? [y/N]: {RESET}").strip().lower()
        if confirm == "y":
            print(f"Uninstalling {target_app}...")
            out = run_tv_shell(tv_ip, f"0 pkgcmd -u -t wgt -q {target_app}; 0 pkgcmd -u -t tpk -q {target_app}")
            print(f"{GREEN}TV Log: {out}{RESET}")
    input("\\nPress Enter to continue...")

def main():
    # If direct CLI args were given: python3 install.py <file.wgt> [tv_ip] [app_id]
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    if len(args) > 0:
        file_arg = args[0]
        tv_ip = args[1] if len(args) > 1 else get_saved_tv_ip()
        app_id = args[2] if len(args) > 2 else None
        stream_and_install_wgt(tv_ip, file_arg, app_id)
        return

    # Interactive TUI Mode
    tv_ip = get_saved_tv_ip()

    while True:
        is_online = check_tv_online(tv_ip)
        status_str = f"{GREEN}● ONLINE{RESET}" if is_online else f"{RED}✖ OFFLINE{RESET}"

        tv_details = get_tv_details(tv_ip) if is_online else {}
        model_name = tv_details.get("model", "Samsung Smart TV")
        tizen_ver = tv_details.get("tizen", "Unknown")
        duid = tv_details.get("duid", "")

        update_status = get_git_update_status()

        print("\n" + "=" * 60)
        print(f"{BOLD}    📺  Tizen Sideload Manager v{SCRIPT_VERSION} (Termux TUI)     {RESET}")
        print("=" * 60)
        print(f" Version  : v{SCRIPT_VERSION} [{update_status}]")
        print(f" Status   : [{status_str}]")
        print(f" TV IP    : {CYAN}{tv_ip}:26101{RESET}")
        if is_online:
            print(f" Model    : {YELLOW}{model_name}{RESET} (Tizen {tizen_ver})")
            storage_info = tv_details.get("storage")
            if storage_info:
                print(f" Storage  : {GREEN}{storage_info}{RESET}")
            if duid:
                print(f" DUID     : {CYAN}{duid}{RESET}")
        print("-" * 60)
        print(" [1] 🚀 Sideload a Local .wgt file")
        print(" [2] 📥 Download & Sideload Pre-signed Apps (TizenBrew/Jellyfin/VLC)")
        print(" [3] ⚙️  Change TV IP Address")
        print(" [4] 📋 Show Installed Apps on TV")
        print(" [5] 🗑️  Uninstall an App from TV")
        print(" [u] ⚡ Check for Script Updates (git pull)")
        print(" [r] 🔄 Refresh (Re-scan files & TV status)")
        print(" [6] 🚪 Exit")
        print("=" * 60)

        choice = input("Select an option [1-5 or r]: ").strip().lower()

        if choice == "1":
            menu_sideload_local(tv_ip)
        elif choice == "2":
            menu_download_app(tv_ip)
        elif choice == "3":
            print(f"\n [1] 🔍 Auto-Scan Wi-Fi Subnet for TV")
            print(f" [2] ✍️  Manually Type IP Address")
            sub_c = input("Choose [1-2]: ").strip()
            if sub_c == "1":
                detected = scan_network_for_tv()
                if detected:
                    tv_ip = detected
                    save_tv_ip(tv_ip)
                    print(f"{GREEN}✔ Connected and saved TV IP: {tv_ip}{RESET}")
            else:
                new_ip = input(f"Enter new TV IP Address [current: {tv_ip}]: ").strip()
                if new_ip:
                    tv_ip = new_ip
                    save_tv_ip(tv_ip)
                    print(f"{GREEN}✔ Saved TV IP: {tv_ip}{RESET}")
        elif choice == "4":
            menu_list_installed_apps(tv_ip)
        elif choice == "5":
            menu_uninstall_app(tv_ip)
        elif choice == "u":
            print(f"\n{CYAN}Checking for updates from GitHub...{RESET}")
            import subprocess
            res = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True)
            print(res.stdout if res.stdout else res.stderr)
            input("\nPress Enter to reload...")
            continue
        elif choice == "r":
            continue
        elif choice == "6":
            print("Goodbye!")
            break
        else:
            print(f"{RED}Invalid selection!{RESET}")

if __name__ == "__main__":
    main()
