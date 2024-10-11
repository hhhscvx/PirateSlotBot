import asyncio
import random
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
            logger.success(f"{session_name} | Signed in! Balance: {round(float(me.get('storedPirBalance')))} PIR")

            # Claim
            claim_info = await pirateslot.claim_info()
            if claim_info['canClaimInSeconds'] == 0 and claim_info['status'] != 'completed':
                success_claimed, claimed_amount = await pirateslot.claim(claim_id=claim_info['id'])
                if success_claimed is True:
                    logger.success(f"{session_name} | Claimed +{claimed_amount} PIR")
            elif (seconds_left := claim_info['canClaimInSeconds']) > 0:
                logger.info(f"{session_name} | Can`t claim yet, {seconds_left} seconds left.")
            await asyncio.sleep(1)

            claim_info = await pirateslot.claim_info()
            if claim_info['status'] == 'completed':
                start_farm = await pirateslot.start()
                if start_farm is not None:
                    logger.success(f"{session_name} | Start Farming")
                await asyncio.sleep(random.uniform(1.5, 3))
            await asyncio.sleep(1)

            # Tasks
            tasks_list = await pirateslot.task_list()
            await asyncio.sleep(1)
            for task in tasks_list:
                if task['completed'] is False:
                    complete = await pirateslot.complete_task(task_id=task['id'])

                    if complete is not None:
                        logger.success(
                            f"{session_name} | Complete task «{task['name']}» | Earned +{task['reward']} PIR")
                    await asyncio.sleep(random.uniform(1.8, 3.5))

            # Game
            if config.PLAY_GAME:
                me = await pirateslot.get_me()
                while True:
                    if pir_balance := float(me['pirBalance']) < config.MINIMAL_PIR_BALANCE:
                        sleep_time = random.uniform(*config.SLEEP_BY_LOW_PIR)
                        logger.info(f"{session_name} | Low Game PIR Balance: {pir_balance} | Total: {me['storedPirBalance']} | "
                                    f"Sleep {sleep_time:.1f}s...")
                        await asyncio.sleep(sleep_time)
                        break
                    bet = random.choice(seq=config.RANDOM_BET_COUNT)
                    reward, _ = await pirateslot.play_game(bet=bet)
                    me = await pirateslot.get_me()
                    if int(reward) == 0:
                        logger.success(f"{session_name} | Play game: Bet: {bet} | Lose | Game Balance:"
                                       f" {round(float(me['pirBalance']))} | Total: {round(float(me['storedPirBalance']))}")
                    elif int(reward) > 0:
                        logger.success(f"{session_name} | Play game! Bet: {bet} | +{int(reward)} PIR! | Game Balance:"
                                       f" {me['pirBalance']} | Total: {me['storedPirBalance']}")
                    await asyncio.sleep(random.uniform(*config.SLEEP_BETWEEN_PLAY))

            await asyncio.sleep(5)
            break

            ...

        except Exception as error:
            logger.error(f"{session_name} | Unknown Error: {error}")
            await asyncio.sleep(delay=3)
            raise error
