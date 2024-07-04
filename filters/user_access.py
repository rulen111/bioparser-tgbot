#######################################################################################################
# Filtering users with access to bot.
#######################################################################################################

from typing import Union

from aiogram.filters import BaseFilter
from aiogram.types import Message

#######################################################################################################

class UserAccessFilter(BaseFilter):
    """
    A class for user access filtration.
    Inherits from aiogram.filters.BaseFilter.
    """
    
    def __init__(self, user_id: Union[int, list]):
        """Initializes filter

        Parameters
        ----------
        user_id : Union[int, list]
            Id of a user trying to access bot
        """
        self.user_id = user_id

    async def __call__(self, message: Message) -> bool:
        """Check if a user has access

        Parameters
        ----------
        message : aiogram.types.Message
            Message from user

        Returns
        -------
        bool
            True if user has access to bot
        """
        if isinstance(self.user_id, int):
            return message.from_user.id == self.user_id
        else:
            return message.from_user.id in self.user_id
