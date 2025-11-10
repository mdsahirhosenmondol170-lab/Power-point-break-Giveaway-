# ===================================================================
# ✅ POWER POINT BREAK — GIVEAWAY BOT (FINAL V3)
# ===================================================================

import os, random, asyncio
from datetime import datetime, timedelta

from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# ================================================================
# ✅ CONFIG
# ================================================================
BOT_TOKEN      = "8373078905:AAHSJGigDoz6gBowjN4Dj2j_pkOcYvqqLhQ"
ADMIN_USERNAME = "MinexxProo"
CHANNEL_ID     = -1003418547744    # <-- Change your Channel ID

# ================================================================
# ✅ GLOBAL STORAGE
# ================================================================
giveaway_active   = False
winner_limit      = 10
joined_users      = []   # store UID only
winner_data       = []   # store (username, uid, time)

# MULTI-WINNER MODE
admin_wait_count  = False
admin_wait_time   = False
mwinner_active    = False
mwinner_count     = 0
mwinner_time_sec  = 0
mwinner_task      = None
mwinner_buffer    = []

# NORMAL COUNTDOWN POST MODE
pending_post      = None
after_post        = None
countdown_time    = None

# NEW — /countpost MODE
countpost_pending      = False
countpost_time_pending = False
countpost_post         = None
countpost_seconds      = None
countpost_running      = False

# ================================================================
# ✅ TEMPALTES
# ================================================================
WELCOME_TEMPLATE = """
━━━━━━━━━━━━━━━━━━━━━━
👋 Welcome To Power Point Break Giveaway!
━━━━━━━━━━━━━━━━━━━━━━

Hello @{username} 🎉
🆔 User ID: {user_id}

📩 To participate in the giveaway,
👉 Please 👇 Tap the button!

┏━━━━━━━━━━━━━━━━━━━━━━┓
🚀🌟 Join the Giveaway Now!
🎁🏆 Don’t miss your chance to win!
┗━━━━━━━━━━━━━━━━━━━━━━┛

✅ If you are selected as a winner,
you will be notified instantly!

💬 Need help?
👉 @{ADMIN_USERNAME}

Good luck! 🍀
━━━━━━━━━━━━━━━━━━━━━━
"""

CLOSED_TEMPLATE = """
━━━━━━━━━━━━━━━━━━━━━━━
⛔️ ❌ GIVEAWAY CLOSED ❌ ⛔️
━━━━━━━━━━━━━━━━━━━━━━━
📩 Contact Admin:
👉 @{ADMIN_USERNAME}

💫 Please try another Giveaway!
━━━━━━━━━━━━━━━━━━━━━━━
"""

ALREADY_TEMPLATE = """
━━━━━━━━━━━━━━━━━━━━━━
⚠️ You have already participated!

📩 For any concerns, please contact:
👉 @{ADMIN_USERNAME}
━━━━━━━━━━━━━━━━━━━━━━
"""

FULL_TEMPLATE = """
━━━━━━━━━━━━━━━━━━━━━━
😔 Oops! All winners are already selected!
🎉 Thanks for joining!

🍀 Try again — more giveaways soon!
💙 Stay with Power Point Break!

📞 For issues:
👉 @{ADMIN_USERNAME}
━━━━━━━━━━━━━━━━━━━━━━
"""

WINNER_DM = """
🎉 CONGRATULATIONS! 🎉
You are one of the WINNERS of our Giveaway! 🏆

📩 Contact Admin to claim your reward:
👉 @{ADMIN_USERNAME}

💙 Hosted by: Power Point Break
"""

# ================================================================
# ✅ UTILITIES
# ================================================================
def now():
    return datetime.now().strftime("%I:%M:%S %p")

def join_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Join the Giveaway Now!", callback_data="join_btn")]
    ])

def progress_bar(percent):
    total = 20
    filled = round(percent * total)
    empty  = total - filled
    return "▰" * filled + "▱" * empty

