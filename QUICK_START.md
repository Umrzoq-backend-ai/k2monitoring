# ⚡ Tezkor Boshlash - Render.com'ga Deploy

## 1️⃣ GitHub'ga yuklash (5 daqiqa)

```bash
# Repository yaratish
git init
git add .
git commit -m "J3 Monitor Bot"

# GitHub'da yangi repository yarating: j3-monitor-bot
# Keyin:
git remote add origin https://github.com/YOUR_USERNAME/j3-monitor-bot.git
git branch -M main
git push -u origin main
```

⚠️ **Muhim:** `.env` fayli GitHub'ga yuklanmaydi (.gitignore'da)

---

## 2️⃣ Render.com'da deploy (3 daqiqa)

### A. Akkaunt ochish
1. [render.com](https://render.com) → Sign Up
2. GitHub bilan kirish

### B. Service yaratish
1. **New +** → **Web Service**
2. Repository'ni tanlang: `j3-monitor-bot`
3. Sozlamalar:
   - **Name:** `j3-monitor-bot`
   - **Region:** `Frankfurt`
   - **Branch:** `main`
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `python j3_monitor_final.py`
   - **Instance Type:** `Free`

### C. Environment Variables qo'shish
**Environment** tab'da **Add Environment Variable** bosing:

```
TELEGRAM_BOT_TOKEN = 7927170307:AAEfnREKmi-S6zhKhsyMAQJl-DR_pCmtDrc
TELEGRAM_CHAT_ID = 991729905
SCHOOL21_PASSWORD = Farrukh0211@
TARGET_ROW = j
TARGET_NUMBER = 3
```

4. **Create Web Service** → Kutib turing (2-3 daqiqa)

✅ Deploy tugadi! URL: `https://j3-monitor-bot.onrender.com`

---

## 3️⃣ Keep-Alive qilish (2 daqiqa)

Render free tier'da 15 daqiqa inactivity'dan keyin uxlaydi. Buni oldini olish:

### UptimeRobot:
1. [uptimerobot.com](https://uptimerobot.com) → Sign Up
2. **Add New Monitor**:
   - **Monitor Type:** HTTP(s)
   - **Friendly Name:** J3 Monitor
   - **URL:** `https://j3-monitor-bot.onrender.com`
   - **Monitoring Interval:** 5 minutes
3. **Create Monitor**

✅ Tayyor! Bot 24/7 ishlaydi.

---

## 4️⃣ Tekshirish

### Browser'da:
```
https://j3-monitor-bot.onrender.com
```

Ko'rinishi:
```json
{
  "status": "alive",
  "bot": "J3 Monitor",
  "timestamp": "2026-05-20T..."
}
```

### Telegram'da:
Bir necha daqiqadan keyin xabar keladi: **"J3 Monitoring Bot ishga tushdi!"**

### Render Logs:
```
J3 Monitoring Bot Starting
Authentication successful
Flask server started
Workplace monitor started
Monitoring: Cluster 36738, J3
```

---

## 🔧 Muammolarni hal qilish

| Muammo | Yechim |
|--------|--------|
| Bot ishlamayapti | Render logs'ni tekshiring |
| "Authentication failed" | `SCHOOL21_PASSWORD` to'g'ri kiritilganini tekshiring |
| Bot uxlab qolyapti | UptimeRobot to'g'ri sozlanganini tekshiring |
| Telegram xabar kelmayapti | `TELEGRAM_BOT_TOKEN` va `CHAT_ID` tekshiring |

---

## 📊 Monitoring

**Render Dashboard:**
- **Logs:** Real-time logs
- **Metrics:** CPU/Memory
- **Events:** Deploy history

**UptimeRobot Dashboard:**
- Uptime statistikasi
- Response time
- Down alerts (email)

---

## 🔄 Yangilash

Kod o'zgartirsangiz:

```bash
git add .
git commit -m "Update: ..."
git push
```

Render avtomatik deploy qiladi!

---

## 💰 Narx

- **Render.com:** Tekin (750 soat/oy)
- **UptimeRobot:** Tekin (50 monitor)
- **Jami:** $0/oy 🎉

---

**Muvaffaqiyatli deploy!** 🚀

Savollar bo'lsa: [Issues](https://github.com/YOUR_USERNAME/j3-monitor-bot/issues)
