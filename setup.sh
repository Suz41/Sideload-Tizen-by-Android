#!/data/data/com.termux/files/usr/bin/bash
set -e

# 0. Check for Updates from GitHub
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [ -d "$SCRIPT_DIR/.git" ]; then
    (
        cd "$SCRIPT_DIR"
        git fetch origin main >/dev/null 2>&1 || true
        LOCAL_HASH=$(git rev-parse HEAD 2>/dev/null || echo "")
        REMOTE_HASH=$(git rev-parse origin/main 2>/dev/null || echo "")
        if [ -n "$LOCAL_HASH" ] && [ -n "$REMOTE_HASH" ] && [ "$LOCAL_HASH" != "$REMOTE_HASH" ]; then
            echo "⚡ Update available! Updating to latest version..."
            git pull origin main >/dev/null 2>&1 || true
            echo "✔ Updated successfully!"
            sleep 1
        fi
    )
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
PHONE_IP=$(python3 -c "import socket; s=socket.socket(socket.AF_INET, socket.SOCK_DGRAM); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()" 2>/dev/null || echo "Unknown")

clear
echo "========================================================"
echo "          Samsung Tizen TV Sideload Setup               "
echo "========================================================"
echo ""
echo " 📁 Put your .wgt files in File Manager at:"
echo "    Internal Storage -> Download -> Samsung-T-Sideload"
echo ""
echo " 📱 YOUR PHONE IP : $PHONE_IP"
echo ""
echo " 1. ON YOUR SAMSUNG TV:"
echo "    • Apps -> Press 1 2 3 4 5 on remote"
echo "    • Turn Developer Mode -> ON"
echo "    • Host IP -> Enter: $PHONE_IP"
echo "    • Hold TV Power button 5s to restart TV"
echo ""
echo " 2. FIND TV IP ON TV:"
echo "    • Settings -> General -> Network -> Network Status"
echo "========================================================"
echo ""

# 5. Launch python manager
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/install.py" "$@"
