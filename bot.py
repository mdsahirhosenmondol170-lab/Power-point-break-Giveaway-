# =============================================================
#  POWER POINT BREAK — GIVEAWAY BOT
#  AUTHOR : POWER POINT BREAK (MINEXX)
#  VERSION: FULL PREMIUM GIVEAWAY SYSTEM
#  PART   : 1 / FULL
# =============================================================

import os
import json
import asyncio
from datetime import datetime, timedelta
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ChatPermissions
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# =============================================================
# ✅ CONFIGURATION — MUST CHANGE BEFORE USE
# =============================================================

BOT_TOKEN       = "8373078905:AAH3JTi0IvXxQGTzEtXYdLNC3W34-QEcitE"
ADMIN_ID        = 5692210187
ADMIN_USERNAME  = "MinexxProo"
CHANNEL_ID      =  -1003180933712    # Must add bot as admin here

# Multiple Admins supported
ADMINS = {ADMIN_ID}

# =============================================================
# ✅ DATA FILES (LOCAL STORAGE)
# =============================================================

WINNERS_FILE = "winners.txt"
USERS_FILE   = "joined_users.json"
ADMINS_FILE  = "admins.json"

# =============================================================
# ✅ CORE STATE VARIABLES
# =============================================================

giveaway_on       = False           # /on → TRUE
restart_mode      = False
winner_limit      = 10

winners           = []              # stored winners
joined_users      = set()           # to prevent re-entry

# second post + countdown scheduling
pending_post_text  = None
pending_seconds    = 0
second_post_text   = None
second_seconds     = 0

post_waiting       = False
time_waiting       = False
spost_waiting      = False
spost_time_waiting = False

countdown_msg_id   = None

# =============================================================
# ✅ INTERNAL UTILS
# =============================================================

def is_admin(uid):
    """Check if User is Admin"""
    return uid in ADMINS

def now_time():
    """Readable time format"""
    return datetime.now().strftime("%I:%M:%S %p")

def winner_entry(username, uid):
    """Formatted winner entry"""
    return f"{username} | {uid} | {now_time()}"

def save_winner(text):
    """Append winner in file"""
    with open(WINNERS_FILE, "a") as f:
        f.write(text + "\n")

def save_users():
    """Store joined user IDs"""
    with open(USERS_FILE, "w") as f:
        json.dump(list(joined_users), f)

def load_users():
    global joined_users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r") as f:
                joined_users = set(json.load(f))
        except:
            joined_users = set()

def save_admins():
    with open(ADMINS_FILE, "w") as f:
        json.dump(list(ADMINS), f)

def load_admins():
    global ADMINS
    if os.path.exists(ADMINS_FILE):
        try:
            with open(ADMINS_FILE, "r") as f:
                ADMINS = set(json.load(f))
        except:
            pass

# Load cache
load_users()
load_admins()

