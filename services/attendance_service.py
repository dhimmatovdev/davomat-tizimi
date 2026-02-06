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
    
    async def get_attendance_summary(
        self,
        attendance_day_id: int,
    ) -> dict:
        """
        Davomat xulosasi.
        
        Returns:
            {
                "total": int,
                "present": int,
                "late": int,
                "absent": int,
                "not_marked": int,
            }
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
            }
        
        # O'quvchilar soni
        students = await self.student_repo.get_by_class(attendance_day.class_id)
        total = len(students)
        
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
