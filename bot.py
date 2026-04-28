import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

import os
TOKEN = os.environ.get("TOKEN")

DATA_FILE = "balance.json"


def load_balance():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)["balance"]
    except:
        return 0


def save_balance(balance):
    with open(DATA_FILE, "w") as f:
        json.dump({"balance": balance}, f)


balance = load_balance()


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global balance

    text = update.message.text.strip()

    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text("Please send a number (e.g. 30 or -17).")
        return

    balance += value
    save_balance(balance)

    if balance > 0:
        msg = f"You owe your roommate: {balance:.2f}"
    elif balance < 0:
        msg = f"Your roommate owes you: {abs(balance):.2f}"
    else:
        msg = "You're even. No one owes anything."

    await update.message.reply_text(msg)


app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()
