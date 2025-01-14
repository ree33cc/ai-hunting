import asyncio
import logging
import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackContext

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = "7520933965:AAFuCR9ao-kB4y44pt2GpVdzzGLEveCzJrw"
CHAT_ID = "1002227186878"

# Base URL of the site to monitor
PUMP_FUN_API = "https://pump.fun/api/bonded-projects"

# Initialize logging
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Global filters for projects
filters = {
    "name": [],
    "ticker": []
}

async def start(update: Update, context: CallbackContext):
    """Send a message when the bot is started."""
    await update.message.reply_text("Hello! Use /filter to add project filters.")

async def filter_projects(update: Update, context: CallbackContext):
    """Add filtering criteria."""
    global filters
    args = context.args
    if len(args) < 2:
        await update.message.reply_text("Usage: /filter <name|ticker> <value>")
        return

    filter_type, value = args[0].lower(), args[1]
    if filter_type not in ["name", "ticker"]:
        await update.message.reply_text("Filter type must be 'name' or 'ticker'.")
        return

    filters[filter_type].append(value)
    await update.message.reply_text(f"Added filter: {filter_type} = {value}")

async def check_projects(app):
    """Monitor pump.fun and send notifications for new projects."""
    global filters

    try:
        # Fetch bonded projects from pump.fun API
        response = requests.get(PUMP_FUN_API)
        response.raise_for_status()
        projects = response.json()  # Assume the API returns a JSON array of projects

        for project in projects:
            name = project.get("name", "").lower()
            ticker = project.get("ticker", "").lower()

            if any(f.lower() in name for f in filters["name"]) or any(f.lower() in ticker for f in filters["ticker"]):
                await app.bot.send_message(chat_id=CHAT_ID, text=f"New bonded project detected: {name} ({ticker})")

    except Exception as e:
        logger.error(f"Error checking projects: {e}")

async def periodic_check(app):
    """Periodically check for new projects."""
    while True:
        await check_projects(app)
        await asyncio.sleep(60)

async def main():
    """Start the bot."""
    # Create the bot application
    application = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("filter", filter_projects))

    # Start the periodic task
    asyncio.create_task(periodic_check(application))

    # Run the bot
    await application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