def save_user(uid, uname):
    try:
        with open("users.txt","a") as f:
            f.write(f"{uname}|{uid}|{now()}\n")
    except: pass

def save_winner(uid, uname):
    try:
        with open("winners.txt","a") as f:
            f.write(f"{uname}|{uid}|{now()}\n")
    except: pass

# ================================================================
# ✅ /start
# ================================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid  = user.id
    uname = user.username or "NoUsername"

    # If both OFF → show closed
    if not giveaway_active and not mwinner_active:
        return await update.message.reply_text(
            CLOSED_TEMPLATE.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )

    # Multi-winner → only collect
    if mwinner_active:
        if uid not in mwinner_buffer:
            mwinner_buffer.append(uid)
        return await update.message.reply_text(
            WELCOME_TEMPLATE.format(
                username=uname,
                user_id=uid,
                ADMIN_USERNAME=ADMIN_USERNAME
            ),
            reply_markup=join_keyboard()
        )

    # Normal mode — Already joined
    if uid in joined_users:
        return await update.message.reply_text(
            ALREADY_TEMPLATE.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )

    # Normal — winner full
    if len(winner_data) >= winner_limit:
        return await update.message.reply_text(
            FULL_TEMPLATE.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )

    msg = WELCOME_TEMPLATE.format(
        username=uname,
        user_id=uid,
        ADMIN_USERNAME=ADMIN_USERNAME
    )
    await update.message.reply_text(msg, reply_markup=join_keyboard())


# ================================================================
# ✅ JOIN BUTTON HANDLER
# ================================================================
async def join_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user  = query.from_user
    uid   = user.id
    uname = user.username or "NoUsername"

    # Giveaway OFF
    if not giveaway_active and not mwinner_active:
        return await query.message.reply_text(
            CLOSED_TEMPLATE.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )

    # ✅ MULTI-WINNER MODE
    if mwinner_active:
        if uid not in mwinner_buffer:
            mwinner_buffer.append(uid)
        return await query.message.reply_text("✅ You have joined the Giveaway! 🍀")

    # ✅ NORMAL MODE
    # Already participated
    if uid in joined_users:
        return await query.message.reply_text(
            ALREADY_TEMPLATE.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )

    # Winner full
    if len(winner_data) >= winner_limit:
        return await query.message.reply_text(
            FULL_TEMPLATE.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )

    # ADD user
    joined_users.append(uid)
    save_user(uid, uname)

    timestamp = now()

    # auto add → normal winner_data
    winner_data.append((uname, uid, timestamp))
    save_winner(uid, uname)

    # Send DM
    try:
        await context.bot.send_message(
            chat_id=uid,
            text=WINNER_DM.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )
    except:
        pass

    # Notify Admin
    try:
        note = (
            "📥 NEW ENTRY RECEIVED\n"
            f"👤 User: @{uname}\n"
            f"🆔 ID: {uid}\n"
            f"⏰ Time: {timestamp}"
        )
        await context.bot.send_message(chat_id=f"@{ADMIN_USERNAME}", text=note)
    except:
        pass

    await query.message.reply_text("✅ You have joined the Giveaway! 🍀")


# ================================================================
# ✅ /on — Start normal giveaway
# ================================================================
async def on_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_active, mwinner_active

    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    giveaway_active = True
    mwinner_active  = False

    await update.message.reply_text("✅ Giveaway is ON!")


# ================================================================
# ✅ /off — Stop
# ================================================================
async def off_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global giveaway_active, mwinner_active

    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    giveaway_active = False
    mwinner_active  = False

    await update.message.reply_text("✅ Giveaway is OFF!")


# ================================================================
# ✅ /setwinner — manual
# ================================================================
async def setwinner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global winner_limit

    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    if not context.args:
        return await update.message.reply_text("❌ Usage → /setwinner 10")

    try:
        x = int(context.args[0])
        winner_limit = x
        await update.message.reply_text(f"✅ Winner limit set → {x}")
    except:
        await update.message.reply_text("❌ Invalid number")


