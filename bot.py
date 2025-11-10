import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters
)

BOT_TOKEN = "8321055873:AAEbXH-5HospdM6Erato-3s1fw_o2NZ4n3I"
ADMIN = "MinexxProo"  # admin username (without @)

giveaway_on = False
winner_limit = 0
winners = []
joined_users = set()


# ---- START ----
async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = f"""
Hello @{user.username} 🎉
🆔 User ID: {user.id}

📩 To participate in the giveaway,
👉 Please 👇 Tap the button!
━━━━━━━━━━━━━━━━━━━━━━
"""

    btn = [
        [InlineKeyboardButton("🚀🌟 Join Giveaway Now!", callback_data="join")]
    ]

    await update.message.reply_text(text,
        reply_markup=InlineKeyboardMarkup(btn)
    )


# ---- /on ----
async def on_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on
    user = update.effective_user

    if user.username != ADMIN:
        return await update.message.reply_text("❌ Not Authorized")

    giveaway_on = True
    await update.message.reply_text("✅ Giveaway Started!\nSend winner limit (e.g. 10)")


# ---- Winner set ----
async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winner_limit, giveaway_on
    user = update.effective_user
    text = update.message.text

    if user.username == ADMIN and giveaway_on and winner_limit == 0 and text.isdigit():
        winner_limit = int(text)
        return await update.message.reply_text(
            f"✅ Winner count set to: {winner_limit}\nGiveaway Started!"
        )

    # When random user sends msg
    return await start_cmd(update, context)


# ---- Join System ----
async def join_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winners, winner_limit, giveaway_on, joined_users

    query = update.callback_query
    user = query.from_user
    await query.answer()

    if not giveaway_on:
        return await query.message.reply_text(
            "⛔️ ❌ GIVEAWAY CLOSED ❌\n━━━━━━━━━━━━━━━━━━━━━━━\n📩 Contact Admin: @MinexxProo\n━━━━━━━━━━━━━━━━━━━━━━━"
        )

    if user.id in joined_users:
        return await query.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n⚠️ You have already participated!\n📩 Contact: @MinexxProo\n━━━━━━━━━━━━━━━━━━━━━━"
        )

    if len(winners) >= winner_limit:
        return await query.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n😔 Oops! All winners selected!\n🎉 Thanks for joining!\n━━━━━━━━━━━━━━━━━━━━━━"
        )

    # ADD WINNER
    winners.append((user.username, user.id))
    joined_users.add(user.id)

    # Notify admin
    await context.bot.send_message(
        chat_id=update.effective_user.id,
        text="🎉 CONGRATULATIONS! 🎉\nYou are WINNER! 🏆\n📩 Contact: @MinexxProo"
    )

    # Send admin user info
    await context.bot.send_message(
        chat_id=f"@{ADMIN}",
        text=f"✅ NEW WINNER\n@{user.username} | {user.id}"
    )


# ---- /off ----
async def off_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on
    user = update.effective_user

    if user.username != ADMIN:
        return await update.message.reply_text("❌ Not Authorized")

    giveaway_on = False
    await update.message.reply_text("✅ Giveaway Closed!")


# ---- /allwiner ----
async def all_winner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winners
    user = update.effective_user

    if user.username != ADMIN:
        return await update.message.reply_text("❌ Not Authorized")

    if not winners:
        return await update.message.reply_text("No winner yet!")

    text = "🏆 Winners List:\n\n"
    for u, i in winners:
        text += f"@{u} — {i}\n"

    await update.message.reply_text(text)


async def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CommandHandler("on", on_cmd))
    app.add_handler(CommandHandler("off", off_cmd))
    app.add_handler(CommandHandler("allwiner", all_winner_cmd))

    app.add_handler(CallbackQueryHandler(join_press))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    print("BOT RUNNING…✅")
    await app.run_polling()


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
