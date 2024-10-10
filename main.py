import os
import argparse
import asyncio
from itertools import zip_longest

from pyrogram import Client

from data import config
from utils.core import get_all_lines
from utils.core.telegram import Accounts
from utils.starter import start


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--action", type=int, help="Action to perform")

    action = parser.parse_args().action
    if not action:
        action = int(input("Select action:\n1. Start soft\n2. Create sessions\n\n> "))

    if not os.path.exists('sessions'):
        os.mkdir('sessions')

    if config.USE_PROXY_FROM_FILE:
        if not os.path.exists(config.PROXY_PATH):
            with open(config.PROXY_PATH, 'w') as f:
                f.write("")
    else:
        if not os.path.exists('sessions/accounts.json'):
            with open("sessions/accounts.json", 'w') as f:
                f.write("[]")

    if action == 2:
        await Accounts().create_sessions()

    if action == 1:
        accounts = await Accounts().get_accounts()

        tasks = []

        if config.USE_PROXY_FROM_FILE:
            proxys = get_all_lines(filepath=config.PROXY_PATH)
            for account, proxy in zip_longest(accounts, proxys):
                if not account:
                    break
                client, proxy = get_client_and_proxy_by_account(account)
                tasks.append(asyncio.create_task(start(tg_client=client, proxy=proxy)))
        else:
            for account in accounts:
                client, proxy = get_client_and_proxy_by_account(account)
                tasks.append(asyncio.create_task(start(tg_client=client, proxy=proxy)))

        await asyncio.gather(*tasks)


def get_client_and_proxy_by_account(account: dict[str, str | int]) -> tuple[Client, str]:
    session_name, _, proxy = account.values()

    proxy_dict: dict | None = None

    if proxy:
        proxy_dict = {
            "scheme": config.PROXY_TYPE_TG,
            "hostname": proxy.split(":")[1].split("@")[1],
            "port": int(proxy.split(":")[2]),
            "username": proxy.split(":")[0],
            "password": proxy.split(":")[1].split("@")[0]
        }

    return Client(
        name=session_name,
        api_id=config.API_ID,
        api_hash=config.API_HASH,
        proxy=proxy_dict,
        workdir=config.WORKDIR
    ), proxy


if __name__ == "__main__":
    asyncio.run(main())