# ================================================================
# ✅ /status
# ================================================================
async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = (
        "✅ GIVEAWAY STATUS\n\n"
        f"Active: {giveaway_active}\n"
        f"Winner limit: {winner_limit}\n"
        f"Joined: {len(joined_users)}\n"
        f"Winners: {len(winner_data)}\n"
        f"MW-Mode: {mwinner_active}\n"
    )
    await update.message.reply_text(txt)


# ================================================================
# ✅ /reset
# ================================================================
async def reset_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global joined_users, winner_data, mwinner_buffer

    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    joined_users   = []
    winner_data    = []
    mwinner_buffer = []

    await update.message.reply_text("✅ Data Reset Completed!")


# ================================================================
# ✅ /help — Admin only
# ================================================================
async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    h = """
✅ ADMIN COMMANDS

/start → user join UI
/on → start giveaway
/off → stop giveaway
/setwinner <n> → set winner count
/setmwinner → auto random mode
/countpost → countdown post mode
/status → show status
/reset → clear data
/backup → user data
/backup_winners → winner data
/adminpanel → admin control panel
"""
    await update.message.reply_text(h)


# ================================================================
# ✅ ADMIN PANEL
# ================================================================
async def adminpanel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ ON",  callback_data="p_on"),
         InlineKeyboardButton("❌ OFF", callback_data="p_off")],
        [InlineKeyboardButton("🔄 RESET", callback_data="p_reset")]
    ])

    await update.message.reply_text(
        "⚙ Admin Panel",
        reply_markup=kb
    )


async def admin_inline_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    user = query.from_user
    if user.username != ADMIN_USERNAME:
        return

    if data == "p_on":
        await on_cmd(update, context)

    elif data == "p_off":
        await off_cmd(update, context)

    elif data == "p_reset":
        await reset_cmd(update, context)

    await query.message.reply_text("✅ OK")


# ================================================================
# ✅ BACKUP
# ================================================================
async def backup_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    try:
        await update.message.reply_document(open("users.txt","rb"))
    except:
        await update.message.reply_text("❌ No file!")


async def backup_winners_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    try:
        await update.message.reply_document(open("winners.txt","rb"))
    except:
        await update.message.reply_text("❌ No file!")


# ================================================================
# ✅ MULTI-WINNER MODE  (/setmwinner)
# ================================================================
async def setmwinner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_wait_count, admin_wait_time, mwinner_active, giveaway_active

    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    admin_wait_count = True
    admin_wait_time  = False
    mwinner_active   = False
    giveaway_active  = False

    await update.message.reply_text(
        "✅ Multi-Winner Mode Enabled!\n\n"
        "➡️ Please send how many winners?\n"
        "(Example: 10)"
    )


# STEP-1 — Capture winner count
async def capture_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_wait_count, admin_wait_time, mwinner_count

    if not admin_wait_count:
        return

    try:
        x = int(update.message.text.strip())
        mwinner_count = x
    except:
        return await update.message.reply_text("❌ Invalid number!")

    admin_wait_count = False
    admin_wait_time  = True

    await update.message.reply_text(
        f"✅ Winner count set → {mwinner_count}\n\n"
        "➡️ Now send countdown time\n"
        "Example: 10s/10m/10h"
    )


# STEP-2 — Capture countdown time
async def capture_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global admin_wait_time, mwinner_time_sec

    if not admin_wait_time:
        return

    raw = update.message.text.strip()

    try:
        unit = raw[-1].lower()
        num  = int(raw[:-1])

        if unit == "s":
            mwinner_time_sec = num
        elif unit == "m":
            mwinner_time_sec = num * 60
        elif unit == "h":
            mwinner_time_sec = num * 3600
        else:
            return await update.message.reply_text("❌ Wrong format!\nUse → 10s/10m/10h")

    except:
        return await update.message.reply_text("❌ Wrong time format!")

    admin_wait_time = False

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Approve", callback_data="mw_yes")],
        [InlineKeyboardButton("❌ Reject", callback_data="mw_no")]
    ])

    await update.message.reply_text(
        f"✅ Countdown set → {raw}\n\n"
        f"➡️ Approve to start countdown!",
        reply_markup=kb
    )


