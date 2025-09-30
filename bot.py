import os
import time
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import requests

# Load config from environment
BOT_TOKEN = os.getenv("BOT_TOKEN")
TRON_ADDRESS = os.getenv("TRON_ADDRESS")
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS")
OWNER_ID = int(os.getenv("OWNER_ID", "0"))
PASSCODE = os.getenv("PASSCODE", "2486")

# How long a successful passcode grants access (seconds)
AUTH_DURATION = 10 * 60  # 10 minutes

# In-memory auth store: {user_id: expiry_timestamp}
AUTH_SESSIONS = {}

def is_authorized(user_id):
    # Immediate allow for owner
    if user_id == OWNER_ID:
        return True
    # Check temporary passcode sessions
    expiry = AUTH_SESSIONS.get(user_id)
    if expiry and time.time() < expiry:
        return True
    return False

def start(update, context):
    update.message.reply_text("👋 Welcome Alari! Your bot is now active.")

def ask_passcode_message(update):
    update.message.reply_text(
        "⛔ You are not authorized to use this command.\n"
        "If you have the passcode, send: /passcode <code>\n\n"
        "Example: /passcode 2486"
    )

def status(update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        ask_passcode_message(update)
        return
    update.message.reply_text("📊 Status: Bot is running and connected!")

def fetch_balances():
    """Return tuple (usdt_balance_str, trx_balance_str) or raise."""
    # USDT/token balances
    url_tokens = f"https://apilist.tronscanapi.com/api/account/tokens?address={TRON_ADDRESS}"
    r = requests.get(url_tokens, timeout=10)
    r.raise_for_status()
    data = r.json()
    usdt_balance = "0"
    for token in data.get("data", []):
        # tokenId can vary by API; compare to provided CONTRACT_ADDRESS
        if token.get("tokenId") == CONTRACT_ADDRESS or token.get("tokenId") == CONTRACT_ADDRESS.lower():
            # token.get("balance") might be a string
            bal = int(token.get("balance", 0))
            decimals = int(token.get("tokenDecimal", 6) or 6)
            usdt_balance = str(bal / (10 ** decimals))
            break

    # TRX balance (main chain)
    url_trx = f"https://apilist.tronscanapi.com/api/account?address={TRON_ADDRESS}"
    r2 = requests.get(url_trx, timeout=10)
    r2.raise_for_status()
    data_trx = r2.json()
    trx_amount = data_trx.get("balance", 0)  # in sun (1 TRX = 1e6 sun)
    trx_balance = str(trx_amount / 1_000_000)

    return usdt_balance, trx_balance

def balance(update, context):
    user_id = update.effective_user.id
    if not is_authorized(user_id):
        ask_passcode_message(update)
        return
    try:
        usdt_balance, trx_balance = fetch_balances()
        update.message.reply_text(
            f"💼 Wallet Balance:\n"
            f"💰 USDT: {usdt_balance}\n"
            f"⚡ TRX: {trx_balance}"
        )
    except Exception as e:
        update.message.reply_text(f"⚠️ Error fetching balance: {e}")

def passcode_handler(update, context):
    """Handle /passcode <code>. If correct, grant temporary access."""
    user_id = update.effective_user.id
    args = context.args or []
    if not args:
        update.message.reply_text("Usage: /passcode <code>")
        return

    code = args[0].strip()
    if code == PASSCODE:
        AUTH_SESSIONS[user_id] = time.time() + AUTH_DURATION
        update.message.reply_text(
            f"✅ Passcode accepted. You have access for {AUTH_DURATION//60} minutes.\n"
            "Now run the command you wanted (e.g., /balance or /status)."
        )
    else:
        update.message.reply_text("❌ Incorrect passcode.")

def unknown(update, context):
    update.message.reply_text("I don't know that command. Use /help to see commands.")

def help_command(update, context):
    update.message.reply_text(
        "/start - Start the bot\n"
        "/status - Check if bot is running (owner or authenticated)\n"
        "/balance - Show USDT & TRX balances (owner or authenticated)\n"
        "/passcode <code> - Enter passcode to gain temporary access\n"
    )

def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("passcode", passcode_handler))
    dp.add_handler(CommandHandler("help", help_command))
    dp.add_handler(MessageHandler(Filters.command, unknown))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
