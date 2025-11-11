# ===========================================
# ✅ POWER POINT BREAK — GIVEAWAY BOT
# ✅ PART-1 — BASE + CONFIG + STORAGE
# ===========================================

import json
import asyncio
import random
import re
from datetime import datetime, timedelta

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup
)
from telegram.ext import (
    ApplicationBuilder, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

# ==============================
# ✅ BOT CONFIG
# ==============================
BOT_TOKEN = "8370403090:AAG-QBNzge4OdldCSGDAIiWtJQEqSRAVnlw"       # << must update with your bot token
ADMIN_USERNAME = "MinexxProo"          # admin username WITHOUT @

DATA_FILE = "botdata.json"             # json database file


# ==============================
# ✅ DEFAULT STORAGE MODEL
# ==============================
DEFAULT_DATA = {
    "giveaway_enabled": False,     # /on → TRUE , /off → FALSE
    "winner_limit": 0,             # /set X

    "winners": [],                 # [{username, user_id, timestamp}]
    "participants": [],            # [user_id]
    "old_winners": [],             # [user_id]

    "winner_history": [],          # lifetime record

    "verification_links": [],      # @requiredChannel list

    "countdown_seconds": 0,        # countdown time (safe mode)
    "countdown_content": "",       # countdown message

    "auto_mode": False             # /winauto → TRUE
}


# ==============================
# ✅ LOAD DATA
# ==============================
def load_data():
    """
    Loads JSON data → returns dictionary
    If missing/corrupt → returns default
    """
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except:
        return DEFAULT_DATA.copy()


# ==============================
# ✅ SAVE DATA
# ==============================
def save_data():
    """
    Save DATA → JSON file
    """
    with open(DATA_FILE, "w") as f:
        json.dump(DATA, f, indent=4)


# ✅ load into memory
DATA = load_data()


# ==============================
# ✅ ADMIN CHECK
# ==============================
def is_admin(user):
    """
    Returns TRUE only if this user is admin
    """
    return (user.username or "").lower() == ADMIN_USERNAME.lower()


# ===========================================
# ✅ PART-2 — UTILITIES + UI
# ===========================================


# ==============================
# ✅ TIME STRING → SECONDS
# Example:
#  1h → 3600
#  10m → 600
#  1h 10m 30s → 4230
# ==============================
def parse_time(text: str):
    text = text.lower().strip()
    pattern = r"(?:(\d+)h)?\s*(?:(\d+)m)?\s*(?:(\d+)s)?"
    match = re.match(pattern, text)
    if not match:
        return 0

    h = int(match.group(1)) if match.group(1) else 0
    m = int(match.group(2)) if match.group(2) else 0
    s = int(match.group(3)) if match.group(3) else 0

    return h * 3600 + m * 60 + s



# ==============================
# ✅ PROGRESS BAR
# percent → box
# ==============================
def progress_bar(percent: float):
    total = 10
    filled = int((percent / 100) * total)
    empty = total - filled
    return "▰" * filled + "▱" * empty



# ==============================
# ✅ FORMAT TIMESTAMP → READABLE
# ==============================
def fmt_time(ts):
    try:
        dt = datetime.fromisoformat(ts)
        return dt.strftime("%Y-%m-%d %H:%M")
    except:
        return "N/A"



# ==============================
# ✅ MAKE WINNER ENTRY
# ==============================
def make_winner_entry(user):
    return {
        "username": user.username or "",
        "user_id": user.id,
        "timestamp": datetime.now().isoformat()
    }



# ==============================
# ✅ SEND START SCREEN — USER
# ==============================
async def send_user_start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    text = (
        f"Hello @{user.username} 🎉\n"
        f"🆔 User ID: {user.id}\n\n"
        "📩 To participate in the giveaway,\n"
        "👉 Please 👇 Tap the button!"
    )

    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Join Giveaway Now!", callback_data="join_gv")],
        [InlineKeyboardButton("💬 Contact Admin", url=f"https://t.me/{ADMIN_USERNAME}")]
    ])

    await update.message.reply_text(text, reply_markup=buttons)



