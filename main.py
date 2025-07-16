#main.py contains all the codes to run the bot using the references to other files
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import logging
from aiogram import Bot, Dispatcher, executor
from aiogram.utils import executor
from aiohttp import web
import start
from loguru import logger
import po_database
import team_management
import po_management
import reminder
from config import BOT_TOKEN, BASEROW_TOKEN, WEBHOOK, WEBHOOK_PATH, WEBHOOK_URL
import invoice
import scheduler
import healthcheck
import baserow
#for requirements.txt use pip3 freeze > requirements.txt
#pip3 list --format=freeze > requirements.txt - latest way to get requirements.txt
#APIs for both the Finance_1TPT telegram bot (created using BotFather) and baserow API
API_token = BOT_TOKEN
baserow_API = BASEROW_TOKEN

logging.basicConfig(level = logging.INFO)
#declaring the bot to run later at the end of the script
bot = Bot(token = API_token)

#Memory storage is needed for the bot to store information for the various classes which would be declared belpw
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage, run_tasks_by_default=True)
runner = executor.Executor(dp)
log = logging.getLogger('broadcast')

async def on_startup_webhook(_):
    await bot.set_webhook(WEBHOOK_URL)

if __name__ == '__main__':
    start.setup(dp)
    po_database.setup(dp)
    po_management.setup(dp)
    team_management.setup(dp)
    reminder.setup(dp)
    invoice.setup(dp)
    scheduler.setup(runner)
    baserow.setup(runner)
    # if WEBHOOK:
    #     logger.info("Running in Webhook Mode")
    #     app = web.Application()
    #     runner.on_startup(on_startup_webhook, webhook=True, polling=False)
    #     runner.set_webhook(
    #         webhook_path=f"/{WEBHOOK_PATH}",
    #         web_app=app
    #     )

    #     healthcheck.setup(runner)

    #     runner.run_app(
    #         host="0.0.0.0", 
    #         port=10000
    #     )
    # else:
    #     logger.info("Running in Polling Mode")
    runner.start_polling()
    
    