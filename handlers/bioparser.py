#######################################################################################################
# Bot handler for bio parsing command.
#######################################################################################################

from aiogram import Router, F, Bot
from aiogram.filters.text import Text
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.types import FSInputFile

from bot import USERS_DIR, WHITELIST
from app.telethon_payload import payload
from filters.user_access import UserAccessFilter

import os

#######################################################################################################

# Initialize Router and user access filter to handle parsing command
router = Router()
router.message.filter(
    UserAccessFilter(user_id=WHITELIST)
)

#######################################################################################################

@router.message(Text(text="Парсинг био", ignore_case=True))
async def bio_parsing(message: Message):
    """Ask user to send a text file with usernames

    Parameters
    ----------
    message: aiogram.types.Message
        Message from user object
    """
    await message.answer(
        "Загрузите .txt файл со списком юзернеймов для обработки",
        reply_markup=ReplyKeyboardRemove()
    )

@router.message(F.document)
async def handle_input_file(message: Message, bot: Bot):
    """Handle text file from user and initiate parsing sequence

    Parameters
    ----------
    message: aiogram.types.Message
        Message from user object
    bot: aiogram.Bot
        Bot object
    """
    if message.document.file_name.endswith('.txt'):
        await message.answer('Начинаю парсинг')

        username_path = USERS_DIR + message.document.file_name
        await bot.download(message.document, username_path)

        result, numbers = await payload(username_path)

        out_doc = FSInputFile(result)
        await message.reply_document(out_doc, caption=f'Успешно обработано {numbers[0]}/{numbers[1]} юзернеймов')

        os.remove(username_path)
        os.remove(result)
    else:
        await message.answer('Пожалуйста, отправьте корректный файл')
