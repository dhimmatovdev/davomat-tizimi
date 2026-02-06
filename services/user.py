"""User service - foydalanuvchilar bilan ishlash biznes mantigi."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.models import User
from repositories.user import UserRepository
from utils.phone import normalize_phone


class UserService:
    """Foydalanuvchilar bilan ishlash servisi."""
    
    def __init__(self, session: AsyncSession):
        self.repo = UserRepository(session)
    
    async def get_or_create_user(
        self,
        telegram_id: int,
        phone: str,
        full_name: str,
    ) -> Optional[User]:
        """
        Foydalanuvchini topish yoki yangi yaratish.
        Agar telefon raqam bazada bo'lsa, foydalanuvchini qaytaradi.
        Agar yo'q bo'lsa, None qaytaradi (admin qo'lda qo'shishi kerak).
        """
        # Telefon raqamni normalizatsiya qilish
        normalized_phone = normalize_phone(phone)
        
        # Avval telegram_id bo'yicha qidirish
        user = await self.repo.get_by_telegram_id(telegram_id)
        if user:
            return user
        
        # Telefon raqam bo'yicha qidirish
        user = await self.repo.get_by_phone(normalized_phone)
        if user:
            # Telegram ID ni yangilash
            user.telegram_id = telegram_id
            user.full_name = full_name
            return await self.repo.update(user)
        
        # Foydalanuvchi topilmadi
        return None
    
    async def create_user(
        self,
        telegram_id: int,
        phone: str,
        full_name: str,
        role: str,
    ) -> User:
        """Yangi foydalanuvchi yaratish (faqat admin)."""
        normalized_phone = normalize_phone(phone)
        return await self.repo.create(
            telegram_id=telegram_id,
            phone=normalized_phone,
            full_name=full_name,
            role=role,
        )
    
    async def get_user_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Telegram ID bo'yicha foydalanuvchini topish."""
        return await self.repo.get_by_telegram_id(telegram_id)
