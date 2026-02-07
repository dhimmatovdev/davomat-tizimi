from sqlalchemy import select, and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload
from core.db.models import AttendanceDay, AttendanceItem, Student


class AttendanceRepository:
    """Davomat CRUD operatsiyalari."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def get_or_create_attendance_day(
        self,
        class_id: int,
        date_val: date,
        marked_by: int,
    ) -> AttendanceDay:
        """Davomat kunini olish yoki yaratish."""
        # Avval qidirish
        result = await self.session.execute(
            select(AttendanceDay)
            .options(joinedload(AttendanceDay.class_))  # Class ma'lumotlarini yuklash
            .where(
                and_(
                    AttendanceDay.class_id == class_id,
                    AttendanceDay.date == date_val,
                )
            )
        )
        attendance_day = result.scalar_one_or_none()
        
        if attendance_day:
            return attendance_day
        
        # Yaratish
        attendance_day = AttendanceDay(
            class_id=class_id,
            date=date_val,
            marked_by=marked_by,
        )
        self.session.add(attendance_day)
        await self.session.commit()
        await self.session.refresh(attendance_day, ["class_"])
        return attendance_day
    
    async def get_attendance_items(
        self,
        attendance_day_id: int,
    ) -> list[AttendanceItem]:
        """Davomat yozuvlarini olish."""
        result = await self.session.execute(
            select(AttendanceItem)
            .options(selectinload(AttendanceItem.student))
            .where(AttendanceItem.attendance_day_id == attendance_day_id)
        )
        return list(result.scalars().all())
    
    async def get_attendance_item(
        self,
        attendance_day_id: int,
        student_id: int,
    ) -> Optional[AttendanceItem]:
        """Bitta davomat yozuvini olish."""
        result = await self.session.execute(
            select(AttendanceItem).where(
                and_(
                    AttendanceItem.attendance_day_id == attendance_day_id,
                    AttendanceItem.student_id == student_id,
                )
            )
        )
        return result.scalar_one_or_none()
        
    async def get_items_count(self, attendance_day_id: int) -> int:
        """Davomat yozuvlari sonini olish."""
        result = await self.session.execute(
            select(func.count())
            .select_from(AttendanceItem)
            .where(AttendanceItem.attendance_day_id == attendance_day_id)
        )
        return result.scalar() or 0
    
    async def set_attendance_status(
        self,
        attendance_day_id: int,
        student_id: int,
        status: int,
    ) -> AttendanceItem:
        """O'quvchi statusini belgilash."""
        # Avval mavjudligini tekshirish
        item = await self.get_attendance_item(attendance_day_id, student_id)
        
        if item:
            # Yangilash
            item.status = status
            item.updated_at = datetime.utcnow()
        else:
            # Yaratish
            item = AttendanceItem(
                attendance_day_id=attendance_day_id,
                student_id=student_id,
                status=status,
            )
            self.session.add(item)
        
        await self.session.commit()
        await self.session.refresh(item)
        return item
    
    async def get_attendance_day_by_id(
        self,
        attendance_day_id: int,
    ) -> Optional[AttendanceDay]:
        """Davomat kunini ID bo'yicha olish (sinf ma'lumotlari bilan)."""
        result = await self.session.execute(
            select(AttendanceDay)
            .options(joinedload(AttendanceDay.class_))
            .where(AttendanceDay.id == attendance_day_id)
        )
        return result.scalar_one_or_none()
        
    async def update_finalized_status(
        self,
        attendance_day_id: int,
        is_finalized: bool,
    ) -> None:
        """Finalized statusini yangilash."""
        attendance_day = await self.get_attendance_day_by_id(attendance_day_id)
        if attendance_day:
            attendance_day.is_finalized = is_finalized
            await self.session.commit()

