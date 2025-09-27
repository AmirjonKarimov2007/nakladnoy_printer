from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

main_menu_for_super_admin = InlineKeyboardMarkup(row_width=2)

main_menu_for_super_admin.add(InlineKeyboardButton(text="➕ Kanal qo'shish", callback_data="add_channel"),
                              InlineKeyboardButton(text="➖ Kanal o'chirish", callback_data="del_channel"),
                              InlineKeyboardButton(text="➕ Admin qo'shish", callback_data="add_admin"),
                              InlineKeyboardButton(text="➖ Admin o'chirish", callback_data="del_admin"),
                              InlineKeyboardButton(text="➕ Post qo'shish   ", callback_data="add_post"),
                              InlineKeyboardButton(text="➕ Tugma Qo'shish", callback_data="add_keyboard"),
                              InlineKeyboardButton(text="👤 Adminlar", callback_data="admins"),
                              InlineKeyboardButton(text="📝 Adminlarga Xabar yuborish",callback_data="send_message_to_admins"),
                              InlineKeyboardButton(text="📝 Reklama Jo'natish", callback_data="send_advertisement"),
                              InlineKeyboardButton(text="📊 Statistika", callback_data="statistics"),
                              )

main_menu_for_admin = InlineKeyboardMarkup(row_width=2)

main_menu_for_admin.add(InlineKeyboardButton(text="📊 Statistika", callback_data="stat"))

back_to_main_menu = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back_to_main_menu")
        ]
    ]
)



def dates_markup(saler_manager_id):
    markup = InlineKeyboardMarkup(row_width=1)
    markup.insert(InlineKeyboardButton(text=f"✅Bugun",callback_data=f"today:{saler_manager_id}"))
    markup.insert(InlineKeyboardButton(text=f"🗓Kechangi",callback_data=f"yesterday:{saler_manager_id}"))
    return markup


def product_keyboard(deal_id,client_id):
    markup = InlineKeyboardMarkup(row_width=2)
    
    markup.insert(InlineKeyboardButton(text="🔢 Dona ➕", callback_data="add_dona"))
    markup.insert(InlineKeyboardButton(text="🔢 Dona ➖", callback_data="minus_dona"))
    
    markup.add(InlineKeyboardButton(text="❌ O'chirish 🗑", callback_data="delete"))
    markup.insert(InlineKeyboardButton(text="✅ Tayyor", callback_data="success"))
    markup.insert(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"fix_order:{deal_id}:{client_id}"))


    return markup