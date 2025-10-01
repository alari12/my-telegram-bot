import requests
from telegram.ext import Updater, CommandHandler

# === CONFIG ===
BOT_TOKEN = "8147464540:AAEF9SuhW-QIO9jM2ZAVkk7AAEoYlWmTGr4"
OWNER_ID = 5252571392
PASSCODE = "2486"

# === TRON CONFIG ===
TRON_ADDRESS = "TF44m3MkLTGfWV5aF2mWVdh8tCp3SujvDy"  # replace with your wallet address
USDT_CONTRACT = "TXLAQ63Xg1NAzckPwKHvzw7CSEmLMEqcdj"  # Official USDT TRC20 contract

# === COMMAND HANDLERS ===
def start(update, context):
    update.message.reply_text("✅ Bot is active and ready!")

def status(update, context):
    update.message.reply_text("🟢 Wallet monitor is running.")

def balance(update, context):
    try:
        url = f"https://apilist.tronscanapi.com/api/account/tokens?address={TRON_ADDRESS}"
        response = requests.get(url).json()

        usdt_balance = 0
        for token in response.get("data", []):
            if token.get("tokenId") == USDT_CONTRACT:
                usdt_balance = int(token.get("balance", 0)) / 1_000_000  # USDT has 6 decimals

        update.message.reply_text(
            f"💰 USDT Balance: {usdt_balance:.2f}\n🏦 Wallet: {TRON_ADDRESS}"
        )
    except Exception as e:
        update.message.reply_text(f"❌ Error fetching balance: {str(e)}")

def passcode(update, context):
    if len(context.args) == 0:
        update.message.reply_text("❌ Please enter a code. Example: /passcode 2486")
        return
    
    code = context.args[0]
    if code == PASSCODE:
        update.message.reply_text("✅ Passcode correct! Access granted.")
    else:
        update.message.reply_text("🚫 Wrong passcode!")

def help_command(update, context):
    update.message.reply_text(
        "📌 Available Commands:\n"
        "/start - Start the bot and confirm it is active\n"
        "/status - Check if the wallet monitor is running\n"
        "/balance - Show current USDT balance of your Tron wallet\n"
        "/passcode <code> - Enter your access code\n"
        "/help - Show all available commands"
    )

# === MAIN ===
def main():
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("status", status))
    dp.add_handler(CommandHandler("balance", balance))
    dp.add_handler(CommandHandler("passcode", passcode))
    dp.add_handler(CommandHandler("help", help_command))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
