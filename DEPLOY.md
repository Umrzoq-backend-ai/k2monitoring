# Render.com'ga Deploy qilish yo'riqnomasi

## 1. Render.com'da akkaunt ochish

1. [render.com](https://render.com) ga kiring
2. GitHub akkauntingiz bilan ro'yxatdan o'ting

## 2. GitHub repository yaratish

```bash
# Git repository'ni initialize qiling
git init
git add .
git commit -m "Initial commit: J3 Monitor Bot"

# GitHub'ga push qiling
git remote add origin https://github.com/YOUR_USERNAME/j3-monitor-bot.git
git branch -M main
git push -u origin main
```

## 3. Render.com'da service yaratish

1. Render dashboard'ga kiring
2. **"New +"** tugmasini bosing
3. **"Web Service"** ni tanlang
4. GitHub repository'ngizni ulang
5. Quyidagi sozlamalarni kiriting:

### Asosiy sozlamalar:
- **Name:** `j3-monitor-bot`
- **Region:** `Frankfurt` (yoki Oregon)
- **Branch:** `main`
- **Runtime:** `Python 3`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `python j3_monitor_final.py`

### Environment Variables:
**Environment** bo'limida quyidagilarni qo'shing:

| Key | Value |
|-----|-------|
| `TELEGRAM_BOT_TOKEN` | `7927170307:AAEfnREKmi-S6zhKhsyMAQJl-DR_pCmtDrc` |
| `TELEGRAM_CHAT_ID` | `991729905` |
| `SCHOOL21_PASSWORD` | `Farrukh0211@` |
| `TARGET_ROW` | `j` |
| `TARGET_NUMBER` | `3` |

6. **"Create Web Service"** tugmasini bosing

## 4. UptimeRobot bilan keep-alive qilish

Render free tier'da service 15 daqiqa inactivity'dan keyin uxlaydi. Buni oldini olish uchun:

### UptimeRobot sozlash:

1. [uptimerobot.com](https://uptimerobot.com) ga kiring va ro'yxatdan o'ting
2. **"Add New Monitor"** tugmasini bosing
3. Quyidagilarni kiriting:
   - **Monitor Type:** `HTTP(s)`
   - **Friendly Name:** `J3 Monitor Bot`
   - **URL:** `https://j3-monitor-bot.onrender.com` (Render'dan olingan URL)
   - **Monitoring Interval:** `5 minutes`
4. **"Create Monitor"** tugmasini bosing

✅ Endi botingiz har 5 daqiqada ping olib, uxlamaydi!

## 5. Tekshirish

1. Render dashboard'da logs'ni ko'ring:
   ```
   J3 Monitoring Bot ishga tushdi!
   Flask server started
   Workplace monitor started
   ```

2. Browser'da ochib ko'ring:
   ```
   https://j3-monitor-bot.onrender.com
   ```
   
   Ko'rinishi kerak:
   ```json
   {
     "status": "alive",
     "bot": "J3 Monitor",
     "timestamp": "2026-05-20T..."
   }
   ```

3. Telegram'da xabar kelishini kutib turing!

## 6. Muammolarni hal qilish

### Bot ishlamayapti:
- Render logs'ni tekshiring
- Environment variables to'g'ri kiritilganini tekshiring
- `.env` faylini GitHub'ga push qilmang (xavfsizlik!)

### Bot uxlab qolyapti:
- UptimeRobot to'g'ri sozlanganini tekshiring
- Monitoring interval 5 daqiqa yoki kamroq bo'lishi kerak

### Token expired:
- Bot avtomatik ravishda tokenni yangilaydi
- Agar muammo bo'lsa, Render'da service'ni restart qiling

## 7. Xavfsizlik

⚠️ **Muhim:** 
- `.env` faylini `.gitignore`'ga qo'shing
- Parol va tokenlarni faqat Render Environment Variables'da saqlang
- GitHub'da public repository bo'lsa, maxfiy ma'lumotlarni push qilmang!

## 8. Monitoring

Render dashboard'da:
- **Logs:** Real-time logs ko'rish
- **Metrics:** CPU, Memory ishlatilishi
- **Events:** Deploy history

## 9. Yangilash

Yangi kod yozganingizda:

```bash
git add .
git commit -m "Update: ..."
git push
```

Render avtomatik ravishda yangi versiyani deploy qiladi!

---

## Qo'shimcha: Cron-job.org alternativasi

Agar UptimeRobot ishlamasa, [cron-job.org](https://cron-job.org) ishlatishingiz mumkin:

1. Akkaunt oching
2. **"Create cronjob"** tugmasini bosing
3. URL: `https://j3-monitor-bot.onrender.com/health`
4. Schedule: `*/5 * * * *` (har 5 daqiqa)
5. Save qiling

---

**Muvaffaqiyatli deploy!** 🚀
