import asyncio

import telebot_core_service

class BotCore:
    """Core class for bot

    """
    def __init__(self):
        """BotCore initialize

        """
        self.telebot_service = telebot_core_service.TelebotCoreService()
        self._register_handlers()


    def _register_handlers(self):
        """Handlers register

        """
        self.telebot_service.bot.message_handler(content_types=['text'])(self.telebot_service.handle_text_message)


    async def run(self):
        """Run a bot


        """
        await self.telebot_service.run()


async def main():
    bot = BotCore()
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
