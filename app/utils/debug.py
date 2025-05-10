# app/utils/debug.py
from typing import TYPE_CHECKING
from app.config import RuntimeFlags

if TYPE_CHECKING:
    from app.conversation import Conversation

class HandlerDebugMixin:
    conversation: "Conversation"

    def debug(self, note: str = None) -> None:
        # short‐circuit if debug mode is off
        if not RuntimeFlags.DEBUG_MODE:
            return None

        # delegate to the real Conversation.debug
        self.conversation.debug(note)

        # make PyCharm happy by returning None explicitly
        return None
