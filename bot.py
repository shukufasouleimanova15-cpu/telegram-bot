import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, ContextTypes, filters

# ----------------------------
# CONFIG
# ----------------------------

TOKEN = os.environ.get("TOKEN")

DATA_FILE = "balance.json"

# ----------------------------
# LOAD / SAVE BALANCE
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
# MESSAGE HANDLER
# ----------------------------

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global balance

    user = update.message.from_user
    text = update.message.text.strip()

    # Convert input to number
    try:
        value = float(text)
    except ValueError:
        await update.message.reply_text("Send a number like 30 or -17.")
        return

    # Update shared balance
    balance += value
    save_balance(balance)

    # Build transparency message
    name = user.first_name

    if balance > 0:
        status = f"📊 Total: You owe {balance:.2f}"
    elif balance < 0:
        status = f"📊 Total: You are owed {abs(balance):.2f}"
    else:
        status = "📊 You are even."

    message = f"💬 {name} sent: {value}\n\n{status}"

    # Send to SAME chat (both of you see it)
    await context.bot.send_message(
        chat_id=update.effective_chat.id,
        text=message
    )


# ----------------------------
# RUN BOT
# ----------------------------

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

print("Bot is running...")
app.run_polling()
