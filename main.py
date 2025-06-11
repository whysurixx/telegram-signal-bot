import asyncio
   import os
   import logging
   from aiogram import Bot, Dispatcher
   from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
   from aiohttp import web
   from handlers import client, admin
   from database.db import DataBase

   # Настройка логирования
   logging.basicConfig(level=logging.INFO)
   logger = logging.getLogger(__name__)

   # Настройки из переменных окружения
   WEBHOOK_PATH = "/webhook"
   WEBHOOK_URL = os.environ.get("WEBHOOK_URL", f"https://{os.environ.get('RENDER_EXTERNAL_HOSTNAME', 'telegram-signal-bot-4elh.onrender.com')}{WEBHOOK_PATH}")
   WEB_SERVER_HOST = "0.0.0.0"
   WEB_SERVER_PORT = int(os.environ.get("PORT", 443))

   async def on_startup(_):
       logger.info(f"Webhook started at {WEBHOOK_URL}")
       await DataBase.on_startup()

   async def on_shutdown(_):
       logger.info("Shutting down webhook")
       await DataBase.close()

   async def handle_root(request):
       logger.info(f"Received request on root: {request.method} {request.path}")
       return web.Response(text="Webhook endpoint is /webhook", status=400)

   async def main():
       bot = Bot(token=os.environ["BOT_TOKEN"])
       dp = Dispatcher()
       
       # Регистрация роутеров
       dp.include_router(client.router)
       dp.include_router(admin.router)
       
       # Инициализация базы данных
       try:
           await DataBase.on_startup()
           logger.info("Database initialized successfully")
       except Exception as e:
           logger.error(f"Database initialization failed: {e}")
           raise
       
       # Удаление старого вебхука (если есть)
       try:
           await bot.delete_webhook(drop_pending_updates=True)
           logger.info("Old webhook deleted")
       except Exception as e:
           logger.error(f"Failed to delete webhook: {e}")
       
       # Настройка нового вебхука с явным путем
       try:
           await bot.set_webhook(
               url=WEBHOOK_URL,
               allowed_updates=["message", "callback_query"]
           )
           logger.info(f"New webhook set at {WEBHOOK_URL}")
       except Exception as e:
           logger.error(f"Failed to set webhook: {e}")
           raise
       
       # Настройка веб-сервера
       app = web.Application()
       app.router.add_get('/', handle_root)
       app.router.add_post('/', handle_root)  # Временный обработчик для диагностики
       webhook_requests_handler = SimpleRequestHandler(dispatcher=dp, bot=bot)
       webhook_requests_handler.register(app, path=WEBHOOK_PATH)
       setup_application(app, dp, bot=bot)
       app.on_startup.append(on_startup)
       app.on_shutdown.append(on_shutdown)
       
       # Запуск сервера
       runner = web.AppRunner(app)
       try:
           await runner.setup()
           site = web.TCPSite(runner, WEB_SERVER_HOST, WEB_SERVER_PORT)
           await site.start()
           logger.info(f"Server started on port {WEB_SERVER_PORT}")
       except Exception as e:
           logger.error(f"Failed to start server: {e}")
           raise
       
       # Держим приложение работающим
       await asyncio.Event().wait()

   if __name__ == "__main__":
       try:
           asyncio.run(main())
       except Exception as e:
           logger.error(f"Application failed: {e}")
       except KeyboardInterrupt:
           logger.info("Application stopped by user")