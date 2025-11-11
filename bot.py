# ================================
# ✅ POWER POINT BREAK GIVEAWAY BOT
# PART-1 — BASE SETUP
# ================================

import asyncio
import random
import json
import re
from datetime import datetime, timedelta

from telegram import (
    Update, InlineKeyboardButton,
    InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)

# ================================
# ✅ CONFIG
# ================================
BOT_TOKEN = "8370403090:AAG-QBNzge4OdldCSGDAIiWtJQEqSRAVnlw"
ADMIN_USERNAME = "MinexxProo"         # without '@'
CHANNEL_ID = "-1003384116631"        # channel to post winners     <== CHANGE THIS

DATA_FILE = "data.json"


# =================================================
# ✅ Load / Save JSON (persistent storage)
# =================================================
def load_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return {
            "giveaway_enabled": False,
            "winner_limit": 0,
            "winners": [],
            "winner_details": [],
            "old_winners": [],
            "participants": [],
            "winner_history": [],
        }


def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)
      # ================================
# ✅ PART-2 — UTILITIES + BASIC UI
# ================================

data = load_data()   # Load from JSON


# =================================================
# ✅ Check Admin
# =================================================
def is_admin(user):
    return (user.username == ADMIN_USERNAME)


# =================================================
# ✅ Save data wrapper
# =================================================
def commit():
    save_data(data)


# =================================================
# ✅ Parse time input
#   Examples:
#   "10s" → 10 sec
#   "10m" → 600 sec
#   "1h"  → 3600 sec
#   "1h 10m 20s" → full parse
# =================================================
def parse_time_string(t):
    total = 0
    matches = re.findall(r"(\d+)([hms])", t)

    for val, unit in matches:
        val = int(val)
        if unit == "h":
            total += val * 3600
        elif unit == "m":
            total += val * 60
        elif unit == "s":
            total += val

    return total


# =================================================
# ✅ Progress Bar Generator
#    fraction = 0.70 → 70%
# =================================================
def progress_bar(fraction):
    length = 10
    filled = int(length * fraction)
    empty = length - filled
    return "▰" * filled + "▱" * empty


# =================================================
# ✅ Make Welcome Button Layout
# =================================================
def welcome_keyboard():
    btn = [
        [InlineKeyboardButton("🚀 Join Giveaway Now!", callback_data="join_now")]
    ]
    return InlineKeyboardMarkup(btn)


# =================================================
# ✅ Normal user Welcome Message
# =================================================
async def send_welcome(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    username = f"@{user.username}" if user.username else "Unknown"

    txt = (
        f"Hello {username} 🎉\n"
        f"🆔 User ID: {user.id}\n\n"
        f"📩 To participate in the giveaway,\n"
        f"👉 Please 👇 Tap the button!\n\n"
        f"┏━━━━━━━━━━━━━━━━━━━━━━┓\n"
        f"🚀🌟 Join the Giveaway Now!\n"
        f"🎁🏆 Don’t miss your chance to win!\n"
        f"┗━━━━━━━━━━━━━━━━━━━━━━┛\n\n"
        f"✅ If you are selected as a winner,\n"
        f"you will be notified instantly!\n\n"
        f"💬 If you need help, contact:\n"
        f"👉 @{ADMIN_USERNAME}\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"Good luck! 🍀"
    )

    await update.message.reply_text(txt, reply_markup=welcome_keyboard())


# =================================================
# ✅ START command
#   Admin → show admin panel
#   User  → normal welcome
# =================================================
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # Admin panel
    if is_admin(user):
        txt = (
            f"👑 Welcome To Your Bot Admin @{ADMIN_USERNAME}\n\n"
            f"Here are your admin controls:\n\n"
            f"/allcd → Show all commands\n"
            f"/on → Start Giveaway\n"
            f"/off → Stop Giveaway\n"
            f"/set X → Set winner count\n"
            f"/setoldwiner → Upload old winners\n"
            f"/allw → Show current winners\n"
            f"/alluserid → Show all winners\n"
            f"/allwinnercount → Full Winner History\n"
            f"/reset → Reset current giveaway\n"
            f"/winauto → Auto Giveaway\n"
            f"/countdown → Custom countdown\n"
        )
        await update.message.reply_text(txt)
        return

    # Normal user welcome
    await send_welcome(update, context)


# =================================================
# ✅ Normal Message handler
#   → Non-admin always show welcome
#   → Admin ignore
# =================================================
async def normal_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if is_admin(user):
        return   # admin normal text ignored
    await send_welcome(update, context)


# ================================
# ✅ PART-3 — MANUAL GIVEAWAY SYSTEM
# ================================


# =================================================
# ✅ /on — Start giveaway
# =================================================
async def on_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user):
        return

    data["giveaway_enabled"] = True
    commit()

    await update.message.reply_text(
        "✅ Giveaway Started!\nUse /set <count> to set winners."
    )


# =================================================
# ✅ /off — Stop giveaway
# =================================================
async def off_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user):
        return

    data["giveaway_enabled"] = False
    commit()

    await update.message.reply_text("⛔ Giveaway Closed!")


# =================================================
# ✅ /set X — set winner count
# =================================================
async def set_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user):
        return

    try:
        num = int(context.args[0])
    except:
        await update.message.reply_text("❌ Invalid!\nUse: /set 10")
        return

    data["winner_limit"] = num
    commit()

    await update.message.reply_text(f"✅ Winner Count Set: {num}")


# =================================================
# ✅ /setoldwiner — load old winners
# =================================================
pending_old = False

async def setoldwiner_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_old
    user = update.effective_user
    if not is_admin(user):
        return

    pending_old = True
    await update.message.reply_text(
        "✅ Please send me old winners!\n\nFormat:\n@rahim | 1234567\n@joy | 9876543"
    )


# =================================================
# ✅ Parse old winners message
# =================================================
async def oldwiner_loader(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global pending_old
    user = update.effective_user
    if not is_admin(user):
        return

    if not pending_old:
        return

    txt = update.message.text.strip()
    lines = txt.split("\n")
    count = 0

    for line in lines:
        m = re.findall(r"\|\s?(\d+)", line)
        if m:
            uid = int(m[0])
            if uid not in data["old_winners"]:
                data["old_winners"].append(uid)
                count += 1

    pending_old = False
    commit()

    await update.message.reply_text(
        f"✅ Old winner list saved!\nTotal added: {count}"
    )


# =================================================
# ✅ /allw — Show current giveaway winners
# =================================================
async def allw_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user):
        return

    if not data["winner_details"]:
        await update.message.reply_text("❌ No winners yet.")
        return

    txt = "🏆 Current Winner List:\n"
    c = 1
    for w in data["winner_details"]:
        txt += f"{c}) {w['username']} | {w['user_id']}\n"
        c += 1

    await update.message.reply_text(txt)


