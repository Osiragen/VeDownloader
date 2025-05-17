#!/bin/bash

# VeDownloader Portable Uninstaller

echo "======================================="
echo "       VeDownloader Uninstaller        "
echo "======================================="

# ตรวจสอบสิทธิ์ root
if [ "$EUID" -ne 0 ]; then
    echo "❗ กรุณารันสคริปต์นี้ด้วย sudo:"
    echo "sudo $0"
    exit 1
fi

# กำหนด path ต่าง ๆ
INSTALL_DIR="/opt/vedownloader"
BIN_LINK="/usr/local/bin/vedownloader"
DESKTOP_FILE="/usr/share/applications/vedownloader.desktop"
ICON_PATH="/usr/share/icons/hicolor/128x128/apps/vedownloader.png"

# ลบไดเรกทอรีโปรแกรม
if [ -d "$INSTALL_DIR" ]; then
    echo "🗑 กำลังลบ $INSTALL_DIR..."
    rm -rf "$INSTALL_DIR"
else
    echo "ℹ️ ไม่พบ $INSTALL_DIR (ข้ามการลบ)"
fi

# ลบ symlink
if [ -f "$BIN_LINK" ]; then
    echo "🗑 กำลังลบ symlink $BIN_LINK..."
    rm -f "$BIN_LINK"
fi

# ลบ .desktop
if [ -f "$DESKTOP_FILE" ]; then
    echo "🗑 กำลังลบ desktop entry..."
    rm -f "$DESKTOP_FILE"
fi

# ลบไอคอน (ถ้ามี)
if [ -f "$ICON_PATH" ]; then
    echo "🗑 กำลังลบไอคอน..."
    rm -f "$ICON_PATH"
fi

# อัปเดตฐานข้อมูลเมนู
echo "🔄 อัปเดตฐานข้อมูลเมนู..."
update-desktop-database /usr/share/applications || true

echo ""
echo "✅ ถอนการติดตั้ง VeDownloader เสร็จเรียบร้อย"

