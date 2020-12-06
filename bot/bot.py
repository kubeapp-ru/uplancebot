import aiotg
import logging

from bot.log_handler import add_handler


class Bot(aiotg.Bot):
    '''Wrapper for base class for adding next step functionality'''
    def __init__(self, *args, **kwargs):
        self._next_step_hanlders = {}
        super().__init__(*args, **kwargs)

    def _process_message(self, message):
        '''Check if chat has a handler for next step'''
        chat = aiotg.Chat.from_message(self, message)
        if chat.id in self._next_step_hanlders:
            callback, kwargs = self._next_step_hanlders.pop(chat.id)
            return callback(chat, message, **kwargs)
        return super()._process_message(message)

    def set_next_step(self, chat, callback, **kwargs):
        '''Use for set handler on next step'''
        self._next_step_hanlders[chat.id] = (callback, kwargs)
