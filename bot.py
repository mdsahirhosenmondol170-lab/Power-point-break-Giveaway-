from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ===========================
# CONFIG
# ===========================
BOT_TOKEN = "8321055873:AAFHMYzvx5GA4RSuik6vttFrGoj5_Xjm5Xc"      # <- paste your token here
ADMIN_USERNAME = "MinexxProo"          # without @

giveaway_on = False
winner_limit = 0
winners = []
joined = set()


def is_admin(username):
    return username == ADMIN_USERNAME


# ===========================
# /start
# ===========================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    
    text = (
        f"Hello @{user.username} 🎉\n"
        f"🆔 User ID: {user.id}\n\n"
        "📩 To participate in the giveaway,\n"
        "👉 Please 👇 Tap the button!\n\n"
        "┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        "🚀🌟 Join the Giveaway Now!\n"
        "🎁🏆 Don’t miss your chance to win!\n"
        "┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        "✅ If you are selected as a winner,\n"
        "you will be notified instantly!\n\n"
        "💬 If you need help, contact:\n"
        "👉 @MinexxProo\n\n"
        "Good luck! 🍀\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    btn = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🎁 JOIN GIVEAWAY", callback_data="join")]]
    )

    await update.message.reply_text(text, reply_markup=btn)


# ===========================
# /on
# ===========================
async def on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, winner_limit, winners, joined

    user = update.effective_user

    if not is_admin(user.username):
        return await update.message.reply_text("❌ Not authorized")

    try:
        limit = int(context.args[0])
    except:
        return await update.message.reply_text("Use:  /on 10")

    winner_limit = limit
    giveaway_on = True
    winners = []
    joined = set()

    await update.message.reply_text(
        f"✅ Giveaway STARTED!\n"
        f"🥇 Winner Limit: {winner_limit}"
    )


# ===========================
# /off
# ===========================
async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on
    user = update.effective_user

    if not is_admin(user.username):
        return await update.message.reply_text("❌ Not authorized")

    giveaway_on = False
    await update.message.reply_text("⛔️ Giveaway CLOSED!")


# ===========================
# /allw
# ===========================
async def allw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_admin(user.username):
        return await update.message.reply_text("❌ Not authorized")

    if not winners:
        return await update.message.reply_text("No winners yet!")

    txt = "🏆 WINNER LIST:\n\n"
    c = 1
    for n, i in winners:
        txt += f"{c}) @{n} | {i}\n"
        c += 1

    await update.message.reply_text(txt)


# ===========================
# /allcd
# ===========================
async def allcd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "📌 BOT COMMANDS\n\n"
        "/on X → Start Giveaway\n"
        "/off → Stop Giveaway\n"
        "/allw → Show Winners\n"
        "/allcd → Show Commands\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(txt)


# ===========================
# JOIN BUTTON
# ===========================
async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, winner_limit, winners, joined

    query = update.callback_query
    user = query.from_user
    await query.answer()

    username = user.username
    uid = user.id

    # Giveaway Closed
    if not giveaway_on:
        text = (
            "⛔️ ❌ GIVEAWAY CLOSED ❌ ⛔️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📩 Contact Admin:\n"
            "👉 @MinexxProo\n\n"
            "💫 Please try another Giveaway!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )
        return await query.message.reply_text(text)

    # Already participated
    if uid in joined:
        text = (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ You have already participated!\n\n"
            "📩 For any concerns, please contact:\n"
            "👉 @MinexxProo\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        return await query.message.reply_text(text)

    # Full winners
    if len(winners) >= winner_limit:
        text = (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "😔 Oops! All winners are already selected!\n"
            "🎉 Thanks for joining!\n\n"
            "🍀 Try again — more giveaways soon!\n"
            "💙 Stay with Power Point Break!\n\n"
            "📞 For support:\n"
            "👉 @MinexxProo\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )
        return await query.message.reply_text(text)

    # Accept entry
    joined.add(uid)
    winners.append((username, uid))

    # Notify admin
    admin = await context.bot.get_chat(f"@{ADMIN_USERNAME}")
    msg = (
        "🏆 **NEW WINNER**\n"
        f"👤 Username: @{username}\n"
        f"🆔 UserID: {uid}\n"
    )
    await admin.send_message(msg)

    # Notify user
    win_msg = (
        "🎉 CONGRATULATIONS! 🎉\n"
        "You are one of the WINNERS of our Giveaway! 🏆\n\n"
        "📩 Contact Admin to claim your reward:\n"
        "👉 @MinexxProo\n\n"
        "💙 Hosted by: Power Point Break"
    )
    await query.message.reply_text(win_msg)


# ===========================
# MESSAGE HANDLER
# ===========================
async def msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await start(update, context)


# ===========================
# MAIN
# ===========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", on))
    app.add_handler(CommandHandler("off", off))
    app.add_handler(CommandHandler("allw", allw))
    app.add_handler(CommandHandler("allcd", allcd))

    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT, msg))

    print("✅ BOT RUNNING…")
    app.run_polling()


if __name__ == "__main__":
    main()
