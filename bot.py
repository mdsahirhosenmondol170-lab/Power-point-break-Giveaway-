# ==============================================
#   Power Point Break — GIVEAWAY BOT
#   by @MinexxProo
#   ✅ Full System + JSON + Hosting Ready
# ==============================================

import json, os, pytz, datetime, asyncio, random
from telegram import *
from telegram.ext import *
from telegram.constants import ParseMode


# ==============================================
#   BASIC CONFIG
# ==============================================

BOT_TOKEN  = "8321055873:AAFYKCVwiBF3Hrc9RdIG_YRRVMkNL6qcaCc"   # <<== MUST UPDATE
CHANNEL_ID =  -1003180933712         # <<== MUST UPDATE (integer only)
OWNER      = "MinexxProo"            # no @

DB_FILE    = "data.json"


# ==============================================
#   JSON DB
# ==============================================

default_db = {
    "giveaway_on"   : False,
    "winner_limit"  : 0,
    "joined"        : [],
    "winners"       : [],
    "admins"        : ["MinexxProo"],
    "saved_post"    : ""
}

def load_db():
    if not os.path.exists(DB_FILE):
        save_db(default_db)
    return json.load(open(DB_FILE,"r"))

def save_db(data):
    json.dump(data, open(DB_FILE,"w"), indent=4)



# ==============================================
#   TIME
# ==============================================

def now_time():
    tz = pytz.timezone("Asia/Dhaka")
    return datetime.datetime.now(tz).strftime("%I:%M:%S %p")



# ==============================================
#   HELPERS
# ==============================================

def is_owner(username):
    return username == OWNER

def is_admin(username):
    db = load_db()
    return username in db["admins"] or username == OWNER



# ==============================================
#   /start
# ==============================================

async def start_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"✅ Hi {user.first_name}!\nWelcome to Power Point Break Giveaway!"
    )



# ==============================================
#   /on  → Start Giveaway
# ==============================================

async def on_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_owner(user.username):
        return await update.message.reply_text("❌ Only Owner can do this!")

    await update.message.reply_text(
        "✅ Giveaway Started!\n\nSet winner count:\n(Example: 10)"
    )

    context.user_data["awaiting_winner"] = True



# ==============================================
#   /off  → Stop Giveaway
# ==============================================

async def off_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_owner(user.username):
        return await update.message.reply_text("❌ Only Owner can do this!")

    db = load_db()
    db["giveaway_on"] = False
    save_db(db)

    await update.message.reply_text("✅ Giveaway Turned OFF ✅")



# ==============================================
#   JOIN PANEL UI
# ==============================================

async def show_join_panel(update, context):
    user = update.effective_user

    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("🚀 Join Giveaway Now!", callback_data="join")]]
    )

    await update.message.reply_text(
f"""
━━━━━━━━━━━━━━━━━━━━━━
👋 Welcome To Power Point Break Giveaway!
━━━━━━━━━━━━━━━━━━━━━━

Hello @{user.username}
🆔 User ID: {user.id}

📩 To participate:
👉 Tap the button below!

✅ If you are selected as a winner,
you will be notified instantly!

💬 Need help?
👉 @{OWNER}

Good luck! 🍀
━━━━━━━━━━━━━━━━━━━━━━
""",
        reply_markup=keyboard
    )



# ==============================================
#   TEXT HANDLER
# ==============================================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    db = load_db()

    # Waiting Winner count → /on
    if context.user_data.get("awaiting_winner"):
        if text.isdigit():
            db["winner_limit"] = int(text)
            db["giveaway_on"]  = True
            db["joined"]  = []
            db["winners"] = []
            save_db(db)

            context.user_data["awaiting_winner"] = False
            return await update.message.reply_text(
                f"✅ Winner Count Set → {text}\nGiveaway ACTIVE ✅"
            )
        else:
            return await update.message.reply_text("❌ Invalid Number")

    # Giveaway OFF
    if not db["giveaway_on"]:
        return await update.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⛔️ ❌ GIVEAWAY CLOSED ❌ ⛔️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📩 Contact Admin:\n👉 @{OWNER}\n"
            "💫 Please try another Giveaway!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )

    # Giveaway ON → Show Join Panel
    return await show_join_panel(update, context)



