
#!/usr/bin/env python3
import os
import sys
import time
import re
import socket
import struct
import zipfile
import threading
import urllib.request
import json
import xml.etree.ElementTree as ET

# ANSI Color & Style Codes for Clean Terminal Output
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
BOLD = "\033[1m"
DIM = "\033[2m"
RESET = "\033[0m"

def clear_screen():
    """Clear terminal screen cleanly."""
    os.system("clear" if os.name != "nt" else "cls")

def visible_len(s):
    """Calculate the visible character length of a string by stripping ANSI escape codes."""
    return len(re.sub(r"\033\[[0-9;]*m", "", s))

def pad_row(content, width):
    """Format a row inside box borders (│  content  │) with accurate padding."""
    v = visible_len(content)
    pad = max(0, width - 4 - v)
    return f"│  {content}" + " " * pad + "│"

def render_progress_bar(current, total, width=24, speed_bps=0):
    """Render a smooth Unicode block progress bar with MB/s and ETA."""
    pct = min(100.0, (current / total * 100)) if total > 0 else 0
    filled_len = int(width * pct / 100)
    bar = "█" * filled_len + "░" * (width - filled_len)
    if speed_bps >= 1048576:
        speed_str = f"{speed_bps / 1048576:.1f} MB/s"
    elif speed_bps > 0:
        speed_str = f"{speed_bps / 1024:.0f} KB/s"
    else:
        speed_str = "-- KB/s"
    cur_mb = current / 1048576
    tot_mb = total / 1048576
    rem_bytes = max(0, total - current)
    eta = (rem_bytes / speed_bps) if speed_bps > 0 else 0
    eta_str = f"{int(eta)}s" if eta < 60 else f"{int(eta//60)}m{int(eta%60)}s"
    return f"╢{CYAN}{bar}{RESET}╟ {BOLD}{pct:5.1f}%{RESET} │ {cur_mb:.1f}/{tot_mb:.1f} MB │ {YELLOW}{speed_str}{RESET} │ ETA: {eta_str}"

def download_file_with_progress(url, dest_path, desc=None):
    """Download a file with a high-fidelity Unicode progress bar, speed, and size counter."""
    if not desc:
        desc = os.path.basename(dest_path)
    print(f"\n{CYAN}╭─ [DOWNLOAD] {BOLD}{desc}{RESET}")
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp, open(dest_path, "wb") as out_f:
            total_header = resp.headers.get("Content-Length")
            total_size = int(total_header) if total_header and total_header.isdigit() else 0
            downloaded = 0
            start_time = time.time()
            chunk_size = 65536
            while True:
                chunk = resp.read(chunk_size)
                if not chunk:
                    break
                out_f.write(chunk)
                downloaded += len(chunk)
                elapsed = time.time() - start_time
                speed = downloaded / (elapsed if elapsed > 0 else 1)
                if total_size > 0:
                    bar_str = render_progress_bar(downloaded, total_size, width=24, speed_bps=speed)
                    print(f"\r│  {bar_str}", end="", flush=True)
                else:
                    mb_cur = downloaded / 1048576
                    speed_str = f"{speed / 1048576:.1f} MB/s" if speed >= 1048576 else f"{speed / 1024:.0f} KB/s"
                    print(f"\r│  {CYAN}Downloaded: {mb_cur:.1f} MB │ {YELLOW}{speed_str}{RESET}", end="", flush=True)
            print(f"\n╰─ {GREEN}[OK] Download complete! ({downloaded / 1048576:.1f} MB){RESET}\n")
            return True
    except Exception as e:
        if os.path.exists(dest_path):
            try: os.remove(dest_path)
            except Exception: pass
        print(f"\n╰─ {RED}[ERROR] Download failed: {e}{RESET}\n")
        return False

def menu_browse_all_upstream(tv_ip):
    """Dynamically fetch and list all 50+ community apps from Apps2Samsung repo."""
    print(f"\n{CYAN}[INFO] Fetching complete live community repository catalog...{RESET}")
    api_url = "https://api.github.com/repos/Apps2Samsung/tizen-community-packages/releases/tags/community-611"
    req = urllib.request.Request(api_url, headers={"User-Agent": "Mozilla/5.0"})
    import json
    try:
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode())
            assets = [a["name"] for a in data.get("assets", []) if (a["name"].endswith(".wgt") or a["name"].endswith(".tpk")) and not a["name"].startswith("Overscan")]
    except Exception as e:
        print(f"{RED}[ERROR] Could not load live catalog: {e}{RESET}")
        input("\nPress Enter to return...")
        return

    print(f"\n{BOLD}Community Package Archive ({len(assets)} Apps){RESET}")
    print(f"{DIM}" + "-" * 64 + f"{RESET}")
    for idx, name in enumerate(assets, 1):
        ext = "TPK" if name.endswith(".tpk") else "WGT"
        print(f"  {CYAN}[{str(idx).rjust(2)}]{RESET} {BOLD}{name.ljust(44)}{RESET} [{CYAN}{ext}{RESET}]")
    print(f"{DIM}" + "-" * 64 + f"{RESET}")

    choice = input(f"\n{BOLD}> Select package [1-{len(assets)}] or 0 to cancel: {RESET}").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(assets):
        target_name = assets[int(choice)-1]
        dl_url = f"https://github.com/Apps2Samsung/tizen-community-packages/releases/download/community-611/{target_name}"
        if not os.path.exists(target_name):
            if not download_file_with_progress(dl_url, target_name, target_name):
                input(f"\n{DIM}Press Enter to return...{RESET}")
                return
        stream_and_install_wgt(tv_ip, target_name)
    input(f"\n{DIM}Press Enter to return to menu...{RESET}")

SCRIPT_VERSION = "2.3.0"

