#!/data/data/com.termux/files/usr/bin/bash
set -e

# Resolve actual script directory even when executed via symlink or PATH
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$DIR/$SOURCE"
done
SCRIPT_DIR="$( cd -P "$( dirname "$SOURCE" )" >/dev/null 2>&1 && pwd )"

# 0. Check for Updates from GitHub
if [ -d "$SCRIPT_DIR/.git" ]; then
    git -C "$SCRIPT_DIR" fetch origin main >/dev/null 2>&1 || true
    LOCAL_HASH=$(git -C "$SCRIPT_DIR" rev-parse HEAD 2>/dev/null || echo "")
    REMOTE_HASH=$(git -C "$SCRIPT_DIR" rev-parse origin/main 2>/dev/null || echo "")
    if [ -n "$LOCAL_HASH" ] && [ -n "$REMOTE_HASH" ] && [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
        CUR_VER=$(grep "^SCRIPT_VERSION =" "$SCRIPT_DIR/install.py" 2>/dev/null | cut -d'"' -f2 || echo "2.1.0")
        REMOTE_VER=$(git -C "$SCRIPT_DIR" show origin/main:install.py 2>/dev/null | grep "^SCRIPT_VERSION =" | cut -d'"' -f2 || echo "latest")
        echo "⚡ Update available: v$CUR_VER ➜ v$REMOTE_VER! Updating..."
        git -C "$SCRIPT_DIR" pull origin main >/dev/null 2>&1 || true
        NEW_VER=$(grep "^SCRIPT_VERSION =" "$SCRIPT_DIR/install.py" 2>/dev/null | cut -d'"' -f2 || echo "$REMOTE_VER")
        echo "✔ Updated successfully to v$NEW_VER!"
        echo "🔄 Auto-restarting script..."
        sleep 1
        exec "$SCRIPT_DIR/setup.sh" "$@"
    fi
fi

# 1. Clean check & install missing tools
PACKAGES=""
command -v python >/dev/null 2>&1 || PACKAGES="$PACKAGES python"
command -v adb >/dev/null 2>&1    || PACKAGES="$PACKAGES android-tools"
command -v curl >/dev/null 2>&1   || PACKAGES="$PACKAGES curl"

if [ -n "$PACKAGES" ]; then
    echo "Installing prerequisites ($PACKAGES)..."
    pkg update -y >/dev/null 2>&1
    pkg install -y $PACKAGES >/dev/null 2>&1
fi

# 2. Ensure Storage permission & Create Samsung-T-Sideload folder in Internal Storage
DEDICATED_DIR="/storage/emulated/0/Download/Samsung-T-Sideload"
if [ ! -d "$HOME/storage" ] && [ ! -d "$DEDICATED_DIR" ]; then
    termux-setup-storage >/dev/null 2>&1 || true
fi
mkdir -p "$DEDICATED_DIR" 2>/dev/null || mkdir -p "$HOME/storage/downloads/Samsung-T-Sideload" 2>/dev/null || true

# 3. Ensure ADB / Tizen keys exist
if [ ! -f "$HOME/.android/adbkey" ]; then
    mkdir -p "$HOME/.android" "$HOME/.tizen"
    adb keygen "$HOME/.tizen/sdbkey" >/dev/null 2>&1
    cp "$HOME/.tizen/sdbkey" "$HOME/.android/adbkey"
    cp "$HOME/.tizen/sdbkey.pub" "$HOME/.android/adbkey.pub"
fi

# 4. Detect Phone IP
PHONE_IP=$(python3 -c "
import subprocess, socket
def get_ip():
    try:
        out = subprocess.check_output(['/system/bin/ip', '-4', 'addr', 'show'], stderr=subprocess.DEVNULL).decode()
        cur = None
        for l in out.splitlines():
            s = l.strip()
            if ': ' in s and ('wlan' in s or 'ap' in s): cur = s
            elif s.startswith('inet ') and cur: return s.split()[1].split('/')[0]
            elif ': ' in s: cur = None
    except Exception: pass
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        res = s.getsockname()[0]
        s.close()
        return res
    except Exception: return 'Unknown'
print(get_ip())
" 2>/dev/null || echo "Unknown")

SAVED_TV_IP=$(cat "$HOME/.tizen_tv_ip" 2>/dev/null || echo "")

clear
echo "========================================================"
echo "          Samsung Tizen TV Sideload Setup               "
echo "========================================================"
echo ""
echo " Put your .wgt / .tpk files in File Manager at:"
echo "    Internal Storage -> Download -> Samsung-T-Sideload"
echo ""
echo "┌───────────────────────────────────────────────────────┐"
echo "│  👉 WHAT TO INPUT IN SAMSUNG TV DEVELOPER MODE:       │"
echo "├───────────────────────────────────────────────────────┤"
echo "│  1. Open 'Apps' -> Press 1 2 3 4 5 on TV remote       │"
echo "│  2. Turn Developer Mode -> [ ON ]                     │"
echo "│  3. In 'Host PC IP' box, enter:                       │"
echo "│     👉  $PHONE_IP"
echo "│  4. Hold TV Remote Power button 5s to reboot TV       │"
echo "└───────────────────────────────────────────────────────┘"
if [ -n "$SAVED_TV_IP" ]; then
echo " Detected Samsung TV IP : $SAVED_TV_IP:26101"
fi
echo "========================================================"
echo ""

# 5. Launch python manager from real script directory
cd "$SCRIPT_DIR"
python3 "$SCRIPT_DIR/install.py" "$@"
