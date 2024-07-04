#######################################################################################################
# Bot interface functionality.
#######################################################################################################

import os
import logging
import datetime
import asyncio
import socks
import platform
import yaml

from glob import glob

from aiogram import Bot, Dispatcher

#######################################################################################################
# Load config.
#######################################################################################################

with open('config.yaml') as c:
    config = yaml.full_load(c)

PROXY = {'proxy_type': socks.PROXY_TYPE_HTTP}

for k, v in config['TELEGRAM']['PROXY'].items():
    PROXY[k] = v

DSN = config['SENTRY']['DSN']
SAMPLE_RATE = config['SENTRY']['SAMPLE_RATE']

if DSN:
    import sentry_sdk
    sentry_sdk.init(
        dsn=DSN,
        traces_sample_rate=SAMPLE_RATE
    )

#######################################################################################################
# Initialize global parameters.
#######################################################################################################

API_ID = config['TELEGRAM']['API_ID']
API_HASH = config['TELEGRAM']['API_HASH']
BOT_TOKEN = config['TELEGRAM']['BOT_TOKEN']
WHITELIST = config['TELEGRAM']['WHITELIST']

SESSIONS_DIR = "./app/session/"
USERS_DIR = "./app/users/"
RES_DIR = "./app/results/"
LOG_DIR = "./app/log/"

for directory in [SESSIONS_DIR, USERS_DIR, RES_DIR, LOG_DIR]:
    if not os.path.exists(directory):
        os.makedirs(directory)

if platform.system()=='Windows':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

NUM_SESS = len(glob(SESSIONS_DIR + "*.session"))

#######################################################################################################
# Initialize logging.
#######################################################################################################

logging.basicConfig(level=logging.INFO, filename=f'{LOG_DIR}{datetime.datetime.now().date()}_log.txt',
                    filemode="a", format="%(asctime)s %(levelname)s %(message)s", encoding='UTF-8')
logging.info('-' * 80)
logging.info(f'LAUNCHING WITH {NUM_SESS} sessions at {datetime.datetime.now()}')
logging.info('-' * 80)

#######################################################################################################

from handlers import common, bioparser

async def main():
    """Starts up bot interface

    """
    logging.info(f'Starting bot at {datetime.datetime.now()}')
    bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
    dp = Dispatcher(bot=bot)
    logging.info(f'Bot started at {datetime.datetime.now()}')
    print(f'Bot started at {datetime.datetime.now()}')

    dp.include_routers(common.router, bioparser.router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
