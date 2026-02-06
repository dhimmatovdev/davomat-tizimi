"""Class repository - sinflar bilan ishlash."""
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from core.db.models import Class, ClassStaff, Student


class ClassRepository:
    """Sinflar CRUD operatsiyalari."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_all(self) -> list[Class]:
        """Barcha sinflarni olish."""
        result = await self.session.execute(
            select(Class).order_by(Class.name)
        )
        return list(result.scalars().all())
    
    async def get_by_id(self, class_id: int) -> Optional[Class]:
        """ID bo'yicha sinf topish."""
        result = await self.session.execute(
            select(Class).where(Class.id == class_id)
        )
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str) -> Optional[Class]:
        """Nom bo'yicha sinf topish."""
        result = await self.session.execute(
            select(Class).where(Class.name == name)
        )
        return result.scalar_one_or_none()
    
    async def create(self, name: str) -> Class:
        """Yangi sinf yaratish."""
        class_obj = Class(name=name)
        self.session.add(class_obj)
        await self.session.commit()
        await self.session.refresh(class_obj)
        return class_obj
    
    async def delete(self, class_obj: Class) -> None:
        """Sinfni o'chirish."""
        await self.session.delete(class_obj)
        await self.session.commit()
    
    async def get_staff_for_class(self, class_id: int) -> list[ClassStaff]:
        """Sinfga biriktirilgan xodimlarni olish (faol)."""
        result = await self.session.execute(
            select(ClassStaff)
            .options(selectinload(ClassStaff.staff_user))
            .where(
                and_(
                    ClassStaff.class_id == class_id,
                    ClassStaff.active_to.is_(None)
                )
            )
        )
        return list(result.scalars().all())
    
    async def get_students_count(self, class_id: int) -> int:
        """Sinfdagi o'quvchilar sonini olish."""
        result = await self.session.execute(
            select(Student).where(
                and_(
                    Student.class_id == class_id,
                    Student.is_active == True
                )
            )
        )
        return len(list(result.scalars().all()))
    
    async def assign_staff(self, class_id: int, staff_user_id: int) -> ClassStaff:
        """Xodimni sinfga biriktirish."""
        class_staff = ClassStaff(
            class_id=class_id,
            staff_user_id=staff_user_id,
        )
        self.session.add(class_staff)
        await self.session.commit()
        await self.session.refresh(class_staff)
        return class_staff
    
    async def remove_staff(self, class_staff: ClassStaff) -> None:
        """Xodimni sinfdan olib tashlash."""
        from datetime import datetime
        class_staff.active_to = datetime.utcnow()
        await self.session.commit()
    
    async def get_staff_assignment(
        self, 
        class_id: int, 
        staff_user_id: int
    ) -> Optional[ClassStaff]:
        """Xodimning sinfga biriktirilganligini tekshirish."""
        result = await self.session.execute(
            select(ClassStaff).where(
                and_(
                    ClassStaff.class_id == class_id,
                    ClassStaff.staff_user_id == staff_user_id,
                    ClassStaff.active_to.is_(None)
                )
            )
        )
        return result.scalar_one_or_none()
