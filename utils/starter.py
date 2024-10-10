import asyncio
from pprint import pprint
from typing import NoReturn

from pyrogram import Client

from utils.pirateslot import PirateSlot
from utils.core import logger
from data import config


async def start(tg_client: Client, proxy: str | None = None) -> NoReturn:
    pirateslot = PirateSlot(tg_client=tg_client, proxy=proxy)
    session_name = tg_client.name + '.session'

    while True:
        try:
            await pirateslot.login()
            me = await pirateslot.get_me()
            logger.success(f"{session_name} | Signed in! Balance: {me.get('storedPirBalance')}")

            # Claim
            claim_info = await pirateslot.claim_info()
            if claim_info['canClaimInSeconds'] == 0 and claim_info['status'] != 'completed':
                success_claimed, claimed_amount = await pirateslot.claim(claim_id=claim_info['id'])
                if success_claimed is True:
                    logger.success(f"{session_name} | Claimed +{claimed_amount} PIR")
            elif seconds_left := claim_info['canClaimInSeconds'] > 0:
                logger.info(f"{session_name} | Can`t claim yet, {seconds_left} seconds left.")


            # Tasks
            tasks_list = await pirateslot.task_list()
            for task in tasks_list:
                if task['completed'] is False:
                    complete = await pirateslot.complete_task(task_id=task['id'])
                    if complete is not None:
                        logger.success(
                            f"{session_name} | Complete task «{task['name']}» | Earned +{task['reward']} PIR")

            # Game

            await asyncio.sleep(5)
            break

            ...

        except Exception as error:
            logger.error(f"{session_name} | Unknown Error: {error}")
            await asyncio.sleep(delay=3)
