import asyncio
from pprint import pprint
from random import randint, uniform
from typing import NoReturn

from pyrogram import Client

from utils.pirateslot import PirateSlot
from utils.core import logger
from data import config


async def start(tg_client: Client, proxy: str | None = None) -> NoReturn:
    pirateslot = PirateSlot(tg_client=tg_client, proxy=proxy)
    session_name = tg_client.name + '.session'

    while True:
        await pirateslot.login()

        me = await pirateslot.get_me()
        pprint(me)
        logger.info(me)

        await asyncio.sleep(5)
        break

        ...