# =================================================
# ✅ JOIN button logic
#
# 6-STEP CHECK:
# 1) giveaway ON?
# 2) old_winners?
# 3) winners?
# 4) slot FULL?
# 5) already participated?
# 6) -> WINNER
# =================================================
async def join_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user
    uid = user.id
    uname = f"@{user.username}" if user.username else "Unknown"

    await query.answer()

    # 1) giveaway ON?
    if not data["giveaway_enabled"]:
        return await query.message.reply_text(
            "⛔️ ❌ GIVEAWAY CLOSED ❌ ⛔️\n━━━━━━━━━━━━━━━━━━━━━━━\n📩 Contact Admin:\n👉 @%s\n\n💫 Please try another Giveaway!\n━━━━━━━━━━━━━━━━━━━━━━━"
            % ADMIN_USERNAME
        )

    # 2) OLD WINNER?
    if uid in data["old_winners"]:
        return await query.message.reply_text(
            "┏━━━━━━━━━━━━━━━━━━━┓\n"
            "🏆 You’ve already won this giveaway!\n\n"
            "⚖️ To keep things fair, repeat participation isn’t allowed.\n"
            "🙏 Thank you for understanding!\n\n"
            f"📩 Admin Support: @{ADMIN_USERNAME}\n"
            "┗━━━━━━━━━━━━━━━━━━━┛"
        )

    # 3) Already WINNER?
    if uid in data["winners"]:
        return await query.message.reply_text(
            "┏━━━━━━━━━━━━━━━━━━━┓\n"
            "🏆 You’ve already won this giveaway!\n\n"
            "⚖️ To keep things fair, repeat participation isn’t allowed.\n"
            "🙏 Thank you for understanding!\n\n"
            f"📩 Admin Support: @{ADMIN_USERNAME}\n"
            "┗━━━━━━━━━━━━━━━━━━━┛"
        )

    # 4) slot FULL?
    if data["winner_limit"] > 0 and len(data["winners"]) >= data["winner_limit"]:
        return await query.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "😔 Oops! All winners are already selected!\n"
            "🎉 Thanks for joining!\n\n"
            "🍀 Try again — more giveaways soon!\n"
            "💙 Stay with Power Point Break!\n\n"
            f"📞 For support:\n👉 @{ADMIN_USERNAME}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    # 5) Already participated?
    if uid in data["participants"]:
        return await query.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "⚠️ You have already participated!\n\n"
            f"📩 For any concerns, please contact:\n👉 @{ADMIN_USERNAME}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    # NEW → WINNER ✅
    data["participants"].append(uid)
    data["winners"].append(uid)

    detail = {
        "username": uname,
        "user_id": uid,
        "time": datetime.now().isoformat()
    }
    data["winner_details"].append(detail)
    data["winner_history"].append(detail)
    commit()

    # DM admin
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=f"✅ WINNER\nUsername: {uname}\nUser ID: {uid}"
    )

    # notify user
    await query.message.reply_text(
        "🎉 CONGRATULATIONS! 🎉\n"
        "You are one of the WINNERS of our Giveaway! 🏆\n\n"
        f"📩 Contact Admin to claim your reward:\n👉 @{ADMIN_USERNAME}\n\n"
        "💙 Hosted by: Power Point Break"
              )


# ================================
# ✅ PART-4 — AUTO GIVEAWAY + HISTORY
# ================================


# =================================================
# ✅ /alluserid — Winner Username | ID
# =================================================
async def alluserid_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user):
        return

    if not data["winner_details"]:
        return await update.message.reply_text("❌ No winners found.")

    txt = "━━━━━━━━━━━━━━━━━━━━━━\n👥 All Winner User List\n━━━━━━━━━━━━━━━━━━━━━━\n"
    for w in data["winner_details"]:
        txt += f"{w['username']} | {w['user_id']}\n"

    await update.message.reply_text(txt)


# =================================================
# ✅ /allwinnercount — FULL WINNER HISTORY
# =================================================
async def allwinnercount_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user):
        return
    
    if not data["winner_history"]:
        return await update.message.reply_text("❌ No winner history found.")

    txt = "━━━━━━━━━━━━━━━━━━━━━━\n🏆 Full Winner History\n━━━━━━━━━━━━━━━━━━━━━━\n"
    
    # count tracker
    count_map = {}
    for w in data["winner_history"]:
        uid = w["user_id"]
        count_map[uid] = count_map.get(uid, 0) + 1

    for w in data["winner_history"]:
        uid = w["user_id"]
        txt += (
            f"{w['username']} | {uid}\n"
            f"🎁 Prize: Giveaway Winner\n"
            f"🧮 Win Count: {count_map[uid]}\n"
            f"🗓️ Last Won: {w['time']}\n"
            f"🎯 Giveaway: Auto/Manual\n"
            "──────────────────────\n"
        )

    await update.message.reply_text(txt)


# =================================================
# ✅ /winauto — AUTO GIVEAWAY
# =================================================

auto_pending_winner_count = None
auto_pending_timer = None
auto_mode = False
auto_winner_buffer = []


async def winauto_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_mode
    user = update.effective_user
    if not is_admin(user):
        return
    
    auto_mode = True
    await update.message.reply_text(
        "✅ Set your Winner Count!\n\nExample: 20"
    )


