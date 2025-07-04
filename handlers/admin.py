from aiogram import F, Router, types, Bot
from aiogram.filters.command import CommandStart
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from keyboards.admin import admin_command
from database.db import DataBase
from aiogram.fsm.context import FSMContext
from config import ADMIN_ID
from aiogram.fsm.state import State, StatesGroup

router = Router()

class Admin_States(StatesGroup):
    get_userinfo = State()
    give_balance = State()
    get_userinfo_del = State()
    delete_balance = State()
    mailing_text = State()
    set_referral = State()

@router.message(F.text == '/admin')
async def admin_handler(message: types.Message, state: FSMContext):
    if message.from_user.id == ADMIN_ID:
        await state.clear()
        users_count = await DataBase.get_users_count()
        verified_count = await DataBase.get_verified_users_count()
        statistics_message = (
            f"<b>Статистика бота:</b>\n"
            f"🔹 <b>Общее количество пользователей:</b> <code>{users_count}</code>\n"
            f"🔹 <b>Количество пользователей прошедших верификацию:</b> <code>{verified_count}</code>"
        )
        await message.answer(statistics_message, reply_markup=await admin_command(), parse_mode="HTML")

@router.callback_query(F.data == 'stat')
async def statistics_handler(callback: types.CallbackQuery):
    users_count = await DataBase.get_users_count()
    verified_count = await DataBase.get_verified_users_count()
    statistics_message = (
        f"<b>Статистика бота:</b>\n"
        f"🔹 <b>Общее количество пользователей:</b> <code>{users_count}</code>\n"
        f"🔹 <b>Количество пользователей прошедших верификацию:</b> <code>{verified_count}</code>"
    )
    await callback.message.answer(statistics_message, parse_mode="HTML")
    await callback.answer()

@router.callback_query(F.data == 'mailing')
async def mailing_state(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Отправьте сообщение")
    await state.set_state(Admin_States.mailing_text)

@router.message(Admin_States.mailing_text)
async def mailing_state(message: types.Message, state: FSMContext, bot: Bot):
    mailing_message = message.message_id
    ikb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text='Отправить', callback_data='send_mailing'), 
         InlineKeyboardButton(text='Отмена', callback_data='decline_mailing')]
    ])
    await bot.copy_message(chat_id=message.chat.id, from_chat_id=message.chat.id,
                           message_id=mailing_message, reply_markup=ikb, parse_mode="HTML")
    await state.update_data(msg=mailing_message)

@router.callback_query(F.data == 'send_mailing')
async def mailing_handler(callback: types.CallbackQuery, state: FSMContext, bot: Bot):
    errors_count = 0
    good_count = 0
    data = await state.get_data()
    mailing_message = data['msg']
    users = await DataBase.get_users()
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Рассылка начата...")
    for i in users:
        try:
            await bot.copy_message(chat_id=i[1], from_chat_id=callback.from_user.id,
                                   message_id=mailing_message, parse_mode="HTML")
            good_count += 1
        except Exception as ex:
            errors_count += 1
            print(ex)
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer(f"<b>Кол-во отосланных сообщений:</b> <code>{good_count}</code>\n\
<b>Кол-во пользователей заблокировавших бота:</b> <code>{errors_count}</code>", parse_mode="HTML")
    await callback.answer()
    await state.clear()

@router.callback_query(F.data == 'decline_mailing')
async def decline_mailing(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Рассылка отменена", reply_markup=await admin_command())
    await state.clear()

@router.callback_query(F.data == 'set_referral')
async def set_referral_state(callback: types.CallbackQuery, state: FSMContext):
    try:
        await callback.message.delete()
    except:
        pass
    await callback.message.answer("Отправьте новый URL рефералки:")
    await state.set_state(Admin_States.set_referral)

@router.message(Admin_States.set_referral)
async def set_referral_handler(message: types.Message, state: FSMContext):
    new_referral_url = message.text.strip()
    if new_referral_url.startswith(('http://', 'https://')):
        await DataBase.set_ref(new_referral_url)
        await message.answer("Рефералка успешно обновлена!", reply_markup=await admin_command())
    else:
        await message.answer("Неверный URL. Используйте http:// или https://", reply_markup=await admin_command())
    await state.clear()