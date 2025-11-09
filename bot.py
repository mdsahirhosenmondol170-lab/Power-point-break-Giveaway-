# ============================================================
#   POWER POINT BREAK — GIVEAWAY BOT
#   FULL VERSION — PART 1
#   Author: @MinexxProo
# ============================================================

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)
import asyncio
from datetime import datetime, timedelta

# ============================================================
# CONFIG
# ============================================================

BOT_TOKEN = "8373078905:AAH3JTi0IvXxQGTzEtXYdLNC3W34-QEcitE"     # <-- change
ADMIN_ID = 5692210187             # <-- change
ADMIN_USERNAME = "MinexxProo"    # <-- change
CHANNEL_ID =  -1003180933712      # <-- change

# ============================================================
# GLOBAL STATES
# ============================================================

giveaway_on = False
restart_mode = False
winner_limit = 10

winners = []
joined_users = set()

pending_post_text = None
pending_seconds = 0
second_post_text = None
countdown_message_id = None

bad_words = ["fuck", "sex", "bitch", "nude", "porn", "সেক্স", "চুদ"]


# ============================================================
# HELPERS
# ============================================================

def contains_bad_word(text: str):
    try:
        t = text.lower()
        return any(w in t for w in bad_words)
    except:
        return False


def parse_time_str(t):
    """Convert `10s`, `5m`, `1h` → seconds"""
    try:
        t = t.lower()
        if t.endswith("s"):
            return int(t[:-1])
        if t.endswith("m"):
            return int(t[:-1]) * 60
        if t.endswith("h"):
            return int(t[:-1]) * 3600
    except:
        return None
    return None


# ============================================================
# START SCREEN
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id
    uname = f"@{user.username}" if user.username else uid

    text = (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👋 Welcome To Power Point Break Giveaway!\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Hello {uname} 🎉\n"
        f"🆔 User ID: {uid}\n\n"
        "📩 To participate in the giveaway,\n"
        "👉 Press the button below 👇\n\n"
        "Good luck! 🍀\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    kb = [
        [InlineKeyboardButton("🎁 Join Giveaway Now", callback_data="join")]
    ]

    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))


# ============================================================
# /on — START GIVEAWAY
# ============================================================

async def on_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, restart_mode, winners, joined_users

    user = update.effective_user
    if user.id != ADMIN_ID:
        return

    giveaway_on = True
    restart_mode = True
    winners.clear()
    joined_users.clear()

    await update.message.reply_text(
        "✅ Giveaway Started!\n"
        "➡ Restart Mode Enabled\n"
        "➡ Waiting for users to press START"
    )


# ============================================================
# ASK RESTART
# ============================================================

async def ask_restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """When giveaway restarted — users must press Start Again button"""

    kb = [
        [InlineKeyboardButton("⚡ Start Again", callback_data="restart_go")]
    ]

    msg = (
        "⚠️ Giveaway Restarted!\n"
        "Please press START AGAIN ⬇️"
    )

    if hasattr(update, "message") and update.message:
        await update.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb))
    else:
        await update.callback_query.message.reply_text(msg, reply_markup=InlineKeyboardMarkup(kb))


# ============================================================
# RESTART CONFIRM
# ============================================================

async def restart_go(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global restart_mode
    await update.callback_query.answer()

    restart_mode = False

    text = (
        "✅ You are ready again!\n\n"
        "Press JOIN to participate."
    )

    kb = [
        [InlineKeyboardButton("🎁 Join Giveaway Now", callback_data="join")]
    ]

    await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(kb))


# ============================================================
# WINNER FORMAT
# ============================================================

