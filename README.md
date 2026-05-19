# J3 Monitoring Bot

Tillakori cluster, J3 ish joyini monitoring qiluvchi bot. Kimdir login yoki logout qilsa darhol xabar beradi va to'liq ma'lumot ko'rsatadi.

## 📋 Xususiyatlar

- ✅ Real-time monitoring (har 60 soniyada tekshiradi)
- ✅ Login/Logout hodisalarini aniqlash
- ✅ Foydalanuvchi haqida to'liq ma'lumot:
  - Login, kampus, sinf, parallel
  - Level va XP
  - Haftalik logtime
  - Login/logout vaqti
  - Sessiya davomiyligi
- ✅ Log faylga yozish
- ✅ Avtomatik token yangilash

## 🚀 Ishga tushirish

### 1. Local'da test qilish

```bash
# Dependencies o'rnatish
pip install -r requirements.txt

# Botni ishga tushirish
python3 j3_monitor_final.py
```

### 2. Render.com'ga deploy qilish (24/7 tekin hosting)

To'liq yo'riqnoma: [DEPLOY.md](DEPLOY.md)

Qisqacha:
1. GitHub'ga push qiling
2. Render.com'da Web Service yarating
3. Environment variables kiriting
4. UptimeRobot bilan keep-alive qiling

Bot URL: `https://your-app.onrender.com`

## 🚀 Ishga tushirish (eski usullar)

### 1. Oddiy versiya (faqat konsolda)

```bash
python3 j3_monitor_bot.py
```

To'xtatish: `Ctrl+C`

### 2. Advanced versiya (log fayl bilan)

```bash
python3 j3_monitor_advanced.py
```

Log fayl: `j3_monitor.log`

### 3. Background da ishlatish

```bash
# Background da ishga tushirish
nohup python3 j3_monitor_advanced.py > /dev/null 2>&1 &

# Process ID ni saqlash
echo $! > j3_monitor.pid

# To'xtatish
kill $(cat j3_monitor.pid)
```

### 4. Systemd service sifatida (Linux)

`/etc/systemd/system/j3-monitor.service` fayl yarating:

```ini
[Unit]
Description=J3 Monitoring Bot
After=network.target

[Service]
Type=simple
User=rrangesi
WorkingDirectory=/home/rrangesi/goinfre/Full Stack developer/Frontend/klaster
ExecStart=/usr/bin/python3 j3_monitor_advanced.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Ishga tushirish:
```bash
sudo systemctl daemon-reload
sudo systemctl start j3-monitor
sudo systemctl enable j3-monitor  # Avtomatik ishga tushish
sudo systemctl status j3-monitor  # Status ko'rish
```

## 📊 Chiqish namunasi

```
🟢 YANGI LOGIN - J3
======================================================================
⏰ Vaqt: 2026-05-19 21:06:18
👤 Login: rrangesi
📍 Kampus: 21 Samarkand
🎓 Sinf: 25_08_SKD
📊 Level: 11 | XP: 13693
⏱️  Haftalik: 42.5 soat
======================================================================
```

```
🔴 LOGOUT - J3
======================================================================
⏰ Vaqt: 2026-05-19 23:30:45
👤 Login: rrangesi
⏱️  Davomiyligi: 144.5 daqiqa (2.4 soat)
🕐 Login vaqti: 2026-05-19 21:06:18
======================================================================
```

## 📁 Fayllar

- `j3_monitor_bot.py` - Oddiy versiya (faqat konsol)
- `j3_monitor_advanced.py` - Advanced versiya (log fayl bilan)
- `j3_monitor.log` - Log fayl (avtomatik yaratiladi)
- `school21_api.py` - School21 API client
- `tillakori_cluster.py` - Tillakori cluster ma'lumotlari
- `samarkand_campus_info.py` - Samarqand kampus ma'lumotlari

## ⚙️ Sozlamalar

`j3_monitor_advanced.py` faylida:

```python
USERNAME = "rrangesi"           # Sizning login
PASSWORD = "Farrukh0211@"       # Sizning parol
CHECK_INTERVAL = 60             # Tekshirish intervali (soniya)
```

## 🔒 Xavfsizlik

⚠️ **Muhim**: Parolni kodda saqlash xavfli! Ishlab chiqarish muhitida environment variable ishlatish tavsiya etiladi:

```bash
export SCHOOL21_USERNAME="rrangesi"
export SCHOOL21_PASSWORD="Farrukh0211@"
```

Kodda:
```python
import os
USERNAME = os.getenv("SCHOOL21_USERNAME")
PASSWORD = os.getenv("SCHOOL21_PASSWORD")
```

## 📞 Telegram integratsiyasi (opsional)

Telegram bot orqali xabar olish uchun:

1. [@BotFather](https://t.me/botfather) dan bot yarating
2. Bot tokenni oling
3. Chat ID ni oling
4. Kodga qo'shing:

```python
import requests

def send_telegram(message: str):
    bot_token = "YOUR_BOT_TOKEN"
    chat_id = "YOUR_CHAT_ID"
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    requests.post(url, json={"chat_id": chat_id, "text": message})
```

## 🐛 Muammolar

### Token muddati tugadi
Bot avtomatik ravishda tokenni yangilaydi (har 5 daqiqada).

### Internet uzilib qoldi
Bot qayta ulanishga harakat qiladi. Agar muammo davom etsa, qayta ishga tushiring.

### Log fayl juda katta
Log faylni vaqti-vaqti bilan tozalang:
```bash
> j3_monitor.log  # Faylni bo'shatish
```

## 📝 Litsenziya

MIT License - erkin foydalaning!

## 👨‍💻 Muallif

rrangesi @ School21 Samarkand
