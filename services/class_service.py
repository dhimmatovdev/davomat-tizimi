"""Class service - sinflar biznes mantiq."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.models import Class, ClassStaff
from repositories.class_repo import ClassRepository
from repositories.user import UserRepository


class ClassService:
    """Sinflar bilan ishlash servisi."""
    
    def __init__(self, session: AsyncSession):
        self.class_repo = ClassRepository(session)
        self.user_repo = UserRepository(session)
    
    async def create_class(self, name: str) -> tuple[Optional[Class], str]:
        """
        Yangi sinf yaratish.
        
        Returns:
            (Class, "") - muvaffaqiyatli
            (None, "error message") - xato
        """
        # Dublikat tekshirish
        existing = await self.class_repo.get_by_name(name)
        if existing:
            return None, f"❌ '{name}' nomli sinf allaqachon mavjud."
        
        # Yaratish
        class_obj = await self.class_repo.create(name)
        return class_obj, ""
    
    async def delete_class(self, class_id: int) -> tuple[bool, str]:
        """
        Sinfni o'chirish.
        
        Returns:
            (True, "") - muvaffaqiyatli
            (False, "error message") - xato
        """
        # Sinfni topish
        class_obj = await self.class_repo.get_by_id(class_id)
        if not class_obj:
            return False, "❌ Sinf topilmadi."
        
        # O'quvchilar tekshirish
        students_count = await self.class_repo.get_students_count(class_id)
        if students_count > 0:
            return False, f"❌ Sinfda {students_count} ta o'quvchi bor. Avval ularni boshqa sinfga o'tkazing."
        
        # O'chirish
        await self.class_repo.delete(class_obj)
        return True, ""
    
    async def get_all_classes(self) -> list[Class]:
        """Barcha sinflarni olish."""
        return await self.class_repo.get_all()
    
    async def get_class_by_id(self, class_id: int) -> Optional[Class]:
        """ID bo'yicha sinf topish."""
        return await self.class_repo.get_by_id(class_id)
    
    async def assign_staff_to_class(
        self, 
        class_id: int, 
        staff_user_id: int
    ) -> tuple[bool, str]:
        """
        Xodimni sinfga biriktirish.
        
        Returns:
            (True, "") - muvaffaqiyatli
            (False, "error message") - xato
        """
        # Sinf va xodimni tekshirish
        class_obj = await self.class_repo.get_by_id(class_id)
        if not class_obj:
            return False, "❌ Sinf topilmadi."
        
        staff_user = await self.user_repo.get_by_id(staff_user_id)
        if not staff_user:
            return False, "❌ Xodim topilmadi."
        
        if staff_user.role != "xodim":
            return False, "❌ Faqat xodimlarni sinfga biriktirish mumkin."
        
        # Allaqachon biriktirilganligini tekshirish
        existing = await self.class_repo.get_staff_assignment(class_id, staff_user_id)
        if existing:
            return False, f"❌ {staff_user.full_name} allaqachon bu sinfga biriktirilgan."
        
        # Biriktirish
        await self.class_repo.assign_staff(class_id, staff_user_id)
        return True, ""
    
    async def remove_staff_from_class(
        self, 
        class_id: int, 
        staff_user_id: int
    ) -> tuple[bool, str]:
        """
        Xodimni sinfdan olib tashlash.
        
        Returns:
            (True, "") - muvaffaqiyatli
            (False, "error message") - xato
        """
        # Biriktirilganligini tekshirish
        assignment = await self.class_repo.get_staff_assignment(class_id, staff_user_id)
        if not assignment:
            return False, "❌ Xodim bu sinfga biriktirilmagan."
        
        # Olib tashlash
        await self.class_repo.remove_staff(assignment)
        return True, ""
    
    async def get_staff_for_class(self, class_id: int) -> list[ClassStaff]:
        """Sinfga biriktirilgan xodimlarni olish."""
        return await self.class_repo.get_staff_for_class(class_id)