def format_winner_list():
    if len(winners) == 0:
        return "No winners yet."

    txt = (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🏆 Power Point Break — Giveaway Winners\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
    )

    for i, w in enumerate(winners, start=1):
        txt += f"#{i} {w['username']} | {w['id']} | {w['time']}\n"

    txt += (
        "\n🎉 Congratulations to all!\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🔰 Hosted By: Power Point Break\n"
        f"📌 Signature: @{ADMIN_USERNAME}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    return txt


# ============================================================
# JOIN GIVEAWAY — MAIN LOGIC
# ============================================================

async def join_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE, from_callback=False):
    global giveaway_on, restart_mode, winner_limit, winners, joined_users

    if not giveaway_on:
        msg = (
            "❌ GIVEAWAY CLOSED ❌\n"
            f"📩 Please contact @{ADMIN_USERNAME}\n"
        )
        return await _reply(update, msg, from_callback)

    # Restart flow
    if restart_mode:
        return await ask_restart(update, context)

    user = update.effective_user
    uid = user.id
    uname = f"@{user.username}" if user.username else uid

    # Already joined
    if uid in joined_users:
        return await _reply(
            update,
            "⚠️ You have already participated!\n"
            f"Contact admin: @{ADMIN_USERNAME}",
            from_callback
        )

    # Winner full
    if len(winners) >= winner_limit:
        return await _reply(
            update,
            "😔 Oops! All winners are already selected!\n"
            f"📞 Admin: @{ADMIN_USERNAME}",
            from_callback
        )

    # Valid join
    joined_users.add(uid)
    now = datetime.now().strftime("%I:%M:%S %p")
    winners.append({"id": uid, "username": uname, "time": now})

    await _reply(update, "🎉 CONGRATULATIONS! YOU ARE A WINNER! 🏆", from_callback)

    # Notify admin
    txt = f"📩 NEW WINNER!\n{uname} | {uid} | {now}"
    await context.bot.send_message(chat_id=ADMIN_ID, text=txt)

    # When full → ask admin approve
    if len(winners) == winner_limit:
        await ask_admin_approve(context)


async def _reply(update, text, from_callback):
    if from_callback:
        await update.callback_query.message.reply_text(text)
    else:
        await update.message.reply_text(text)


# ============================================================
# ASK ADMIN APPROVE
# ============================================================

async def ask_admin_approve(context: ContextTypes.DEFAULT_TYPE):
    text = (
        "✅ Winner List Complete!\n\n"
        "Approve to post?"
    )

    kb = [
        [
            InlineKeyboardButton("✅ Approve", callback_data="approve"),
            InlineKeyboardButton("❌ Reject", callback_data="reject")
        ]
    ]

    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=text,
        reply_markup=InlineKeyboardMarkup(kb)
    )
# ============================================================
# ADMIN APPROVE / REJECT
# ============================================================

async def approve_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, restart_mode

    await update.callback_query.answer()

    wl = format_winner_list()

    # POST TO CHANNEL
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=wl
        )
    except:
        await update.callback_query.message.reply_text(
            "❌ Failed to post to channel"
        )
        return

    await update.callback_query.message.reply_text(
        "✅ Winner List Posted Successfully!"
    )

    giveaway_on = False
    restart_mode = False


async def reject_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await update.callback_query.message.reply_text(
        "❌ Winner List Rejected!"
    )


# ============================================================
# /off — STOP GIVEAWAY
# ============================================================

async def off_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on
    if update.effective_user.id != ADMIN_ID:
        return

    giveaway_on = False

    await update.message.reply_text(
        "✅ Giveaway Stopped!\n"
        "No new messages will be processed."
    )


# ============================================================
# /resetlist
# ============================================================

async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winners, joined_users
    if update.effective_user.id != ADMIN_ID:
        return

    winners.clear()
    joined_users.clear()

    await update.message.reply_text("✅ Winners Cleared!")


# ============================================================
# ADMIN PANEL
# ============================================================

async def adminpanel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    kb = [
        [InlineKeyboardButton("✅ Show Winners", callback_data="ap_show")],
        [InlineKeyboardButton("♻ Reset Winners", callback_data="ap_reset")],
        [InlineKeyboardButton("🔴 Stop Giveaway", callback_data="ap_off")]
    ]

    await update.message.reply_text(
        "⚙️ Admin Panel",
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def adminpanel_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winners, giveaway_on, joined_users

    q = update.callback_query
    await q.answer()

    action = q.data

    if action == "ap_show":
        wl = format_winner_list()
        await q.message.reply_text(wl)

    elif action == "ap_reset":
        winners.clear()
        joined_users.clear()
        await q.message.reply_text("✅ Winners Reset!")

    elif action == "ap_off":
        giveaway_on = False
        await q.message.reply_text("✅ Giveaway Stopped!")


# ============================================================
# /setwinner
# ============================================================

async def setwinner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winner_limit

    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) == 0:
        return await update.message.reply_text(
            "Usage: /setwinner <number>"
        )

    try:
        winner_limit = int(context.args[0])
        await update.message.reply_text(
            f"✅ Winner limit set to {winner_limit}"
        )
    except:
        await update.message.reply_text("❌ Invalid number!")


