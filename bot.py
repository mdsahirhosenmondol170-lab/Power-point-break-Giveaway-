# ============================================================
# POWER POINT BREAK — GIVEAWAY BOT
# FULL CLEAN REBUILD — PART-1 (Line ~1–400)
# Language: Python (python-telegram-bot v20+)
# ============================================================

import os
import asyncio
import datetime
from datetime import timedelta
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

# ============================================================
# ========== CONFIG (EDIT THESE) =============================
# ============================================================

BOT_TOKEN      = "8373078905:AAH3JTi0IvXxQGTzEtXYdLNC3W34-QEcitE"
ADMIN_ID       = 5692210187
ADMIN_USERNAME = "MinexxProo"
CHANNEL_ID     = -1003180933712     # MUST be negative

# ✅ Dynamic Admin List (main admin always added)
ADMINS = {ADMIN_ID}

# ============================================================
# ========== GLOBAL STATE ====================================
# ============================================================

giveaway_on       = False
restart_mode      = False
winner_limit      = 10

winners           = []
joined_users      = set()

pending_post_text = None
pending_seconds   = 0
second_post_text  = None

countdown_msg_id  = None

bad_words = ["fuck", "sex", "nude", "bitch", "porn"]

# ============================================================
# ========== BASIC HELPERS ===================================
# ============================================================

def now_time():
    return datetime.datetime.now().strftime("%I:%M:%S %p")

def make_winner_entry(uname, uid):
    return f"{uname} | {uid} | {now_time()}"

def is_admin(uid):
    return uid in ADMINS

async def safe_reply(update, txt):
    try:
        await update.message.reply_text(txt)
    except:
        pass

def bad_word_found(msg):
    msg = msg.lower()
    return any(w in msg for w in bad_words)

# Save Winner into file
def save_winner_to_file(entry):
    with open("winners.txt", "a") as f:
        f.write(entry + "\n")

