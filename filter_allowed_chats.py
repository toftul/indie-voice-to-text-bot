from telegram import Message
from telegram.ext.filters import MessageFilter
import logging


class FilterAllowedChats(MessageFilter):

    def __init__(self, allowed_chat_ids):
        super().__init__()
        self.allowed_chat_ids = allowed_chat_ids

    def filter(self, message: Message) -> bool:
        is_voice = bool(message.voice)
        chat_id = str(message.chat.id)
        #is_allowed_user = chat_id in self.allowed_chat_ids
        is_allowed_user = True
        is_allowed = is_voice and is_allowed_user
        if not is_allowed:
            logging.error(f"chat_id={chat_id} is not allowed")
        return is_allowed
