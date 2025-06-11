from aiogram import Bot, Dispatcher, types, executor
from database import init_db, save_data, get_data

bot = Bot(token="YOUR_BOT_TOKEN")
dp = Dispatcher(bot)
db_conn = init_db()

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    chat_id = message.chat.id
    username = message.from_user.username
    save_data(db_conn, chat_id, username, "Hello data")
    data = get_data(db_conn, chat_id)
    await message.reply(f"Welcome {username}! Your data: {data[1] if data else 'None'}")

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)