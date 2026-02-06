"""Staff handlerlari - placeholder."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery

from bot.keyboards.inline import get_back_button

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data == "s:menu:attendance")
async def staff_attendance_menu(callback: CallbackQuery):
    """Xodim - Bugungi davomat."""
    await callback.message.edit_text(
        "✅ Bugungi davomat\n\n"
        "Bu bo'lim keyingi fazada ishlab chiqiladi.",
        reply_markup=get_back_button("back_to_menu"),
    )
    await callback.answer()


@router.callback_query(F.data == "s:menu:students")
async def staff_students_menu(callback: CallbackQuery):
    """Xodim - O'quvchilar."""
    await callback.message.edit_text(
        "👨‍🎓 O'quvchilar\n\n"
        "Bu bo'lim keyingi fazada ishlab chiqiladi.",
        reply_markup=get_back_button("back_to_menu"),
    )
    await callback.answer()


@router.callback_query(F.data == "s:menu:transfer")
async def staff_transfer_menu(callback: CallbackQuery):
    """Xodim - Transfer."""
    await callback.message.edit_text(
        "🔄 Transfer\n\n"
        "Bu bo'lim keyingi fazada ishlab chiqiladi.",
        reply_markup=get_back_button("back_to_menu"),
    )
    await callback.answer()


@router.callback_query(F.data == "s:menu:myclass")
async def staff_myclass_menu(callback: CallbackQuery):
    """Xodim - Sinfim."""
    await callback.message.edit_text(
        "📖 Sinfim\n\n"
        "Bu bo'lim keyingi fazada ishlab chiqiladi.",
        reply_markup=get_back_button("back_to_menu"),
    )
    await callback.answer()