# APPROVE → Start countdown
async def mwinner_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global mwinner_active

    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if user.username != ADMIN_USERNAME:
        return await query.message.reply_text("❌ Not Authorized")

    if data == "mw_no":
        return await query.message.reply_text("❌ Cancelled!")

    if data == "mw_yes":
        mwinner_active = True
        await query.message.reply_text("✅ Auto-Winner Mode Started!")

        context.application.create_task(auto_timer(context))


# COUNTDOWN LOOP
async def auto_timer(context: ContextTypes.DEFAULT_TYPE):
    global mwinner_active, mwinner_time_sec, mwinner_buffer, mwinner_count

    total = mwinner_time_sec
    start = datetime.now()

    while True:
        passed = (datetime.now() - start).total_seconds()
        left   = total - passed

        if left <= 0:
            break

        bar = progress_bar(passed / total)
        msg = (
            f"🚀 Giveaway starting soon…\n"
            f"⏰ Time Left: {int(left)} sec\n"
            f"{bar}"
        )
        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
        except:
            pass

        await asyncio.sleep(3)

    # Time finished → Pick winners
    if not mwinner_buffer:
        mwinner_active = False
        return await context.bot.send_message(
            chat_id=f"@{ADMIN_USERNAME}",
            text="❌ No participants!"
        )

    random.shuffle(mwinner_buffer)
    selected = mwinner_buffer[:mwinner_count]

    final  = []
    tstamp = now()

    for uid in selected:
        try:
            u = await context.bot.get_chat(uid)
            uname = u.username or "NoUser"
        except:
            uname = "NoUser"

        winner_data.append((uname, uid, tstamp))
        save_winner(uid, uname)
        final.append((uname, uid, tstamp))

        # DM Winner
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=WINNER_DM.format(ADMIN_USERNAME=ADMIN_USERNAME)
            )
        except:
            pass

    # Notify Admin
    txt = "✅ AUTO-WINNER LIST ✅\n\n"
    c = 1
    for n, u, t in final:
        txt += f"#{c} → @{n} | {u} | {t}\n"
        c += 1

    await context.bot.send_message(
        chat_id=f"@{ADMIN_USERNAME}",
        text=txt
    )

    # Ask admin → post to channel ?
    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Post", callback_data="mw_post_yes")],
        [InlineKeyboardButton("❌ Cancel", callback_data="mw_post_no")]
    ])

    await context.bot.send_message(
        chat_id=f"@{ADMIN_USERNAME}",
        text="✅ Auto winners ready!\nPost to channel?",
        reply_markup=kb
    )


# POST winners to Channel
async def mwinner_post_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if user.username != ADMIN_USERNAME:
        return await query.message.reply_text("❌ Not Authorized")

    if data == "mw_post_no":
        return await query.message.reply_text("❌ Cancelled!")

    if data == "mw_post_yes":
        txt = (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🏆 Power Point Break — Giveaway Winners\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        c = 1
        for n, u, t in winner_data:
            txt += f"#{c} @{n} | {u} | {t}\n"
            c += 1

        txt += (
            "\n🎉 Congratulations to all!\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👑 Admin: @{ADMIN_USERNAME}\n"
            "🎙 Hosted by: Power Point Break"
        )

        try:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=txt
            )
        except:
            pass

        await query.message.reply_text("✅ Posted to channel!")

# ================================================================
# ✅ NORMAL /setpost SYSTEM
#   Admin: /setpost
#   → ask for post
#   → ask for time
#   → approve → post to channel + countdown
# ================================================================

