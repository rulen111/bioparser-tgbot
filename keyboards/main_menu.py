#######################################################################################################
# Bot main menu keyboard.
#######################################################################################################

from aiogram.types import ReplyKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder

#######################################################################################################

def main_menu_kb() -> ReplyKeyboardMarkup:
    """Send keyboard markup

    Returns
    -------
    aiogram.types.ReplyKeyboardMarkup
        Built keyboard markup
    """
    kb = ReplyKeyboardBuilder()
    kb.button(text="Парсинг био")
    kb.adjust(1)
    return kb.as_markup(resize_keyboard=True)