# ==============================================
#   JOIN CALLBACK → AUTO-WINNER
# ==============================================

async def join_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user  = query.from_user
    await query.answer()

    db = load_db()

    # Giveaway OFF
    if not db["giveaway_on"]:
        return await query.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⛔️ ❌ GIVEAWAY CLOSED ❌ ⛔️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📩 Contact Admin:\n👉 @{OWNER}\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )

    # Already joined
    for x in db["joined"]:
        if x["id"] == user.id:
            return await query.message.reply_text(
                "━━━━━━━━━━━━━━━━━━━━━━\n"
                "⚠️ You have already participated!\n"
                f"📩 Contact: @{OWNER}\n"
                "━━━━━━━━━━━━━━━━━━━━━━"
            )

    # winner slot full
    if len(db["joined"]) >= db["winner_limit"]:
        return await query.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━\n"
            "😔 Oops! All winners are already selected!\n"
            "🎉 Thanks for joining!\n"
            f"📞 @{OWNER}\n"
            "━━━━━━━━━━━━━━━━━━━━━━"
        )

    # SAVE USER
    entry = {
        "username": user.username,
        "id"      : user.id,
        "time"    : now_time()
    }

    db["joined"].append(entry)
    save_db(db)

    # AUTO WIN (first N users)
    if len(db["joined"]) <= db["winner_limit"]:
        db["winners"].append(entry)
        save_db(db)

        await query.message.reply_text(
            "🎉 CONGRATULATIONS! 🎉\n"
            "You WON the Giveaway! 🏆\n\n"
            f"📩 Contact Admin:\n👉 @{OWNER}\n\n"
            "💙 Hosted by: Power Point Break"
        )

    # if winners full → send preview
    if len(db["winners"]) == db["winner_limit"]:
        await send_winner_preview(context)

    return

# ==============================================
#   PART-2 — WINNER PREVIEW + APPROVE / REJECT
# ==============================================

async def send_winner_preview(context):
    db = load_db()

    text = "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += "🏆 Power Point Break — Giveaway Winners\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

    c = 1
    for x in db["winners"]:
        text += f"#{c} @{x['username']} | {x['id']} | {x['time']}\n"
        c += 1

    text += "\n🎉 Congratulations to all!\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("✅ Approve", callback_data="approve"),
            InlineKeyboardButton("❌ Reject",  callback_data="reject")
        ]
    ])

    await context.bot.send_message(
        chat_id=f"@{OWNER}",
        text=text,
        reply_markup=keyboard
    )



# ==============================================
#   APPROVE / REJECT CALLBACK HANDLER
# ==============================================

async def approve_reject(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    db    = load_db()
    data  = query.data

    # Only OWNER allowed
    if not is_owner(query.from_user.username):
        return await query.answer("❌ Not Allowed", show_alert=True)

    # ✅ APPROVE → Post to Channel
    if data == "approve":

        text = "━━━━━━━━━━━━━━━━━━━━━━\n"
        text += "🏆 Power Point Break — Giveaway Winners\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n\n"

        c = 1
        for x in db["winners"]:
            text += f"#{c} @{x['username']} | {x['id']} | {x['time']}\n"
            c += 1

        text += "\n🎉 Congratulations to all!\n"
        text += "━━━━━━━━━━━━━━━━━━━━━━\n"
        text += f"👑 Admin: @{OWNER}\n"
        text += "🎙 Hosted by: Power Point Break"

        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=text
        )

        await query.message.reply_text(
            "✅ Winner list posted successfully!"
        )

    # ❌ REJECT
    elif data == "reject":
        await query.message.reply_text("❌ Winner Post Canceled!")

    # turn off giveaway
    db["giveaway_on"] = False
    save_db(db)



