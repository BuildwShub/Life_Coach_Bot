"""
Shub's Personal Life Coach Bot 🔥
Sends scheduled reminders, tracks habits, motivates daily.
"""

import os
import asyncio
import logging
from datetime import datetime, time
import pytz
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # Your personal chat ID (set after /start)
IST = pytz.timezone("Asia/Kolkata")

# ─── Shub's Daily Schedule ─────────────────────────────────────────────────────
SCHEDULE = [
    {
        "time": time(13, 0),   # 1:00 PM
        "emoji": "🌅",
        "title": "WAKE UP TIME",
        "message": (
            "🌅 *1:00 PM — RISE UP, SHUB.*\n\n"
            "No phone for 15 minutes.\n"
            "Drink water. Stretch.\n\n"
            "You slept. Now you BUILD.\n"
            "Today is not wasted. It starts NOW."
        ),
        "buttons": [("✅ I'm up", "up"), ("😴 5 more min", "snooze")]
    },
    {
        "time": time(13, 30),  # 1:30 PM
        "emoji": "💪",
        "title": "GYM TIME",
        "message": (
            "💪 *1:30 PM — GYM. NO EXCUSES.*\n\n"
            "You don't need motivation. You need to MOVE.\n"
            "30 minutes minimum. That's it.\n\n"
            "Gym bag. Shoes. GO.\n"
            "_The people who change their lives don't wait to feel ready._"
        ),
        "buttons": [("💪 Going now!", "gym_yes"), ("🏠 Home workout", "gym_home"), ("❌ Skipping", "gym_skip")]
    },
    {
        "time": time(14, 30),  # 2:30 PM
        "emoji": "📚",
        "title": "STUDY BLOCK",
        "message": (
            "📚 *2:30 PM — COURSE TIME.*\n\n"
            "One module. That's your only job right now.\n"
            "Close Instagram. Close YouTube.\n\n"
            "Open your Data Science course.\n"
            "Set a 45-minute timer. START.\n\n"
            "_Every module is one step closer to that job you want._"
        ),
        "buttons": [("📖 Starting now", "study_yes"), ("⏭️ Doing project instead", "study_proj")]
    },
    {
        "time": time(15, 30),  # 3:30 PM
        "emoji": "🐙",
        "title": "GITHUB COMMIT",
        "message": (
            "🐙 *3:30 PM — PUSH TO GITHUB.*\n\n"
            "One commit. Even if it's just a README update.\n"
            "Your GitHub graph is your resume.\n\n"
            "Open VS Code. Make one change. Push it.\n"
            "_Consistency > Perfection._"
        ),
        "buttons": [("✅ Pushed!", "github_yes"), ("🔄 Still working", "github_wip")]
    },
    {
        "time": time(15, 50),  # 3:50 PM
        "emoji": "💼",
        "title": "GET READY FOR WORK",
        "message": (
            "💼 *3:50 PM — WORK IN 10 MINUTES.*\n\n"
            "Wrap up. Get ready.\n"
            "You did the work BEFORE your shift.\n"
            "That's what winners do. 🔥"
        ),
        "buttons": [("👍 Ready", "work_ready")]
    },
    {
        "time": time(13, 5),   # 1:05 AM (represented as next day — see scheduling note)
        "emoji": "🌙",
        "title": "JOB ENDS — WIND DOWN",
        "message": (
            "🌙 *Job Done. Good work.*\n\n"
            "No doom scrolling.\n"
            "10 minutes: write tomorrow's 3 tasks.\n\n"
            "Then rest. You earned it. 💪"
        ),
        "buttons": [("📝 Planning now", "plan_yes"), ("😴 Too tired", "plan_tired")]
    },
    {
        "time": time(3, 30),   # 3:30 AM
        "emoji": "😴",
        "title": "SLEEP TIME",
        "message": (
            "😴 *3:30 AM — PUT THE PHONE DOWN.*\n\n"
            "Sleep is not lazy. It's recovery.\n"
            "Your gym session, your learning — all consolidates during sleep.\n\n"
            "Target: asleep by 3:30 AM.\n"
            "We shift this 30 min earlier every 2 weeks. 📈"
        ),
        "buttons": [("😴 Going to sleep", "sleep_yes"), ("📱 Few more mins", "sleep_late")]
    },
]

