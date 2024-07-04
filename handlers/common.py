#######################################################################################################
# Bot handler for common commands on starting stage.
#######################################################################################################

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.main_menu import main_menu_kb
from bot import WHITELIST

from filters.user_access import UserAccessFilter

#######################################################################################################

# Initialize Router and user access filter to handle common commands
router = Router()
router.message.filter(
    UserAccessFilter(user_id=WHITELIST)
)

#######################################################################################################

@router.message(Command("start"))
async def cmd_start(message: Message):
    """Handle /start command

    Parameters
    ----------
    message: aiogram.types.Message
        Message from user object
    """
    await message.answer("Выберите интересующий раздел в меню", reply_markup=main_menu_kb())

@router.message(Command("help"))
async def cmd_help(message: Message):
    """Handle /help command

    Parameters
    ----------
    message: aiogram.types.Message
        Message from user object
    """
    await message.answer("NOT IMPLEMENTED", reply_markup=ReplyKeyboardRemove())
