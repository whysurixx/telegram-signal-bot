from aiogram.utils.keyboard import InlineKeyboardBuilder

async def admin_command():
    ikb = InlineKeyboardBuilder()

    ikb.button(text="Рассылка📩", callback_data="mailing")
    ikb.button(text="Смена реферальной ссылки🔗", callback_data="set_referral")
    ikb.button(text="Статистика📊", callback_data="stat")
    ikb.adjust(1)
    return ikb.as_markup()

