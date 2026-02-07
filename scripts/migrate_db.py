import asyncio
import logging
from sqlalchemy import text
from core.db import engine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate():
    """Manual migration to add new columns."""
    async with engine.begin() as conn:
        # 1. Add total_students to classes
        try:
            logger.info("Adding total_students to classes...")
            await conn.execute(text("ALTER TABLE classes ADD COLUMN total_students INTEGER NOT NULL DEFAULT 0"))
            logger.info("total_students added.")
        except Exception as e:
            logger.warning(f"Failed to add total_students (maybe exists): {e}")

        # 2. Add is_finalized to attendance_days
        try:
            logger.info("Adding is_finalized to attendance_days...")
            await conn.execute(text("ALTER TABLE attendance_days ADD COLUMN is_finalized BOOLEAN NOT NULL DEFAULT 0"))
            logger.info("is_finalized added.")
        except Exception as e:
            logger.warning(f"Failed to add is_finalized (maybe exists): {e}")

        # 3. Populate total_students
        try:
            logger.info("Populating total_students from existing students count...")
            await conn.execute(text("UPDATE classes SET total_students = (SELECT COUNT(*) FROM students WHERE students.class_id = classes.id AND students.is_active = 1)"))
            logger.info("total_students populated.")
        except Exception as e:
            logger.error(f"Failed to populate total_students: {e}")


if __name__ == "__main__":
    asyncio.run(migrate())