# =================================================
# ✅ Step-2: Read Winner Count
# =================================================
async def auto_read_winner_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_pending_winner_count, auto_mode
    user = update.effective_user
    if not is_admin(user):
        return
    if not auto_mode:
        return

    try:
        c = int(update.message.text.strip())
    except:
        return await update.message.reply_text("❌ Invalid number!\nExample: 20")

    auto_pending_winner_count = c
    data["winner_limit"] = c
    commit()

    await update.message.reply_text(
        f"✅ Winner Count set to {c}!\nNow send your time:\nExample:\n10s\n10m\n1h\n1h 10m 20s"
    )


# =================================================
# ✅ Step-3: Read Time + Start COUNTDOWN
# =================================================
async def auto_read_timer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global auto_pending_timer, auto_mode
    user = update.effective_user
    if not is_admin(user):
        return
    if not auto_mode:
        return

    t = update.message.text.strip()
    sec = parse_time_string(t)

    if sec <= 0:
        return await update.message.reply_text("❌ Invalid time format!")

    auto_pending_timer = sec

    await update.message.reply_text(
        f"✅ Auto Giveaway Started!\n⏳ Time Left: {t}"
    )

    # Countdown
    await auto_countdown_worker(context, sec)


# =================================================
# ✅ COUNTDOWN WORKER
# =================================================
async def auto_countdown_worker(context, sec):
    global auto_mode

    # Make giveaway live
    data["giveaway_enabled"] = True
    commit()

    total = sec

    while sec > 0:
        fraction = sec / total
        bar = progress_bar(fraction)

        text = (
            f"⏳ Time Left: {format_time(sec)}\n"
            f"{bar} {int(fraction * 100)}%\n\n"
            f"⏰ Time is running! Hurry up! ⚡"
        )

        # Send to admin only or channel?  
        # You may forward to channel — optional  
        try:
            await context.bot.send_message(chat_id=admin_chat_id(), text=text)
        except:
            pass

        await asyncio.sleep(1)
        sec -= 1

    # END MESSAGE
    await context.bot.send_message(
        chat_id=admin_chat_id(),
        text=(
            "⏳ Countdown has ended!\n"
            "🎉 Stay ready — Winners will be announced very soon!\n\n"
            "🎙 Hosted by: Power Point Break"
        )
    )

    # Now pick winners
    await auto_pick_winners(context)


# =================================================
# ✅ Helper: format seconds → H:M:S
# =================================================
def format_time(sec):
    h = sec // 3600
    m = (sec % 3600) // 60
    s = sec % 60
    if h > 0:
        return f"{h:02d}:{m:02d}:{s:02d}"
    else:
        return f"{m:02d}:{s:02d}"


# =================================================
# ✅ Helper: admin chat id (DM)
# =================================================
def admin_chat_id():
    # later updated by first admin contact
    return 0   # must be replaced


# =================================================
# ✅ AUTO RANDOM WINNER SELECTION
# =================================================
async def auto_pick_winners(context):
    global auto_pending_winner_count, auto_mode

    # Collect only valid participants
    valid = [
        x for x in data["participants"]
        if x not in data["old_winners"]
    ]

    random.shuffle(valid)

    selected = valid[:auto_pending_winner_count]

    final_list = []

    for uid in selected:
        name = f"@unknown"
        # try find username from winner_details history
        for u in data["winner_details"]:
            if u["user_id"] == uid:
                name = u["username"]

        final_list.append({"username": name, "user_id": uid})

        # store history
        detail = {
            "username": name,
            "user_id": uid,
            "time": datetime.now().isoformat()
        }
        data["winner_history"].append(detail)
        data["winners"].append(uid)

        # DM winner
        try:
            await context.bot.send_message(
                chat_id=uid,
                text=(
                    "🎉 CONGRATULATIONS! 🎉\n"
                    "You are one of the WINNERS of our Giveaway! 🏆\n\n"
                    f"📩 Contact Admin to claim your reward:\n👉 @{ADMIN_USERNAME}\n\n"
                    "💙 Hosted by: Power Point Break"
                )
            )
        except:
            pass

    commit()

    # Ask admin approval
    txt = "✅ AUTO WINNER LIST\n\n"
    c = 1
    for w in final_list:
        txt += f"{c}) {w['username']} | {w['user_id']}\n"
        c += 1

    btn = [
        [InlineKeyboardButton("✅ APPROVE & POST", callback_data="auto_post")],
        [InlineKeyboardButton("❌ REJECT", callback_data="auto_reject")]
    ]

    await context.bot.send_message(
        chat_id=admin_chat_id(),
        text=txt + "\nPost to channel?",
        reply_markup=InlineKeyboardMarkup(btn)
    )

    auto_mode = False


