from aiogram.utils.executor import Executor
from aiohttp_healthcheck import HealthCheck
from loguru import logger

from config import WEBHOOK_URL


health = HealthCheck()


def setup(runner: Executor):
    logger.info("Setting up Health Check...")
    health.add_check(check_webhook)
    runner.web_app.router.add_get("/healthcheck", health)


async def check_webhook():
    from main import bot

    webhook = await bot.get_webhook_info()
    if webhook.url and webhook.url == WEBHOOK_URL:
        return True, f"Webhook configured correctly."
    else:
        logger.error(f"Configured wrong webhook URL {webhook}", webhook=webhook.url)
        return False, "Configured invalid webhook URL"