# ==============================================
#   PART-3 — MULTI-ADMIN
# ==============================================

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_owner(user.username):
        return await update.message.reply_text("❌ Only OWNER can add admin!")

    if len(context.args) != 1:
        return await update.message.reply_text("Usage: /addadmin username")

    new_admin = context.args[0].replace("@","")
    db = load_db()

    if new_admin in db["admins"]:
        return await update.message.reply_text(
            f"⚠️ Already admin: @{new_admin}"
        )

    db["admins"].append(new_admin)
    save_db(db)

    await update.message.reply_text(
        f"✅ @{new_admin} added as admin!"
    )



async def del_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_owner(user.username):
        return await update.message.reply_text("❌ Only OWNER can remove admin!")

    if len(context.args) != 1:
        return await update.message.reply_text("Usage: /deladmin username")

    target = context.args[0].replace("@","")
    db = load_db()

    if target == OWNER:
        return await update.message.reply_text("❌ OWNER cannot be removed!")

    if target not in db["admins"]:
        return await update.message.reply_text(
            f"⚠️ @{target} is not an admin!"
        )

    db["admins"].remove(target)
    save_db(db)

    await update.message.reply_text(
        f"✅ @{target} removed from admin list!"
    )



async def admin_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db   = load_db()

    if not is_admin(user.username):
        return await update.message.reply_text("❌ Admin only!")

    text = "👑 **Admin List**\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"⭐ OWNER: @{OWNER}\n\n"
    text += "✅ ADMINS:\n"

    if len(db["admins"]) == 1:
        text += "(Only Owner)\n"
    else:
        for a in db["admins"]:
            text += f"• @{a}\n"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)



# ==============================================
#   PART-4 — /stats + /me
# ==============================================

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.username):
        return await update.message.reply_text("❌ Admin only!")

    db = load_db()

    total_joined  = len(db["joined"])
    total_winners = len(db["winners"])
    daily         = len(db["joined"])  # basic
    unique_users  = len({x["id"] for x in db["joined"]})

    text = "📊 **Giveaway Stats**\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━\n"
    text += f"👥 Total Participants: **{total_joined}**\n"
    text += f"🎖 Total Winners: **{total_winners}**\n"
    text += f"📅 Daily Participants: **{daily}**\n"
    text += f"🧩 Unique Users: **{unique_users}**\n"
    text += "━━━━━━━━━━━━━━━━━━━━━━"

    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)



async def me_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    db = load_db()

    joined_count = 0
    won_count    = 0
    last_win     = "N/A"

    for x in db["joined"]:
        if x["id"] == user.id:
            joined_count += 1

    for x in db["winners"]:
        if x["id"] == user.id:
            won_count += 1
            last_win = x["time"]

    text = f"""
👤 **Profile — @{user.username}**
━━━━━━━━━━━━━━━━━━━━━━
✅ Times Participated: **{joined_count}**
🏆 Times Won: **{won_count}**
⏳ Last Win: **{last_win}**
━━━━━━━━━━━━━━━━━━━━━━
"""
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


# ==============================================
#   PART-5 — /setmwinner (Timer + Random)
# ==============================================

timer_data = {}

async def setmwinner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not is_admin(user.username):
        return await update.message.reply_text("❌ Admin only!")

    await update.message.reply_text(
        "✅ Set Winner Count:\n(Example: 10)"
    )
    context.user_data["setmwinner_wait_count"] = True


