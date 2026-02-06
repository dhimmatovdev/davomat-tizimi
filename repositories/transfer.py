"""Transfer repository - transfer bilan ishlash."""
from typing import Optional
from datetime import datetime
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from core.db.models import Transfer


class TransferRepository:
    """Transfer CRUD operatsiyalari."""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(
        self,
        student_id: int,
        from_class_id: int,
        to_class_id: int,
        by_user_id: int,
    ) -> Transfer:
        """Yangi transfer yaratish."""
        transfer = Transfer(
            student_id=student_id,
            from_class_id=from_class_id,
            to_class_id=to_class_id,
            by_user_id=by_user_id,
            transferred_at=datetime.utcnow(),
        )
        self.session.add(transfer)
        await self.session.commit()
        await self.session.refresh(transfer)
        return transfer
    
    async def get_by_student(self, student_id: int) -> list[Transfer]:
        """O'quvchi transferlarini olish."""
        result = await self.session.execute(
            select(Transfer)
            .options(
                selectinload(Transfer.from_class),
                selectinload(Transfer.to_class),
                selectinload(Transfer.by_user),
            )
            .where(Transfer.student_id == student_id)
            .order_by(Transfer.transferred_at.desc())
        )
        return list(result.scalars().all())