pending_post    = False
pending_time    = False
stored_post     = None
stored_seconds  = None
post_running    = False


async def setpost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_post, pending_time, post_running

    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    if post_running:
        return await update.message.reply_text("⚠️ Another scheduled post is running!")

    pending_post = True
    pending_time = False
    await update.message.reply_text(
        "✅ Send the post you want to schedule.\n"
        "👉 Text / Photo allowed."
    )


async def capture_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_post, stored_post, pending_time

    if not pending_post:
        return

    stored_post  = update.message
    pending_post = False
    pending_time = True

    await update.message.reply_text(
        "✅ Post saved!\n"
        "Now send Countdown time (10s / 10m / 10h)"
    )


async def capture_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_time, stored_seconds

    if not pending_time:
        return

    raw = update.message.text.strip()

    try:
        unit = raw[-1].lower()
        num  = int(raw[:-1])

        if unit == "s":
            stored_seconds = num
        elif unit == "m":
            stored_seconds = num * 60
        elif unit == "h":
            stored_seconds = num * 3600
        else:
            return await update.message.reply_text("❌ Wrong time format!\nUse: 10s/10m/10h")

    except:
        return await update.message.reply_text("❌ Wrong time format!")

    pending_time = False

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Approve", callback_data="sp_yes")],
        [InlineKeyboardButton("❌ Reject",  callback_data="sp_no")]
    ])

    await update.message.reply_text(
        f"✅ Countdown set → {raw}\nApprove?",
        reply_markup=kb
    )


# ================================================================
# ✅ /setpost — Callback Approve/Reject
# ================================================================

async def setpost_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global stored_post, stored_seconds, post_running

    query = update.callback_query
    await query.answer()

    user = query.from_user
    data = query.data

    if user.username != ADMIN_USERNAME:
        return await query.message.reply_text("❌ Not Authorized")

    # Cancel
    if data == "sp_no":
        stored_post    = None
        stored_seconds = None
        return await query.message.reply_text("❌ Cancelled!")

    # Approve
    if data == "sp_yes":
        if not stored_post or not stored_seconds:
            return await query.message.reply_text("❌ Missing data!")

        # Post → Channel
        try:
            if stored_post.text:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=stored_post.text
                )
            elif stored_post.photo:
                await context.bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=stored_post.photo[-1].file_id,
                    caption=stored_post.caption
                )
        except:
            return await query.message.reply_text("❌ Failed to post!")

        await query.message.reply_text("✅ Posted!\n⏳ Countdown started…")

        post_running = True
        context.application.create_task(run_post_timer(context))


# ================================================================
# ✅ /setpost — Timer Loop + Progress
# ================================================================

async def run_post_timer(context: ContextTypes.DEFAULT_TYPE):
    global stored_seconds, post_running

    total = stored_seconds
    start = datetime.now()

    while True:
        passed = (datetime.now() - start).total_seconds()
        left   = total - passed

        if left <= 0:
            break

        bar = progress_bar(passed / total)
        t_left = int(left)

        msg = (
            "🚀 Giveaway Starting Soon…\n"
            f"⏰ Time Left: {t_left} sec\n"
            f"{bar}"
        )

        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
        except:
            pass

        await asyncio.sleep(3)

    # Finish
    post_running    = False
    stored_seconds  = None

    end_message = (
        "⌛ Countdown Finished!\n\n"
        "😔 Time is over…\n\n"
        "🏆 Stay tuned — Giveaway winners are coming!"
    )

    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=end_message
        )
    except:
        pass

# ================================================================
# ✅ /countpost SYSTEM
#   - /countpost → ask post
#   - ask time
#   - approve → post + live countdown
# ================================================================

