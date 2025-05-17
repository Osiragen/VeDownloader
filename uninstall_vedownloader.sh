#!/bin/bash

echo "========================================"
echo "       VeDownloader Uninstaller        "
echo "========================================"

# ตรวจสอบว่ารันด้วยสิทธิ์ root
if [ "$EUID" -ne 0 ]; then
    echo "❗ กรุณารันสคริปต์นี้ด้วย sudo:"
    echo "sudo $0"
    exit 1
fi

# ลบโฟลเดอร์โปรแกรม
echo "🧹 ลบโฟลเดอร์โปรแกรมที่ /opt/vedownloader..."
rm -rf /opt/vedownloader

# ลบ shortcut (desktop entry)
echo "🧹 ลบไฟล์ .desktop ที่ /usr/share/applications/vedownloader.desktop..."
rm -f /usr/share/applications/vedownloader.desktop

# ลบ symlink
echo "🧹 ลบ symlink ที่ /usr/local/bin/vedownloader..."
rm -f /usr/local/bin/vedownloader

# อัปเดต database ของเมนู (optional)
echo "🔄 อัพเดทฐานข้อมูลเมนู..."
update-desktop-database /usr/share/applications || true

echo ""
echo "✅ ถอนการติดตั้ง VeDownloader เสร็จสมบูรณ์แล้ว!"
echo "========================================"

