#!/data/data/com.termux/files/usr/bin/bash
set -e

clear
echo "========================================================"
echo "      Samsung Tizen TV Sideload - Uninstaller           "
echo "========================================================"
echo ""
echo "This will clean up and remove the local files on your phone."
echo ""
echo "Options to remove:"
echo " [1] Clean cache & temporary downloads only (keeps project)"
echo " [2] Complete uninstall (removes project folder, config, and cache)"
echo " [0] Cancel"
echo ""
read -p "Select an option [0-2]: " choice

case "$choice" in
    1)
        echo ""
        echo "Cleaning cache and temporary .wgt/.tpk downloads..."
        SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
        rm -f "$SCRIPT_DIR"/*.wgt "$SCRIPT_DIR"/*.tpk 2>/dev/null || true
        rm -rf "$SCRIPT_DIR"/__pycache__ 2>/dev/null || true
        echo "Done! Cache cleaned."
        ;;
    2)
        echo ""
        read -p "Are you sure you want to completely remove this tool? [y/N]: " confirm
        if [ "$confirm" = "y" ] || [ "$confirm" = "Y" ]; then
            echo ""
            echo "Removing configuration and project..."
            rm -f "$HOME/.tizen_tv_ip" 2>/dev/null || true
            SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
            cd "$HOME"
            rm -rf "$SCRIPT_DIR"
            echo "Done! Sideload manager completely removed."
        else
            echo "Cancelled."
        fi
        ;;
    *)
        echo "Cancelled. Nothing removed."
        ;;
esac