# ============================================================
# /setpost → FIRST POST
# ============================================================

async def setpost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_post_text

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "✅ Send giveaway post"
    )
    context.user_data["awaiting_post"] = True


async def capture_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_post_text

    if context.user_data.get("awaiting_post"):
        pending_post_text = update.message.text
        context.user_data["awaiting_post"] = False
        context.user_data["awaiting_time"] = True

        await update.message.reply_text(
            "✅ Post saved!\nNow send time (10s / 5m / 1h)"
        )


# ============================================================
# CAPTURE TIME
# ============================================================

async def capture_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_seconds

    if context.user_data.get("awaiting_time"):
        sec = parse_time_str(update.message.text)

        if not sec:
            return await update.message.reply_text(
                "❌ Invalid time!\nExample: 10s / 5m / 1h"
            )

        pending_seconds = sec
        context.user_data["awaiting_time"] = False

        text = (
            "✅ Review your giveaway:\n\n"
            f"📌 Post:\n{pending_post_text}\n\n"
            f"⏳ Time: {update.message.text}\n\n"
            "Approve to schedule?"
        )

        kb = [
            [
                InlineKeyboardButton("✅ Approve", callback_data="setpost_ok"),
                InlineKeyboardButton("❌ Reject", callback_data="setpost_no")
            ]
        ]

        await update.message.reply_text(
            text,
            reply_markup=InlineKeyboardMarkup(kb)
        )


# ============================================================
# /spost → SECOND POST
# ============================================================

async def spost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global second_post_text

    if update.effective_user.id != ADMIN_ID:
        return

    await update.message.reply_text(
        "✅ Send second post content"
    )
    context.user_data["awaiting_spost"] = True


async def capture_spost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global second_post_text

    if context.user_data.get("awaiting_spost"):
        second_post_text = update.message.text
        context.user_data["awaiting_spost"] = False

        await update.message.reply_text(
            "✅ SECOND POST SAVED!\n"
            "It will auto publish when countdown is done ✅"
        )

# ============================================================
# POST APPROVE / REJECT (SETPOST)
# ============================================================

async def setpost_ok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_post_text, pending_seconds, countdown_message_id

    q = update.callback_query
    await q.answer()

    # ✅ Send first post to Channel
    try:
        sent = await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=pending_post_text
        )
        countdown_message_id = sent.message_id
    except:
        return await q.message.reply_text("❌ Failed to post to channel")

    # ✅ Start countdown
    asyncio.create_task(countdown_job(context))

    await q.message.reply_text(
        "✅ Scheduled Post Published\n"
        "⏳ Countdown Started!"
    )


async def setpost_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_post_text, pending_seconds

    q = update.callback_query
    await q.answer()

    pending_post_text = None
    pending_seconds = 0

    await q.message.reply_text("❌ Cancelled!")


# ============================================================
# COUNTDOWN JOB
# ============================================================

async def countdown_job(context: ContextTypes.DEFAULT_TYPE):
    global pending_seconds, countdown_message_id, second_post_text

    total = pending_seconds

    while pending_seconds > 0:
        mins, secs = divmod(pending_seconds, 60)
        hrs, mins = divmod(mins, 60)
        time_str = f"{hrs:02}:{mins:02}:{secs:02}"

        # Make progress bar
        done = total - pending_seconds
        progress = int((done / total) * 20)
        bar = "▰" * progress + "▱" * (20 - progress)

        txt = (
            "🚀  Giveaway Starting Soon…\n"
            f"⏰ {time_str}\n"
            f"{bar}"
        )

        try:
            await context.bot.edit_message_text(
                chat_id=CHANNEL_ID,
                message_id=countdown_message_id,
                text=txt
            )
        except:
            pass

        await asyncio.sleep(1)
        pending_seconds -= 1

    # ✅ TIME FINISHED
    try:
        await context.bot.edit_message_text(
            chat_id=CHANNEL_ID,
            message_id=countdown_message_id,
            text="✅ TIME UP!\nGiveaway is LIVE NOW! 🎉"
        )
    except:
        pass

    # ✅ Send second post
    if second_post_text:
        try:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=second_post_text
            )
        except:
            pass