# ==============================
# ✅ SEND START SCREEN — ADMIN
# ==============================
async def send_admin_start(update: Update):
    user = update.effective_user

    buttons = [
        [InlineKeyboardButton("📜 Show Commands", callback_data="help")],
    ]

    await update.message.reply_text(
        f"👋 Hello Admin @{user.username}!\nWelcome to your Giveaway Bot ✅",
        reply_markup=InlineKeyboardMarkup(buttons)
    )



# ==============================
# ✅ SHOW FORCE JOIN UI
# when user NOT joined channels
# ==============================
async def show_force_join_ui(update: Update, context: ContextTypes.DEFAULT_TYPE):
    links = DATA.get("verification_links", [])
    btns = []

    i = 1
    for u in links:
        btns.append(
            [InlineKeyboardButton(f"✅ Join Channel {i}", url=f"https://t.me/{u.replace('@', '')}")]
        )
        i += 1

    btns.append([InlineKeyboardButton("✅ Join Giveaway", callback_data="join_gv")])

    await update.callback_query.message.reply_text(
        "⚠️ You must join our channels to participate!\n\n"
        "✅ After joining, click → *Join Giveaway*",
        reply_markup=InlineKeyboardMarkup(btns),
        parse_mode="Markdown"
)



# ===========================================
# ✅ PART-3 — CORE ADMIN COMMANDS
# ===========================================


# ==============================
# ✅ /start
# ==============================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    # ADMIN
    if is_admin(user):
        return await send_admin_start(update)

    # USER
    return await send_user_start(update, context)



# ==============================
# ✅ /on → Enable Giveaway
# ==============================
async def enable_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    DATA["giveaway_enabled"]    = True
    DATA["participants"]        = []
    DATA["winners"]             = []
    DATA["auto_mode"]           = False
    DATA["winner_limit"]        = 0
    save_data()

    await update.message.reply_text(
        "✅ Giveaway Started!\n\n"
        "Now set how many winners will be selected:\n"
        "➡ /set <number>\n\n"
        "Example:\n/set 10"
    )



# ==============================
# ✅ /off → Disable Giveaway
# ==============================
async def disable_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    DATA["giveaway_enabled"] = False
    save_data()

    await update.message.reply_text(
        "⛔️ Giveaway Closed!\n"
        "Users can’t join now ✅"
    )



# ==============================
# ✅ /set X → Set winner count
# ==============================
async def set_winner_limit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    if not context.args:
        return await update.message.reply_text("⚠ Usage:\n/set 10")

    try:
        n = int(context.args[0])
    except:
        return await update.message.reply_text("⚠ Invalid number")

    DATA["winner_limit"] = n
    save_data()

    await update.message.reply_text(f"✅ Winner Count set to {n}!")



