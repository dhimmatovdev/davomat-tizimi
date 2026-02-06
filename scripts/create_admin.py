"""Birinchi admin foydalanuvchini qo'shish uchun script."""
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from core.db import get_session
from repositories.user import UserRepository
from utils.phone import normalize_phone


async def create_admin():
    """Birinchi admin yaratish."""
    print("=" * 50)
    print("BIRINCHI ADMIN YARATISH")
    print("=" * 50)
    
    # Ma'lumotlarni so'rash
    telegram_id = input("Telegram ID: ").strip()
    phone = input("Telefon raqam (masalan: +998901234567): ").strip()
    full_name = input("To'liq ism: ").strip()
    
    # Validatsiya
    if not telegram_id.isdigit():
        print("❌ Telegram ID faqat raqamlardan iborat bo'lishi kerak!")
        return
    
    telegram_id = int(telegram_id)
    phone = normalize_phone(phone)
    
    if not phone:
        print("❌ Telefon raqam noto'g'ri!")
        return
    
    if not full_name:
        print("❌ To'liq ism kiritilmagan!")
        return
    
    # Database'ga qo'shish
    async for session in get_session():
        repo = UserRepository(session)
        
        # Tekshirish
        existing = await repo.get_by_telegram_id(telegram_id)
        if existing:
            print(f"❌ Bu Telegram ID allaqachon mavjud: {existing.full_name}")
            return
        
        existing = await repo.get_by_phone(phone)
        if existing:
            print(f"❌ Bu telefon raqam allaqachon mavjud: {existing.full_name}")
            return
        
        # Yaratish
        user = await repo.create(
            telegram_id=telegram_id,
            phone=phone,
            full_name=full_name,
            role="admin",
        )
        
        print("\n✅ Admin muvaffaqiyatli yaratildi!")
        print(f"ID: {user.id}")
        print(f"Telegram ID: {user.telegram_id}")
        print(f"Telefon: {user.phone}")
        print(f"Ism: {user.full_name}")
        print(f"Role: {user.role}")


if __name__ == "__main__":
    asyncio.run(create_admin())