async def setmwinner_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    db   = load_db()

    # STEP-1 → count
    if context.user_data.get("setmwinner_wait_count"):
        if text.isdigit():

            db["winner_limit"] = int(text)
            timer_data["winner_limit"] = int(text)
            save_db(db)

            context.user_data["setmwinner_wait_count"] = False
            context.user_data["setmwinner_wait_time"]  = True

            return await update.message.reply_text(
                "✅ Winner Count Saved!\nNow set Time (ex: 1h / 10m / 30s)"
            )
        else:
            return await update.message.reply_text("❌ Invalid number!")


    # STEP-2 → time
    if context.user_data.get("setmwinner_wait_time"):

        sec = convert_to_seconds(text)
        if sec is None:
            return await update.message.reply_text("❌ Invalid time format!")

        timer_data["duration"] = sec

        # reset
        db["joined"]      = []
        db["winners"]     = []
        db["giveaway_on"] = True
        save_db(db)

        context.user_data["setmwinner_wait_time"] = False

        await update.message.reply_text(
            f"✅ Timer started for {text} ⏳\nUsers can JOIN now!"
        )

        asyncio.create_task(timer_countdown(sec, context))
        return



def convert_to_seconds(value):
    try:
        if value.endswith("h"):
            return int(value[:-1]) * 3600
        if value.endswith("m"):
            return int(value[:-1]) * 60
        if value.endswith("s"):
            return int(value[:-1])
    except:
        return None
    return None



async def timer_countdown(duration, context):
    await asyncio.sleep(duration)

    db = load_db()
    participants = db["joined"]

    if len(participants) == 0:
        return await context.bot.send_message(
            chat_id=f"@{OWNER}",
            text="❌ No Participants Found!"
        )

    need = db["winner_limit"]

    if len(participants) <= need:
        winners = participants
    else:
        winners = random.sample(participants, need)

    db["winners"] = winners
    save_db(db)

    await send_winner_preview(context)

# ==============================================
#   PART-6 — /setpost + /setsavepost
#   Auto Timer + Countdown + Progress
# ==============================================

post_data = {
    "pending_text": "",
    "active": False,
    "duration": 0,
    "time_left": 0
}


# ✅ /setsavepost → only save post text
async def setsavepost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_admin(user.username):
        return await update.message.reply_text("❌ Admin only!")

    raw = update.message.text.replace("/setsavepost", "").strip()

    if not raw:
        return await update.message.reply_text(
            "❌ Usage:\n/setsavepost Your post text"
        )

    post_data["pending_text"] = raw
    return await update.message.reply_text(
        "✅ Post saved successfully!"
    )



# ✅ /setpost → schedule post
async def setpost_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if not is_admin(user.username):
        return await update.message.reply_text("❌ Admin only!")

    context.user_data["setpost_wait_text"] = True
    return await update.message.reply_text(
        "✅ Send post text now:"
    )



# ==============================================
#   /setpost text processor
# ==============================================

async def setpost_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    # STEP-1 → take post text
    if context.user_data.get("setpost_wait_text"):
        post_data["pending_text"] = text
        context.user_data["setpost_wait_text"] = False
        context.user_data["setpost_wait_time"] = True

        return await update.message.reply_text(
            "✅ Post Saved!\nNow set time (ex: 1h / 10m / 30s)"
        )


    # STEP-2 → take time
    if context.user_data.get("setpost_wait_time"):

        sec = convert_to_seconds(text)
        if sec is None:
            return await update.message.reply_text(
                "❌ Invalid time format!"
            )

        post_data["duration"]  = sec
        post_data["time_left"] = sec
        post_data["active"]    = True

        context.user_data["setpost_wait_time"] = False

        await update.message.reply_text(
            f"✅ Timer started for {text} ⏳\nCountdown LIVE!"
        )

        asyncio.create_task(run_post_countdown(context))
        return



# ==============================================
#   Countdown Loop
# ==============================================

async def run_post_countdown(context):
    total = post_data["duration"]
    post_data["time_left"] = total

    # update every 10s
    while post_data["time_left"] > 0:

        left = post_data["time_left"]
        percent = int((total - left) / total * 100)
        bar = draw_progress(percent)

        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=f"""
⏳ Giveaway Starting Soon...

Time Left: {format_time(left)}
{bar}
"""
        )

        await asyncio.sleep(10)
        post_data["time_left"] -= 10


    # timer finished → post it
    if post_data["pending_text"]:
        await context.bot.send_message(
            chat_id=CHANNEL_ID,
            text=post_data["pending_text"]
        )

    # reset
    post_data["active"] = False
    post_data["pending_text"] = ""