# =============================================================
# ✅ START MESSAGE + JOIN BUTTON
# =============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    kb = [
        [
            InlineKeyboardButton(
                "🚀 Join Giveaway ✅",
                callback_data="join_btn"
            )
        ]
    ]
    mark = InlineKeyboardMarkup(kb)

    txt = (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👋 Welcome To Power Point Break Giveaway!\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Hello @{user.username} 🎉\n"
        f"🆔 User ID: {user.id}\n\n"
        "📩 To participate in the giveaway,\n"
        "👉 Tap the button below!\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "🚀🌟 Join the Giveaway Now!\n"
        "🎁🏆 Don’t miss your chance to win!\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "✅ If selected, you will be notified instantly!\n\n"
        "💬 Need help? Contact:\n"
        f"👉 @{ADMIN_USERNAME}\n\n"
        "🍀 Good luck!\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    try:
        await update.message.reply_text(txt, reply_markup=mark)
    except:
        await update.callback_query.message.reply_text(txt, reply_markup=mark)

# =============================================================
# ✅ JOIN BUTTON HANDLER
# =============================================================

async def join_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winners, winner_limit, giveaway_on

    q = update.callback_query
    user = q.from_user
    uid  = user.id
    uname = f"@{user.username}" if user.username else user.first_name

    await q.answer()

    # Already participated
    if uid in joined_users:
        txt = (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ You have already participated!\n\n"
            "📩 For any concerns, contact:\n"
            f"👉 @{ADMIN_USERNAME}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        return await q.message.reply_text(txt)

    # Add user
    joined_users.add(uid)
    save_users()

    # Notify admin
    notify = (
        "📥 NEW ENTRY RECEIVED\n"
        f"👤 User: {uname}\n"
        f"🆔 ID: {uid}\n"
        f"⏰ Time: {now_time()}"
    )
    try:
        await context.bot.send_message(chat_id=ADMIN_ID, text=notify)
    except:
        pass

    # If giveaway is not ON
    if not giveaway_on:
        return await q.message.reply_text(
            "✅ You have successfully joined!\n"
            "Please wait for the next Giveaway! 🍀"
        )

    # Winner slot available
    if len(winners) < winner_limit:
        entry = winner_entry(uname, uid)
        winners.append(entry)
        save_winner(entry)

        txt = (
            "🎉 CONGRATULATIONS 🎉\n"
            "You are a WINNER of our Giveaway! 🏆\n\n"
            f"👤 Username: {uname}\n"
            f"🆔 User ID: {uid}\n\n"
            "📩 Contact Admin to claim prize:\n"
            f"👉 @{ADMIN_USERNAME}\n\n"
            "💙 Hosted by: Power Point Break"
        )
        try:
            await context.bot.send_message(chat_id=uid, text=txt)
        except:
            pass

        # Notify admin
        try:
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=(
                    "🏆 NEW WINNER!\n\n"
                    f"👤 {uname}\n"
                    f"🆔 {uid}\n"
                    f"⏰ {now_time()}"
                )
            )
        except:
            pass

    else:
        txt = (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "😔 Oops! All winners are already selected!\n"
            "🎉 Thanks for joining!\n\n"
            "🍀 Try again next giveaway!\n"
            "💙 Power Point Break\n\n"
            "📞 Support:\n"
            f"👉 @{ADMIN_USERNAME}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        return await q.message.reply_text(txt)

# =============================================================
# ✅ ADMIN — START/STOP GIVEAWAY
# =============================================================

async def cmd_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, winners, joined_users, restart_mode

    uid = update.effective_user.id
    if not is_admin(uid):
        return await update.message.reply_text("❌ Admin only")

    giveaway_on = True
    restart_mode = False
    winners = []
    joined_users = set()
    save_users()

    await update.message.reply_text(
        "✅ Giveaway STARTED!\n"
        f"Winner Limit: {winner_limit}\n\n"
        "⏳ Waiting for participants..."
    )


async def cmd_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, restart_mode

    uid = update.effective_user.id
    if not is_admin(uid):
        return await update.message.reply_text("❌ Admin only")

    giveaway_on = False
    restart_mode = False

    await update.message.reply_text("🛑 Giveaway turned OFF!")


# =============================================================
# ✅ SET WINNER COUNT
# =============================================================

async def setwinner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winner_limit
    uid = update.effective_user.id

    if not is_admin(uid):
        return await update.message.reply_text("❌ Admin only")

    try:
        n = int(context.args[0])
        winner_limit = n
    except:
        return await update.message.reply_text("❌ Usage: /setwinner 10")

    await update.message.reply_text(
        f"✅ Winner limit set to **{winner_limit}**"
    )


# =============================================================
# ✅ SEND ADMIN PANEL WHEN FULL
# =============================================================

async def send_approve_panel(context: ContextTypes.DEFAULT_TYPE):
    global winners, winner_limit, CHANNEL_ID

    if len(winners) < winner_limit:
        return

    # Winner list preview
    msg = "━━━━━━━━━━━━━━━━━━━━━━\n"
    msg += "🏆 Power Point Break — Giveaway Winners\n"
    msg += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for i, w in enumerate(winners, start=1):
        msg += f"#{i} {w}\n"

    msg += "\n✅ Approve post to channel?\n"

    kb = [
        [
            InlineKeyboardButton("✅ Approve", callback_data="approve_post"),
            InlineKeyboardButton("❌ Reject", callback_data="reject_post")
        ]
    ]
    mark = InlineKeyboardMarkup(kb)

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=msg,
            reply_markup=mark
        )
    except:
        pass


# =============================================================
# ✅ APPROVE / REJECT
# =============================================================

async def approve_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winners, CHANNEL_ID

    q = update.callback_query
    uid = q.from_user.id

    if not is_admin(uid):
        return await q.answer("❌ Admin only", show_alert=True)

    # Prepare final post
    txt = "━━━━━━━━━━━━━━━━━━━━━━\n"
    txt += "🏆 **Giveaway Winners Announced!**\n"
    txt += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

    for i, w in enumerate(winners, start=1):
        txt += f"#{i} {w}\n"

    txt += (
        "\n🎉 Congratulations to all!\n"
        f"🎙 Hosted by: Power Point Break\n"
        f"👑 Admin: @{ADMIN_USERNAME}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    # Post to channel
    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=txt)
    except:
        pass

    await q.message.reply_text("✅ Posted Successfully!")


async def reject_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    uid = q.from_user.id

    if not is_admin(uid):
        return await q.answer("❌ Admin only", show_alert=True)

    await q.message.reply_text("❌ Giveaway Cancelled!")


# =============================================================
# ✅ CALLBACK Router
# =============================================================

async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query.data

    if q == "join_btn":
        return await join_button(update, context)
    if q == "approve_post":
        return await approve_handler(update, context)
    if q == "reject_post":
        return await reject_handler(update, context)

# =============================================================
# ✅ ADMIN — ADD / REMOVE ADMIN
# =============================================================

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return await update.message.reply_text("❌ Only Admin can use this.")

    try:
        new = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Usage: /addadmin <user_id>")

    ADMINS.add(new)
    save_admins()

    await update.message.reply_text(f"✅ Added new admin: `{new}`")


async def del_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return await update.message.reply_text("❌ Only Admin can use this.")

    try:
        rem = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Usage: /deladmin <user_id>")

    if rem in ADMINS:
        ADMINS.remove(rem)
        save_admins()
        await update.message.reply_text(f"✅ Removed Admin: `{rem}`")
    else:
        await update.message.reply_text("❌ User is not an admin!")


# =============================================================
# ✅ /HELP — ADMIN ONLY
# =============================================================

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if not is_admin(uid):
        return await update.message.reply_text("❌ Admin only")

    txt = (
        "✅ **Admin Commands:**\n\n"
        "/on  – Start Giveaway\n"
        "/off – Stop Giveaway\n"
        "/setwinner <num> – Set winner count\n"
        "/addadmin <id> – Add new admin\n"
        "/deladmin <id> – Remove admin\n"
        "/resetlist – Clear past participants\n"
        "/setpost – Set first post + countdown\n"
        "/spost – Set final post for auto publish\n"
        "/help – Show admin commands\n"
    )
    await update.message.reply_text(txt)


# =============================================================
# ✅ RESET JOIN LIST (NEW GIVEAWAY)
# =============================================================

async def resetlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global joined_users, winners

    uid = update.effective_user.id
    if not is_admin(uid):
        return await update.message.reply_text("❌ Admin only")

    joined_users = set()
    winners = []
    save_users()

    # Clear winners file
    open(WINNERS_FILE, "w").close()

    await update.message.reply_text("✅ All user data cleared!")


# =============================================================
# ✅ RESTART MODE → USER MUST PRESS START
# =============================================================

async def restart_giveaway():
    """Used when next giveaway starts → Notify all users to click again."""
    pass


# =============================================================
# ✅ START NEW GIVEAWAY MSG TO USERS
# =============================================================

async def send_restart_msg(context: ContextTypes.DEFAULT_TYPE):
    """Broadcast starter message to joined users."""
    global joined_users

    msg = (
        "🚀 New Giveaway Started!\n\n"
        "✨ Please tap below to join again:"
    )

    kb = [
        [
            InlineKeyboardButton(
                "🚀 Join Again ✅",
                callback_data="join_btn"
            )
        ]
    ]

    mark = InlineKeyboardMarkup(kb)

    # DM all previous users
    for uid in list(joined_users):
        try:
            await context.bot.send_message(chat_id=uid, text=msg, reply_markup=mark)
        except:
            pass


# =============================================================
# ✅ SECOND POST — STORE TEXT
# =============================================================

async def spost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global spost_waiting

    uid = update.effective_user.id
    if not is_admin(uid):
        return await update.message.reply_text("❌ Admin only")

    spost_waiting = True
    await update.message.reply_text("📩 Send second post content now…")


# =============================================================
# ✅ STORE FIRST POST
# =============================================================

async def setpost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global post_waiting

    uid = update.effective_user.id
    if not is_admin(uid):
        return await update.message.reply_text("❌ Admin only")

    post_waiting = True
    await update.message.reply_text("📨 Send first post text now…")


# =============================================================
# ✅ CAPTURE POST / SECOND POST
# =============================================================

async def capture_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global post_waiting, pending_post_text

    if not post_waiting:
        return

    pending_post_text = update.message.text
    post_waiting = False

    await update.message.reply_text(
        "✅ Post saved!\n"
        "Now send time like 10s / 1m / 1h\n"
        "(Use /settime <value>)"
    )


async def capture_spost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global spost_waiting, second_post_text

    if not spost_waiting:
        return

    second_post_text = update.message.text
    spost_waiting = False

    await update.message.reply_text("✅ Second post saved!")


# =============================================================
# ✅ SET TIME COMMAND
# =============================================================

async def settime(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_seconds

    uid = update.effective_user.id
    if not is_admin(uid):
        return await update.message.reply_text("❌ Admin only")

    try:
        t = context.args[0]
    except:
        return await update.message.reply_text("❌ Usage: /settime 10s/1m/1h")

    num = int(t[:-1])
    unit = t[-1]

    if unit == "s":
        pending_seconds = num
    elif unit == "m":
        pending_seconds = num * 60
    elif unit == "h":
        pending_seconds = num * 3600
    else:
        return await update.message.reply_text("❌ format -> 10s / 1m / 1h")

    await update.message.reply_text(f"✅ Time set: {pending_seconds}s")

# =============================================================
# ✅ COUNTDOWN + PROGRESS BAR
# =============================================================

async def countdown_worker(context: ContextTypes.DEFAULT_TYPE):
    """Runs first countdown + posts second after finish."""
    global pending_seconds, pending_post_text, second_post_text, CHANNEL_ID

    if not pending_seconds or not pending_post_text:
        return

    msg = await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text="⏳ Giveaway Starting Soon..."
    )

    remaining = pending_seconds

    while remaining > 0:
        mins, secs = divmod(remaining, 60)
        hrs, mins = divmod(mins, 60)

        t = f"{hrs:02}:{mins:02}:{secs:02}"

        # progress bar
        try:
            percent = int(((pending_seconds - remaining) / pending_seconds) * 100)
        except:
            percent = 0

        filled = int(percent / 5)
        bar = "▰" * filled + "▱" * (20 - filled)

        countdown_text = (
            "🚀  Giveaway Starting Soon…\n"
            f"⏰ {t}\n"
            f"{bar}"
        )

        try:
            await context.bot.edit_message_text(
                chat_id=CHANNEL_ID,
                message_id=msg.message_id,
                text=countdown_text
            )
        except:
            pass

        await asyncio.sleep(1)
        remaining -= 1

    # COUNTDOWN DONE → POST FIRST POST
    try:
        await context.bot.edit_message_text(
            chat_id=CHANNEL_ID,
            message_id=msg.message_id,
            text=pending_post_text
        )
    except:
        pass

    # SECOND AUTO-POST IF EXISTS
    if second_post_text:
        try:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=second_post_text
            )
        except:
            pass


