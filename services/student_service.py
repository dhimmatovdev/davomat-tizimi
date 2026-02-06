"""Student service - o'quvchilar biznes mantiq."""
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.models import Student
from repositories.student import StudentRepository
from repositories.class_repo import ClassRepository


class StudentService:
    """O'quvchilar bilan ishlash servisi."""
    
    def __init__(self, session: AsyncSession):
        self.student_repo = StudentRepository(session)
        self.class_repo = ClassRepository(session)
    
    async def add_student(
        self,
        class_id: int,
        full_name: str,
    ) -> tuple[Optional[Student], str]:
        """
        Yangi o'quvchi qo'shish.
        
        Returns:
            (Student, "") - muvaffaqiyatli
            (None, "error message") - xato
        """
        # Sinfni tekshirish
        class_obj = await self.class_repo.get_by_id(class_id)
        if not class_obj:
            return None, "❌ Sinf topilmadi."
        
        # Yaratish
        student = await self.student_repo.create(class_id, full_name)
        return student, ""
    
    async def remove_student(self, student_id: int) -> tuple[bool, str]:
        """
        O'quvchini o'chirish.
        
        Returns:
            (True, "") - muvaffaqiyatli
            (False, "error message") - xato
        """
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            return False, "❌ O'quvchi topilmadi."
        
        await self.student_repo.delete(student)
        return True, ""
    
    async def get_students_by_class(self, class_id: int) -> list[Student]:
        """Sinfdagi o'quvchilarni olish."""
        return await self.student_repo.get_by_class(class_id)
    
    async def transfer_student(
        self,
        student_id: int,
        to_class_id: int,
        by_user_id: int,
    ) -> tuple[bool, str]:
        """
        O'quvchini boshqa sinfga o'tkazish.
        
        Returns:
            (True, "") - muvaffaqiyatli
            (False, "error message") - xato
        """
        # O'quvchini topish
        student = await self.student_repo.get_by_id(student_id)
        if not student:
            return False, "❌ O'quvchi topilmadi."
        
        # Maqsad sinfni tekshirish
        to_class = await self.class_repo.get_by_id(to_class_id)
        if not to_class:
            return False, "❌ Maqsad sinf topilmadi."
        
        # Bir xil sinfga o'tkazish tekshiruvi
        if student.class_id == to_class_id:
            return False, "❌ O'quvchi allaqachon shu sinfda."
        
        # Transfer yaratish
        from repositories.transfer import TransferRepository
        transfer_repo = TransferRepository(self.student_repo.session)
        
        await transfer_repo.create(
            student_id=student_id,
            from_class_id=student.class_id,
            to_class_id=to_class_id,
            by_user_id=by_user_id,
        )
        
        # O'quvchini o'tkazish
        await self.student_repo.transfer_student(student, to_class_id)
        
        return True, ""
