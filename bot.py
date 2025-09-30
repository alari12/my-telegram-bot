from telegram.ext import Application, CommandHandler
import os

async def start(update, context):
    await update.message.reply_text("Hello! 🚀 Your bot is alive!")

def main():
    TOKEN = os.getenv("TOKEN")  # BotFather token stored in Railway
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()

if __name__ == "__main__":
    main()
