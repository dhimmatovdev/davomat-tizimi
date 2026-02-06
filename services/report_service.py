"""Report service - hisobotlar biznes mantiq."""
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from repositories.attendance import AttendanceRepository
from repositories.student import StudentRepository
from repositories.class_repo import ClassRepository
from services.attendance_service import AttendanceService
from reports.generator import ReportGenerator


class ReportService:
    """Hisobotlar bilan ishlash servisi."""
    
    def __init__(self, session: AsyncSession):
        self.attendance_repo = AttendanceRepository(session)
        self.student_repo = StudentRepository(session)
        self.class_repo = ClassRepository(session)
        self.attendance_service = AttendanceService(session)
    
    async def get_daily_report(
        self,
        class_id: int,
        date_val: date,
    ) -> tuple[str, bool]:
        """
        Kunlik hisobot olish.
        
        Returns:
            (report_text, success)
        """
        # Sinfni topish
        class_obj = await self.class_repo.get_by_id(class_id)
        if not class_obj:
            return "❌ Sinf topilmadi.", False
        
        # Davomat kunini topish
        from sqlalchemy import select, and_
        from core.db.models import AttendanceDay
        
        result = await self.attendance_repo.session.execute(
            select(AttendanceDay).where(
                and_(
                    AttendanceDay.class_id == class_id,
                    AttendanceDay.date == date_val,
                )
            )
        )
        attendance_day = result.scalar_one_or_none()
        
        if not attendance_day:
            return f"❌ {date_val} sanasida davomat topilmadi.", False
        
        # Xulosa olish
        summary = await self.attendance_service.get_attendance_summary(attendance_day.id)
        
        # Hisobot yaratish
        report = ReportGenerator.generate_daily_summary(
            date_val=date_val,
            class_name=class_obj.name,
            total=summary['total'],
            present=summary['present'],
            late=summary['late'],
            absent=summary['absent'],
            not_marked=summary['not_marked'],
        )
        
        return report, True
    
    async def get_class_report(self, class_id: int) -> tuple[str, bool]:
        """
        Sinf hisoboti olish.
        
        Returns:
            (report_text, success)
        """
        # Sinfni topish
        class_obj = await self.class_repo.get_by_id(class_id)
        if not class_obj:
            return "❌ Sinf topilmadi.", False
        
        # O'quvchilar
        all_students = await self.student_repo.get_by_class(class_id, active_only=False)
        active_students = await self.student_repo.get_by_class(class_id, active_only=True)
        
        # Xodimlar
        staff_assignments = await self.class_repo.get_staff_for_class(class_id)
        staff_names = [assignment.staff_user.full_name for assignment in staff_assignments]
        
        # Hisobot yaratish
        report = ReportGenerator.generate_class_report(
            class_name=class_obj.name,
            total_students=len(all_students),
            active_students=len(active_students),
            staff_count=len(staff_assignments),
            staff_names=staff_names,
        )
        
        return report, True
