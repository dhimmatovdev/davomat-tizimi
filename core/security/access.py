"""Role-based access control."""
from typing import Optional
from aiogram.types import Message, CallbackQuery
from core.config import settings
from core.db.models import User


def is_admin(user: Optional[User]) -> bool:
    """Foydalanuvchi admin ekanligini tekshirish."""
    if not user:
        return False
    return user.role == settings.ROLE_ADMIN and user.is_active


def is_staff(user: Optional[User]) -> bool:
    """Foydalanuvchi xodim ekanligini tekshirish."""
    if not user:
        return False
    return user.role == settings.ROLE_STAFF and user.is_active


def has_access(user: Optional[User]) -> bool:
    """Foydalanuvchi tizimga kirish huquqiga ega ekanligini tekshirish."""
    if not user:
        return False
    return user.is_active and user.role in [settings.ROLE_ADMIN, settings.ROLE_STAFF]


async def check_admin_access(user: Optional[User]) -> tuple[bool, str]:
    """Admin huquqini tekshirish va xabar qaytarish."""
    if not user:
        return False, "❌ Siz tizimda ro'yxatdan o'tmagansiz."
    
    if not user.is_active:
        return False, "❌ Sizning hisobingiz faol emas."
    
    if not is_admin(user):
        return False, "❌ Sizda bu amalni bajarish uchun ruxsat yo'q."
    
    return True, ""


async def check_staff_access(user: Optional[User]) -> tuple[bool, str]:
    """Xodim huquqini tekshirish va xabar qaytarish."""
    if not user:
        return False, "❌ Siz tizimda ro'yxatdan o'tmagansiz."
    
    if not user.is_active:
        return False, "❌ Sizning hisobingiz faol emas."
    
    if not is_staff(user) and not is_admin(user):
        return False, "❌ Sizda bu amalni bajarish uchun ruxsat yo'q."
    
    return True, ""
