"""Student repository - o'quvchilar bilan ishlash."""
from typing import Optional
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.models import Student


class StudentRepository:
    """O'quvchilar CRUD operatsiyalari."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_by_class(self, class_id: int, active_only: bool = True) -> list[Student]:
        """Sinfdagi o'quvchilarni olish."""
        query = select(Student).where(Student.class_id == class_id)
        
        if active_only:
            query = query.where(Student.is_active == True)
        
        query = query.order_by(Student.full_name)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
    
    async def get_by_id(self, student_id: int) -> Optional[Student]:
        """ID bo'yicha o'quvchini topish."""
        result = await self.session.execute(
            select(Student).where(Student.id == student_id)
        )
        return result.scalar_one_or_none()
    
    async def create(self, class_id: int, full_name: str) -> Student:
        """Yangi o'quvchi yaratish."""
        student = Student(
            class_id=class_id,
            full_name=full_name,
            is_active=True,
        )
        self.session.add(student)
        await self.session.commit()
        await self.session.refresh(student)
        return student
    
    async def delete(self, student: Student) -> None:
        """O'quvchini o'chirish (soft delete)."""
        student.is_active = False
        await self.session.commit()
    
    async def transfer_student(self, student: Student, to_class_id: int) -> None:
        """O'quvchini boshqa sinfga o'tkazish."""
        student.class_id = to_class_id
        await self.session.commit()