async def countpost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global countpost_pending, countpost_time_pending, countpost_running

    user = update.effective_user
    if user.username != ADMIN_USERNAME:
        return await update.message.reply_text("❌ Not Authorized")

    if countpost_running:
        return await update.message.reply_text("⚠️ Another countdown is already running!")

    countpost_pending      = True
    countpost_time_pending = False

    await update.message.reply_text(
        "✅ Send the post you want to publish!\n"
        "👉 Text / Photo allowed."
    )


async def capture_countpost_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global countpost_pending, countpost_time_pending, countpost_post

    if not countpost_pending:
        return

    countpost_post  = update.message
    countpost_pending      = False
    countpost_time_pending = True

    await update.message.reply_text(
        "✅ Post saved!\n"
        "Now send countdown → (10s / 10m / 10h)"
    )


async def capture_countpost_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global countpost_time_pending, countpost_seconds

    if not countpost_time_pending:
        return

    raw = update.message.text.strip()

    try:
        unit = raw[-1].lower()
        num  = int(raw[:-1])

        if unit == "s":
            countpost_seconds = num
        elif unit == "m":
            countpost_seconds = num * 60
        elif unit == "h":
            countpost_seconds = num * 3600
        else:
            return await update.message.reply_text("❌ Wrong format!\nUse: 10s/10m/10h")

    except:
        return await update.message.reply_text("❌ Wrong time format!")

    countpost_time_pending = False

    kb = InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Publish to Channel", callback_data="cpost_yes")],
        [InlineKeyboardButton("❌ Cancel",             callback_data="cpost_no")]
    ])

    await update.message.reply_text(
        f"✅ Countdown set → {raw}\nPublish now?",
        reply_markup=kb
    )


async def countpost_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global countpost_post, countpost_seconds, countpost_running

    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if user.username != ADMIN_USERNAME:
        return await query.message.reply_text("❌ Not Authorized")

    # cancel
    if data == "cpost_no":
        countpost_post      = None
        countpost_seconds   = None
        return await query.message.reply_text("❌ Cancelled!")

    # YES — publish
    if data == "cpost_yes":
        if not countpost_post or not countpost_seconds:
            return await query.message.reply_text("❌ Missing data!")

        # post → channel
        try:
            if countpost_post.text:
                await context.bot.send_message(
                    chat_id=CHANNEL_ID,
                    text=countpost_post.text
                )
            elif countpost_post.photo:
                await context.bot.send_photo(
                    chat_id=CHANNEL_ID,
                    photo=countpost_post.photo[-1].file_id,
                    caption=countpost_post.caption
                )
        except:
            return await query.message.reply_text("❌ Failed to post!")

        await query.message.reply_text("✅ Posted! Countdown started!")

        countpost_running = True
        context.application.create_task(countpost_timer(context))


async def countpost_timer(context: ContextTypes.DEFAULT_TYPE):
    global countpost_seconds, countpost_running

    total = countpost_seconds
    start = datetime.now()

    while True:
        passed = (datetime.now() - start).total_seconds()
        left   = total - passed

        if left <= 0:
            break

        bar = progress_bar(passed / total)
        t_left = int(left)

        msg = (
            "🚀 Countdown Running…\n"
            f"⏰ Time Left: {t_left} sec\n"
            f"{bar}"
        )

        try:
            await context.bot.send_message(chat_id=CHANNEL_ID, text=msg)
        except:
            pass

        await asyncio.sleep(3)

    countpost_running = False
    countpost_seconds = None

    final = (
        "⌛ Countdown Finished!\n\n"
        "😔 Time is over…\n\n"
        "🏆 Stay tuned — Giveaway winners are coming!"
    )

    try:
        await context.bot.send_message(chat_id=CHANNEL_ID, text=final)
    except:
        pass

