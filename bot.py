import os
from telegram.ext import Updater, CommandHandler
import requests

BOT_TOKEN = os.getenv("BOT_TOKEN")
TRON_ADDRESS = os.getenv("TRON_ADDRESS")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")  # USDT contract
OWNER_ID = int(os.getenv("OWNER_ID", "0"))

# /start
def start(update, context):
    update.message.reply_text("👋 Welcome Alari! Your bot is now active.")

# /status (owner only)
def status(update, context):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        update.message.reply_text("⛔ You are not authorized to use this command.")
        return
    update.message.reply_text("📊 Status: Bot is running and connected!")

# /balance (owner only)
def balance(update, context):
    user_id = update.effective_user.id
    if user_id != OWNER_ID:
        update.message.reply_text("⛔ You are not authorized to use this command.")
        return
    try:
        # Get token balances (USDT + others)
        url = f"https://apilist.tronscanapi.com/api/account/tokens?address={TRON_ADDRESS}"
        response = requests.get(url).json()

        usdt_balance = "0"
        for token in response.get("data", []):
            if token.get("tokenId") == CONTRACT_ADDRESS:  # USDT contract
                usdt_balance = str(int(token.get("balance")) / (10 ** token.get("tokenDecimal", 6)))

        # Get TRX balance
        url_trx = f"https://apilist.tronscanapi.com/api/account?address={TRON_ADDRESS}"
        response_trx = requests.get(url_trx).json()
        trx_balance = str(response_trx.get("balance", 0) / 1_000_000)  # TRX uses 6 decimals

        # Reply with balances
        update.message.reply_text(
            f"💼 Wallet Balance:\n"
            f"💰 USDT: {usdt_balance}\n"
            f"⚡ TRX: {trx_balance}"
        )

    except Exception as e:
        update.message.reply_text(f"⚠️ Error fetching balance: {e}")

if __name__ == "__main__":
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("balance", balance))

    updater.start_polling()
    updater.idle()
