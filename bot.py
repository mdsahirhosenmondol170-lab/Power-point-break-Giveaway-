from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    CallbackQueryHandler, ContextTypes, filters
)

# ======================
# CONFIG
# ======================
BOT_TOKEN = "8373078905:AAH3JTi0IvXxQGTzEtXYdLNC3W34-QEcitE"     # <-- put your bot token
ADMIN_ID  = 5692210187           # <-- your Telegram numeric ID
ADMIN_USERNAME = "MinexxProo"    # used in user-facing messages (without @)

# Words to block
BAD_WORDS = ["fuck", "bitch", "asshole", "motherfucker", "mc", "bc"]

# Giveaway state
giveaway_on   = False
winner_limit  = 0
winners       = []        # "@username"
joined_users  = set()     # user IDs


# ======================
# SAFE USERNAME
# ======================
def safe_username(user) -> str:
    if user.username:
        return f"@{user.username}"
    return f"ID:{user.id}"


# ======================
# MESSAGE BLOCK TEMPLATES
# ======================

def msg_welcome_user(uname, uid):
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👋 Welcome To Power Point Break Giveaway!\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Hello {uname} 🎉\n"
        f"🆔 User ID: {uid}\n\n"
        "📩 To participate in the giveaway,\n"
        "👉 Please send any message!\n\n"
        "✅ If you are selected as a winner,\n"
        "you will be notified instantly!\n\n"
        "💬 For any issues or help,\n"
        f"👉 Please contact Admin: @{ADMIN_USERNAME}\n\n"
        "Good luck! 🍀\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


def msg_welcome_admin():
    return (
        "👋 Welcome to the Giveaway Bot (Admin)!\n\n"
        "✅ Commands:\n"
        "/on – Start Giveaway\n"
        "/off – Stop Giveaway\n"
        "/setwinner <number> – Set winner count\n"
        "/adminpanel – Open Admin Panel\n\n"
        "Good luck & have fun! 🎉"
    )


def msg_congrats():
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "🎉 CONGRATULATIONS! 🏆\n"
        "You have been selected as a WINNER!\n"
        "Please wait for your reward. 💝\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


def msg_duplicate():
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ You have already participated!\n\n"
        "📩 For any concerns, please contact:\n"
        f"👉 @{ADMIN_USERNAME}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


def msg_full():
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "😔 Oops! All winners are already selected!\n"
        "🎉 Thanks for joining!\n\n"
        "🍀 Try again — more giveaways soon!\n"
        "💙 Stay with Power Point Break!\n\n"
        "📞 For support or any issues,\n"
        f"👉 Please contact Admin: @{ADMIN_USERNAME}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


def msg_closed():
    return (
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "❌ GIVEAWAY CLOSED ❌\n"
        "━━━━━━━━━━━━━━━━━━━━━\n"
        "📩 Please contact Admin:\n"
        f"👉 @{ADMIN_USERNAME}\n\n"
        "✨ Please try the next Giveaway!"
    )


def msg_bad():
    return (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "⚠️ Bad words are NOT allowed.\n"
        "Please keep it respectful. ❌\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )


# ======================
# /start
# ======================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid   = user.id
    uname = safe_username(user)

    # Admin
    if uid == ADMIN_ID:
        await update.message.reply_text(msg_welcome_admin())
        return

    # Normal User
    await update.message.reply_text(msg_welcome_user(uname, uid))


# ======================
# /on  (admin)
# ======================
async def cmd_on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on
    if update.effective_user.id != ADMIN_ID:
        return
    giveaway_on = True
    await update.message.reply_text(
        "✅ Giveaway has been STARTED!\n"
        "Please set winner count using:\n"
        "/setwinner <number>\n"
        "Example: /setwinner 10"
    )


# ======================
# /off (admin)
# ======================
async def cmd_off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on
    if update.effective_user.id != ADMIN_ID:
        return
    giveaway_on = False
    await update.message.reply_text("❌ Giveaway has been STOPPED!")


# ======================
# /setwinner X (admin)
# ======================
async def cmd_setwinner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winner_limit
    if update.effective_user.id != ADMIN_ID:
        return

    if len(context.args) != 1 or not context.args[0].isdigit():
        await update.message.reply_text("Usage: /setwinner <number>\nExample: /setwinner 10")
        return

    n = int(context.args[0])
    if n < 1:
        await update.message.reply_text("❌ Winner count must be at least 1.")
        return

    winner_limit = n
    await update.message.reply_text(f"✅ Winner Count Set → {winner_limit}")


# ======================
# /adminpanel (admin)
# ======================
async def cmd_adminpanel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return

    keyboard = [
        [InlineKeyboardButton("✅ Show Winner List", callback_data="show_winner")],
        [InlineKeyboardButton("♻ Reset Giveaway",    callback_data="reset_giveaway")],
        [InlineKeyboardButton("🔴 Turn OFF",          callback_data="turn_off")],
    ]
    await update.message.reply_text(
        "⚙️ ADMIN PANEL",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


# ======================
# Admin Button Handler
# ======================
async def on_admin_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, winners, joined_users
    query = update.callback_query
    await query.answer()

    if update.effective_user.id != ADMIN_ID:
        await query.edit_message_text("❌ You are not allowed.")
        return

    data = query.data

    if data == "show_winner":
        if not winners:
            await query.edit_message_text("❌ No winners yet.")
            return

        text = "🏆 Winner List:\n" + "\n".join(f"• {w}" for w in winners)
        await query.edit_message_text(text)

    elif data == "reset_giveaway":
        winners.clear()
        joined_users.clear()
        await query.edit_message_text("✅ Giveaway has been RESET.\nAll entries cleared.")

    elif data == "turn_off":
        giveaway_on = False
        await query.edit_message_text("✅ Giveaway has been turned OFF.")


# ======================
# Message Handler
# ======================
async def on_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, winner_limit, winners, joined_users

    if not update.message or not update.message.text:
        return

    user = update.effective_user
    uid  = user.id
    uname = safe_username(user)
    text = update.message.text.lower()

    # Bad-word filter
    for bad in BAD_WORDS:
        if bad in text:
            await update.message.reply_text(msg_bad())
            return

    # Giveaway OFF
    if not giveaway_on:
        await update.message.reply_text(msg_closed())
        return

    # Already joined
    if uid in joined_users:
        await update.message.reply_text(msg_duplicate())
        return

    # Slots Full
    if len(winners) >= winner_limit:
        await update.message.reply_text(msg_full())
        return

    # Accept Winner
    winners.append(uname)
    joined_users.add(uid)

    # Notify User
    await update.message.reply_text(msg_congrats())

    # Notify Admin
    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=f"📩 NEW WINNER!\nUsername: {uname}\nUserID: {uid}"
        )
    except:
        pass


# ======================
# MAIN
# ======================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start",      start))
    app.add_handler(CommandHandler("on",         cmd_on))
    app.add_handler(CommandHandler("off",        cmd_off))
    app.add_handler(CommandHandler("setwinner",  cmd_setwinner))
    app.add_handler(CommandHandler("adminpanel", cmd_adminpanel))

    app.add_handler(CallbackQueryHandler(on_admin_button))

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, on_message))

    print("✅ BOT RUNNING...")
    app.run_polling()


if __name__ == "__main__":
    main()
