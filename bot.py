"""
Shub's Personal Life Coach Bot 🔥
New schedule: Wake 10 AM, Sleep 2 AM
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
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
IST = pytz.timezone("Asia/Kolkata")

SCHEDULE = [
    {
        "time": time(10, 0),
        "emoji": "🌅",
        "title": "WAKE UP",
        "message": (
            "🌅 *10:00 AM — WAKE UP SHUB!*\n\n"
            "No phone for 15 minutes.\n"
            "Drink water. Stretch. Breathe.\n\n"
            "You're waking up at 10 AM now.\n"
            "That's 3 hours earlier than before.\n"
            "_This is already a win. Now build on it._ 🔥"
        ),
        "buttons": [("✅ I'm up!", "up"), ("😴 5 more min", "snooze")]
    },
    {
        "time": time(10, 30),
        "emoji": "🍳",
        "title": "BREAKFAST",
        "message": (
            "🍳 *10:30 AM — EAT SOMETHING.*\n\n"
            "No gym on empty stomach.\n"
            "Quick meal — eggs, roti, anything real.\n"
            "Fuel your body. It's going to work today. 💪"
        ),
        "buttons": [("✅ Eating now", "eat_yes")]
    },
    {
        "time": time(11, 15),
        "emoji": "💪",
        "title": "GYM TIME",
        "message": (
            "💪 *11:15 AM — GYM. LET'S GO.*\n\n"
            "You have 2.5 hours before your study block.\n"
            "30-45 minutes is all you need.\n\n"
            "Gym bag. Shoes. Out the door.\n"
            "_The version of you that goes to gym today\n"
            "is the version that gets rich._ 🏋️"
        ),
        "buttons": [("💪 Going!", "gym_yes"), ("🏠 Home workout", "gym_home"), ("❌ Skipping", "gym_skip")]
    },
    {
        "time": time(13, 0),
        "emoji": "📚",
        "title": "STUDY BLOCK",
        "message": (
            "📚 *1:00 PM — STUDY TIME.*\n\n"
            "One module. 60 minutes. That's it.\n"
            "Close Instagram. Close YouTube.\n\n"
            "Open your Data Science course RIGHT NOW.\n"
            "Set a timer. Start.\n\n"
            "_1 module/week = 52 modules/year.\n"
            "That's a complete education._ 🎓"
        ),
        "buttons": [("📖 Starting!", "study_yes"), ("⏭️ Doing project instead", "study_proj")]
    },
    {
        "time": time(14, 15),
        "emoji": "🐙",
        "title": "GITHUB COMMIT",
        "message": (
            "🐙 *2:15 PM — PUSH TO GITHUB.*\n\n"
            "One commit. Even one line changed.\n"
            "Your GitHub graph is your public resume.\n\n"
            "Open VS Code → make a change → push.\n"
            "_Recruiters look at GitHub. Make them see green._ ✅"
        ),
        "buttons": [("✅ Pushed!", "github_yes"), ("🔄 Still working", "github_wip")]
    },
    {
        "time": time(15, 30),
        "emoji": "🍽️",
        "title": "LUNCH + PREP FOR WORK",
        "message": (
            "🍽️ *3:30 PM — EAT + GET READY.*\n\n"
            "Lunch time. Then get work-ready.\n"
            "You already did more today than most people.\n\n"
            "Gym ✅ Study ✅ GitHub ✅\n"
            "_Now go earn that salary._ 💼"
        ),
        "buttons": [("💼 Ready for work", "work_ready")]
    },
    {
        "time": time(16, 0),
        "emoji": "💼",
        "title": "WORK STARTS",
        "message": (
            "💼 *4:00 PM — WORK TIME.*\n\n"
            "You already crushed your personal goals today.\n"
            "Now be a professional. Stay focused.\n"
            "See you at 1 AM. 🌙"
        ),
        "buttons": [("👊 Let's go", "work_start")]
    },
    {
        "time": time(1, 10),
        "emoji": "🌙",
        "title": "WORK DONE",
        "message": (
            "🌙 *1:10 AM — JOB DONE.*\n\n"
            "Good work today. Seriously.\n\n"
            "Now wind down:\n"
            "→ No doom scrolling\n"
            "→ Write 3 tasks for tomorrow (10 min)\n"
            "→ In bed by 2 AM\n\n"
            "_You sleep at 2 AM now. That's the new you._ 😴"
        ),
        "buttons": [("📝 Planning now", "plan_yes"), ("😴 Too tired", "plan_tired")]
    },
    {
        "time": time(1, 45),
        "emoji": "😴",
        "title": "SLEEP REMINDER",
        "message": (
            "😴 *1:45 AM — 15 MINUTES TO SLEEP.*\n\n"
            "Wrap up whatever you're doing.\n"
            "Brush teeth. Put the phone down.\n\n"
            "Target: asleep by 2:00 AM.\n"
            "Wake up at 10:00 AM.\n"
            "8 hours of sleep = a weapon. 🔋"
        ),
        "buttons": [("😴 Going to sleep", "sleep_yes"), ("📱 Few more mins", "sleep_late")]
    },
]

BUTTON_REPLIES = {
    "up": "LET'S GO! 🔥 Breakfast in 30 min, gym by 11:15. You're already ahead of yesterday.",
    "snooze": "5 minutes. That's it. When the alarm hits — feet on the floor. No negotiation. ⏰",
    "eat_yes": "Good. Fuel = performance. Gym in 45 minutes. Don't waste this energy. 💪",
    "gym_yes": "YESSS! That's the builder! 💪 Tell me how it goes. Every session counts.",
    "gym_home": "Home workout is 100% valid! Push-ups, squats, anything. You showed up. ✅",
    "gym_skip": "Okay. No lecture. But write down WHY you skipped — that reason is what we fix next week. 📝",
    "study_yes": "LOCKED IN. 📚 60-minute timer. One module. No distractions. You've got this.",
    "study_proj": "Project work counts! Push that commit too. Both are progress. 🐙",
    "github_yes": "COMMIT PUSHED! 🎉 That green square is yours forever. Screenshot it. LinkedIn post?",
    "github_wip": "Keep going! WIP commits count too. Push what you have. Done > Perfect. 💻",
    "work_ready": "You already won today before work even started. Go be great. 💼",
    "work_start": "Professional mode ON. See you on the other side. 🌙",
    "plan_yes": "3 tasks. Written down. Future-you says thank you. Sleep well. 📝",
    "plan_tired": "That's okay. Rest is recovery. Tomorrow we go again. Sleep by 2 AM. 🌙",
    "sleep_yes": "Good. 8 hours. See you at 10 AM sharp. 💪",
    "sleep_late": "10 minutes MAX. Then phone down. 2 AM is the line. Don't cross it. 😴",
}

SUNDAY_CHECKIN = (
    "☀️ *SUNDAY CHECK-IN — HONEST REVIEW*\n\n"
    "No BS. Just truth.\n\n"
    "This week:\n"
    "🐙 GitHub commits: ?\n"
    "💪 Gym sessions: ?\n"
    "📚 Course modules: ?\n"
    "😴 Slept by 2 AM: ? nights\n"
    "🌅 Woke by 10 AM: ? days\n\n"
    "Reply with your numbers. I'll tell you exactly what to fix. 💪"
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"🔥 *SHUB'S LIFE COACH BOT IS LIVE*\n\n"
        f"Your Chat ID: `{chat_id}`\n\n"
        f"Your new daily schedule:\n"
        f"• 🌅 10:00 AM — Wake up\n"
        f"• 🍳 10:30 AM — Breakfast\n"
        f"• 💪 11:15 AM — Gym\n"
        f"• 📚 1:00 PM — Study block\n"
        f"• 🐙 2:15 PM — GitHub commit\n"
        f"• 🍽️ 3:30 PM — Lunch + work prep\n"
        f"• 💼 4:00 PM — Job starts\n"
        f"• 🌙 1:10 AM — Job ends, wind down\n"
        f"• 😴 2:00 AM — SLEEP\n\n"
        f"Commands:\n"
        f"/status — What you should do RIGHT NOW\n"
        f"/checkin — Log today's wins\n"
        f"/linkedin — Generate a LinkedIn post\n"
        f"/project — Next data science project idea\n\n"
        f"Let's change your life. 💪",
        parse_mode="Markdown"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now(IST)
    hour = now.hour
    minute = now.minute

    if hour == 10 and minute < 30:
        current = "🌅 Wake up ritual — no phone, water, stretch"
    elif hour == 10:
        current = "🍳 Breakfast time — eat before gym"
    elif hour == 11 or (hour == 12 and minute < 30):
        current = "💪 GYM — you should be working out right now"
    elif hour == 13 or (hour == 14 and minute < 15):
        current = "📚 Study block — open your course NOW"
    elif hour == 14 or (hour == 15 and minute < 30):
        current = "🐙 GitHub commit time — push something"
    elif hour == 15:
        current = "🍽️ Lunch + getting ready for work"
    elif hour >= 16 and hour <= 23:
        current = "💼 Work shift — stay focused"
    elif hour == 1 and minute < 45:
        current = "🌙 Wind down — plan tomorrow, sleep by 2 AM"
    elif hour == 1 and minute >= 45:
        current = "😴 SLEEP TIME — phone down NOW"
    elif hour == 2 or hour == 3:
        current = "😴 You should be ASLEEP. Phone down."
    else:
        current = "😴 Sleep time — rest up for tomorrow"

    await update.message.reply_text(
        f"⏰ *RIGHT NOW — {now.strftime('%I:%M %p')} IST*\n\n"
        f"You should be: {current}",
        parse_mode="Markdown"
    )

async def linkedin_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📝 *LINKEDIN POST*\n\n"
        "Tell me what you completed today and I'll write the full post.\n\n"
        "Example:\n'Finished EDA on NYC Taxi data — found night trips have 23% higher tips'\n\n"
        "What did you do? 👇",
        parse_mode="Markdown"
    )

async def project_idea(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🚀 *YOUR NEXT PROJECT IDEAS*\n\n"
        "You're doing NYC Taxi EDA. After that:\n\n"
        "1. 🚕 *Trip Duration ML Model* — predict trip time using your taxi data\n"
        "2. 🏏 *IPL Stats Dashboard* — Indians love cricket, LinkedIn will too\n"
        "3. 📈 *NIFTY50 Stock EDA* — finance + data = great combo\n"
        "4. 🛒 *Customer Churn Predictor* — classic ML, loved by recruiters\n"
        "5. 🍽️ *Zomato Delhi Analysis* — local data, personal angle\n\n"
        "Each = 1 week = 1 GitHub repo = 1 LinkedIn post.\n\n"
        "Which one? Reply with the number. 💪",
        parse_mode="Markdown"
    )

async def checkin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🌅 Woke up by 10 AM", callback_data="ci_wake")],
        [InlineKeyboardButton("💪 Went to Gym", callback_data="ci_gym")],
        [InlineKeyboardButton("📚 Completed Study", callback_data="ci_study")],
        [InlineKeyboardButton("🐙 Pushed to GitHub", callback_data="ci_github")],
        [InlineKeyboardButton("😴 Slept by 2 AM", callback_data="ci_sleep")],
    ]
    await update.message.reply_text(
        "✅ *DAILY CHECK-IN*\n\nWhat did you complete today?",
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="Markdown"
    )

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    checkin_replies = {
        "ci_wake": "🌅 Woke at 10 AM logged! That's 3 hours earlier than before. MASSIVE win. Keep this streak!",
        "ci_gym": "💪 Gym logged! Most important habit. Protect this at all costs.",
        "ci_study": "📚 Study logged! One module closer to that data science job. Keep going.",
        "ci_github": "🐙 GitHub commit logged! Green square secured. Screenshot that contribution graph.",
        "ci_sleep": "😴 Slept by 2 AM logged! 8 hours incoming. Recovery = performance.",
    }

    if data in BUTTON_REPLIES:
        await query.message.reply_text(BUTTON_REPLIES[data])
    elif data in checkin_replies:
        await query.message.reply_text(checkin_replies[data])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.lower()
    if any(w in text for w in ["procrastinat", "can't start", "stuck", "lazy", "not doing", "cant"]):
        await update.message.reply_text(
            "🎯 *STOP. DO THIS RIGHT NOW.*\n\n"
            "1. Set a 2-minute timer on your phone\n"
            "2. Open your laptop\n"
            "3. Do ANYTHING — open the course, open VS Code\n\n"
            "You don't need to feel ready.\n"
            "You just need to START.\n\n"
            "_Go. I'll check on you._ ⏱️",
            parse_mode="Markdown"
        )
    elif any(w in text for w in ["linkedin", "post", "content"]):
        await linkedin_post(update, context)
    elif any(w in text for w in ["project", "idea", "build", "github"]):
        await project_idea(update, context)
    else:
        await update.message.reply_text(
            "I'm here. 💪\n\n"
            "/status — What to do right now\n"
            "/checkin — Log your wins\n"
            "/linkedin — Get a LinkedIn post\n"
            "/project — Next project idea"
        )

async def send_reminder(app, message_text, buttons=None):
    if not CHAT_ID:
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
    jq = app.job_queue
    for item in SCHEDULE:
        t = item["time"].replace(tzinfo=IST)
        jq.run_daily(
            callback=lambda ctx, msg=item["message"], btns=item.get("buttons"): send_reminder(app, msg, btns),
            time=t,
            name=item["title"]
        )
        logger.info(f"Scheduled: {item['title']} at {item['time']}")

    # Sunday 10 AM check-in
    jq.run_daily(
        callback=lambda ctx: send_reminder(app, SUNDAY_CHECKIN),
        time=time(10, 0, tzinfo=IST),
        days=(6,),
        name="Sunday Check-in"
    )
    logger.info("All reminders scheduled ✅")

def main():
    if not TOKEN:
        raise ValueError("Set TELEGRAM_BOT_TOKEN in environment!")

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
