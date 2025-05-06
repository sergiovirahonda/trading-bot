# Python imports
import telegram

class TelegramAdapter:
    def __init__(self, api_token: str, chat_id: str):
        self.api_token = api_token
        self.chat_id = chat_id
        self.bot = telegram.Bot(token=self.api_token)

    async def send_message(self, message: str):
        """Send a message to the Telegram chat."""
        await self.bot.send_message(chat_id=self.chat_id, text=message)