# ===========================================
# ✅ PART-5A — AUTO APPROVE + COUNTDOWN SYSTEM
# ===========================================


# =====================================================
# ✅ AUTO — APPROVE / POST TO CHANNEL
# =====================================================
async def auto_approve_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    if not is_admin(user):
        await query.answer("❌ Not Authorized")
        return

    await query.answer("✅ Approved! Posting...")

    # Build final text
    txt = "🏆 Power Point Break — Giveaway Winners (Auto)\n"
    txt += "────────────────────────\n"

    c = 1
    for w in data["winner_details"]:
        txt += f"#{c} {w['username']} | {w['user_id']}\n"
        c += 1

    txt += (
        "────────────────────────\n"
        "🎉 Congratulations to all!\n"
        "💙 Stay with Power Point Break!\n"
        f"📞 Admin: @{ADMIN_USERNAME}"
    )

    try:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=txt
        )
        await query.message.reply_text("✅ Posted to Channel!")
    except:
        await query.message.reply_text("❌ Failed to post to channel!")


# =====================================================
# ✅ AUTO — REJECT
# =====================================================
async def auto_reject_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user = query.from_user

    if not is_admin(user):
        await query.answer("❌ Not Authorized")
        return

    await query.answer("❌ Canceled")
    await query.message.reply_text("❌ Auto winner announcement cancelled.")


