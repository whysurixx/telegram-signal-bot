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
    await dp.start_polling(bot)  # Используем start_polling вместо run_polling

if __name__ == "__main__":
    try:
        # Проверяем, есть ли уже запущенный цикл событий
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Если цикл уже запущен, добавляем задачу
            loop.create_task(main())
        else:
            # Если цикла нет, запускаем через run
            asyncio.run(main())
    except RuntimeError:
        # Альтернативный способ для сред с запущенным циклом
        asyncio.ensure_future(main())
        loop = asyncio.get_event_loop()
        loop.run_forever()