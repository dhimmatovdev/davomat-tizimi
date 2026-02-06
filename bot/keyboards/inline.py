"""Inline keyboard builderlar."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_contact_share_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni ulashish uchun keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📱 Raqamni ulashish", request_contact=True))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Admin asosiy menyu."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📚 Sinflar", callback_data="a:menu:classes"),
        InlineKeyboardButton(text="👥 Xodimlar", callback_data="a:menu:staff"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Hisobotlar", callback_data="a:menu:reports"),
        InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="a:menu:settings"),
    )
    return builder.as_markup()


def get_staff_menu_keyboard() -> InlineKeyboardMarkup:
    """Xodim asosiy menyu."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Bugungi davomat", callback_data="s:menu:attendance"),
    )
    builder.row(
        InlineKeyboardButton(text="👨‍🎓 O'quvchilar", callback_data="s:menu:students"),
        InlineKeyboardButton(text="🔄 Transfer", callback_data="s:menu:transfer"),
    )
    builder.row(
        InlineKeyboardButton(text="📖 Sinfim", callback_data="s:menu:myclass"),
    )
    return builder.as_markup()


def get_back_button(callback_data: str = "back") -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="◀️ Orqaga", callback_data=callback_data))
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Bekor qilish tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"))
    return builder.as_markup()
