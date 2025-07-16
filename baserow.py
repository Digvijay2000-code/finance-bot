import asyncio
import ujson
import typing as t
import datetime as dt
from io import BytesIO
from functools import wraps
from loguru import logger
from aiolimiter import AsyncLimiter
from aiogram.utils.executor import Executor
from aiohttp import ClientSession, FormData
from apscheduler.triggers.date import DateTrigger

from config import BASEROW_TOKEN, BASEROW_USERNAME, BASEROW_PASSWORD
from scheduler import scheduler

API_BASE_URL = "https://api.baserow.io/api/database/rows/table"

HEADERS = {"Authorization": f'Token {BASEROW_TOKEN}'}
HEADERS_JSON = {"Authorization": f'Token {BASEROW_TOKEN}', "Content-Type": "application/json"}


class BaserowClient:
    JWT_EXPIRATION = dt.timedelta(minutes=55)

    def __init__(self) -> None:
        logger.info("Initializing BaserowClient...")
        self._jwt: t.Optional[str] = None
        self.rate_limit: t.Optional[AsyncLimiter] = None
        self.session: t.Optional[ClientSession] = None


    def _handle_exception(brfunc: t.Callable) -> bool:
        @wraps(brfunc)
        async def wrapped(*args, **kwargs):
            try:
                return await brfunc(*args, **kwargs)
            except Exception:
                logger.exception("BaserowClient Exception")
                return False
        return wrapped

    
    def update_jwt(self, token: str):
        logger.info("JWT Update")
        self._jwt = token
        scheduler.add_job(
            self.token_refresh,
            trigger=DateTrigger(dt.datetime.now() + self.JWT_EXPIRATION)
        )

    @_handle_exception
    async def token_auth(self):
        async with self.rate_limit:
            payload = {'username': BASEROW_USERNAME, 'password': BASEROW_PASSWORD}
            resp = await self.session.post(
                'https://api.baserow.io/api/user/token-auth/',
                json=payload
            )
            r = await resp.json()
            self.update_jwt(r["token"])
            return True


    @_handle_exception
    async def token_refresh(self):
        async with self.rate_limit:
            payload = {'token': self._jwt}
            resp = await self.session.post(
                'https://api.baserow.io/api/user/token-refresh/',
                json=payload
            )
            r = await resp.json()
            self.update_jwt(r["token"])
            return True


    @_handle_exception
    async def _upload_file(self, file: BytesIO, filename: str):
        async with self.rate_limit:
            data = FormData()
            data.add_field("file", file, filename=filename)
            headers = {"Authorization": f'JWT {self._jwt}'}
            return await self.session.post(
                'https://api.baserow.io/api/user-files/upload-file/',
                headers=headers,
                data=data
            )

    async def upload_file(self, file: BytesIO, filename: str):
        resp = await self._upload_file(file, filename)
        match resp.status:
            case 200:
                r = await resp.json()
                return r.get("name", False)
            case 401:
                auth = await self.token_auth()
                if auth:
                    retry = await self._upload_file(file, filename)
                    if retry.status == 200:
                        r = await retry.json()
                        return r.get("name", False)
                    else:
                        logger.error("Baserow File Upload Failed")
        
        return False
    
            
    @_handle_exception
    async def create_row(self, table: str, json: dict):
        async with self.rate_limit:
            await self.session.post(
                f'{API_BASE_URL}/{table}/?user_field_names=true',
                headers=HEADERS_JSON,
                json=json
            )
            return True

    @_handle_exception
    async def update_row(self, table: str, row_id: int, json: dict):
        async with self.rate_limit:
            await self.session.patch(
                f'{API_BASE_URL}/{table}/{row_id}/?user_field_names=true',
                headers=HEADERS_JSON,
                json=json
            )
            return True

    @_handle_exception
    async def list_rows(self, table: str, params: dict) -> dict:
        async with self.rate_limit:
            resp = await self.session.get(
                f'{API_BASE_URL}/{table}/?user_field_names=true',
                headers=HEADERS,
                params=params
            )
            return await resp.json()

    @_handle_exception
    async def get_row(self, table: str, row_id: int) -> dict:
        async with self.rate_limit:
            resp = await self.session.get(
                f'{API_BASE_URL}/{table}/{row_id}/?user_field_names=true',
                headers=HEADERS,
            )
            return await resp.json()


baserow = BaserowClient()


async def on_startup(_):
    logger.info("Setting BaserowClient instance variables...")
    baserow.rate_limit = AsyncLimiter(5, 1)
    baserow.session = ClientSession(json_serialize=ujson.dumps)
    logger.info("Getting Baserow JWT...")
    await baserow.token_auth()


async def on_shutdown(_):
    logger.info("Closing BaserowClient aiohttp.ClientSession...")
    # Wait 250 ms for the underlying SSL connections to close
    # https://docs.aiohttp.org/en/stable/client_advanced.html#graceful-shutdown
    await asyncio.sleep(0.250)
    await baserow.session.close()


def setup(runner: Executor):
    runner.on_startup(on_startup)
    runner.on_shutdown(on_shutdown)