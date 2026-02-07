"""Attendance service - davomat biznes mantiq."""
from typing import Optional
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from core.db.models import AttendanceDay, AttendanceItem, Student
from core.config import settings
from repositories.attendance import AttendanceRepository
from repositories.student import StudentRepository


class AttendanceService:
    """Davomat bilan ishlash servisi."""
    
    def __init__(self, session: AsyncSession):
        self.attendance_repo = AttendanceRepository(session)
        self.student_repo = StudentRepository(session)
    
    async def get_today_attendance(
        self,
        class_id: int,
        user_id: int,
    ) -> tuple[Optional[AttendanceDay], list[dict]]:
        """
        Bugungi davomat olish.
        
        Returns:
            (AttendanceDay, [student_data]) - muvaffaqiyatli
            student_data = {
                "student": Student,
                "status": int | None,
                "status_text": str,
                "status_emoji": str,
            }
        """
        today = date.today()
        
        # Davomat kunini olish yoki yaratish
        attendance_day = await self.attendance_repo.get_or_create_attendance_day(
            class_id=class_id,
            date_val=today,
            marked_by=user_id,
        )
        
        # O'quvchilarni olish
        students = await self.student_repo.get_by_class(class_id)
        
        # Davomat yozuvlarini olish
        items = await self.attendance_repo.get_attendance_items(attendance_day.id)
        items_dict = {item.student_id: item for item in items}
        
        # Natijani tayyorlash
        result = []
        for student in students:
            item = items_dict.get(student.id)
            status = item.status if item else None
            
            result.append({
                "student": student,
                "status": status,
                "status_text": self._get_status_text(status),
                "status_emoji": self._get_status_emoji(status),
            })
        
        return attendance_day, result
    
    async def mark_attendance(
        self,
        attendance_day_id: int,
        student_id: int,
        status: int,
    ) -> tuple[bool, str]:
        """
        Davomat belgilash.
        
        Returns:
            (True, "") - muvaffaqiyatli
            (False, "error message") - xato
        """
        # Finalized statusini tekshirish
        day = await self.attendance_repo.get_attendance_day_by_id(attendance_day_id)
        if day and day.is_finalized:
            return False, "🔒 Davomat allaqachon yakunlangan. O'zgartirish mumkin emas."

        # Statusni tekshirish
        if status not in [settings.STATUS_PRESENT, settings.STATUS_LATE, settings.STATUS_ABSENT]:
            return False, "❌ Noto'g'ri status."
        
        # Belgilash
        await self.attendance_repo.set_attendance_status(
            attendance_day_id=attendance_day_id,
            student_id=student_id,
            status=status,
        )
        
        return True, ""
    
    async def validate_attendance(self, attendance_day_id: int) -> tuple[bool, str]:
        """
        Davomat to'liqligini tekshirish.
        
        Returns:
            (True, "") - valid
            (False, error) - invalid
        """
        day = await self.attendance_repo.get_attendance_day_by_id(attendance_day_id)
        if not day:
            return False, "Davomat kuni topilmadi."
            
        # Class total students
        total_students = day.class_.total_students
        
        # Marked students count
        marked_count = await self.attendance_repo.get_items_count(attendance_day_id)
        
        if marked_count != total_students:
            diff = total_students - marked_count
            return False, f"❌ Davomat to'liq emas! {diff} ta o'quvchi belgilanmagan ({marked_count}/{total_students})."
            
        return True, ""

    async def finalize_attendance(self, attendance_day_id: int) -> tuple[bool, str]:
        """Davomatni yakunlash (lock)."""
        # Validate
        is_valid, error = await self.validate_attendance(attendance_day_id)
        if not is_valid:
            return False, error
            
        # Finalize
        await self.attendance_repo.update_finalized_status(attendance_day_id, True)
        return True, ""

    async def reopen_attendance(self, attendance_day_id: int) -> tuple[bool, str]:
        """Davomatni qayta ochish (faqat admin)."""
        await self.attendance_repo.update_finalized_status(attendance_day_id, False)
        return True, ""

    async def get_attendance_summary(
        self,
        attendance_day_id: int,
    ) -> dict:
        """
        Davomat xulosasi.
        """
        # Davomat kunini olish
        attendance_day = await self.attendance_repo.get_attendance_day_by_id(attendance_day_id)
        if not attendance_day:
            return {
                "total": 0,
                "present": 0,
                "late": 0,
                "absent": 0,
                "not_marked": 0,
                "is_finalized": False,
            }
        
        # O'quvchilar soni (DB dan)
        total = attendance_day.class_.total_students
        
        # Davomat yozuvlari
        items = await self.attendance_repo.get_attendance_items(attendance_day_id)
        
        present = sum(1 for item in items if item.status == settings.STATUS_PRESENT)
        late = sum(1 for item in items if item.status == settings.STATUS_LATE)
        absent = sum(1 for item in items if item.status == settings.STATUS_ABSENT)
        not_marked = total - len(items)
        
        return {
            "total": total,
            "present": present,
            "late": late,
            "absent": absent,
            "not_marked": not_marked,
            "is_finalized": attendance_day.is_finalized,
        }
    
    def _get_status_text(self, status: Optional[int]) -> str:
        """Status matnini olish."""
        if status is None:
            return "Belgilanmagan"
        elif status == settings.STATUS_PRESENT:
            return "Keldi"
        elif status == settings.STATUS_LATE:
            return "Kechikdi"
        elif status == settings.STATUS_ABSENT:
            return "Kelmadi"
        else:
            return "Noma'lum"
    
    def _get_status_emoji(self, status: Optional[int]) -> str:
        """Status emoji olish."""
        if status is None:
            return "⚪"
        elif status == settings.STATUS_PRESENT:
            return "✅"
        elif status == settings.STATUS_LATE:
            return "🟡"
        elif status == settings.STATUS_ABSENT:
            return "❌"
        else:
            return "❓"

