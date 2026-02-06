"""Admin handlerlari - placeholder."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.inline import get_back_button

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "a:menu:classes")
async def admin_classes_menu(callback: CallbackQuery):
    """Admin - Sinflar menyusi."""
    await callback.message.edit_text(
        "📚 Sinflar boshqaruvi\n\n"
        "Bu bo'lim keyingi fazada ishlab chiqiladi.",
        reply_markup=get_back_button("back_to_menu"),
    )
    await callback.answer()


@router.callback_query(F.data == "a:menu:staff")
async def admin_staff_menu(callback: CallbackQuery):
    """Admin - Xodimlar menyusi."""
    await callback.message.edit_text(
        "👥 Xodimlar boshqaruvi\n\n"
        "Bu bo'lim keyingi fazada ishlab chiqiladi.",
        reply_markup=get_back_button("back_to_menu"),
    )
    await callback.answer()


@router.callback_query(F.data == "a:menu:reports")
async def admin_reports_menu(callback: CallbackQuery):
    """Admin - Hisobotlar menyusi."""
    await callback.message.edit_text(
        "📊 Hisobotlar\n\n"
        "Bu bo'lim keyingi fazada ishlab chiqiladi.",
        reply_markup=get_back_button("back_to_menu"),
    )
    await callback.answer()


@router.callback_query(F.data == "a:menu:settings")
async def admin_settings_menu(callback: CallbackQuery):
    """Admin - Sozlamalar menyusi."""
    await callback.message.edit_text(
        "⚙️ Sozlamalar\n\n"
        "Bu bo'lim keyingi fazada ishlab chiqiladi.",
        reply_markup=get_back_button("back_to_menu"),
    )
    await callback.answer()