# ==============================================
#   Progress / Time helpers
# ==============================================

def draw_progress(percent):
    full  = percent // 10
    empty = 10 - full
    return "▰" * full + "▱" * empty + f" {percent}%"


def format_time(sec):
    h = sec // 3600
    sec %= 3600
    m = sec // 60
    s = sec % 60
    return f"{h:02d}:{m:02d}:{s:02d}"



# ==============================================
#   /help + /allcd
# ==============================================

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    txt = f"""
✅ Available Commands

/on         → Start Giveaway
/off        → Stop Giveaway
/setmwinner → Auto timer + random winner
/setpost    → Timed post + countdown
/setsavepost→ Save post only

/addadmin <user>
/deladmin <user>
/adminlist

/stats      → Giveaway stats
/me         → Your profile
/help
/allcd
    """
    await update.message.reply_text(txt)



async def allcd_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    return await help_cmd(update, context)



# ==============================================
#   MASTER TEXT HANDLER (router)
# ==============================================

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text
    db = load_db()

    # /setpost
    if context.user_data.get("setpost_wait_text") or context.user_data.get("setpost_wait_time"):
        return await setpost_text(update, context)

    # /setmwinner
    if context.user_data.get("setmwinner_wait_count") or context.user_data.get("setmwinner_wait_time"):
        return await setmwinner_text(update, context)

    # /on → awaiting_winner
    if context.user_data.get("awaiting_winner"):
        if text.isdigit():
            db["winner_limit"] = int(text)
            db["giveaway_on"]  = True
            db["joined"]  = []
            db["winners"] = []
            save_db(db)

            context.user_data["awaiting_winner"] = False
            return await update.message.reply_text(
                f"✅ Winner Count Set → {text}\nGiveaway ACTIVE ✅"
            )
        else:
            return await update.message.reply_text("❌ Invalid Number")

    # OFF mode
    if not db["giveaway_on"]:
        return await update.message.reply_text(
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            "⛔️ ❌ GIVEAWAY CLOSED ❌ ⛔️\n"
            "━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"📩 Contact Admin:\n👉 @{OWNER}\n"
            "💫 Please try another Giveaway!\n"
            "━━━━━━━━━━━━━━━━━━━━━━━"
        )

    # ON → show panel
    return await show_join_panel(update, context)



# ==============================================
#   MAIN
# ==============================================

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    # ===== COMMANDS =====
    app.add_handler(CommandHandler("start",      start_cmd))
    app.add_handler(CommandHandler("on",         on_cmd))
    app.add_handler(CommandHandler("off",        off_cmd))
    app.add_handler(CommandHandler("help",       help_cmd))
    app.add_handler(CommandHandler("allcd",      allcd_cmd))

    app.add_handler(CommandHandler("setmwinner", setmwinner_cmd))
    app.add_handler(CommandHandler("setpost",    setpost_cmd))
    app.add_handler(CommandHandler("setsavepost",setsavepost_cmd))

    app.add_handler(CommandHandler("addadmin",   add_admin))
    app.add_handler(CommandHandler("deladmin",   del_admin))
    app.add_handler(CommandHandler("adminlist",  admin_list))

    app.add_handler(CommandHandler("stats",      stats_cmd))
    app.add_handler(CommandHandler("me",         me_cmd))

    # ===== CALLBACKS =====
    app.add_handler(CallbackQueryHandler(join_handler,    pattern="join"))
    app.add_handler(CallbackQueryHandler(approve_reject,  pattern="approve|reject"))

    # ===== TEXT =====
    app.add_handler(MessageHandler(filters.TEXT, text_handler))

    print("✅ Power Point Break Bot Running...")
    app.run_polling()



# ==============================================
#   RUN
# ==============================================
if __name__ == "__main__":
    main()