# =============================================================
# ✅ START COUNTDOWN
# =============================================================

async def start_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_seconds, pending_post_text

    uid = update.effective_user.id
    if not is_admin(uid):
        return await update.message.reply_text("❌ Admin only")

    if not pending_post_text:
        return await update.message.reply_text("❌ Post not set. Use /setpost")

    if not pending_seconds:
        return await update.message.reply_text("❌ Time not set. Use /settime")

    await update.message.reply_text("✅ Countdown started…")

    # create async task
    context.application.create_task(countdown_worker(context))


# =============================================================
# ✅ CAPTURE TIME FROM MESSAGE
# =============================================================

async def capture_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_seconds, time_waiting

    if not time_waiting:
        return

    t = update.message.text.strip()

    try:
        num = int(t[:-1])
        unit = t[-1]

        if unit == "s":
            pending_seconds = num
        elif unit == "m":
            pending_seconds = num * 60
        elif unit == "h":
            pending_seconds = num * 3600
        else:
            return await update.message.reply_text(
                "❌ Format → 10s / 1m / 1h"
            )

        time_waiting = False
        await update.message.reply_text("✅ Time updated!")

    except:
        await update.message.reply_text("❌ Invalid time value!")


# =============================================================
# ✅ ROUTERS → RAW MSG STACK
# =============================================================

async def user_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    User normal message → ignore.
    """
    pass


# =============================================================
# ✅ REGISTER HANDLERS
# =============================================================

def setup_handlers(app):

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", cmd_on))
    app.add_handler(CommandHandler("off", cmd_off))
    app.add_handler(CommandHandler("setwinner", setwinner))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("resetlist", resetlist))
    app.add_handler(CommandHandler("addadmin", add_admin))
    app.add_handler(CommandHandler("deladmin", del_admin))
    app.add_handler(CommandHandler("setpost", setpost))
    app.add_handler(CommandHandler("spost", spost))
    app.add_handler(CommandHandler("settime", settime))
    app.add_handler(CommandHandler("startcount", start_count))

    app.add_handler(CallbackQueryHandler(callback_router))

    # This order is IMPORTANT
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_time))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_post))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_spost))

    # last
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_msg))


# =============================================================
# ✅ MAIN APP
# =============================================================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    setup_handlers(app)
    print("✅ Giveaway Bot Running…")
    app.run_polling()


if __name__ == "__main__":
    main()





