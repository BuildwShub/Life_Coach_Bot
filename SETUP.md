# 🔥 Shub's Life Coach Bot — Setup Guide

## What This Bot Does
Sends you loud Telegram reminders every day at your exact times:
- 1:00 PM — Wake up
- 1:30 PM — GYM (no excuses)
- 2:30 PM — Study block
- 3:30 PM — GitHub commit
- 3:50 PM — Work prep
- 3:30 AM — Sleep
- Every Sunday 10 AM — Weekly review

---

## STEP 1: Create Your Telegram Bot (5 minutes)

1. Open Telegram → search **@BotFather**
2. Send: `/newbot`
3. Name it: `Shub Life Coach`
4. Username: `shub_life_coach_bot` (or anything ending in `bot`)
5. BotFather gives you a **TOKEN** — copy it. Looks like: `7123456789:AAHabc...`

---

## STEP 2: Deploy for FREE on Railway (10 minutes)

Railway gives you free hosting that runs 24/7.

1. Go to **railway.app** → Sign up with GitHub
2. Click **"New Project"** → **"Deploy from GitHub repo"**
3. Push this folder to a GitHub repo first:
   ```
   git init
   git add .
   git commit -m "shub coach bot"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/shub-coach-bot.git
   git push -u origin main
   ```
4. In Railway → select your repo → click **Deploy**
5. Go to **Variables** tab → Add:
   - `TELEGRAM_BOT_TOKEN` = your token from Step 1
   - `TELEGRAM_CHAT_ID` = leave blank for now

---

## STEP 3: Get Your Chat ID

1. Once deployed, open Telegram
2. Search your bot by its username
3. Send `/start`
4. Bot replies with your **Chat ID** (a number like `987654321`)
5. Go back to Railway → Variables → Add `TELEGRAM_CHAT_ID` = that number
6. Railway redeploys automatically

---

## STEP 4: Set Notification to LOUD on Telegram

1. Open Telegram → tap your bot chat
2. Tap the bot name at the top
3. Make sure notifications are ON
4. On your Android: Settings → Apps → Telegram → Notifications → set to **Urgent / Heads Up**

---

## Done! Your bot is now live 24/7

Commands you can send to your bot:
- `/status` — What you should be doing RIGHT NOW
- `/checkin` — Log today's wins
- `/linkedin` — Generate a LinkedIn post
- `/project` — Get your next data science project idea

---

## Alternative: Run Locally (if you don't want Railway)

```bash
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your token and chat ID
python bot.py
```
Note: This only works while your laptop is on.
