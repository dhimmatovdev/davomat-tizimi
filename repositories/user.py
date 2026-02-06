"""User repository - foydalanuvchilar bilan ishlash."""
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.models import User


class UserRepository:
    """Foydalanuvchilar CRUD operatsiyalari."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_telegram_id(self, telegram_id: int) -> Optional[User]:
        """Telegram ID bo'yicha foydalanuvchini topish."""
        result = await self.session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_phone(self, phone: str) -> Optional[User]:
        """Telefon raqam bo'yicha foydalanuvchini topish."""
        result = await self.session.execute(
            select(User).where(User.phone == phone)
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, user_id: int) -> Optional[User]:
        """ID bo'yicha foydalanuvchini topish."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def create(
        self,
        telegram_id: int,
        phone: Optional[str],
        full_name: str,
        role: str,
    ) -> User:
        """Yangi foydalanuvchi yaratish."""
        user = User(
            telegram_id=telegram_id,
            phone=phone,
            full_name=full_name,
            role=role,
            is_active=True,
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def update(self, user: User) -> User:
        """Foydalanuvchini yangilash."""
        await self.session.commit()
        await self.session.refresh(user)
        return user
    
    async def get_all_staff(self) -> list[User]:
        """Barcha xodimlarni olish."""
        result = await self.session.execute(
            select(User).where(User.role == "xodim", User.is_active == True)
        )
        return list(result.scalars().all())
    
    async def get_all_admins(self) -> list[User]:
        """Barcha adminlarni olish."""
        result = await self.session.execute(
            select(User).where(User.role == "admin", User.is_active == True)
        )
        return list(result.scalars().all())
