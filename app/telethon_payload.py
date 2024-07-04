#######################################################################################################
# Core functionality of bioparser. Initializes clients and parses user profile data.
#######################################################################################################

from telethon import TelegramClient, errors
from telethon.tl.functions.users import GetFullUserRequest

import csv
import json
import logging
import datetime
import asyncio
import sys

from glob import glob
from tqdm.asyncio import tqdm as atqdm

from bot import PROXY, API_ID, API_HASH, SESSIONS_DIR, USERS_DIR, RES_DIR, LOG_DIR, NUM_SESS

#######################################################################################################
logging.basicConfig(level=logging.INFO, filename=f'{LOG_DIR}{datetime.datetime.now().date()}_log.txt',
                    filemode="a", format="%(asctime)s %(levelname)s %(message)s", encoding='UTF-8')
#######################################################################################################

async def start_client(args, clients, phone):
    """Initializes Telegram Client connection 
    with given parameters.

    Parameters
    ----------
    args : dict
        Dictionary with arguments for telethon.TelegramClient
    clients : list
        List that aggregates all active clients
    phone : str
        Phone number of a telegram client
    """
    try:
        client = await TelegramClient(**args).start()
    
    except Exception:
        e = sys.exc_info()
        logging.error(f'Problem starting {phone} client\n{e}')
    
    finally:
        logging.info(f'Client {phone} connected')
        clients.append((client, phone))

async def make_clients():
    """Batch client initialization.
    
    Returns
    -------
    list
        List with Union[object, str]
        for every Telegram session provided by user.
    """
    session_list = glob(SESSIONS_DIR + "*.session")
    json_list = glob(SESSIONS_DIR + "*.json")
    
    json_params = []
    for idx, fjson in enumerate(json_list):
        with open(fjson, 'r') as fp:
            params_tmp = json.load(fp)
            json_params.append(params_tmp)

    sessions = [{'session': ses, 'json': js} for ses, js in zip(session_list, json_params)]

    logging.info(f'Starting {NUM_SESS} clients')
    clients = []
    tasks = []
    for session in sessions:
        params = session['json']
        args = {'session': session['session'], 'api_id': API_ID, 'api_hash': API_HASH,
                'proxy': PROXY, 'device_model': params['device'], 'app_version': params['app_version'],
                'lang_code': params['lang_pack'], 'system_lang_code': params['system_lang_pack']}

        phone = params['session_file']
        task = asyncio.create_task(start_client(args, clients, phone))
        tasks.append(task)

    await atqdm.gather(*tasks)

    logging.info(f'Successfully started {NUM_SESS} clients')

    return clients

async def get_user_info(client_tup, username):
    """Get telegram user profile information.

    Parameters
    ----------
    client_tup : Union[object, str]
        telethon.TelegramClient object and phone number
        of initialized client.
    username : str
        Username to be parsed

    Returns
    -------
    dict
        User account link, full name and bio
    """
    username = username.strip('@\n')
    link = 'https://t.me/' + username
    client = client_tup[0]
    phone = client_tup[1]

    logging.info(f'{phone} attempting to get {"@" + username}')
    try:
        entity = await client.get_input_entity(username)
        
    except errors.FloodWaitError as er:
        logging.error(f'{phone} FloodWaitError on get_input_entity({"@" + username}). Have to sleep {er.seconds}')
        time.sleep(er.seconds)

    except ValueError:
        e = sys.exc_info()
        logging.error(f'{phone} ValueError on get_input_entity({"@" + username}): {e[1]}')
        entity = None

    except Exception:
        e = sys.exc_info()
        logging.error(f'{phone} UnhandledError on get_input_entity({"@" + username}): {e[1]}')
        entity = None

    finally:
        if entity:
            try:
                full = await client(GetFullUserRequest(entity))

            except errors.FloodWaitError as er:
                logging.error(f'{phone} FloodWaitError on GetFullUserRequest({"@" + username}). Have to sleep {er.seconds}')
                time.sleep(er.seconds)

            except Exception:
                e = sys.exc_info()
                logging.error(f'{phone} UnhandledError on GetFullUserRequest({"@" + username}): {e[1]}')
                return None

            finally:
                logging.info(f'{phone} successfully parsed {"@" + username}')

                first, last = full.users[0].first_name, full.users[0].last_name
                name = ' '
                if first:
                    name = first + name
                if last:
                    name = name + last
        
                bio = full.full_user.about
                row = {'LINK': link, 'NAME': name, 'BIO': bio}    
            
                return row
        else:
            return None

def get_index(n):
    """Index generator for client rotation.

    Parameters
    ----------
    n : int
        Maximum index

    Yields
    -------
    int
        Either next or first index from 0 to n
    """
    cnt = 0
    while True:
        if cnt - n == 0:
            cnt = 0
            yield cnt
            cnt += 1
        else:
            yield cnt
            cnt += 1

async def proccess(rows, client_tup, username):
    """Proccess one username with given client.

    Parameters
    ----------
    rows : list
        List of user data to append
    client_tup : Union[object, str]
        telethon.TelegramClient object and phone number
        of initialized client.
    username : str
        Username to parse
    """
    row = await get_user_info(client_tup, username)

    if row:
        rows.append(row)
    else:
        pass

async def payload(username_path):
    """Main function of module.

    Parameters
    ----------
    username_path : str
        Path to file with usernames to parse

    Returns
    -------
    Union[str, Union[int, int]]
        Path to resulting .csv file and list
        with number of parsed and processed users
    """
    fn = username_path
    csv_path = (RES_DIR + fn.replace(USERS_DIR, '') + '(bio).csv')

    print(f'Starting clients at {datetime.datetime.now()}')

    clients = await make_clients()
    idx_gen = get_index(NUM_SESS)
    user_rows = []
    async_tasks = []

    with open(username_path, 'r') as fin:
        username_list = fin.readlines()

    with open(csv_path, 'w', newline='', encoding='utf-8') as fout:
        logging.info(f'Starting parsing of {len(username_list)} usernames')
        fieldnames = ['LINK', 'NAME', 'BIO']
        writer = csv.DictWriter(fout, fieldnames=fieldnames)
        writer.writeheader()

        print(f'Launching parsing proccess')

        for line in username_list:
            idx = next(idx_gen)
            task = asyncio.create_task(proccess(user_rows, clients[idx], str(line)))
            async_tasks.append(task)

        await atqdm.gather(*async_tasks)

        for row in user_rows:
            writer.writerow(row)

        numbers = (len(user_rows), len(username_list))

        print(f'Successfuly parsed {numbers[0]}/{numbers[1]} users')
        logging.info(f'Successfuly parsed {numbers[0]}/{numbers[1]} users')

        return (csv_path, numbers)
