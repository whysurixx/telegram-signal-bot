import asyncio
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import client, admin
from database.db import DataBase

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Регистрация роутеров
    dp.include_router(client.router)
    dp.include_router(admin.router)
    
    # Инициализация базы данных
    await DataBase.on_startup()
    
    # Запуск поллинга
    await dp.run_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())