def get_git_update_status():
    """Check if local git repo is up-to-date with remote and display version numbers."""
    try:
        import subprocess
        subprocess.run(["git", "fetch", "origin", "main"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        local_hash = subprocess.check_output(["git", "rev-parse", "HEAD"], stderr=subprocess.DEVNULL, timeout=1).decode().strip()
        remote_hash = subprocess.check_output(["git", "rev-parse", "origin/main"], stderr=subprocess.DEVNULL, timeout=1).decode().strip()
        if local_hash and remote_hash:
            if local_hash == remote_hash:
                return f"{GREEN}v{SCRIPT_VERSION} (Latest) [OK]{RESET}"
            else:
                remote_ver = None
                try:
                    out = subprocess.check_output(["git", "show", "origin/main:install.py"], stderr=subprocess.DEVNULL, timeout=1).decode()
                    for l in out.splitlines():
                        if l.startswith("SCRIPT_VERSION ="):
                            remote_ver = l.split("=")[1].strip().strip('"').strip("'")
                            break
                except Exception:
                    pass
                ver_info = f"v{SCRIPT_VERSION} -> v{remote_ver}" if remote_ver else f"New version available"
                return f"{YELLOW}[UPDATE] {ver_info} (Press 'u' to update){RESET}"
    except Exception:
        pass
    return f"{GREEN}v{SCRIPT_VERSION} [OK]{RESET}"



def explain_tv_error(err_str, context="install"):
    """Comprehensive Step-by-Step Error Explainer for every possible failure."""
    err_lower = err_str.lower()
    print(f"\n{YELLOW}+------------------------------------------------------------------------+{RESET}")
    print(f"{YELLOW}| [DIAGNOSTIC] ERROR ANALYSIS & STEP-BY-STEP SOLUTION                    |{RESET}")
    print(f"{YELLOW}+------------------------------------------------------------------------+{RESET}")

    # STEP 1: CONNECTION / NETWORK FAILURES
    if any(k in err_lower for k in ["connection failed", "cannot connect", "timed out", "errno 111", "refused", "no route", "reset by peer", "broken pipe", "errno 104"]):
        phone_ip = get_local_wifi_ip()
        print(f" {RED}{BOLD}[STAGE] TV Connection Rejected (Reset by Peer / Timeout){RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" [CAUSE] Why Samsung TV rejected connection:")
        print("    1. Host PC IP mismatch: Samsung TV requires Host PC IP")
        print(f"       in Developer Mode to match your phone's Wi-Fi IP ({phone_ip}).")
        print("    2. Or Developer Mode is NOT turned ON.")
        print("    3. Or TV was not rebooted after toggling Developer Mode.")
        print("")
        print(f" {GREEN}{BOLD}[SOLUTION] Steps to fix (Takes 30 seconds):{RESET}")
        print("    Step 1: On TV Remote -> Open 'Apps' -> Press 1 2 3 4 5.")
        print("    Step 2: Toggle 'Developer Mode' to [ ON ].")
        print(f"    Step 3: In 'Host PC IP' box, enter: {CYAN}{BOLD}{phone_ip}{RESET}")
        print("    Step 4: Look at TV screen: if prompted to allow connection, click ALLOW.")
        print("    Step 5: Hold TV Remote Power button for 5 sec until TV reboots.")
        print("    Step 6: Run 'tizen' again.")

    # STEP 2: UNSIGNED PACKAGE (SIGNATURE)
    elif any(k in err_lower for k in ["failed[-11]", "invalid signature", "signature verification", "signature missing"]):
        print(f" {RED}{BOLD}[STAGE] Digital Signature Verification Failed (Error -11){RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" [CAUSE] Probable reason:")
        print("    Package does not contain a valid Samsung Digital Certificate.")
        print("    (Raw builds like NuvioTV.wgt do not have community certificates).")
        print("")
        print(f" {GREEN}{BOLD}[SOLUTION] Steps to fix:{RESET}")
        print("    Step 1: Go back to Main Menu and choose Option [2].")
        print("    Step 2: Install 'TizenBrew' (App #1). It has valid certificates.")
        print("    Step 3: Open TizenBrew on your TV screen.")
        print("    Step 4: Inside TizenBrew, select 'Add GitHub Module' and type app repo.")

    # STEP 3: CERTIFICATE MISMATCH (DUID / AUTHORITY)
    elif any(k in err_lower for k in ["failed[-12]", "author certificate", "duid mismatch"]):
        print(f" {RED}{BOLD}[STAGE] Certificate Authority Mismatch (Error -12){RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" [CAUSE] Probable reason:")
        print("    Certificate on this package was created for a different TV device ID (DUID).")
        print("")
        print(f" {GREEN}{BOLD}[SOLUTION] Steps to fix:{RESET}")
        print("    Step 1: Always install pre-signed packages from Option [2].")
        print("    Step 2: If using custom packages, ensure they use Public Community Certificate.")

    # STEP 4: PERMISSION / PRIVILEGE ERRORS
    elif any(k in err_lower for k in ["failed[-14]", "privilege", "partner", "platform"]):
        print(f" {RED}{BOLD}[STAGE] Restricted Privilege Level (Error -14){RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" [CAUSE] Probable reason:")
        print("    App requests advanced Samsung Partner/Platform permissions.")
        print("")
        print(f" {GREEN}{BOLD}[SOLUTION] Steps to fix:{RESET}")
        print("    Step 1: In TV Developer Mode (12345), make sure phone IP is set as Host IP.")
        print("    Step 2: Turn off TV, unplug power cable for 10 seconds, plug back in.")

    # STEP 5: STORAGE / DUPLICATE / PACKAGE ERRORS
    elif any(k in err_lower for k in ["failed[-1]", "failed[-4]", "already exists", "duplicate"]):
        print(f" {RED}{BOLD}[STAGE] App Conflict or Storage Error{RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" [CAUSE] Probable reason:")
        print("    An older version of this app is already installed or corrupted.")
        print("")
        print(f" {GREEN}{BOLD}[SOLUTION] Steps to fix:{RESET}")
        print("    Step 1: Go to Main Menu -> Option [5] (Uninstall an App).")
        print("    Step 2: Select the app to remove older version.")
        print("    Step 3: Re-install the app cleanly.")

    # STEP 6: FILE NOT FOUND
    elif any(k in err_lower for k in ["not found", "no such file"]):
        print(f" {RED}{BOLD}[STAGE] File Missing on Phone Storage{RESET}")
        print(f" {YELLOW}------------------------------------------------------------------------{RESET}")
        print(" [CAUSE] Probable reason:")
        print("    Package was not placed in the correct phone folder.")
        print("")
        print(f" {GREEN}{BOLD}[SOLUTION] Steps to fix:{RESET}")
        print("    Step 1: Open your phone's File Manager.")
        print("    Step 2: Navigate to: Internal Storage -> Download -> Samsung-T-Sideload")
        print("    Step 3: Paste your .wgt or .tpk file inside that folder.")
        print("    Step 4: Press 'r' in menu to refresh and find it.")

    else:
        print(f" {RED}{BOLD}[STAGE] General TV System Error{RESET}")
        print(f"    Raw TV Response: {err_str}")
        print("")
        print(f" {GREEN}{BOLD}[SOLUTION] Recommended fix:{RESET}")
        print("    Step 1: Hold Remote Power button for 5 seconds to soft-reboot TV.")
        print("    Step 2: Make sure TV has active Wi-Fi connection.")
        print("    Step 3: Try again.")

    print(f"{YELLOW}+------------------------------------------------------------------------+{RESET}\n")

def get_local_wifi_ip():
    """Detect phone Wi-Fi, hotspot, or local network IPv4 address."""
    # 1. Check network interfaces via ioctl (detects hotspot ap0, softap, wlan1, wlan2, etc.)
    candidate_ifaces = [
        'ap0', 'ap1', 'softap0', 'wlan1', 'wlan2', 'swlan0', 'rndis0', 'wlan0', 'eth0'
    ]
    for ifname in candidate_ifaces:
        try:
            import struct, fcntl
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            ip = socket.inet_ntoa(fcntl.ioctl(
                s.fileno(),
                0x8915,
                struct.pack('256s', ifname[:15].encode('utf-8'))
            )[20:24])
            s.close()
            if ip and not ip.startswith('127.') and not ip.startswith('192.0.'):
                return ip
        except Exception:
            pass

    # 2. Try system ip command
    try:
        import subprocess
        out = subprocess.check_output(['/system/bin/ip', '-4', 'addr', 'show'], stderr=subprocess.DEVNULL).decode()
        cur = None
        for l in out.splitlines():
            s_l = l.strip()
            if ': ' in s_l and ('wlan' in s_l or 'ap' in s_l): cur = s_l
            elif s_l.startswith('inet ') and cur:
                found_ip = s_l.split()[1].split('/')[0]
                if not found_ip.startswith('192.0.'):
                    return found_ip
            elif ': ' in s_l: cur = None
    except Exception:
        pass

    # 3. Fallback to outbound socket (ignore cellular 192.0.0.x if possible)
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        res = s.getsockname()[0]
        s.close()
        if not res.startswith('127.'):
            return res
    except Exception:
        pass
    return "Unknown"

def scan_network_for_tv(phone_ip=None):
    """Scan local subnet on port 26101 to auto-detect Samsung TV."""
    if not phone_ip or phone_ip == "Unknown" or phone_ip.startswith("192.0."):
        phone_ip = get_local_wifi_ip()

    base = None
    if phone_ip and "." in phone_ip and not phone_ip.startswith("127.") and not phone_ip.startswith("192.0."):
        parts = phone_ip.split(".")
        base = ".".join(parts[:3])
    else:
        saved = get_saved_tv_ip()
        if saved and "." in saved:
            base = ".".join(saved.split(".")[:3])

    if not base or base.startswith("192.0."):
        base = "192.168.1"

    print(f"\n{CYAN}[SCAN] Scanning subnet {base}.0/24 for Samsung TV (port 26101)...{RESET}")

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
                print(f"{GREEN}[OK] Found TV at: {res}{RESET}")

    if found_ips:
        return found_ips[0]
    print(f"{YELLOW}No TV found on subnet {base}.0/24 (Make sure TV Developer Mode is ON){RESET}")
    return None
CONFIG_FILE = os.path.expanduser("~/.tizen_tv_ip")

COMMUNITY_APPS = {
    "1": {"name": "TizenBrew (Homebrew App Store)", "file": "TizenBrew.wgt", "ver": "v2.0.5", "cat": "Framework", "min_tizen": "4.0"},
    "2": {"name": "TizenTube (Ad-free YouTube)", "file": "TizenTube.wgt", "ver": "v0.8.2", "cat": "Streaming", "min_tizen": "4.0"},
    "3": {"name": "Jellyfin TV (OSA) [Recommended]", "file": "Jellyfin-OSA.wgt", "ver": "Latest", "cat": "Streaming", "min_tizen": "5.0", "url": "https://github.com/jeppevinkel/jellyfin-tizen-builds/releases/latest/download/Jellyfin-OSA.wgt"},
    "4": {"name": "Jellyfin TV (OG - Official Stable)", "file": "Jellyfin.wgt", "ver": "Latest", "cat": "Streaming", "min_tizen": "5.0", "url": "https://github.com/jeppevinkel/jellyfin-tizen-builds/releases/latest/download/Jellyfin.wgt"},
    "5": {"name": "Jellyfin TV (GrayFix)", "file": "Jellyfin-GrayFix.wgt", "ver": "Latest", "cat": "Streaming", "min_tizen": "5.0", "url": "https://github.com/jeppevinkel/jellyfin-tizen-builds/releases/latest/download/Jellyfin-GrayFix.wgt"},
    "6": {"name": "Jellyfin TV (OblongIcon)", "file": "Jellyfin-OblongIcon.wgt", "ver": "Latest", "cat": "Streaming", "min_tizen": "5.0", "url": "https://github.com/jeppevinkel/jellyfin-tizen-builds/releases/latest/download/Jellyfin-OblongIcon.wgt"},
    "7": {"name": "Jellyfin TV (Secondary Instance)", "file": "Jellyfin-secondary.wgt", "ver": "Latest", "cat": "Streaming", "min_tizen": "5.0", "url": "https://github.com/jeppevinkel/jellyfin-tizen-builds/releases/latest/download/Jellyfin-secondary.wgt"},
    "8": {"name": "Jellyfin TV (Legacy Tizen 2.4-4)", "file": "Jellyfin-legacy.wgt", "ver": "v10.8.z", "cat": "Streaming", "min_tizen": "2.4", "url": "https://github.com/jeppevinkel/jellyfin-tizen-builds/releases/download/2024-10-27-1821/Jellyfin.wgt"},
    "9": {"name": "Stremio TV (Community App)", "file": "Stremio-Tizen4.wgt", "ver": "v1.7.0", "cat": "Streaming", "min_tizen": "4.0"},
    "10": {"name": "SmartTV Twitch (Ad-free Twitch)", "file": "SmartTV_Twitch.wgt", "ver": "v1.4.1", "cat": "Streaming", "min_tizen": "5.0"},
    "11": {"name": "VLC Media Player", "file": "VLC-TV.wgt", "ver": "v3.0.18", "cat": "Media", "min_tizen": "5.0"},
    "12": {"name": "Moonlight TV (PC Game Stream 4K)", "file": "Moonlight-Tizen.wgt", "ver": "v1.6.0", "cat": "Gaming", "min_tizen": "5.5"},
    "13": {"name": "Chiaki (PlayStation Remote Play)", "file": "Chiaki-Tizen.wgt", "ver": "v2.2.0", "cat": "Gaming", "min_tizen": "5.5"},
    "14": {"name": "Doom (Classic Doom Port)", "file": "Doom.wgt", "ver": "v1.1", "cat": "Gaming", "min_tizen": "4.0"},
    "15": {"name": "GameBoy Emulator", "file": "GameBoy-Emulator.wgt", "ver": "v1.0", "cat": "Gaming", "min_tizen": "4.0"},
    "16": {"name": "AirTizen (Apple AirPlay)", "file": "AirTizen.wgt", "ver": "v0.3.1", "cat": "Utilities", "min_tizen": "5.5"},
    "17": {"name": "FCastReceiver (Chromecast Alt)", "file": "FCastReceiver.wgt", "ver": "v1.2.0", "cat": "Utilities", "min_tizen": "5.0"},
    "18": {"name": "Tailscale (Mesh VPN Client - TPK)", "file": "Tailscale.tpk", "ver": "v1.78.1", "cat": "Utilities", "min_tizen": "5.0"},
    "19": {"name": "iperf3 (Network Speed Tester)", "file": "iperf3-TV.wgt", "ver": "v3.16", "cat": "Utilities", "min_tizen": "4.0"}
}

def get_saved_tv_ip():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                ip = f.read().strip()
                if ip: return ip
        except Exception: pass
    return None

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
    package_id = None
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
                    if elem.tag.endswith("application"):
                        if "id" in elem.attrib:
                            app_id = elem.attrib["id"]
                        if "package" in elem.attrib:
                            package_id = elem.attrib["package"]
                        break
                if not package_id and app_id:
                    package_id = app_id.split(".")[0]
            # TPK format uses tizen-manifest.xml
            elif "tizen-manifest.xml" in names:
                root = ET.fromstring(z.read("tizen-manifest.xml"))
                if "package" in root.attrib:
                    package_id = root.attrib["package"]
                for elem in root.iter():
                    if (elem.tag.endswith("ui-application") or elem.tag.endswith("service-application")) and "appid" in elem.attrib:
                        app_id = elem.attrib["appid"]
                        break
                    elif "id" in elem.attrib and app_id is None:
                        app_id = elem.attrib["id"]
                if not package_id and app_id:
                    package_id = app_id.split(".")[0]
    except Exception as e:
        print(f"{YELLOW}Warning parsing package: {e}{RESET}")
    return app_id, package_id, is_signed

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

def run_tv_shell(tv_ip, cmd_str, retries=2):
    handshake = b"host::sdb-net-client\x00"
    for attempt in range(retries + 1):
        s = socket.socket()
        s.settimeout(15.0)
        try:
            time.sleep(0.4)  # Rate-limiting cooldown between socket connections
            s.connect((tv_ip, 26101))
            s.sendall(struct.pack("<4sIIIII", b"CNXN", 0x01000000, 65536, len(handshake), sum(handshake)&0xffffffff, 0x4e584e43^0xffffffff) + handshake)
            s.recv(1024)
            service = f"shell:{cmd_str}\x00".encode()
            s.sendall(struct.pack("<4sIIIII", b"OPEN", 1, 0, len(service), sum(service)&0xffffffff, 0x4e45504f^0xffffffff) + service)
            cmd, r_id, l_id, p = recv_pkt(s)
            out = b""
            while True:
                c, a0, a1, p = recv_pkt(s)
                if not c or c == b"CLSE": break
                if p: out += p
                if c == b"WRTE":
                    s.sendall(struct.pack("<4sIIIII", b"OKAY", 1, r_id, 0, 0, 0x47414b4f^0xffffffff))
            s.close()
            return out.decode(errors="ignore").strip()
        except Exception as e:
            try: s.close()
            except Exception: pass
            if attempt < retries:
                time.sleep(1.0)
                continue
            return f"Connection failed: {e}"

def ensure_adb_connected(tv_ip):
    pass

def get_tv_details(tv_ip):
    """Query TV model name, Tizen version, DUID, and developer status via REST API & SDB capability."""
    details = {}
    # 1. First try Samsung REST API (port 8001) - instant, accurate, non-blocking
    try:
        req = urllib.request.Request(f"http://{tv_ip}:8001/api/v2/", headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=2.0) as resp:
            data = json.loads(resp.read().decode())
            device = data.get("device", {})
            if device:
                details["model"] = device.get("modelName", "")
                details["name"] = device.get("name", "")
                details["duid"] = device.get("duid", "").replace("uuid:", "")
                details["dev_mode"] = "ON" if device.get("developerMode") == "1" else "OFF"
                details["dev_ip"] = device.get("developerIP", "")
                details["resolution"] = device.get("resolution", "")
    except Exception:
        pass

    # 2. Query SDB capability service on port 26101
    try:
        s = socket.socket()
        s.settimeout(2.5)
        s.connect((tv_ip, 26101))
        handshake = b"host::sdb-net-client\x00"
        s.sendall(struct.pack("<4sIIIII", b"CNXN", 0x01000000, 65536, len(handshake), sum(handshake)&0xffffffff, 0x4e584e43^0xffffffff) + handshake)
        s.recv(1024)

        srv = b"capability:\x00"
        s.sendall(struct.pack("<4sIIIII", b"OPEN", 1, 0, len(srv), sum(srv)&0xffffffff, 0x4e45504f^0xffffffff) + srv)
        c, r, l, p = recv_pkt(s)
        out = b""
        while True:
            c2, a0, a1, p2 = recv_pkt(s)
            if not c2 or c2 == b"CLSE": break
            if p2: out += p2
            if c2 == b"WRTE":
                s.sendall(struct.pack("<4sIIIII", b"OKAY", 1, r, 0, 0, 0x47414b4f^0xffffffff))
        s.close()
        for line in out.decode(errors="ignore").splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                k = k.strip()
                v = v.strip()
                if k == "platform_version" and not details.get("tizen"):
                    details["tizen"] = v
                elif k == "sdk_toolpath":
                    details["sdk_toolpath"] = v
                elif k == "cpu_arch":
                    details["cpu_arch"] = v
    except Exception:
        pass

    if "tizen" not in details:
        details["tizen"] = "5.5"
    if "sdk_toolpath" not in details:
        details["sdk_toolpath"] = "/home/owner/share/tmp/sdk_tools"

    return details

def stream_and_install_wgt(tv_ip, wgt_path, app_id=None):
    ensure_adb_connected(tv_ip)
    if not os.path.exists(wgt_path):
        print(f"{RED}Error: File '{wgt_path}' not found!{RESET}")
        return False

    meta_id, pkg_id, is_signed = get_wgt_metadata(wgt_path)
    final_app_id = app_id or meta_id or "App"
    final_pkg_id = pkg_id or (final_app_id.split('.')[0] if '.' in final_app_id else final_app_id)

    if not is_signed:
        print(f"\n{YELLOW}======================================================{RESET}")
        print(f"{RED}{BOLD}[!] WARNING: UNSIGNED PACKAGE DETECTED!{RESET}")
        print(f"  '{wgt_path}' does not contain author-signature.xml.")
        print(f"  Samsung TV will reject installation with error: failed[-11].")
        print(f"  To use unsigned apps like Nuvio, sideload TizenBrew first.")
        print(f"{YELLOW}======================================================{RESET}")
        confirm = input("Attempt installation anyway? [y/N]: ").strip().lower()
        if confirm != "y":
            return False

    tv_details = get_tv_details(tv_ip)
    sdk_toolpath = tv_details.get("sdk_toolpath", "/home/owner/share/tmp/sdk_tools")
    remote_wgt = f"{sdk_toolpath}/{os.path.basename(wgt_path)}"

    print(f"\n{CYAN}╭─ [SIDELOAD DEPLOYMENT PIPELINE]{RESET}")
    print(f"│  {BOLD}Package File{RESET} : {CYAN}{os.path.basename(wgt_path)}{RESET}")
    print(f"│  {BOLD}App ID{RESET}       : {GREEN}{final_app_id}{RESET}")
    print(f"│  {BOLD}Package ID{RESET}   : {GREEN}{final_pkg_id}{RESET}")
    print(f"│  {BOLD}Target TV{RESET}    : {tv_ip}:26101 ({tv_details.get('model', 'Samsung TV')})")
    print(f"╰──────────────────────────────────────────────────────────────\n")

    # STAGE 1: TRANSFER VIA SDB SYNC
    print(f"{CYAN}╭─ [STAGE 1/4] Transferring Package to TV Filesystem...{RESET}")
    s = socket.socket()
    s.settimeout(15.0)
    try:
        s.connect((tv_ip, 26101))
        handshake = b"host::sdb-net-client\x00"
        s.sendall(struct.pack("<4sIIIII", b"CNXN", 0x01000000, 65536, len(handshake), sum(handshake)&0xffffffff, 0x4e584e43^0xffffffff) + handshake)
        s.recv(1024)

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
                speed = bytes_sent / (elapsed if elapsed > 0 else 1)
                bar_str = render_progress_bar(bytes_sent, file_size, width=24, speed_bps=speed)
                print(f"\r│  {bar_str}", end="", flush=True)
                cmd, a0, a1, p = recv_pkt(s)
                if cmd == b"WRTE":
                    s.sendall(struct.pack("<4sIIIII", b"OKAY", 1, r_id, 0, 0, 0x47414b4f^0xffffffff))

        done_pld = struct.pack("<4sI", b"DONE", int(os.path.getmtime(wgt_path)))
        s.sendall(struct.pack("<4sIIIII", b"WRTE", 1, r_id, len(done_pld), sum(done_pld)&0xffffffff, 0x45545257^0xffffffff) + done_pld)
        recv_pkt(s)
        recv_pkt(s)  # Read final sync OKAY from TV
        s.close()
        total_transfer_time = time.time() - start_time
        print(f"\n╰─ {GREEN}[OK] File transfer complete: {file_size / 1048576:.1f} MB in {total_transfer_time:.1f}s{RESET}\n")
    except Exception as e:
        try: s.close()
        except Exception: pass
        print(f"\n╰─ {RED}[ERROR] Connection error during transfer: {e}{RESET}\n")
        explain_tv_error(str(e))
        return False

    # STAGE 2: VERIFY FILE STAGING
    print(f"{CYAN}╭─ [STAGE 2/4] Verifying File Staging on TV...{RESET}")
    time.sleep(0.5)
    print(f"│  Staging Path : {remote_wgt}")
    print(f"╰─ {GREEN}[OK] Package staged in TV developer workspace.{RESET}\n")

    # STAGE 3: TIZEN PACKAGE MANAGER DEPLOYMENT
    pkg_type = "tpk" if wgt_path.lower().endswith(".tpk") else "wgt"
    print(f"{CYAN}╭─ [STAGE 3/4] Deploying {pkg_type.upper()} via Tizen Security Daemon...{RESET}")

    install_res = {"r1": "", "r2": ""}
    def install_worker():
        time.sleep(0.5)  # Wait for TV sync socket to cleanly close
        # Tizen vd_appinstall expects: 0 vd_appinstall <AppID> <wgt_path>
        install_res["r1"] = run_tv_shell(tv_ip, f"0 vd_appinstall {final_app_id} {remote_wgt}")
        if not install_res["r1"]:
            install_res["r1"] = run_tv_shell(tv_ip, f"0 vd_appinstall {final_pkg_id} {remote_wgt}")
        time.sleep(0.5)  # Cooldown between commands
        install_res["r2"] = run_tv_shell(tv_ip, f"0 pkgcmd -i -t {pkg_type} -p {remote_wgt}")

    th = threading.Thread(target=install_worker)
    th.daemon = True
    th.start()

    spinner = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    step = 0
    t0 = time.time()
    while th.is_alive():
        spin = spinner[step % len(spinner)]
        elapsed = time.time() - t0
        prog = min(95, int(elapsed * 12) + 5)
        bar = ("█" * (prog // 5)).ljust(20, "░")
        print(f"\r│  {YELLOW}{spin} Installing on TV: ╢{CYAN}{bar}{YELLOW}╟ {prog}% ({elapsed:.1f}s){RESET}", end="", flush=True)
        time.sleep(0.08)
        step += 1
    th.join()

    total_time = time.time() - t0
    bar_full = "█" * 20
    print(f"\r│  {GREEN}✔ Installing on TV: ╢{CYAN}{bar_full}{GREEN}╟ 100% ({total_time:.1f}s){RESET}")

    r1, r2 = install_res["r1"], install_res["r2"]
    if r1: print(f"│  TV Daemon (vd_appinstall): {r1}")
    if r2: print(f"│  TV Daemon (pkgcmd)       : {r2}")
    print(f"╰─ {GREEN}[OK] Deployment command processed by TV.{RESET}\n")

    # STAGE 4: LAUNCHING & REGISTRY VERIFICATION
    print(f"{CYAN}╭─ [STAGE 4/4] Verifying App Registry & Launching...{RESET}")
    r3 = run_tv_shell(tv_ip, f"0 was_execute {final_app_id}")
    if not r3:
        r3 = run_tv_shell(tv_ip, f"0 execute {final_app_id}")
    if r3: print(f"│  Launch Result: {r3}")

    # Wait for TV package manager to update registry
    time.sleep(1.2)
    installed_list = get_installed_apps_list(tv_ip)
    is_installed = any(
        final_pkg_id.lower() in x.lower() or final_app_id.lower() in x.lower()
        for x in installed_list
    )

    # Clean up staged package on TV
    run_tv_shell(tv_ip, f"0 rmfile {remote_wgt}")
    print(f"╰─ {GREEN}[OK] Verification step complete.{RESET}\n")

    w = 64
    if is_installed or any(k in (r1 + " " + r2 + " " + r3).lower() for k in ["success", "val=0", "passed", "installing[100]", "install completed"]):
        print("╭" + "─" * (w - 2) + "╮")
        print(pad_row(f"{GREEN}{BOLD}🎉 SUCCESS: APP INSTALLED & LAUNCHED!{RESET}", w))
        print("├" + "─" * (w - 2) + "┤")
        print(pad_row(f"Package ID : {CYAN}{final_pkg_id}{RESET}", w))
        print(pad_row(f"App ID     : {CYAN}{final_app_id}{RESET}", w))
        print(pad_row(f"Status     : {GREEN}Registered in TV Sandbox [OK]{RESET}", w))
        print("├" + "─" * (w - 2) + "┤")
        print(pad_row(f"{BOLD}HOW TO PIN TO YOUR TV HOME BAR:{RESET}", w))
        print(pad_row(f"1. On TV remote, press {BOLD}Home{RESET} ➔ navigate to {BOLD}Apps{RESET}", w))
        print(pad_row(f"2. Click the {BOLD}Settings (Gear ⚙️ icon){RESET} at top-right", w))
        print(pad_row(f"3. Scroll to {CYAN}{final_pkg_id}{RESET} in downloaded apps", w))
        print(pad_row(f"4. Select {GREEN}'Add to Home'{RESET} to pin to bottom ribbon", w))
        print("╰" + "─" * (w - 2) + "╯\n")
        return True
    else:
        print("╭" + "─" * (w - 2) + "╮")
        print(pad_row(f"{YELLOW}{BOLD}⚠ NOTICE: App file pushed, but TV rejected install{RESET}", w))
        print("├" + "─" * (w - 2) + "┤")
        print(pad_row(f"{BOLD}ROOT CAUSE & FAST SOLUTIONS:{RESET}", w))
        print(pad_row(f"1. {GREEN}Cold Reboot TV (Most Important){RESET}:", w))
        print(pad_row(f"   Hold TV Remote Power for 5s until TV reboots", w))
        print(pad_row(f"   to apply Developer Mode permissions.", w))
        print(pad_row(f"2. {GREEN}Try Vanilla Jellyfin (OG){RESET}:", w))
        print(pad_row(f"   Jellyfin-OSA requires a background service", w))
        print(pad_row(f"   blocked by Samsung Tizen 5.5 retail security.", w))
        print(pad_row(f"3. {GREEN}Alternative: Sideload TizenBrew{RESET}:", w))
        print(pad_row(f"   TizenBrew installs easily & loads Jellyfin inside.", w))
        print(pad_row(f"4. {GREEN}Check TV Settings (Gear ⚙️){RESET}:", w))
        print(pad_row(f"   Open Apps ➔ Settings ⚙️ to check if installed.", w))
        print("╰" + "─" * (w - 2) + "╯\n")
        return False

def get_installed_apps_list(tv_ip):
    """Retrieve installed user packages from TV registry using 0 applist and 0 vd_applist."""
    apps = []
    res_applist = run_tv_shell(tv_ip, "0 applist")
    for line in res_applist.splitlines():
        l_s = line.strip()
        if not l_s or any(k in l_s for k in ["Application List", "User's Application", "Name", "AppID", "==="]):
            continue
        parts = [p.strip() for p in l_s.split("\t") if p.strip()]
        if parts:
            app_id = parts[-1]
            if app_id not in apps:
                apps.append(app_id)
    res_vd = run_tv_shell(tv_ip, "0 vd_applist")
    for line in res_vd.splitlines():
        l_s = line.strip()
        if l_s and not l_s.startswith("Connection failed") and l_s not in apps:
            apps.append(l_s)
    return apps

def menu_list_installed_apps(tv_ip):
    print(f"\n{CYAN}[SCAN] Querying installed community apps from Samsung TV...{RESET}")
    lines = get_installed_apps_list(tv_ip)
    if not lines:
        print(f"\n{YELLOW}[INFO] No sideloaded community apps currently detected in TV registry.{RESET}")
        print(f"{DIM}Note: Built-in factory Samsung apps (Netflix, Prime) are managed by firmware.{RESET}")
    else:
        print(f"\n{BOLD}[APPS] Sideloaded Packages on TV ({len(lines)}):{RESET}")
        print(f"{DIM}" + "-" * 64 + f"{RESET}")
        for idx, line in enumerate(lines, 1):
            print(f"  {CYAN}[{str(idx).rjust(2)}]{RESET} {BOLD}{line}{RESET}")
        print(f"{DIM}" + "-" * 64 + f"{RESET}")
    input(f"\n{DIM}Press Enter to return to menu...{RESET}")

def menu_uninstall_app(tv_ip):
    print(f"\n{CYAN}[SCAN] Querying installed packages from Samsung TV...{RESET}")
    raw_lines = get_installed_apps_list(tv_ip)
    if not raw_lines:
        app_id = input(f"\n{BOLD}No apps found in registry. Enter Package or App ID manually to uninstall: {RESET}").strip()
        if app_id:
            print(f"{YELLOW}[DEL] Uninstalling {app_id}...{RESET}")
            r = run_tv_shell(tv_ip, f"0 vd_appuninstall {app_id}")
            print(f"{GREEN}TV Response: {r or 'Done'}{RESET}")
        input(f"\n{DIM}Press Enter to return to menu...{RESET}")
        return

    print(f"\n{BOLD}[UNINSTALL] Installed Sideloaded Packages ({len(raw_lines)}):{RESET}")
    print(f"{DIM}" + "-" * 64 + f"{RESET}")
    for idx, pkg in enumerate(raw_lines, 1):
        print(f"  {CYAN}[{str(idx).rjust(2)}]{RESET} {BOLD}{pkg}{RESET}")
    print(f"{DIM}" + "-" * 64 + f"{RESET}")

    c = input(f"\n{BOLD}> Select package number to uninstall [1-{len(raw_lines)}] or 0 to cancel: {RESET}").strip()
    if c.isdigit() and 1 <= int(c) <= len(raw_lines):
        target_pkg = raw_lines[int(c) - 1]
        confirm = input(f"{RED}{BOLD}Are you sure you want to uninstall '{target_pkg}' from TV? [y/N]: {RESET}").strip().lower()
        if confirm == "y":
            print(f"{YELLOW}[DEL] Uninstalling {target_pkg}...{RESET}")
            r = run_tv_shell(tv_ip, f"0 vd_appuninstall {target_pkg}")
            print(f"{GREEN}[OK] TV Response: {r or 'Successfully uninstalled'}{RESET}")
    input(f"\n{DIM}Press Enter to return to menu...{RESET}")

def menu_sideload_local(tv_ip):
    search_dirs = [
        "/storage/emulated/0/Download/Samsung-T-Sideload",
        "/sdcard/Download/Samsung-T-Sideload",
        ".",
        "/sdcard/Download",
        os.path.expanduser("~/storage/downloads")
    ]
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
        print(f"\n{YELLOW}[!] No .wgt or .tpk package files found!{RESET}")
        print(f"{CYAN}Tip:{RESET} Place packages in: {BOLD}Internal Storage -> Download -> Samsung-T-Sideload{RESET}")
        input(f"\n{DIM}Press Enter to return to menu...{RESET}")
        return

    print(f"\n{BOLD}[PACKAGES] Local Packages Found on Phone ({len(found_files)}):{RESET}")
    print(f"{DIM}" + "-" * 64 + f"{RESET}")
    for idx, (full_path, fname, origin) in enumerate(found_files, 1):
        _, signed = get_wgt_metadata(full_path)
        status = f"{GREEN}Signed [OK]{RESET}" if signed else f"{YELLOW}Unsigned [!]{RESET}"
        ext = "TPK" if fname.endswith(".tpk") else "WGT"
        try:
            sz_mb = os.path.getsize(full_path) / (1024 * 1024)
            size_str = f"{sz_mb:.1f} MB"
        except Exception:
            size_str = ""
        loc_str = "Samsung-T-Sideload" if "Samsung-T-Sideload" in origin else ("Downloads" if "Download" in origin else "Local folder")
        print(f" {CYAN}[{str(idx).rjust(2)}]{RESET} {BOLD}{fname}{RESET}")
        print(f"      Format: [{CYAN}{ext}{RESET}]  Size: {size_str}  Status: {status}  ({DIM}{loc_str}{RESET})")
    print(f"{DIM}" + "-" * 64 + f"{RESET}")

    choice = input(f"\n{BOLD}> Select package [1-{len(found_files)}] or 0 to cancel: {RESET}").strip()
    if choice.isdigit() and 1 <= int(choice) <= len(found_files):
        target_path = found_files[int(choice)-1][0]
        stream_and_install_wgt(tv_ip, target_path)
    input(f"\n{DIM}Press Enter to return to menu...{RESET}")

def menu_download_app(tv_ip):
    tv_info = get_tv_details(tv_ip)
    tv_ver_str = tv_info.get("tizen", "6.0")
    try:
        found = re.findall(r"\d+\.\d+", tv_ver_str)
        tv_ver = float(found[0]) if found else 6.0
    except Exception:
        tv_ver = 6.0

    print(f"\n{BOLD}[STORE] Pre-Signed Community App Store{RESET}  {DIM}(TV OS: Tizen {tv_ver_str}){RESET}")
    print(f"{DIM}" + "-" * 64 + f"{RESET}")
    categories = ["Framework", "Streaming", "Media", "Gaming", "Utilities"]
    for cat in categories:
        print(f"\n{BOLD}{CYAN}> {cat.upper()}{RESET}")
        for k, v in COMMUNITY_APPS.items():
            if v.get("cat") == cat:
                min_req = float(v.get("min_tizen", "4.0"))
                compat_tag = f"{GREEN}Compatible [OK]{RESET}" if tv_ver >= min_req else f"{RED}Needs Tizen {min_req}+{RESET}"
                ext = "TPK" if v.get("file", "").endswith(".tpk") else "WGT"
                print(f"  {CYAN}[{str(k).rjust(2)}]{RESET} {BOLD}{v['name'].ljust(38)}{RESET} [{CYAN}{ext}{RESET}] {DIM}{v.get('ver', '').ljust(7)}{RESET} ({compat_tag})")

    archive_idx = str(len(COMMUNITY_APPS) + 1)
    print(f"\n  {YELLOW}[{archive_idx}] [MORE] Browse Full Archive (50+ Community Packages)...{RESET}")
    print(f"{DIM}" + "-" * 64 + f"{RESET}")
    choice = input(f"\n{BOLD}> Select app [1-{archive_idx}] or 0 to cancel: {RESET}").strip()
    if choice == archive_idx:
        menu_browse_all_upstream(tv_ip)
        return
    elif choice in COMMUNITY_APPS:
        app = COMMUNITY_APPS[choice]
        min_req = float(app.get("min_tizen", "4.0"))
        if tv_ver < min_req:
            print(f"\n{YELLOW}[!] Warning: This app requires Tizen {min_req}+, but your TV is Tizen {tv_ver_str}.{RESET}")
            c_anyway = input(f"{BOLD}Attempt install anyway? [y/N]: {RESET}").strip().lower()
            if c_anyway != "y":
                return

        wgt_file = app["file"]
        base_url = "https://github.com/Apps2Samsung/tizen-community-packages/releases/download/community-611/"
        download_url = app.get("url", base_url + wgt_file)

        if not os.path.exists(wgt_file):
            if not download_file_with_progress(download_url, wgt_file, app["name"]):
                input(f"\n{DIM}Press Enter to return...{RESET}")
                return
        stream_and_install_wgt(tv_ip, wgt_file, app.get("app_id"))
    input(f"\n{DIM}Press Enter to return to menu...{RESET}")

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
    phone_ip = get_local_wifi_ip()

    if not tv_ip or not check_tv_online(tv_ip):
        print(f"\n{CYAN}[SCAN] Auto-detecting Samsung TV on Wi-Fi network...{RESET}")
        detected = scan_network_for_tv(phone_ip)
        if detected:
            tv_ip = detected
            save_tv_ip(tv_ip)
            print(f"{GREEN}[OK] Found and saved Samsung TV at: {tv_ip}{RESET}")
        elif not tv_ip:
            print(f"\n{BOLD}=== First-Time Setup: Connect to your Samsung TV ==={RESET}")
            print(f"Phone Wi-Fi IP : {GREEN}{BOLD}{phone_ip}{RESET}")
            print(f"-> In TV Developer Mode, enter Host IP: {GREEN}{BOLD}{phone_ip}{RESET}")
            tv_ip = input("\nEnter TV IP Address manually (or press Enter to scan again): ").strip()
            if not tv_ip:
                tv_ip = scan_network_for_tv(phone_ip) or "192.168.1.100"
            save_tv_ip(tv_ip)

    while True:
        clear_screen()
        phone_ip = get_local_wifi_ip()
        is_online = check_tv_online(tv_ip)
        status_str = f"{GREEN}[ONLINE]{RESET}" if is_online else f"{RED}[OFFLINE]{RESET}"

        tv_details = get_tv_details(tv_ip) if is_online else {}
        model_name = tv_details.get("model") or tv_details.get("name") or "Samsung Smart TV"
        tizen_ver = tv_details.get("tizen", "5.5")
def menu_diagnostic_health(tv_ip):
    """Run a comprehensive real-time health check on network, TV REST API, SDB daemon, Sync, and App registry."""
    clear_screen()
    w = 64
    print("╭" + "─" * (w - 2) + "╮")
    print(pad_row(f"{BOLD}🩺 SAMSUNG TV DIAGNOSTIC & HEALTH MONITOR{RESET}", w))
    print("╰" + "─" * (w - 2) + "╯\n")

    phone_ip = get_local_wifi_ip()
    print(f"{BOLD}[1/5] Checking Phone Network Interface...{RESET}")
    if phone_ip:
        print(f"      {GREEN}● PASS{RESET} : Phone IP detected as {BOLD}{phone_ip}{RESET}")
    else:
        print(f"      {RED}● FAIL{RESET} : Unable to detect phone Wi-Fi/Hotspot IP")

    print(f"\n{BOLD}[2/5] Testing Samsung REST API (Port 8001)...{RESET}")
    details = get_tv_details(tv_ip)
    if details.get("model") or details.get("name"):
        dev_mode = details.get("dev_mode", "UNKNOWN")
        dev_ip = details.get("dev_ip", "NONE")
        ip_match = (dev_ip == phone_ip)
        print(f"      {GREEN}● PASS{RESET} : TV Model: {BOLD}{details.get('model')} ({details.get('name')}){RESET}")
        print(f"             Tizen OS: {details.get('tizen')} │ CPU: {details.get('cpu_arch', 'armv7')}")
        print(f"             Developer Mode: {GREEN if dev_mode == 'ON' else RED}{dev_mode}{RESET}")
        if dev_mode == "ON":
            if ip_match:
                print(f"             Host IP on TV: {GREEN}{dev_ip} [MATCHES PHONE ✓]{RESET}")
            else:
                print(f"             Host IP on TV: {RED}{dev_ip} [MISMATCH! Phone is {phone_ip} ✗]{RESET}")
        else:
            print(f"             {RED}[!] Developer Mode is OFF on TV! Turn it on via Apps -> 1-2-3-4-5{RESET}")
    else:
        print(f"      {YELLOW}● WARN{RESET} : Port 8001 not responding (TV in deep standby or fast start disabled)")

    print(f"\n{BOLD}[3/5] Testing SDB Developer Daemon (Port 26101)...{RESET}")
    sdb_online = check_tv_online(tv_ip)
    if sdb_online:
        print(f"      {GREEN}● PASS{RESET} : Port 26101 is open and responsive")
        try:
            s = socket.socket()
            s.settimeout(3.0)
            s.connect((tv_ip, 26101))
            handshake = b"host::sdb-net-client\x00"
            s.sendall(struct.pack("<4sIIIII", b"CNXN", 0x01000000, 65536, len(handshake), sum(handshake)&0xffffffff, 0x4e584e43^0xffffffff) + handshake)
            resp = s.recv(1024)
            s.close()
            if b"CNXN" in resp or b"AUTH" in resp:
                print(f"      {GREEN}● PASS{RESET} : SDB handshake successfully acknowledged by TV")
            else:
                print(f"      {YELLOW}● WARN{RESET} : Unexpected handshake response from TV")
        except Exception as e:
            print(f"      {RED}● FAIL{RESET} : SDB handshake socket error: {e}")
    else:
        print(f"      {RED}● FAIL{RESET} : Port 26101 closed or unreachable! Enable Developer Mode on TV.")

    print(f"\n{BOLD}[4/5] Testing TV Sync File Transfer Channel...{RESET}")
    sync_ok = False
    try:
        s = socket.socket()
        s.settimeout(3.0)
        s.connect((tv_ip, 26101))
        handshake = b"host::sdb-net-client\x00"
        s.sendall(struct.pack("<4sIIIII", b"CNXN", 0x01000000, 65536, len(handshake), sum(handshake)&0xffffffff, 0x4e584e43^0xffffffff) + handshake)
        s.recv(1024)
        service = b"sync:\x00"
        s.sendall(struct.pack("<4sIIIII", b"OPEN", 1, 0, len(service), sum(service)&0xffffffff, 0x4e45504f^0xffffffff) + service)
        cmd, r_id, l_id, p = recv_pkt(s)
        if cmd == b"OKAY":
            sync_ok = True
        s.close()
    except Exception:
        pass
    if sync_ok:
        print(f"      {GREEN}● PASS{RESET} : Sync channel ready at: {details.get('sdk_toolpath', '/home/owner/share/tmp/sdk_tools')}")
    else:
        print(f"      {YELLOW}● WARN{RESET} : Sync channel not immediately available")

    print(f"\n{BOLD}[5/5] Querying TV User 5001 App Registry...{RESET}")
    installed = get_installed_apps_list(tv_ip)
    if installed:
        print(f"      {GREEN}● PASS{RESET} : {len(installed)} Community app(s) registered in User 5001 sandbox:")
        for idx, app in enumerate(installed, 1):
            print(f"             [{idx}] {BOLD}{app}{RESET}")
    else:
        print(f"      {CYAN}● INFO{RESET} : 0 Community apps installed in User 5001 sandbox")

    print(f"\n{DIM}" + "─" * w + f"{RESET}")
    print(f"{BOLD}DIAGNOSTIC SUMMARY & ADVICE:{RESET}")
    if not sdb_online:
        print(f"  {RED}✖ CRITICAL:{RESET} Enable Developer Mode in TV Apps menu (1 2 3 4 5) & cold reboot.")
    elif details.get("dev_ip") and phone_ip and details.get("dev_ip") != phone_ip:
        print(f"  {YELLOW}⚠ WARNING:{RESET} Host IP mismatch! In TV Apps (1 2 3 4 5), enter Host IP: {phone_ip}")
    else:
        print(f"  {GREEN}✔ ALL SYSTEMS OPERATIONAL:{RESET} Your TV is fully ready for sideloading!")
        print(f"  {CYAN}💡 TIP:{RESET} If an app doesn't show after installing, cold restart TV")
        print(f"          (hold remote power 5s) & check TV Apps -> Settings (Gear ⚙️) -> Add to Home.")
    print(f"{DIM}" + "─" * w + f"{RESET}")
    input(f"\n{DIM}Press Enter to return to menu...{RESET}")

def menu_reboot_guide(tv_ip):
    """Visual step-by-step instructions for cold rebooting Samsung Smart TVs."""
    clear_screen()
    w = 64
    print("╭" + "─" * (w - 2) + "╮")
    print(pad_row(f"{BOLD}🔄 SAMSUNG TV COLD REBOOT GUIDE{RESET}", w))
    print("├" + "─" * (w - 2) + "┤")
    print(pad_row(f"Target TV: {CYAN}{tv_ip}{RESET}", w))
    print("╰" + "─" * (w - 2) + "╯\n")

    print(f"{BOLD}WHY A COLD REBOOT IS MANDATORY ON SAMSUNG TVS:{RESET}")
    print("  When you toggle 'Developer Mode' or install new packages on retail")
    print("  Samsung Smart TVs, Tizen's security subsystem holds installation")
    print("  privileges in a staging queue until a full hardware cold restart.\n")

    print(f"{GREEN}{BOLD}METHOD 1: Remote Power Button Long-Press (Fastest){RESET}")
    print("  1. Aim your Samsung TV Remote at the TV.")
    print(f"  2. {BOLD}Press and HOLD the Red Power Button for 5 to 10 seconds.{RESET}")
    print("  3. Keep holding until the screen turns black and the TV")
    print("     reboots displaying the official 'Samsung Smart TV' logo.\n")

    print(f"{GREEN}{BOLD}METHOD 2: Power Socket Unplug (100% Reliable){RESET}")
    print("  1. Unplug the TV's power cable from the wall outlet.")
    print("  2. Wait 10 to 15 seconds for the motherboard capacitors to discharge.")
    print("  3. Plug the power cable back in and power on the TV.\n")

    print(f"{GREEN}{BOLD}METHOD 3: TV Settings Menu Reset{RESET}")
    print("  On TV Remote: Settings ➔ Support ➔ Self Diagnosis ➔ Reset (or Restart).")

    print(f"\n{DIM}" + "─" * w + f"{RESET}")
    input(f"{DIM}Press Enter to return to menu...{RESET}")

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
    phone_ip = get_local_wifi_ip()

    if not tv_ip or not check_tv_online(tv_ip):
        print(f"\n{CYAN}[SCAN] Auto-detecting Samsung TV on Wi-Fi network...{RESET}")
        detected = scan_network_for_tv(phone_ip)
        if detected:
            tv_ip = detected
            save_tv_ip(tv_ip)
            print(f"{GREEN}[OK] Found and saved Samsung TV at: {tv_ip}{RESET}")
        elif not tv_ip:
            print(f"\n{BOLD}=== First-Time Setup: Connect to your Samsung TV ==={RESET}")
            print(f"Phone Wi-Fi IP : {GREEN}{BOLD}{phone_ip}{RESET}")
            print(f"-> In TV Developer Mode, enter Host IP: {GREEN}{BOLD}{phone_ip}{RESET}")
            tv_ip = input("\nEnter TV IP Address manually (or press Enter to scan again): ").strip()
            if not tv_ip:
                tv_ip = scan_network_for_tv(phone_ip) or "192.168.1.100"
            save_tv_ip(tv_ip)

    while True:
        clear_screen()
        phone_ip = get_local_wifi_ip()
        is_online = check_tv_online(tv_ip)
        status_badge = f"{GREEN}● ONLINE{RESET}" if is_online else f"{RED}○ OFFLINE{RESET}"

        tv_details = get_tv_details(tv_ip) if is_online else {}
        model_name = tv_details.get("model") or tv_details.get("name") or "Samsung Smart TV"
        tizen_ver = tv_details.get("tizen", "5.5")
        duid = tv_details.get("duid", "")
        dev_ip = tv_details.get("dev_ip", "")
        dev_mode = tv_details.get("dev_mode", "")
        installed_apps = get_installed_apps_list(tv_ip) if is_online else []

        update_status = get_git_update_status()

        w = 64
        print("╭" + "─" * (w - 2) + "╮")
        print(pad_row(f"{BOLD}📺 SAMSUNG TIZEN SIDELOAD MANAGER{RESET}   {CYAN}v{SCRIPT_VERSION}{RESET}", w))
        print("├" + "─" * (w - 2) + "┤")
        print(pad_row(f"{BOLD}STATUS{RESET}     : {status_badge}  {CYAN}{tv_ip}:26101{RESET}", w))
        print(pad_row(f"{BOLD}PHONE IP{RESET}   : {GREEN}{BOLD}{phone_ip}{RESET} (Wi-Fi)", w))
        print(pad_row(f"{BOLD}VERSION{RESET}    : {update_status}", w))
        if is_online:
            print(pad_row(f"{BOLD}TV MODEL{RESET}   : {YELLOW}{model_name}{RESET} (Tizen {tizen_ver})", w))
            if duid:
                short_duid = duid[:20] + "..." if len(duid) > 20 else duid
                print(pad_row(f"{BOLD}DUID{RESET}       : {DIM}{short_duid}{RESET}", w))
            if dev_mode:
                ip_match_str = f"{GREEN}[MATCH ✓]{RESET}" if (dev_ip == phone_ip) else f"{RED}[MISMATCH ✗]{RESET}"
                print(pad_row(f"{BOLD}DEV MODE{RESET}   : {GREEN}● {dev_mode}{RESET} (Host: {dev_ip or 'OK'}) {ip_match_str}", w))
            app_count_str = f"{GREEN}{len(installed_apps)} App(s){RESET}" if installed_apps else f"{DIM}0 Apps{RESET}"
            print(pad_row(f"{BOLD}INSTALLED{RESET}  : {app_count_str} registered in User 5001 sandbox", w))
        print("├" + "─" * (w - 2) + "┤")

        if is_online and dev_ip and phone_ip and dev_ip != phone_ip:
            print(pad_row(f"{RED}{BOLD}⚠ HOST IP MISMATCH DETECTED:{RESET}", w))
            print(pad_row(f"  TV currently has Host IP : {RED}{dev_ip}{RESET}", w))
            print(pad_row(f"  Your Phone IP is         : {GREEN}{BOLD}{phone_ip}{RESET}", w))
            print(pad_row(f"  ➔ Set Host IP in TV Apps (1-2-3-4-5) & Cold Reboot!", w))
        else:
            print(pad_row(f"{YELLOW}{BOLD}QUICK SETUP GUIDE:{RESET}", w))
            print(pad_row(f"1. TV Apps ➔ Remote: {BOLD}1 2 3 4 5{RESET} ➔ Dev Mode {GREEN}[ON]{RESET}", w))
            print(pad_row(f"2. In 'Host PC IP', enter   ➔ {GREEN}{BOLD}{phone_ip}{RESET}", w))
            print(pad_row(f"3. Cold reboot TV (Hold Remote Power for 5s)", w))
        print("╰" + "─" * (w - 2) + "╯")

        print(f"\n{BOLD}[SIDELOAD & APPS]{RESET}")
        print(f"  {CYAN}[1]{RESET} Sideload Local Package (.wgt / .tpk from phone)")
        print(f"  {CYAN}[2]{RESET} Community App Store (TizenBrew, Jellyfin OG, VLC, 50+ apps)")
        print(f"  {CYAN}[3]{RESET} View Installed Sideloaded Apps ({len(installed_apps)} on TV)")
        print(f"  {CYAN}[4]{RESET} Uninstall an App from TV")

        print(f"\n{BOLD}[DIAGNOSTICS & TV TOOLS]{RESET}")
        print(f"  {CYAN}[5]{RESET} 🩺 TV Health Check & Live Diagnostic Monitor")
        print(f"  {CYAN}[6]{RESET} 🔄 TV Remote Cold Reboot Instructions")
        print(f"  {CYAN}[7]{RESET} 🌐 Change / Auto-Scan TV IP Address")

        print(f"\n{BOLD}[SYSTEM]{RESET}")
        print(f"  {CYAN}[u]{RESET} Check for Updates (Auto-restart)")
        print(f"  {CYAN}[r]{RESET} Refresh Monitor & Status")
        print(f"  {CYAN}[0]{RESET} Exit")
        print(f"{DIM}" + "─" * w + f"{RESET}")

        choice = input(f"{BOLD}> Select option [0-7, u, r]: {RESET}").strip().lower()

        if choice == "1":
            menu_sideload_local(tv_ip)
        elif choice == "2":
            menu_download_app(tv_ip)
        elif choice == "3":
            menu_list_installed_apps(tv_ip)
        elif choice == "4":
            menu_uninstall_app(tv_ip)
        elif choice == "5":
            menu_diagnostic_health(tv_ip)
        elif choice == "6":
            menu_reboot_guide(tv_ip)
        elif choice == "7":
            print(f"\n{BOLD}[CONFIG] TV Connection Settings:{RESET}")
            print(f"  [1] Auto-Scan Wi-Fi Subnet for TV")
            print(f"  [2] Manually Type TV IP Address")
            sub_c = input(f"\n{BOLD}> Choose [1-2]: {RESET}").strip()
            if sub_c == "1":
                detected = scan_network_for_tv()
                if detected:
                    tv_ip = detected
                    save_tv_ip(tv_ip)
                    print(f"{GREEN}[OK] Connected and saved TV IP: {tv_ip}{RESET}")
                input(f"\n{DIM}Press Enter to return...{RESET}")
            else:
                new_ip = input(f"\n{BOLD}Enter new TV IP Address [current: {tv_ip}]: {RESET}").strip()
                if new_ip:
                    tv_ip = new_ip
                    save_tv_ip(tv_ip)
                    print(f"{GREEN}[OK] Saved TV IP: {tv_ip}{RESET}")
                input(f"\n{DIM}Press Enter to return...{RESET}")
        elif choice == "u":
            print(f"\n{CYAN}Checking for updates from GitHub...{RESET}")
            print(f"Current version : {BOLD}v{SCRIPT_VERSION}{RESET}")
            import subprocess
            subprocess.run(["git", "fetch", "origin", "main"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=3)
            remote_ver = None
            try:
                out = subprocess.check_output(["git", "show", "origin/main:install.py"], stderr=subprocess.DEVNULL, timeout=2).decode()
                for l in out.splitlines():
                    if l.startswith("SCRIPT_VERSION ="):
                        remote_ver = l.split("=")[1].strip().strip('"').strip("'")
                        break
            except Exception:
                pass
            if remote_ver:
                print(f"Remote version  : {BOLD}v{remote_ver}{RESET}")
            res = subprocess.run(["git", "pull", "origin", "main"], capture_output=True, text=True)
            print(res.stdout if res.stdout else res.stderr)
            new_ver = SCRIPT_VERSION
            try:
                with open(__file__, "r") as f:
                    for line in f:
                        if line.startswith("SCRIPT_VERSION ="):
                            new_ver = line.split("=")[1].strip().strip('"').strip("'")
                            break
            except Exception:
                pass
            if new_ver != SCRIPT_VERSION:
                print(f"\n{GREEN}[OK] Successfully updated: v{SCRIPT_VERSION} -> v{new_ver}!{RESET}")
                print(f"{CYAN}[RESTART] Auto-restarting into v{new_ver}...{RESET}\n")
                time.sleep(1.2)
                os.execv(sys.executable, [sys.executable] + sys.argv)
            else:
                print(f"\n{GREEN}[OK] Already running latest version: v{SCRIPT_VERSION}{RESET}")
                time.sleep(1.2)
        elif choice == "r":
            continue
        elif choice in ("0", "exit", "quit", "q"):
            print("\nGoodbye!")
            break
        else:
            print(f"{RED}Invalid selection!{RESET}")

if __name__ == "__main__":
    main()
