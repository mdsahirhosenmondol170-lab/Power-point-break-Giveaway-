import json
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, ADMIN_ID

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)

giveaway_enabled = False
winner_limit = 0
winners = []           # store user ids
winner_details = []    # store username + id


### Helper --- Save winner list
def save_data():
    with open("winners.json", "w") as f:
        json.dump(winner_details, f, indent=4)


### /start
@dp.message_handler(commands=['start'])
async def start_cmd(msg: types.Message):
    username = msg.from_user.username
    user_id = msg.from_user.id

    text = f"""
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

💬 If you need help, contact:
👉 @MinexxProo
━━━━━━━━━━━━━━━━━━━━━━
"""

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🎁 Join Giveaway", callback_data="join"))

    await msg.answer(text, reply_markup=kb)


### /on
@dp.message_handler(commands=['on'])
async def on_cmd(msg: types.Message):
    global giveaway_enabled
    if msg.from_user.id != ADMIN_ID:
        return
    giveaway_enabled = True
    await msg.reply("✅ Giveaway Started!\nUse /set <count> to set winners.")


### /set X
@dp.message_handler(commands=['set'])
async def set_winner_cmd(msg: types.Message):
    global winner_limit
    if msg.from_user.id != ADMIN_ID:
        return
    try:
        winner_limit = int(msg.text.split()[1])
        await msg.reply(f"✅ Winner Count Set: {winner_limit}")
    except:
        await msg.reply("❌ Usage: /set 10")


### /off
@dp.message_handler(commands=['off'])
async def off_cmd(msg: types.Message):
    global giveaway_enabled
    if msg.from_user.id != ADMIN_ID:
        return
    giveaway_enabled = False
    await msg.reply("⛔ Giveaway Closed!")


### /allw → Show winners
@dp.message_handler(commands=['allw'])
async def allw_cmd(msg: types.Message):
    if msg.from_user.id != ADMIN_ID:
        return

    if not winner_details:
        return await msg.reply("No winners yet!")

    txt = "🏆 Winner List:\n"
    c = 1
    for w in winner_details:
        txt += f"{c}) @{w['username']} | {w['id']}\n"
        c += 1

    await msg.reply(txt)


### Join Button
@dp.callback_query_handler(lambda c: c.data == "join")
async def join_handler(callback: types.CallbackQuery):
    global giveaway_enabled, winners, winner_details

    user = callback.from_user
    user_id = user.id
    username = user.username or "Unknown"

    if not giveaway_enabled:
        return await callback.message.answer(
            """
⛔️ ❌ GIVEAWAY CLOSED ❌ ⛔️
━━━━━━━━━━━━━━━━━━━━━━━
📩 Contact Admin:
👉 @MinexxProo

💫 Please try another Giveaway!
━━━━━━━━━━━━━━━━━━━━━━━
"""
        )

    if user_id in winners:
        return await callback.message.answer(
            """
━━━━━━━━━━━━━━━━━━━━━━
⚠️ You have already participated!

📩 For any concerns, please contact:
👉 @MinexxProo
━━━━━━━━━━━━━━━━━━━━━━
"""
        )

    if len(winners) >= winner_limit:
        return await callback.message.answer(
            """
━━━━━━━━━━━━━━━━━━━━━━
😔 Oops! All winners are already selected!
🎉 Thanks for joining!

🍀 Try again — more giveaways soon!
💙 Stay with Power Point Break!
📞 For support:
👉 @MinexxProo
━━━━━━━━━━━━━━━━━━━━━━
"""
        )

    ### Mark winner
    winners.append(user_id)
    winner_details.append({"username": username, "id": user_id})
    save_data()

    ### User message
    await callback.message.answer(
        """
🎉 CONGRATULATIONS! 🎉
You are one of the WINNERS of our Giveaway! 🏆

📩 Contact Admin to claim your reward:
👉 @MinexxProo

💙 Hosted by: Power Point Break
"""
    )

    ### Notify Admin
    await bot.send_message(
        ADMIN_ID,
        f"✅ WINNER\nUsername: @{username}\nUser ID: {user_id}",
    )


### Run
if __name__ == "__main__":
    print("Bot Running…")
    executor.start_polling(dp)