# Daily check-in replies
BUTTON_REPLIES = {
    "up": "Let's GO. Gym in 30 minutes. Don't waste this momentum. 🔥",
    "snooze": "5 minutes is fine. But when that alarm hits — you GET UP. No second chances. ⏰",
    "gym_yes": "YESSS! That's the builder mentality! 💪 Crush it. Tell me how it went after.",
    "gym_home": "Home workout counts 100%! Push-ups, squats, anything. Movement is movement. 💪",
    "gym_skip": "Okay. I won't lecture you. But write down WHY you skipped. That reason is the thing we need to fix. 📝",
    "study_yes": "LOCK IN. 45-minute timer. No phone. You've got this. 📚",
    "study_proj": "Project work counts! Push that commit. Still wins. 🐙",
    "github_yes": "COMMIT PUSHED! 🎉 Screenshot that notification and save it. That's your proof. LinkedIn post soon?",
    "github_wip": "Keep going! Every line of code is progress. Even WIP counts. 💻",
    "work_ready": "Go be professional. You already won before work started today. 💼",
    "plan_yes": "Three tasks tomorrow. Write them down. Future-you will thank you. 📝",
    "plan_tired": "That's okay. Even just thinking of ONE thing you'll do tomorrow helps. Rest well. 🌙",
    "sleep_yes": "Good. See you at 1 PM. Tomorrow we go again. 💪",
    "sleep_late": "15 minutes max. Then PHONE DOWN. Your sleep schedule won't fix itself. 😴",
}

# Weekly Sunday check-in
SUNDAY_CHECKIN = (
    "☀️ *SUNDAY CHECK-IN — THE HONEST REVIEW*\n\n"
    "No BS. Just truth.\n\n"
    "This week:\n"
    "🐙 GitHub commits: ?\n"
    "💪 Gym sessions: ?\n"
    "📚 Course modules: ?\n\n"
    "Reply with your numbers. I'll tell you exactly what to fix next week.\n\n"
    "_Progress, not perfection._"
)

# ─── Bot Handlers ──────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"🔥 *SHUB'S LIFE COACH BOT IS LIVE*\n\n"
        f"Your Chat ID: `{chat_id}`\n\n"
        f"Save this in your .env as TELEGRAM_CHAT_ID\n\n"
        f"I'll remind you daily:\n"
        f"• 1:00 PM — Wake up\n"
        f"• 1:30 PM — Gym\n"
        f"• 2:30 PM — Study\n"
        f"• 3:30 PM — GitHub commit\n"
        f"• 3:50 PM — Work prep\n"
        f"• 3:30 AM — Sleep\n\n"
        f"Type /status to see today's progress.\n"
        f"Type /linkedin to get a LinkedIn post template.\n"
        f"Type /project to get your next project idea.\n\n"
        f"Let's change your life. 💪",
        parse_mode="Markdown"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(IST)
    hour = now.hour
    if hour >= 13 and hour < 14:
        current = "Should be at gym or heading there 💪"
    elif hour >= 14 and hour < 15:
        current = "Study block — course or project 📚"
    elif hour >= 15 and hour < 16:
        current = "GitHub commit time 🐙"
    elif hour >= 16 and hour < 25:
        current = "Work shift in progress 💼"
    else:
        current = "Wind down / sleep time 🌙"

    await update.message.reply_text(
        f"⏰ *RIGHT NOW ({now.strftime('%I:%M %p')} IST)*\n\n"
        f"You should be: {current}\n\n"
        f"Type /checkin to log your progress.",
        parse_mode="Markdown"
    )

async def linkedin_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 *LINKEDIN POST TEMPLATE*\n\n"
        "Tell me what you completed today and I'll write the full post.\n\n"
        "Example: 'I finished the EDA on NYC Taxi data and found that night trips have higher tips'\n\n"
        "Just reply with what you did 👇",
        parse_mode="Markdown"
    )

