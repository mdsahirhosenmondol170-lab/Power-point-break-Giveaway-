from telegram import (
    Update,
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

# ===========================
# CONFIG
# ===========================
BOT_TOKEN = "YOUR_BOT_TOKEN"     # <<< paste your token here
ADMIN_USERNAME = "MinexxProo"    # without @

giveaway_on = False
waiting_for_limit = False
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

    try:
        await update.message.reply_text(text, reply_markup=btn)
    except:
        await update.callback_query.message.reply_text(text, reply_markup=btn)


# ===========================
# /on
# ===========================
async def on(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, winners, joined, waiting_for_limit

    if not is_admin(update.effective_user.username):
        return await update.message.reply_text("❌ Not authorized")

    waiting_for_limit = True
    giveaway_on = False
    winners = []
    joined = set()

    await update.message.reply_text(
        "🟢 Giveaway Starting…\n\n"
        "➡️ How many winners?\n"
        "(Send a number — Example: 10)"
    )


# ===========================
# Handle admin winner limit
# ===========================
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global waiting_for_limit, winner_limit, giveaway_on

    user = update.effective_user

    # If admin is setting limit
    if waiting_for_limit and is_admin(user.username):
        try:
            winner_limit = int(update.message.text)
        except:
            return await update.message.reply_text("❌ Send a valid number")

        waiting_for_limit = False
        giveaway_on = True

        return await update.message.reply_text(
            f"✅ Giveaway STARTED!\n"
            f"🥇 Winner Limit: {winner_limit}"
        )

    # For other case -> normal start screen
    return await start(update, context)


# ===========================
# /off
# ===========================
async def off(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on

    if not is_admin(update.effective_user.username):
        return await update.message.reply_text("❌ Not authorized")

    giveaway_on = False
    await update.message.reply_text("⛔️ Giveaway CLOSED!")


# ===========================
# /allw + /allwinner
# ===========================
async def show_winners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.username):
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
        "/on → Start Giveaway\n"
        "/off → Stop Giveaway\n"
        "/allw → Show Winners\n"
        "/allwinner → Show Winners\n"
        "/allcd → Show Commands\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )
    await update.message.reply_text(txt)


# ===========================
# JOIN BUTTON
# ===========================
async def join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, winner_limit, winners, joined

    query = update.callback_query
    await query.answer()
    user = query.from_user

    username = user.username
    uid = user.id

    # Giveaway Closed
    if not giveaway_on:
        return await query.message.reply_text(
            "⛔️ ❌ GIVEAWAY CLOSED ❌ ⛔️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "📩 Contact Admin:\n"
            "👉 @MinexxProo\n\n"
            "💫 Please try another Giveaway!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )

    # Already Joined
    if uid in joined:
        return await query.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ You have already participated!\n\n"
            "📩 For any concerns, please contact:\n"
            "👉 @MinexxProo\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    # Winner Full
    if len(winners) >= winner_limit:
        return await query.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "😔 Oops! All winners are already selected!\n"
            "🎉 Thanks for joining!\n\n"
            "🍀 Try again — more giveaways soon!\n"
            "💙 Stay with Power Point Break!\n\n"
            "📞 For support:\n"
            "👉 @MinexxProo\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    # Accept
    joined.add(uid)
    winners.append((username, uid))

    # Notify Admin
    await context.bot.send_message(
        f"@{ADMIN_USERNAME}",
        f"🏆 NEW WINNER\n@{username} | {uid}"
    )

    # Notify user
    await query.message.reply_text(
        "🎉 CONGRATULATIONS! 🎉\n"
        "You are one of the WINNERS of our Giveaway! 🏆\n\n"
        "📩 Contact Admin to claim your reward:\n"
        "👉 @MinexxProo\n\n"
        "💙 Hosted by: Power Point Break"
    )


# ===========================
# MAIN
# ===========================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", on))
    app.add_handler(CommandHandler("off", off))
    app.add_handler(CommandHandler("allw", show_winners))
    app.add_handler(CommandHandler("allwinner", show_winners))
    app.add_handler(CommandHandler("allcd", allcd))

    app.add_handler(CallbackQueryHandler(join_callback))
    app.add_handler(MessageHandler(filters.TEXT, text_handler))

    print("✅ BOT RUNNING…")
    app.run_polling()


if __name__ == "__main__":
    main()
