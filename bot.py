import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ----------------------------
# CONFIG
# ----------------------------

TOKEN = os.environ.get("TOKEN")

# OPTIONAL: leave empty list if you truly want public access
# OR put IDs if you want only you + roommate
ALLOWED_USERS = []

DATA_FILE = "balance.json"

# ----------------------------
# BALANCE STORAGE
# ----------------------------

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

# ----------------------------
# MAIN LOGIC
# ----------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global balance

    user = update.message.from_user
    text = update.message.text.strip()

    # If you want access control (optional)
    if ALLOWED_USERS and user.id not in ALLOWED_USERS:
        return

    # Validate number input
    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text("Send a number (e.g. 30 or -17).")
        return

    # Update balance
    balance += value
    save_balance(balance)

    # Build message
    name = user.first_name

    if balance > 0:
        status = f"You owe total: {balance:.2f}"
    elif balance < 0:
        status = f"You are owed: {abs(balance):.2f}"
    else:
        status = "You're even."

    message = f"📌 {name} sent {value}\n\n{status}"

    # ----------------------------
    # TRANSPARENCY: send to ALL chat participants
    # ----------------------------

    chat_id = update.effective_chat.id

    await context.bot.send_message(chat_id=chat_id, text=message)


# ----------------------------
# RUN BOT
# ----------------------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()