async def project_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *NEXT PROJECT IDEAS FOR YOU*\n\n"
        "You're doing NYC Taxi EDA. Next steps:\n\n"
        "1. 🚕 *Trip Duration Predictor* — ML model on your taxi data\n"
        "2. 🏏 *IPL Stats Dashboard* — Indians love cricket, LinkedIn will too\n"
        "3. 📈 *Stock Price EDA* — NIFTY50 historical data\n"
        "4. 🛒 *Customer Churn* — Telecom dataset, binary classifier\n"
        "5. 🍽️ *Zomato Analysis* — Ratings, cost, cuisine clustering\n\n"
        "Each one = 1 week = 1 LinkedIn post = 1 GitHub repo.\n\n"
        "Which one calls to you? Reply with the number.",
        parse_mode="Markdown"
    )

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🐙 Pushed to GitHub", callback_data="ci_github")],
        [InlineKeyboardButton("💪 Went to Gym", callback_data="ci_gym")],
        [InlineKeyboardButton("📚 Completed Study", callback_data="ci_study")],
        [InlineKeyboardButton("😴 Slept on Time", callback_data="ci_sleep")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "✅ *DAILY CHECK-IN*\n\nWhat did you complete today?",
        reply_markup=reply_markup, parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data in BUTTON_REPLIES:
        await query.message.reply_text(BUTTON_REPLIES[data])
    elif data == "ci_github":
        await query.message.reply_text("🐙 GitHub commit logged! Your streak grows. Screenshot the contribution graph and post it on LinkedIn this week!")
    elif data == "ci_gym":
        await query.message.reply_text("💪 GYM LOGGED! That's the most important habit. Keep this streak alive!")
    elif data == "ci_study":
        await query.message.reply_text("📚 Study logged! One module at a time. You're building real knowledge.")
    elif data == "ci_sleep":
        await query.message.reply_text("😴 Sleep logged! Recovery is part of the grind. Your body thanks you.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if any(w in text for w in ["procrastinat", "can't start", "stuck", "lazy", "not doing"]):
        await update.message.reply_text(
            "🎯 *PROCRASTINATION BUSTER*\n\n"
            "Set a 2-minute timer RIGHT NOW.\n"
            "Open your laptop.\n"
            "Do ANYTHING related to your goal.\n\n"
            "_You don't have to feel like it. You just have to start._\n\n"
            "Go. I'll check on you in 30 minutes.",
            parse_mode="Markdown"
        )
    elif any(w in text for w in ["linkedin", "post", "content"]):
        await update.message.reply_text(
            "📝 Tell me what you completed and I'll write your LinkedIn post.\n"
            "Even small things count. What did you build/learn today?"
        )
    else:
        await update.message.reply_text(
            "I heard you. 💪\n\n"
            "Commands:\n"
            "/status — What you should be doing now\n"
            "/checkin — Log today's wins\n"
            "/linkedin — Get a LinkedIn post\n"
            "/project — Next project idea"
        )

# ─── Scheduled Reminders ───────────────────────────────────────────────────────

async def send_reminder(app, message_text, buttons=None):
    if not CHAT_ID:
        logger.warning("CHAT_ID not set. Run /start first to get your chat ID.")
        return
    reply_markup = None
    if buttons:
        keyboard = [[InlineKeyboardButton(label, callback_data=cb)] for label, cb in buttons]
        reply_markup = InlineKeyboardMarkup(keyboard)
    await app.bot.send_message(
        chat_id=CHAT_ID,
        text=message_text,
        parse_mode="Markdown",
        reply_markup=reply_markup
    )

def schedule_daily_jobs(app):
    """Register all daily reminders with job queue."""
    jq = app.job_queue
    for item in SCHEDULE:
        jq.run_daily(
            callback=lambda ctx, msg=item["message"], btns=item.get("buttons"): send_reminder(app, msg, btns),
            time=item["time"].replace(tzinfo=IST),
            name=item["title"]
        )
        logger.info(f"Scheduled: {item['title']} at {item['time']}")

    # Sunday check-in at 10 AM IST
    jq.run_daily(
        callback=lambda ctx: send_reminder(app, SUNDAY_CHECKIN),
        time=time(10, 0, tzinfo=IST),
        days=(6,),  # Sunday
        name="Sunday Check-in"
    )
    logger.info("All jobs scheduled ✅")

# ─── Main ──────────────────────────────────────────────────────────────────────

def main():
    if not TOKEN:
        raise ValueError("Set TELEGRAM_BOT_TOKEN in your environment!")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(CommandHandler("checkin", checkin))
    app.add_handler(CommandHandler("linkedin", linkedin_post))
    app.add_handler(CommandHandler("project", project_idea))
    app.add_handler(CallbackQueryHandler(button_callback))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    schedule_daily_jobs(app)

    logger.info("🔥 Shub's Life Coach Bot is LIVE")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
