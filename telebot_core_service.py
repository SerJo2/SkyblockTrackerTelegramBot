import datetime
import json

from telebot import types, logger
from telebot.async_telebot import AsyncTeleBot

import asyncio
from telebot.async_telebot import AsyncTeleBot
from config import BotConfing


from hypixelez import HypixelClient, constants, SkyblockProfileData

class TelebotCoreService:

    def __init__(self):
        self.config = BotConfing.from_env()
        self.bot = AsyncTeleBot(self.config.TELEGRAM_API_TOKEN)
        self.hypixel_api_client = HypixelClient(self.config.HYPIXEL_API_TOKEN)

    async def run(self):
        try:
            await self.send_scheduled_stats()

            await self.bot.polling()
        except Exception as e:
            raise

    async def handle_text_message(self, message):
        try:
            message_thread_id = self._get_message_thread_id(message)

            command_handlers = {
                "/setup": self._handle_setup_command,
                "/get_diff": self._handle_get_diff_command
            }

            clean_command = message.text.split('@')[0] if '@' in message.text else message.text
            if clean_command in command_handlers:
                await command_handlers[clean_command](message, message_thread_id)
            elif message.reply_to_message:
                await self._handle_reply(message, message_thread_id)

        except Exception as e:
            raise

    @staticmethod
    def _get_message_thread_id(message):
        try:
            return message.reply_to_message.message_thread_id
        except AttributeError:
            return "General"

    async def _handle_setup_command(self, message, message_thread_id):
        await self.bot.send_message(
            message.chat.id,
            "Send Reply To This Message With Minecraft Name And Skyblock Profile Name on separate lines. Example: \nNeono4ka\nPeach",
            message_thread_id=message_thread_id
        )


    async def _handle_reply(self, message, message_thread_id):
        if (message.reply_to_message and
                "Send Minecraft Name And Skyblock Profile Name" in message.reply_to_message.text):
            minecraft = message.text.split('\n')[0]
            skyblock = message.text.split('\n')[1]

            uuid = self.hypixel_api_client.get_uuid_by_name(minecraft)
            profile_uuid = self.hypixel_api_client.get_profile_names_ids_by_id(uuid)[skyblock]
            print(minecraft, skyblock, uuid, profile_uuid)

            data = self.hypixel_api_client.fetch_profile_info(uuid, profile_uuid)

            tg_data = {
                message.chat.id: {
                    "uuid": uuid,
                    "profile_uuid": profile_uuid,
                    "init_data": data._data
                },
            }

            with open("db.json", "w", encoding="utf-8") as f:
                json.dump(tg_data, f, indent=4, ensure_ascii=False)
                f.close()

    async def _handle_get_diff_command(self, message, message_thread_id):
        print(constants.COLLECTION_KEY_VALUES)

        with open('db.json', 'r', encoding='utf-8') as file:
            db_data = json.load(file)

            stats = ""
            new_data = self.hypixel_api_client.fetch_profile_info(db_data[message.chat.id]["uuid"], db_data[message.chat.id]['profile_uuid'])
            old_data = SkyblockProfileData(db_data[message.chat.id]["init_data"], db_data[message.chat.id]["uuid"])
            for key in constants.COLLECTION_KEY_VALUES:
                if old_data.get_collection(key) != new_data.get_collection(key):
                    diff = new_data.get_collection(key) - old_data.get_collection(key)
                    stats += "\n" + key + ": "+ str(diff)
            db_data[message.chat.id]["init_data"] = new_data._data
            await self.bot.send_message(message.chat.id, stats)

            file.close()

        with open("db.json", "w", encoding="utf-8") as f:
            json.dump(db_data, f, indent=4, ensure_ascii=False)
            f.close()