# ============================================================
# BAD WORD BLOCK
# ============================================================

async def user_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, restart_mode

    msg = update.message.text or ""

    # ✅ Bad words
    if contains_bad_word(msg):
        return await update.message.reply_text(
            "⚠️ Bad words are NOT allowed ❌\n"
            "You are blocked from giveaway!"
        )

    # Giveaway OFF → ignore
    if not giveaway_on:
        return

    # Restart mode
    if restart_mode:
        return await ask_restart(update, context)

    # If message is normal → treat as join
    await join_giveaway(update, context, from_callback=False)


# ============================================================
# JOIN BUTTON CALLBACK
# ============================================================

async def join_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer()
    await join_giveaway(update, context, from_callback=True)


# ============================================================
# APPROVE / REJECT CALLBACKS
# ============================================================

async def approve_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await approve_post(update, context)


async def reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await reject_post(update, context)


# ============================================================
# SETPOST BUTTON CALLBACK
# ============================================================

async def setpost_approve_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await setpost_ok(update, context)


async def setpost_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await setpost_no(update, context)


# ============================================================
# ADMINPANEL CALLBACK
# ============================================================

async def adminpanel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await adminpanel_buttons(update, context)

# ============================================================
# ============================================================
# /help — SHOW COMMAND LIST (ADMIN ONLY)
# ============================================================

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id != ADMIN_ID:
        return await update.message.reply_text(
            "❌ You are not allowed to use this command."
        )

    txt = (
        "📖 POWER POINT BREAK BOT — COMMAND MENU\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 /start – show welcome menu\n"
        "🔹 /on – start giveaway\n"
        "🔹 /off – stop giveaway\n"
        "🔹 /setwinner <n> – set winner count\n"
        "🔹 /resetlist – clear winners\n"
        "🔹 /adminpanel – admin panel\n"
        "🔹 /setpost – schedule giveaway post\n"
        "🔹 /spost – set final post\n"
        "🔹 /help – show this menu\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"👑 Admin: @{ADMIN_USERNAME}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(txt)
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", on_cmd))
    app.add_handler(CommandHandler("off", off_cmd))
    app.add_handler(CommandHandler("resetlist", reset_cmd))
    app.add_handler(CommandHandler("setwinner", setwinner_cmd))
    app.add_handler(CommandHandler("adminpanel", adminpanel_cmd))
    app.add_handler(CommandHandler("setpost", setpost_cmd))
    app.add_handler(CommandHandler("spost", spost_cmd))

    # ✅ General message: time → post → spost → user
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_time), 0)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_post), 1)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_spost), 2)
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_msg), 3)
    # ✅ Callback buttons
    app.add_handler(CallbackQueryHandler(join_button, pattern="^join$"))
    app.add_handler(CallbackQueryHandler(restart_go, pattern="^restart_go$"))

    # ✅ approval buttons
    app.add_handler(CallbackQueryHandler(approve_callback, pattern="^approve$"))
    app.add_handler(CallbackQueryHandler(reject_callback, pattern="^reject$"))

    # ✅ setpost confirm buttons
    app.add_handler(CallbackQueryHandler(setpost_approve_callback, pattern="^setpost_ok$"))
    app.add_handler(CallbackQueryHandler(setpost_reject_callback, pattern="^setpost_no$"))

    # ✅ adminpanel buttons
    app.add_handler(CallbackQueryHandler(adminpanel_callback, pattern="^ap_"))

    app.run_polling()


# ============================================================
#  SCRIPT ENTRY
# ============================================================

if __name__ == "__main__":
    main()