# ================================================================
# ✅ ROUTERS → MULTI-WINNER POST
# ================================================================
async def mwinner_post_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user = query.from_user
    data = query.data

    if user.username != ADMIN_USERNAME:
        return await query.message.reply_text("❌ Not Authorized")

    if data == "mw_post_no":
        return await query.message.reply_text("❌ Cancelled!")

    if data == "mw_post_yes":
        txt = (
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "🏆 Power Point Break — Giveaway Winners\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
        )

        c = 1
        for n, u, t in winner_data:
            txt += f"#{c} @{n} | {u} | {t}\n"
            c += 1

        txt += (
            "\n🎉 Congratulations to all!\n"
            "━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"👑 Admin: @{ADMIN_USERNAME}\n"
            "🎙 Hosted by: Power Point Break"
        )

        try:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=txt
            )
        except:
            pass

        await query.message.reply_text("✅ Posted to channel!")


# ================================================================
# ✅ ADD HANDLERS
# ================================================================
def setup_handlers(app):

    # MAIN cmds
    app.add_handler(CommandHandler("start",     start))
    app.add_handler(CommandHandler("on",        on_cmd))
    app.add_handler(CommandHandler("off",       off_cmd))
    app.add_handler(CommandHandler("setwinner", setwinner_cmd))
    app.add_handler(CommandHandler("status",    status_cmd))
    app.add_handler(CommandHandler("reset",     reset_cmd))
    app.add_handler(CommandHandler("help",      help_cmd))
    app.add_handler(CommandHandler("adminpanel", adminpanel))

    # BACKUPS
    app.add_handler(CommandHandler("backup",         backup_cmd))
    app.add_handler(CommandHandler("backup_winners", backup_winners_cmd))

    # MULTI-WINNER
    app.add_handler(CommandHandler("setmwinner", setmwinner_cmd))
    app.add_handler(CallbackQueryHandler(mwinner_router,     pattern="^mw_"))
    app.add_handler(CallbackQueryHandler(mwinner_post_router, pattern="^mw_post"))

    # /setpost
    app.add_handler(CommandHandler("setpost", setpost_cmd))
    app.add_handler(CallbackQueryHandler(setpost_router, pattern="^sp_"))

    # /countpost
    app.add_handler(CommandHandler("countpost", countpost_cmd))
    app.add_handler(CallbackQueryHandler(countpost_router, pattern="^cpost"))

    # JOIN BTN
    app.add_handler(CallbackQueryHandler(join_button, pattern="join_btn"))

    # TEXT CAPTURE ORDER VERY IMPORTANT
    # 1) Multi-Winner
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_count))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_time))

    # 2) /setpost
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_post))

    # 3) /countpost
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_countpost_post))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, capture_countpost_time))

    # 4) Default user msg
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_msg))



# ================================================================
# ✅ FALLBACK USER MSG
# ================================================================
async def user_msg(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid  = user.id
    uname = user.username or "NoUsername"

    # Giveaway OFF
    if not giveaway_active and not mwinner_active:
        return await update.message.reply_text(
            CLOSED_TEMPLATE.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )

    # Multi-winner
    if mwinner_active:
        if uid not in mwinner_buffer:
            mwinner_buffer.append(uid)
        return await update.message.reply_text("✅ You have joined the Giveaway! 🍀")

    # Normal
    if uid in joined_users:
        return await update.message.reply_text(
            ALREADY_TEMPLATE.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )

    # Full
    if len(winner_data) >= winner_limit:
        return await update.message.reply_text(
            FULL_TEMPLATE.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )

    # Accept
    joined_users.append(uid)
    timestamp = now()

    winner_data.append((uname, uid, timestamp))
    save_winner(uid, uname)
    save_user(uid, uname)

    # DM
    try:
        await context.bot.send_message(
            chat_id=uid,
            text=WINNER_DM.format(ADMIN_USERNAME=ADMIN_USERNAME)
        )
    except:
        pass

    await update.message.reply_text("✅ You joined the Giveaway!")


# ================================================================
# ✅ MAIN
# ================================================================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    setup_handlers(app)
    print("✅ BOT STARTED…")
    app.run_polling()


if __name__ == "__main__":
    main()