# ==============================
# ✅ /reset → reset current giveaway
# ==============================
async def reset_giveaway(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    DATA["winners"]        = []
    DATA["participants"]   = []
    DATA["winner_limit"]   = 0
    save_data()

    await update.message.reply_text("✅ Current Giveaway Reset Done!")



# ==============================
# ✅ /verificationlink
#    start receiving channels
# ==============================
async def verificationlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    context.user_data["await_veri_links"] = True
    DATA["verification_links"] = []
    save_data()

    await update.message.reply_text(
        "📩 Send @channel usernames (max 5)\n"
        "One per message.\n"
        "Send /done when finished.\n\n"
        "Example:\n@PowerPointBreak"
    )



# ==============================
# ✅ capture channels
# ==============================
async def capture_verification(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_veri_links"):
        return

    txt = update.message.text.strip()

    if txt.lower() == "/done":
        context.user_data["await_veri_links"] = False
        save_data()
        return await update.message.reply_text("✅ Force-Join Channels Saved!")

    if not txt.startswith("@"):
        return await update.message.reply_text("⚠ Must start with @name")

    if len(DATA["verification_links"]) >= 5:
        return await update.message.reply_text("⚠ Only 5 allowed!")

    DATA["verification_links"].append(txt)
    save_data()

    await update.message.reply_text(f"✅ Added: {txt}\nSend more or /done")



# ==============================
# ✅ /setoldwiner
#    start receiving old winner
# ==============================
async def set_oldwinner(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    context.user_data["await_old"] = True

    await update.message.reply_text(
        "📩 Send old winners:\n"
        "@user | 123456\n@bbb | 99999"
    )



# ==============================
# ✅ capture old winners
# ==============================
async def capture_old(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_old"):
        return

    lines = update.message.text.splitlines()

    for line in lines:
        if "|" not in line:
            continue
        name, uid = line.split("|", 1)
        name = name.strip().replace("@", "")
        uid  = uid.strip()

        if uid.isdigit():
            DATA["old_winners"].append(int(uid))

    context.user_data["await_old"] = False
    save_data()

    await update.message.reply_text("✅ Old Winners Saved!")



# ==============================
# ✅ /allw → show current winners
# ==============================
async def show_current_winners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    if not DATA["winners"]:
        return await update.message.reply_text("No winner yet!")

    txt = "🏆 Current Winners:\n\n"
    c = 1
    for w in DATA["winners"]:
        txt += f"{c}) @{w['username']} | {w['user_id']}\n"
        c += 1

    await update.message.reply_text(txt)



# ==============================
# ✅ /alluserid
# ==============================
async def show_alluser_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    if not DATA["winners"]:
        return await update.message.reply_text("No winner yet!")

    txt = "✅ All Winner IDs:\n\n"
    for w in DATA["winners"]:
        txt += f"{w['user_id']}\n"

    await update.message.reply_text(txt)



# ==============================
# ✅ /allwinnercount → history log
# ==============================
async def show_winner_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    if not DATA["winner_history"]:
        return await update.message.reply_text("No history!")

    txt = "📊 Winner History:\n\n"
    for w in DATA["winner_history"]:
        txt += (
            f"@{w['username']} | {w['user_id']}\n"
            f"Time: {fmt_time(w['timestamp'])}\n\n"
        )

    await update.message.reply_text(txt)



# ==============================
# ✅ /allcd → show command list
# ==============================
async def all_commands(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    txt = (
        "✅ COMMANDS\n\n"
        "/start\n/on\n/off\n/set X\n/reset\n"
        "/verificationlink\n/setoldwiner\n"
        "/allw\n/alluserid\n/allwinnercount\n"
        "/winauto\n/countdown"
    )

    await update.message.reply_text(txt)



# ===========================================
# ✅ PART-4 — JOIN GIVEAWAY SYSTEM
# ===========================================


# ==============================
# ✅ FORCE-JOIN CHECK
# returns TRUE → user joined all channels
# returns FALSE → not joined
# ==============================
async def check_force_join(user_id, context: ContextTypes.DEFAULT_TYPE):
    links = DATA.get("verification_links", [])
    if not links:
        return True   # no force join required

    for ch in links:
        try:
            # proper username only → @name → remove "@"
            chat = f"@{ch.replace('@', '')}"
            member = await context.bot.get_chat_member(chat, user_id)

            if member.status not in ("member", "administrator", "creator"):
                return False
        except:
            return False

    return True



# ==============================
# ✅ callback: join giveaway
# ==============================
async def join_gv(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user  = query.from_user
    uid   = user.id
    uname = user.username or ""

    # ---------------------------------------
    # 1) GIVEAWAY ACTIVE CHECK
    # ---------------------------------------
    if not DATA["giveaway_enabled"]:
        return await query.message.reply_text(
            "⛔️ ❌ GIVEAWAY CLOSED ❌ ⛔️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📩 Contact Admin:\n👉 @{ADMIN_USERNAME}\n"
            "💫 Please try another Giveaway!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )


    # ---------------------------------------
    # 2) FORCE-JOIN CHECK
    # ---------------------------------------
    ok = await check_force_join(uid, context)
    if not ok:
        return await show_force_join_ui(update, context)


    # ---------------------------------------
    # 3) OLD WINNER BLOCK
    # ---------------------------------------
    if uid in DATA["old_winners"]:
        return await query.message.reply_text(
            "┏━━━━━━━━━━━━━━━━━━━┓\n"
            "🏆 You’ve already won this giveaway!\n\n"
            "⚖️ To keep things fair, repeat participation isn’t allowed.\n"
            "🙏 Thank you for understanding!\n\n"
            f"📩 Admin Support: @{ADMIN_USERNAME}\n"
            "┗━━━━━━━━━━━━━━━━━━━┛"
        )


    # ---------------------------------------
    # 4) ALREADY WINNER THIS ROUND
    # ---------------------------------------
    for w in DATA["winners"]:
        if w["user_id"] == uid:
            return await query.message.reply_text(
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "⚠️ You have already participated!\n\n"
                f"📩 For any concerns, please contact:\n👉 @{ADMIN_USERNAME}\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )


    # ---------------------------------------
    # 5) SLOT FULL?
    # ---------------------------------------
    if len(DATA["winners"]) >= DATA["winner_limit"]:
        return await query.message.reply_text(
            "😔 Oops! All winners are already selected!\n"
            "🎉 Thanks for joining!\n\n"
            "🍀 Try again — more giveaways soon!\n"
            "💙 Stay with Power Point Break!\n\n"
            f"📞 For support:\n👉 @{ADMIN_USERNAME}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )


    # ---------------------------------------
    # 6) ADD TO PARTICIPANTS (SAFE)
    # ---------------------------------------
    if uid not in DATA["participants"]:
        DATA["participants"].append(uid)


    # ---------------------------------------
    # 7) SELECT AS WINNER
    # ---------------------------------------
    new_winner = make_winner_entry(user)

    DATA["winners"].append(new_winner)
    DATA["winner_history"].append(new_winner)
    save_data()

    # ---------------------------------------
    # 8) DM → USER
    # ---------------------------------------
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

    # ---------------------------------------
    # 9) DM → ADMIN
    # ---------------------------------------
    try:
        await context.bot.send_message(
            chat_id=f"@{ADMIN_USERNAME}",
            text=(
                "✅ NEW WINNER SELECTED!\n"
                f"👤 User: @{uname}\n"
                f"🆔 User ID: {uid}"
            )
        )
    except:
        pass

    # ---------------------------------------
    # 10) REPLY → PUBLIC
    # ---------------------------------------
    await query.message.reply_text(
        "🎉 You are SELECTED as Winner!\n"
        "Check your DM! 💌"
      )


# ===========================================
# ✅ PART-5 — AUTO GIVEAWAY + COUNTDOWN
# ===========================================


# ==============================
# ✅ /winauto → start auto-mode
# ==============================
async def winauto(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    DATA["auto_mode"] = True
    save_data()

    await update.message.reply_text(
        "✅ Auto-Giveaway Mode Enabled!\n\n"
        "➡ Send Winner Count\n\n"
        "Example:\n20"
    )

    context.user_data["await_auto_winner_count"] = True



# ==============================
# ✅ CAPTURE WINNER LIMIT (AUTO)
# ==============================
async def capture_auto_winner_count(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_auto_winner_count"):
        return

    txt = update.message.text.strip()
    if not txt.isdigit():
        return await update.message.reply_text("⚠ Enter a valid number!")

    DATA["winner_limit"] = int(txt)
    save_data()
    context.user_data["await_auto_winner_count"] = False

    await update.message.reply_text(
        f"✅ Winner Count set to {txt}!\n\n"
        "➡ Now send Countdown time\n"
        "Example:\n10s | 10m | 1h | 1h 20m"
    )

    context.user_data["await_auto_time"] = True



# ==============================
# ✅ CAPTURE TIME → START COUNTDOWN
# ==============================
async def capture_auto_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_auto_time"):
        return

    txt = update.message.text.strip()
    sec = parse_time(txt)

    if sec <= 0:
        return await update.message.reply_text("⚠ Invalid time format!")

    DATA["countdown_seconds"] = sec
    save_data()
    context.user_data["await_auto_time"] = False

    # START COUNTDOWN
    await update.message.reply_text("✅ Countdown Started!")

    await run_auto_countdown(update, context)



# ==============================
# ✅ AUTO COUNTDOWN (SAFE MODE)
# ==============================
async def run_auto_countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    sec = DATA["countdown_seconds"]

    msg = await update.message.reply_text("⏳ Starting...")

    while sec > 0:
        percent = (sec / DATA["countdown_seconds"]) * 100
        bar = progress_bar(percent)

        m = sec // 60
        s = sec % 60
        timetxt = f"{m:02d}:{s:02d}"

        try:
            await msg.edit_text(
                f"⏳ Time Left: {timetxt}\n{bar}\n\n"
                "⏰ Time is running! Hurry up! ⚡"
            )
        except:
            pass

        await asyncio.sleep(1)
        sec -= 1

    await msg.edit_text(
        "⏳ Countdown has ended!\n"
        "🎉 Stay ready — Winners will be announced very soon!\n\n"
        "🎙 Hosted by: Power Point Break"
    )

    # After countdown → auto pick
    await auto_pick_winners(update, context)



# ==============================
# ✅ AUTO RANDOM PICK
# ==============================
async def auto_pick_winners(update: Update, context: ContextTypes.DEFAULT_TYPE):
    limit = DATA["winner_limit"]
    part  = DATA["participants"].copy()
    old   = DATA["old_winners"]

    # remove OLD winners
    valid = [uid for uid in part if uid not in old]

    if not valid:
        return await update.message.reply_text("⚠ No valid participants!")

    # random pick
    if len(valid) <= limit:
        selected = valid
    else:
        selected = random.sample(valid, limit)

    winner_list = []

    for uid in selected:
        try:
            user = await context.bot.get_chat(uid)
            w = make_winner_entry(user)
            DATA["winners"].append(w)
            DATA["winner_history"].append(w)
            winner_list.append(w)

            # DM
            try:
                await context.bot.send_message(
                    chat_id=uid,
                    text=(
                        "🎉 CONGRATULATIONS! 🎉\n"
                        "You are one of the WINNERS of our Giveaway! 🏆\n\n"
                        f"📩 Contact Admin:\n👉 @{ADMIN_USERNAME}\n\n"
                        "💙 Hosted by: Power Point Break"
                    )
                )
            except:
                pass
        except:
            pass

    save_data()

    # Ask admin to APPROVE / REJECT
    txt = "🏆 AUTO WINNER LIST:\n\n"
    c = 1
    for w in winner_list:
        txt += f"{c}) @{w['username']} | {w['user_id']}\n"
        c += 1

    kb = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ APPROVE", callback_data="auto_ok"),
            InlineKeyboardButton("❌ REJECT",  callback_data="auto_no"),
        ]
    ])

    await update.message.reply_text(txt, reply_markup=kb)



# ==============================
# ✅ APPROVE / REJECT
# ==============================
async def auto_approve(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user  = query.from_user

    if not is_admin(user):
        return await query.answer("❌ Not allowed")

    txt = "━━━━━━━━━━━━━━━━━━━━━━\n"
    txt += "🏆 Power Point Break — Giveaway Winners\n"
    txt += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

    c = 1
    for w in DATA["winners"]:
        txt += f"#{c}) @{w['username']} | {w['user_id']}\n"
        c += 1

    txt += (
        "\n🎉 Congratulations to all!\n"
        f"📞 Contact Admin: @{ADMIN_USERNAME}\n"
        "🎙 Hosted by: Power Point Break"
    )

    await query.message.reply_text(txt)
    await query.answer("✅ Posted")


async def auto_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user  = query.from_user

    if not is_admin(user):
        return await query.answer("❌ Not allowed")

    await query.message.reply_text("❌ Cancelled!")
    await query.answer("Cancelled")



# ===========================================
# ✅ PART-6 — MANUAL COUNTDOWN + HANDLERS + RUN
# ===========================================


# ==============================
# ✅ /countdown → manual countdown
# ==============================
async def countdown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user):
        return

    context.user_data["await_cd_message"] = True

    await update.message.reply_text(
        "📩 Send countdown message text\n\n"
        "Example:\n🔥 Giveaway starts soon!"
    )


# ==============================
# ✅ capture countdown message
# ==============================
async def capture_cd_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_cd_message"):
        return

    DATA["countdown_content"] = update.message.text
    save_data()
    context.user_data["await_cd_message"] = False

    await update.message.reply_text(
        "✅ Message Saved!\nNow send countdown time:\nExamples:\n10s\n10m\n1h\n1h 20m"
    )

    context.user_data["await_cd_time"] = True


# ==============================
# ✅ capture countdown time
# ==============================
async def capture_cd_time(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.user_data.get("await_cd_time"):
        return

    sec = parse_time(update.message.text)
    if sec <= 0:
        return await update.message.reply_text("⚠ Invalid time format!")

    DATA["countdown_seconds"] = sec
    save_data()
    context.user_data["await_cd_time"] = False

    # START COUNTDOWN SAFE MODE
    msg = await update.message.reply_text("⏳ Countdown started...")

    total = sec
    while sec > 0:
        percent = (sec / total) * 100
        bar = progress_bar(percent)

        m = sec // 60
        s = sec % 60
        timetxt = f"{m:02d}:{s:02d}"

        try:
            await msg.edit_text(
                f"{DATA['countdown_content']}\n\n"
                f"⏳ Time Left: {timetxt}\n"
                f"{bar}\n\n"
                "⏰ Time is running! Hurry up! ⚡"
            )
        except:
            pass

        await asyncio.sleep(1)
        sec -= 1

    await msg.edit_text(
        "⏳ Countdown has ended!\n"
        "🎉 Stay ready — Winners will be announced very soon!\n\n"
        "🎙 Hosted by: Power Point Break"
    )


# ==============================
# ✅ CALLBACK ROUTER
# ==============================
async def callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    data = update.callback_query.data

    if data == "join_gv":
        return await join_gv(update, context)

    if data == "auto_ok":
        return await auto_approve(update, context)

    if data == "auto_no":
        return await auto_reject(update, context)

    if data == "help":
        return await all_commands(update, context)


# ==============================
# ✅ HANDLERS + RUN
# ==============================
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("on", enable_giveaway))
    app.add_handler(CommandHandler("off", disable_giveaway))
    app.add_handler(CommandHandler("set", set_winner_limit))
    app.add_handler(CommandHandler("reset", reset_giveaway))
    app.add_handler(CommandHandler("verificationlink", verificationlink))
    app.add_handler(CommandHandler("setoldwiner", set_oldwinner))
    app.add_handler(CommandHandler("allw", show_current_winners))
    app.add_handler(CommandHandler("alluserid", show_alluser_id))
    app.add_handler(CommandHandler("allwinnercount", show_winner_history))
    app.add_handler(CommandHandler("allcd", all_commands))
    app.add_handler(CommandHandler("winauto", winauto))
    app.add_handler(CommandHandler("countdown", countdown))

    # Message capture
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), capture_verification))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), capture_old))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), capture_auto_winner_count))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), capture_auto_time))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), capture_cd_message))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), capture_cd_time))

    # Callbacks
    app.add_handler(CallbackQueryHandler(callback_handler))

    print("✅ BOT RUNNING…")
    app.run_polling()


if __name__ == "__main__":
    main()

