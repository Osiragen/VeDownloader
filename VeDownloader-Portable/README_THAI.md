# VeDownloader

แอปพลิเคชันดาวน์โหลดวิดีโอที่ใช้งานง่ายด้วย PyQt5

## คุณสมบัติ

- อินเทอร์เฟซผู้ใช้ที่เรียบง่ายและใช้งานง่าย
- ดาวน์โหลดวิดีโอจากแหล่งต่างๆ
- เลือกโฟลเดอร์ปลายทาง
- เลือกคุณภาพและรูปแบบวิดีโอ
- ติดตามประวัติการดาวน์โหลด
- ติดตามความคืบหน้า

## การติดตั้ง

### Linux/Ubuntu/Xubuntu

#### ตัวเลือกที่ 1: ใช้สคริปต์ติดตั้ง

1. ทำให้สคริปต์ติดตั้งสามารถเรียกใช้ได้:
   ```
   chmod +x install_linux.sh
   ```
2. รันสคริปต์ติดตั้งด้วย sudo:
   ```
   sudo ./install_linux.sh
   ```
3. เปิดแอปพลิเคชันจากเมนูแอปพลิเคชันหรือโดยการรัน:
   ```
   vedownloader
   ```

#### ตัวเลือกที่ 2: การติดตั้งด้วยตนเอง

1. ทำให้สคริปต์เรียกใช้สามารถเรียกใช้ได้:
   ```
   chmod +x vedownloader.sh
   ```
2. รันสคริปต์เรียกใช้:
   ```
   ./vedownloader.sh
   ```

## การใช้งาน

### เวอร์ชันพื้นฐาน

รันเวอร์ชันพื้นฐานด้วย:
```
python main.py
```

### เวอร์ชันขั้นสูง

รันเวอร์ชันขั้นสูงด้วย:
```
python advanced_gui.py
```

### เวอร์ชัน Linux

รันเวอร์ชัน Linux ด้วย:
```
./vedownloader.sh
```

## โครงสร้างแอปพลิเคชัน

- `main.py` - แอปพลิเคชัน GUI พื้นฐาน
- `advanced_gui.py` - GUI ขั้นสูงพร้อมคุณสมบัติเพิ่มเติม
- `vedownloader.sh` - สคริปต์เรียกใช้ Linux
- `install_linux.sh` - สคริปต์ติดตั้ง Linux
- `VeDownloader.desktop` - ไฟล์รายการเดสก์ท็อป Linux

## ข้อกำหนด

- Python 3.6 หรือสูงกว่า
- PyQt5
- yt-dlp
- FFmpeg (แนะนำสำหรับฟังก์ชันการทำงานเต็มรูปแบบ)

## การแก้ไขปัญหาบน Xubuntu

### ปัญหา: ไม่พบ Qt platform plugin

หากคุณพบข้อผิดพลาด "Could not find the Qt platform plugin" ให้ติดตั้งแพ็คเกจเพิ่มเติมดังนี้:

```
sudo apt install libxcb-xinerama0 libxcb-icccm4 libxcb-image0 libxcb-keysyms1 libxcb-render-util0 libxcb-xkb1 libxkbcommon-x11-0
```

### ปัญหา: FFmpeg ไม่ได้ติดตั้ง

หากคุณพบข้อผิดพลาดเกี่ยวกับ FFmpeg ให้ติดตั้งด้วย:

```
sudo apt install ffmpeg
```

### ปัญหา: ปัญหาการแสดงผล

หากคุณพบปัญหาการแสดงผลหรือแอปพลิเคชันไม่เปิด ให้ลองตั้งค่าตัวแปรสภาพแวดล้อมต่อไปนี้:

```
export QT_QPA_PLATFORM=xcb
export QT_DEBUG_PLUGINS=1
```

## การสร้างไฟล์ Executable

หากต้องการสร้างไฟล์ executable สำหรับ Linux ให้รัน:

```
python build_linux.py
```

ไฟล์ executable จะถูกสร้างในโฟลเดอร์ 'dist'

## ลิขสิทธิ์

MIT