# =====================================================
# ✅ CALLBACK HANDLER ROUTER
#   (approve / reject / join)
# =====================================================
async def callback_router(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data_cb = query.data

    if data_cb == "join_now":
        return await join_callback(update, context)

    elif data_cb == "auto_post":
        return await auto_approve_callback(update, context)

    elif data_cb == "auto_reject":
        return await auto_reject_callback(update, context)

    await query.answer("❌ Unknown Action")


# =====================================================
# ✅ /countdown → Custom Post + Timer + Progress
# =====================================================
countdown_wait_post = False
countdown_wait_time = False
countdown_content = ""
countdown_seconds = 0


async def countdown_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global countdown_wait_post
    user = update.effective_user

    if not is_admin(user):
        return

    countdown_wait_post = True
    await update.message.reply_text("✅ Send your custom post text!")


# =====================================================
# ✅ STEP-1 → Receive Custom Post
# =====================================================
async def countdown_receive_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global countdown_wait_post, countdown_wait_time, countdown_content
    user = update.effective_user

    if not is_admin(user):
        return
    if not countdown_wait_post:
        return

    countdown_content = update.message.text
    countdown_wait_post = False
    countdown_wait_time = True

    await update.message.reply_text(
        "✅ Post Saved!\n\n"
        "Now send your countdown time.\n\n"
        "✅ Examples:\n"
        "10s → 10 sec\n"
        "10m → 10 min\n"
        "1h → 1 hour\n"
        "1h 10m → 1h10m\n"
        "10m 20s → 10m20s\n"
        "1h 10m 20s → full"
    )


# =====================================================
# ✅ STEP-2 → Receive Time + Start Countdown
# =====================================================
async def countdown_receive_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global countdown_wait_time, countdown_seconds
    user = update.effective_user

    if not is_admin(user):
        return
    if not countdown_wait_time:
        return

    t = update.message.text.strip()
    sec = parse_time_string(t)

    if sec <= 0:
        return await update.message.reply_text("❌ Invalid time!")

    countdown_seconds = sec
    countdown_wait_time = False

    await update.message.reply_text("✅ Countdown Started!")

    asyncio.create_task(
        countdown_worker(context)
    )


# =====================================================
# ✅ COUNTDOWN WORKER
# =====================================================
async def countdown_worker(context):
    global countdown_seconds

    total = countdown_seconds
    sec = countdown_seconds

    while sec > 0:
        fraction = sec / total
        bar = progress_bar(fraction)

        text = (
            f"{countdown_content}\n\n"
            f"⏳ Time Left: {format_time(sec)}\n"
            f"{bar} {int(fraction * 100)}%\n\n"
            f"⏰ Time is running! Hurry up! ⚡"
        )

        # You can send to channel or admin
        try:
            await context.bot.send_message(
                chat_id=CHANNEL_ID,
                text=text
            )
        except:
            pass

        await asyncio.sleep(1)
        sec -= 1

    # END output
    end_text = (
        "⏳ Countdown has ended!\n"
        "🎉 Stay ready — Winners will be announced very soon!\n\n"
        "🎙 Hosted by: Power Point Break"
    )

    await context.bot.send_message(
        chat_id=CHANNEL_ID,
        text=end_text
  )


# ===========================================
# ✅ PART-5B — HANDLERS + BOT RUN
# ===========================================

# =====================================================
# ✅ HANDLER REGISTRATION
# =====================================================

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # ✅ Commands
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("on", on_command))
    app.add_handler(CommandHandler("off", off_command))
    app.add_handler(CommandHandler("set", set_command))
    app.add_handler(CommandHandler("setoldwiner", setoldwiner_command))
    app.add_handler(CommandHandler("allw", allw_command))
    app.add_handler(CommandHandler("alluserid", alluserid_command))
    app.add_handler(CommandHandler("allwinnercount", allwinnercount_command))
    app.add_handler(CommandHandler("reset", reset_command))
    app.add_handler(CommandHandler("winauto", winauto_command))
    app.add_handler(CommandHandler("countdown", countdown_command))
    app.add_handler(CommandHandler("allcd", allcd_command))

    # ✅ Messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, normal_message))

    # ✅ Old winner loader
    app.add_handler(MessageHandler(filters.TEXT & filters.USER(ADMIN_USERNAME), oldwiner_loader))

    # ✅ Auto winner count input
    app.add_handler(MessageHandler(filters.TEXT & filters.USER(ADMIN_USERNAME), auto_read_winner_count))

    # ✅ Auto timer input
    app.add_handler(MessageHandler(filters.TEXT & filters.USER(ADMIN_USERNAME), auto_read_timer))

    # ✅ Countdown post receiver
    app.add_handler(MessageHandler(filters.TEXT & filters.USER(ADMIN_USERNAME), countdown_receive_post))

    # ✅ Countdown time receiver
    app.add_handler(MessageHandler(filters.TEXT & filters.USER(ADMIN_USERNAME), countdown_receive_time))

    # ✅ Callback
    app.add_handler(CallbackQueryHandler(callback_router))

    print("✅ BOT IS RUNNING…")
    app.run_polling()


# =====================================================
# ✅ /reset — CLEAR current giveaway data (Keep history)
# =====================================================
async def reset_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user):
        return

    data["winners"] = []
    data["winner_details"] = []
    data["participants"] = []
    data["winner_limit"] = 0
    commit()

    await update.message.reply_text("✅ All current giveaway data cleared!")


# =====================================================
# ✅ /allcd — Show commands
# =====================================================
async def allcd_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user):
        return

    txt = (
        "✅ COMMAND LIST ✅\n\n"
        "/start → Start\n"
        "/on → Start Giveaway\n"
        "/off → Stop Giveaway\n"
        "/set X → Set winner count\n"
        "/setoldwiner → Upload old winners\n"
        "/allw → Show current winners\n"
        "/alluserid → Show all winners username & ID\n"
        "/allwinnercount → Full winner history\n"
        "/reset → Reset current giveaway data\n"
        "/winauto → Auto Giveaway\n"
        "/countdown → Custom countdown\n"
    )

    await update.message.reply_text(txt)


# =====================================================
# ✅ Run main
# =====================================================
if __name__ == "__main__":
    main()

