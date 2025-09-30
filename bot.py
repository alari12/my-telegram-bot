import os
from telegram.ext import Updater, CommandHandler
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
TRON_ADDRESS = os.getenv("TRON_ADDRESS")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")

# Replace with your Telegram user ID (not username)
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# /start command
def start(update, context):
    update.message.reply_text("👋 Welcome Alari! Your bot is now active.")

# /status command (only owner can use it)
def status(update, context):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        update.message.reply_text("⛔ You are not authorized to use this command.")
        return

    try:
        # Call Tron API for USDT balance
        url = f"https://apilist.tronscanapi.com/api/account/tokens?address={TRON_ADDRESS}"
        response = requests.get(url).json()

        balance = "0"
        for token in response.get("data", []):
            if token.get("tokenId") == CONTRACT_ADDRESS:
                balance = str(int(token.get("balance")) / (10 ** token.get("tokenDecimal", 6)))

        update.message.reply_text(f"📊 USDT Balance for {TRON_ADDRESS}:\n💰 {balance} USDT")

    except Exception as e:
        update.message.reply_text(f"⚠️ Error fetching balance: {e}")

if __name__ == "__main__":
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))

    updater.start_polling()
    updater.idle()
