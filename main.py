import asyncio
import os
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web
from handlers import client, admin
from database.db import DataBase


WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = os.environ.get("WEBHOOK_URL", "https://telegram-bot-1win.onrender.com" + WEBHOOK_PATH)
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.environ.get("PORT", 8080))

async def on_startup(_):
    print(f"Webhook started at {WEBHOOK_URL}")

async def main():
    bot = Bot(token=os.environ["BOT_TOKEN"])
    dp = Dispatcher()
       
    dp.include_router(client.router)
    dp.include_router(admin.router)
       
    await DataBase.on_startup()
       
    await bot.delete_webhook(drop_pending_updates=True)
       
    await bot.set_webhook(
        url=WEBHOOK_URL,
        allowed_updates=["message", "callback_query"]
    )
       
    app = web.Application()
    webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    setup_application(app, dp, bot=bot)
       
    # Запуск сервера
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, WEB_SERVER_HOST, WEB_SERVER_PORT)
    await site.start()
       
    # Держим приложение работающим
    await asyncio.Event().wait()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass