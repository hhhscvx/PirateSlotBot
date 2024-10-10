import asyncio
from random import uniform
from urllib.parse import quote, unquote
from http import HTTPStatus

import aiohttp
from aiohttp_socks import ProxyConnector
from pyrogram import Client
from pyrogram.raw.functions.messages import RequestWebView
from pyrogram.raw.types import WebViewResultUrl
from fake_useragent import UserAgent

from data import config
from utils.core import logger


class PirateSlot:
    def __init__(self, tg_client: Client, proxy: str | None = None) -> None:
        self.client = tg_client
        self.session_name = tg_client.name
        self.proxy = f"{config.PROXY_TYPE_REQUESTS}://{proxy}" if proxy else None
        connector = ProxyConnector.from_url(url=self.proxy) if proxy else aiohttp.TCPConnector(verify_ssl=False)

        headers = {
            'User-Agent': UserAgent(os='android', browsers='chrome').random,
        }
        self.session = aiohttp.ClientSession(headers=headers, trust_env=True, connector=connector)

    async def get_me(self) -> dict[str, str | int]:
        resp = await self.session.get(url='https://back.pirate-farm.ink/users/me')
        resp_json = await resp.json()
        return resp_json

    async def claim(self, claim_id: int) -> tuple[bool, int]:
        resp = await self.session.post(url='https://back.pirate-farm.ink/farming/complete',
                                       json={'jobId': claim_id})
        resp_json: dict = await resp.json()
        success_claimed = resp_json.get('status') == 'completed'
        claimed_amount = resp_json.get('amount')  # str
        return success_claimed, claimed_amount

    async def start(self) -> dict[str, str | int] | None:
        """Если не None, то логировать что саксес старт"""
        resp = await self.session.post(url='https://back.pirate-farm.ink/farming/start')
        return (await resp.json()) if resp.status == HTTPStatus.CREATED else None

    async def claim_info(self) -> dict[str, str | int]:
        """клеймить когда «canClaimInSeconds» == 0 и status != completed"""
        resp = await self.session.get(url='https://back.pirate-farm.ink/farming/get-latest')
        return await resp.json()

    async def task_list(self) -> list[dict[str, str | int | bool]]:
        """Проходиться по каждому и если completed = false - выполнять"""
        resp = await self.session.get(url='https://back.pirate-farm.ink/tasks/list')
        return await resp.json()

    async def complete_task(self, task_id: int) -> dict:
        resp = await self.session.post(url='https://back.pirate-farm.ink/tasks/complete',
                                       json={'taskId': task_id})
        return (await resp.json()) if resp.status == HTTPStatus.CREATED else None

    async def play_game(self, bet: int, currency: str = "pir") -> tuple[str, str]:
        """Если reward = 0 - логировать что lose"""
        resp = await self.session.post(url='https://back.pirate-farm.ink/games/create-game',
                                       json={'bet': f'{bet:.2f}', 'currency': currency})
        resp_json = await resp.json()
        return resp_json.get('reward'), resp_json.get('modifier')

    async def login(self) -> bool:
        await asyncio.sleep(uniform(*config.DELAY_CONN_ACCOUNT))
        query = await self.get_tg_web_data()

        if query is None:
            logger.error(f"{self.session_name} | Session {self.account} invalid")
            await self.logout()
            return None

        self.session.headers['Tg-Init-Data'] = query
        return True

    async def get_tg_web_data(self) -> str | None:
        try:
            await self.client.connect()

            web_view: WebViewResultUrl = await self.client.invoke(RequestWebView(
                peer=await self.client.resolve_peer('PIRATE_SLOT_BOT'),
                bot=await self.client.resolve_peer('PIRATE_SLOT_BOT'),
                platform='android',
                from_bot_menu=False,
                url="https://front.pirate-farm.ink/"
            ))
            await self.client.disconnect()
            auth_url = web_view.url

            query = unquote(string=unquote(string=auth_url.split('tgWebAppData=')[1].split('&tgWebAppVersion')[0]))
            query_id = query.split('query_id=')[1].split('&user=')[0]
            user = quote(query.split("&user=")[1].split('&auth_date=')[0])
            auth_date = query.split('&auth_date=')[1].split('&hash=')[0]
            hash_ = query.split('&hash=')[1]

            return f"query_id={query_id}&user={user}&auth_date={auth_date}&hash={hash_}"

        except Exception as error:
            raise error
            return None
