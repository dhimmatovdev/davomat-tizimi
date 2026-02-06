"""Start va login handlerlari."""
import logging
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from core.db import get_session
from core.security.access import is_admin, is_staff
from services.user import UserService
from bot.keyboards.inline import (
    get_contact_share_keyboard,
    get_admin_menu_keyboard,
    get_staff_menu_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    """
    /start komandasi - foydalanuvchini kutib olish.
    """
    await state.clear()
    
    # Telefon raqamni so'rash
    await message.answer(
        "👋 Assalomu alaykum!\n\n"
        "Maktab davomat tizimiga xush kelibsiz.\n\n"
        "Davom etish uchun telefon raqamingizni ulashing.",
        reply_markup=get_contact_share_keyboard(),
    )


@router.message(F.contact)
async def handle_contact(message: Message):
    """
    Telefon raqam ulashilganda.
    """
    contact = message.contact
    
    # Faqat o'z raqamini ulashgan bo'lishi kerak
    if contact.user_id != message.from_user.id:
        await message.answer(
            "❌ Iltimos, o'z telefon raqamingizni ulashing.",
            reply_markup=get_contact_share_keyboard(),
        )
        return
    
    # Database'dan foydalanuvchini qidirish
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_or_create_user(
            telegram_id=message.from_user.id,
            phone=contact.phone_number,
            full_name=message.from_user.full_name or "Noma'lum",
        )
        
        if not user:
            await message.answer(
                "❌ Sizning telefon raqamingiz tizimda topilmadi.\n\n"
                "Iltimos, administrator bilan bog'laning.",
            )
            return
        
        if not user.is_active:
            await message.answer(
                "❌ Sizning hisobingiz faol emas.\n\n"
                "Iltimos, administrator bilan bog'laning.",
            )
            return
        
        # Role bo'yicha menu ko'rsatish
        if is_admin(user):
            await message.answer(
                f"✅ Xush kelibsiz, {user.full_name}!\n\n"
                f"Siz admin sifatida tizimga kirdingiz.",
                reply_markup=get_admin_menu_keyboard(),
            )
        elif is_staff(user):
            await message.answer(
                f"✅ Xush kelibsiz, {user.full_name}!\n\n"
                f"Siz xodim sifatida tizimga kirdingiz.",
                reply_markup=get_staff_menu_keyboard(),
            )
        else:
            await message.answer(
                "❌ Sizning rolingiz noto'g'ri.\n\n"
                "Iltimos, administrator bilan bog'laning.",
            )


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    """Asosiy menyuga qaytish."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Siz tizimda ro'yxatdan o'tmagansiz.", show_alert=True)
            return
        
        if is_admin(user):
            await callback.message.edit_text(
                f"Admin panel",
                reply_markup=get_admin_menu_keyboard(),
            )
        elif is_staff(user):
            await callback.message.edit_text(
                f"Xodim panel",
                reply_markup=get_staff_menu_keyboard(),
            )
        
        await callback.answer()