# ============================================================
# ========== /start ==========================================
# ============================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    kb = [
        [InlineKeyboardButton("Join Giveaway ✅", callback_data="join_btn")]
    ]
    markup = InlineKeyboardMarkup(kb)

    txt = (
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        "👋 Welcome To Power Point Break Giveaway!\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Hello {update.effective_user.mention_html()} 🎉\n"
        f"🆔 User ID: {update.effective_user.id}\n\n"
        "📩 To participate in the giveaway,\n"
        "👉 Press the button below!\n\n"
        "Good luck! 🍀\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚠ Admin: @{ADMIN_USERNAME}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    await update.message.reply_html(txt, reply_markup=markup)

# ============================================================
# ========== JOIN CALLBACK ===================================
# ============================================================

async def join_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global joined_users, winners, winner_limit

    q = update.callback_query
    user = q.from_user

    await q.answer()

    if user.id in joined_users:
        return await q.message.reply_text("⚠️ You already joined!")

    joined_users.add(user.id)

    # If giveaway is ON → accept as winner
    if giveaway_on:
        if len(winners) < winner_limit:
            entry = make_winner_entry("@" + (user.username or "nouser"), user.id)
            winners.append(entry)
            save_winner_to_file(entry)

            await q.message.reply_text(
                f"✅ NEW WINNER!\n{entry}"
            )

        # If full — announce
        if len(winners) >= winner_limit:
            await q.message.reply_text("✅ Winner limit reached!")
    else:
        await q.message.reply_text("✅ Joined! Giveaway not started yet.")

# ============================================================
# ========== /on  (Start Giveaway + Notify Admin) =============
# ============================================================

async def on_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on, restart_mode

    uid = update.effective_user.id
    if uid not in ADMINS:
        return await update.message.reply_text("❌ You are not admin!")

    giveaway_on = True
    restart_mode = True

    await update.message.reply_text(
        "✅ Giveaway Started!\n"
        "🔁 Restart Mode Enabled\n"
        "➡ Waiting for users to join…"
    )

    # ✅ Notify Admin
    try:
        await context.bot.send_message(
            chat_id=uid,
            text="✅ Giveaway is now ON!\n🔥 Winners will be collected automatically."
        )
    except:
        pass


# ============================================================
# ========== /off =============================================
# ============================================================

async def off_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_on
    uid = update.effective_user.id

    if uid not in ADMINS:
        return await update.message.reply_text("❌ You are not admin!")

    giveaway_on = False
    await update.message.reply_text(
        "✅ Giveaway Stopped!\n"
        "No new winners will be added."
    )


# ============================================================
# ========== /setwinner <n> ===================================
# ============================================================

async def setwinner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winner_limit
    uid = update.effective_user.id

    if uid not in ADMINS:
        return await update.message.reply_text("❌ You are not admin!")

    if len(context.args) < 1:
        return await update.message.reply_text("Usage: /setwinner <number>")

    try:
        n = int(context.args[0])
        winner_limit = n
    except:
        return await update.message.reply_text("❌ Invalid number")

    await update.message.reply_text(f"✅ Winner limit set to: {winner_limit}")


# ============================================================
# ========== /resetlist ======================================
# ============================================================

async def resetlist(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winners
    uid = update.effective_user.id

    if uid not in ADMINS:
        return await update.message.reply_text("❌ You are not admin!")

    winners = []
    with open("winners.txt", "w") as f:
        f.write("")

    await update.message.reply_text("♻️ Winner list cleared!")


# ============================================================
# ========== /adminadd <user_id> ==============================
# ============================================================

async def adminadd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    # Only MAIN admin can add new admin
    if uid != ADMIN_ID:
        return await update.message.reply_text("❌ Only Main Admin can add others!")

    if len(context.args) != 1:
        return await update.message.reply_text("Usage: /adminadd <user_id>")

    try:
        new_id = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Invalid user ID")

    ADMINS.add(new_id)
    await update.message.reply_text(f"✅ New Admin Added: {new_id}")


# ============================================================
# ========== /adminremove <user_id> ===========================
# ============================================================

async def adminremove(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid != ADMIN_ID:
        return await update.message.reply_text("❌ Only Main Admin can remove!")

    if len(context.args) != 1:
        return await update.message.reply_text("Usage: /adminremove <user_id>")

    try:
        rem_id = int(context.args[0])
    except:
        return await update.message.reply_text("❌ Invalid user ID")

    if rem_id == ADMIN_ID:
        return await update.message.reply_text("❌ Cannot remove main admin!")

    if rem_id in ADMINS:
        ADMINS.remove(rem_id)
        return await update.message.reply_text(f"✅ Removed Admin: {rem_id}")
    else:
        return await update.message.reply_text("❌ User not admin!")


# ============================================================
# ========== /adminpanel =====================================
# ============================================================

async def adminpanel_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if uid not in ADMINS:
        return await update.message.reply_text("❌ You are not admin!")

    kb = [
        [InlineKeyboardButton("✅ Show Winners",  callback_data="show_win")],
        [InlineKeyboardButton("♻️ Reset Winners", callback_data="reset_win")],
        [InlineKeyboardButton("🔴 Stop Giveaway", callback_data="stop_give")],
    ]

    markup = InlineKeyboardMarkup(kb)

    await update.message.reply_text("⚙ Admin Panel", reply_markup=markup)


# ============================================================
# ========== ADMIN CALLBACK ==================================
# ============================================================

async def adminpanel_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winners, giveaway_on

    q   = update.callback_query
    uid = q.from_user.id

    if uid not in ADMINS:
        return await q.answer("❌ Not allowed", show_alert=True)

    data = q.data

    if data == "show_win":
        if not winners:
            return await q.message.reply_text("❌ No winners yet!")

        txt = "🏆 WINNERS:\n\n"
        for w in winners:
            txt += f"✅ {w}\n"
        return await q.message.reply_text(txt)

    if data == "reset_win":
        winners = []
        with open("winners.txt", "w") as f:
            f.write("")
        return await q.message.reply_text("♻️ Winner list reset!")

    if data == "stop_give":
        giveaway_on = False
        return await q.message.reply_text("🔴 Giveaway Stopped!")

# ============================================================
# ========== /setpost  — FIRST POST ===========================
# ============================================================

pending_post_text = None
pending_seconds   = 0

async def setpost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_post_text, pending_seconds

    uid = update.effective_user.id
    if uid not in ADMINS:
        return await update.message.reply_text("❌ You are not admin!")

    pending_post_text = None
    pending_seconds   = 0

    await update.message.reply_text("✅ Send Giveaway Post (Text Only)")


async def capture_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_post_text, pending_seconds

    # Only accept post if waiting
    if pending_post_text is None and update.effective_user.id in ADMINS:
        pending_post_text = update.message.text

        await update.message.reply_text(
            "✅ Post Saved!\n⏳ Now Send Time (Ex: 10s, 5m, 1h)"
        )
        return


# ============================================================
# ========== /spost  — SECOND POST ============================
# ============================================================

second_post_text = None

async def spost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global second_post_text

    uid = update.effective_user.id
    if uid not in ADMINS:
        return await update.message.reply_text("❌ You are not admin!")

    second_post_text = None
    await update.message.reply_text("✅ Send SECOND Post (Auto after main)")


async def capture_spost(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global second_post_text

    if update.effective_user.id not in ADMINS:
        return

    if second_post_text is None:
        second_post_text = update.message.text
        await update.message.reply_text("✅ Second Post Saved!")
        return



# ============================================================
# ========== TIME PARSER =====================================
# ============================================================

def parse_time(txt):
    txt = txt.lower().strip()
    try:
        if txt.endswith("s"):
            return int(txt[:-1])
        if txt.endswith("m"):
            return int(txt[:-1]) * 60
        if txt.endswith("h"):
            return int(txt[:-1]) * 3600
    except:
        return None
    return None


async def capture_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_seconds, pending_post_text

    if update.effective_user.id not in ADMINS:
        return

    if pending_post_text is None:
        return

    sec = parse_time(update.message.text)
    if sec is None:
        return

    pending_seconds = sec

    await update.message.reply_text(f"✅ Time Set: {pending_seconds}s")

    # Start countdown
    asyncio.create_task(
        do_scheduled_post(update, context)
    )



# ============================================================
# ========== COUNTDOWN + AUTO-POST ============================
# ============================================================

async def do_scheduled_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_seconds, pending_post_text, second_post_text, countdown_msg_id

    if pending_seconds <= 0 or not pending_post_text:
        return

    msg = await update.message.reply_text(
        f"⏳ Giveaway Will Post After {pending_seconds} sec"
    )
    countdown_msg_id = msg.message_id

    total = pending_seconds

    while pending_seconds > 0:
        try:
            bar = make_progress(total, pending_seconds)
            t = str(pending_seconds)

            await context.bot.edit_message_text(
                chat_id=update.effective_chat.id,
                message_id=countdown_msg_id,
                text=f"🚀 Giveaway Starting Soon…\n⏰ {t}s\n{bar}"
            )
        except:
            pass

        await asyncio.sleep(1)
        pending_seconds -= 1

    # POST MAIN MESSAGE
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=pending_post_text
        )
    except:
        await update.message.reply_text("❌ Failed main post")

    # POST SECOND MESSAGE
    if second_post_text:
        try:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=second_post_text
            )
        except:
            await update.message.reply_text("❌ Failed second post")

    await context.bot.edit_message_text(
        chat_id=update.effective_chat.id,
        message_id=countdown_msg_id,
        text="✅ Giveaway Posted!"
    )


# ============================================================
# ========== PROGRESS BAR ====================================
# ============================================================

def make_progress(total, left):
    done = total - left
    pct  = done / total
    bars = int(pct * 16)

    return "▰" * bars + "▱" * (16 - bars)


# ============================================================
# ========== /help ===========================================
# ============================================================

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id not in ADMINS:
        return await update.message.reply_text(
            "❌ You are not allowed to use this command."
        )

    txt = (
        "📘 POWER POINT BREAK BOT — COMMANDS\n"
        "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        "🔹 /start – Show menu\n"
        "🔹 /on – Start Giveaway\n"
        "🔹 /off – Stop Giveaway\n"
        "🔹 /setwinner N – Winner Count\n"
        "🔹 /resetlist – Clear Winners\n"
        "🔹 /adminpanel – Admin Panel\n"
        "🔹 /setpost – Schedule First Post\n"
        "🔹 /spost – Schedule Second Post\n"
        "🔹 /adminadd <id> – Add Admin\n"
        "🔹 /adminremove <id> – Remove Admin\n"
        "🔹 /help – Show this menu\n\n"
        f"👑 Main Admin: @{ADMIN_USERNAME}\n"
        "━━━━━━━━━━━━━━━━━━━━━━"
    )

    await update.message.reply_text(txt)


# ============================================================
# ========== FALLBACK USER MESSAGE ===========================
# ============================================================

async def user_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if bad_word_found(update.message.text):
        await update.message.reply_text("⚠ Bad word detected!")

# ============================================================
# ========== MAIN CALLBACK HANDLERS ==========================
# ============================================================

async def structure_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass   # reserved for future


# ============================================================
# ========== MAIN()  =========================================
# ============================================================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ✅ Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", on_cmd))
    app.add_handler(CommandHandler("off", off_cmd))
    app.add_handler(CommandHandler("setwinner", setwinner_cmd))
    app.add_handler(CommandHandler("resetlist", resetlist))
    app.add_handler(CommandHandler("adminpanel", adminpanel_cmd))
    app.add_handler(CommandHandler("setpost", setpost_cmd))
    app.add_handler(CommandHandler("spost", spost_cmd))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("adminadd", adminadd))
    app.add_handler(CommandHandler("adminremove", adminremove))

    # ✅ General message priority
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_time))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_post))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_spost))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_msg))

    # ✅ Callback buttons
    app.add_handler(CallbackQueryHandler(join_button, pattern="^join_btn$"))
    app.add_handler(CallbackQueryHandler(adminpanel_callback, pattern="^show_win$"))
    app.add_handler(CallbackQueryHandler(adminpanel_callback, pattern="^reset_win$"))
    app.add_handler(CallbackQueryHandler(adminpanel_callback, pattern="^stop_give$"))

    # ✅ Bot RUN
    print("✅ BOT RUNNING…")
    app.run_polling()



# ============================================================
# ========== RUN SCRIPT ======================================
# ============================================================

if __name__ == "__main__":
    main()

  
