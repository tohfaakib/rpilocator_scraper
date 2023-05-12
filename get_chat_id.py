import asyncio
from telegram import Bot

# Replace 'YOUR_BOT_TOKEN' with your own bot token
bot_token = ''

async def get_channel_chat_id():
    bot = Bot(token=bot_token)
    chat = await bot.get_chat('@')
    return chat.id

async def main():
    chat_id = await get_channel_chat_id()
    print(f"Chat ID for the channel: {chat_id}")

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
