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
        echo "[UPDATE] Update available: v$CUR_VER -> v$REMOTE_VER! Updating..."
        git -C "$SCRIPT_DIR" pull origin main >/dev/null 2>&1 || true
        NEW_VER=$(grep "^SCRIPT_VERSION =" "$SCRIPT_DIR/install.py" 2>/dev/null | cut -d'"' -f2 || echo "$REMOTE_VER")
        echo "[OK] Updated successfully to v$NEW_VER!"
        echo "[RESTART] Auto-restarting script..."
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
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from install import get_local_wifi_ip
print(get_local_wifi_ip())
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
echo "+-------------------------------------------------------+"
echo "|  [!] WHAT TO INPUT IN SAMSUNG TV DEVELOPER MODE:      |"
echo "+-------------------------------------------------------+"
echo "|  1. Open 'Apps' -> Press 1 2 3 4 5 on TV remote       |"
echo "|  2. Turn Developer Mode -> [ ON ]                     |"
echo "|  3. In 'Host PC IP' box, enter:                       |"
echo "|     -> $PHONE_IP"
echo "|  4. Hold TV Remote Power button 5s to reboot TV       |"
echo "+-------------------------------------------------------+"
if [ -n "$SAVED_TV_IP" ]; then
echo " Detected Samsung TV IP : $SAVED_TV_IP:26101"
fi
echo "========================================================"
echo ""

# 5. Launch python manager from real script directory
cd "$SCRIPT_DIR"
python3 "$SCRIPT_DIR/install.py" "$@"
