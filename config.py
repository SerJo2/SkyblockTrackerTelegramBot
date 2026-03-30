import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()

@dataclass
class BotConfing:
    TELEGRAM_API_TOKEN: str
    HYPIXEL_API_TOKEN: str

    @classmethod
    def from_env(cls):
        return cls(
            TELEGRAM_API_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN"),
            HYPIXEL_API_TOKEN=os.getenv("HYPIXEL_API_TOKEN"),
        )