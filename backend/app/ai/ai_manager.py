import socket
from typing import Literal

from ..config import get_settings
from .offline_ai import OfflineAIService
from .online_ai import OnlineAIService


class AIManager:
    def __init__(self):
        self.settings = get_settings()
        self.online = OnlineAIService()
        self.offline = OfflineAIService()

    def _has_internet(self) -> bool:
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=1.5)
            return True
        except OSError:
            return False

    def resolve_mode(self, requested: Literal["online", "offline", "auto"]) -> Literal["online", "offline"]:
        if requested in {"online", "offline"}:
            return requested
        if self.settings.ai_mode in {"online", "offline"}:
            return self.settings.ai_mode
        return "online" if self._has_internet() else "offline"

    def generate_article(
        self,
        author_name: str,
        title: str,
        topic: str,
        category: str,
        requested_mode: Literal["online", "offline", "auto"] = "auto",
    ) -> tuple[str, str]:
        mode = self.resolve_mode(requested_mode)
        if mode == "online":
            return self.online.generate_article(author_name, title, topic, category), mode
        return self.offline.generate_article(author_name, title, topic, category), mode
