# BioParser Telegram Bot
This bot takes a text file with Telegram usernames and returns a .csv table with Link, Full Name and Bio for each of the given users.

## Prerequisites
- Bot interface uses [aiogram](https://github.com/aiogram/aiogram);
- Main payload runs on [telethon](https://github.com/LonamiWebs/Telethon);
- For proxy usage you will need [PySocks](https://github.com/Anorov/PySocks).

Every required library is listed in [requirements.txt](https://github.com/rulen111/bioparser-tgbot/blob/main/requirements.txt).

Note that in order for this bot to function you will need to at least create a Telegram Bot using BotFather and **have configured proxys as well as Telegram sessions in {session-json} format!**

## How to use
1. First thing you should do is saving **YOUR** credentials in ```./config.yaml``` file for this bot to work. You have to add **IDs** in ```WHITELIST``` (example already inside) of users that would have access to the bot;
2. After that you should create ```./session/``` directory and put your SESSION+JSON account files inside. These accounts will be used for the actual parsing proccess;
3. Now you just have to create an environment, ```pip install -r requirements.txt``` and finally ```python bot.py``` to start the bot.
