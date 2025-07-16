from aiogram.utils.executor import Executor
from loguru import logger
from apscheduler.jobstores.memory import MemoryJobStore
from apscheduler.executors.asyncio import AsyncIOExecutor
from apscheduler.schedulers.asyncio import AsyncIOScheduler


jobstores = {"default": MemoryJobStore()}
executors = {"default": AsyncIOExecutor()}

scheduler = AsyncIOScheduler(
    jobstores=jobstores, executors=executors
)

async def on_startup(_):
    logger.info("Starting APScheduler...")
    scheduler.start()


async def on_shutdown(_):
    logger.info("Shutting down APScheduler...")
    scheduler.shutdown()


def setup(executor: Executor):
    executor.on_startup(on_startup)
    executor.on_shutdown(on_shutdown)