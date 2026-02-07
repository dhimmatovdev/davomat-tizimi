"""Database modellari."""
from datetime import datetime
from typing import Optional
from sqlalchemy import (
    String,
    Integer,
    BigInteger,
    Boolean,
    DateTime,
    Date,
    ForeignKey,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base


class User(Base):
    """Foydalanuvchilar jadvali."""
    
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    telegram_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False, index=True)
    phone: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(20), nullable=False)  # admin | xodim
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    class_assignments: Mapped[list["ClassStaff"]] = relationship(
        "ClassStaff", back_populates="staff_user", cascade="all, delete-orphan"
    )
    transfers_made: Mapped[list["Transfer"]] = relationship(
        "Transfer", back_populates="by_user", foreign_keys="Transfer.by_user_id"
    )


class Class(Base):
    """Sinflar jadvali."""
    
    __tablename__ = "classes"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    total_students: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    staff_assignments: Mapped[list["ClassStaff"]] = relationship(
        "ClassStaff", back_populates="class_", cascade="all, delete-orphan"
    )

# ... (Student model omitted)

class AttendanceDay(Base):
    """Davomat kunlari jadvali."""
    
    __tablename__ = "attendance_days"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    marked_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    is_finalized: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    students: Mapped[list["Student"]] = relationship(
        "Student", back_populates="class_", foreign_keys="Student.class_id"
    )
    attendance_days: Mapped[list["AttendanceDay"]] = relationship(
        "AttendanceDay", back_populates="class_", cascade="all, delete-orphan"
    )


class ClassStaff(Base):
    """Sinfga xodim biriktirish jadvali."""
    
    __tablename__ = "class_staff"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    staff_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    active_from: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    active_to: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    # Relationships
    class_: Mapped["Class"] = relationship("Class", back_populates="staff_assignments")
    staff_user: Mapped["User"] = relationship("User", back_populates="class_assignments")


class Student(Base):
    """O'quvchilar jadvali."""
    
    __tablename__ = "students"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    class_: Mapped["Class"] = relationship("Class", back_populates="students", foreign_keys=[class_id])
    attendance_items: Mapped[list["AttendanceItem"]] = relationship(
        "AttendanceItem", back_populates="student", cascade="all, delete-orphan"
    )
    transfers: Mapped[list["Transfer"]] = relationship(
        "Transfer", back_populates="student", foreign_keys="Transfer.student_id"
    )


class AttendanceDay(Base):
    """Davomat kunlari jadvali."""
    
    __tablename__ = "attendance_days"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id", ondelete="CASCADE"), nullable=False)
    date: Mapped[datetime] = mapped_column(Date, nullable=False)
    marked_by: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    class_: Mapped["Class"] = relationship("Class", back_populates="attendance_days")
    items: Mapped[list["AttendanceItem"]] = relationship(
        "AttendanceItem", back_populates="attendance_day", cascade="all, delete-orphan"
    )


class AttendanceItem(Base):
    """Davomat yozuvlari jadvali."""
    
    __tablename__ = "attendance_items"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    attendance_day_id: Mapped[int] = mapped_column(Integer, ForeignKey("attendance_days.id", ondelete="CASCADE"), nullable=False)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)  # 1=PRESENT, 2=LATE, 3=ABSENT
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    attendance_day: Mapped["AttendanceDay"] = relationship("AttendanceDay", back_populates="items")
    student: Mapped["Student"] = relationship("Student", back_populates="attendance_items")


class Transfer(Base):
    """O'quvchi transferlari jadvali."""
    
    __tablename__ = "transfers"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    student_id: Mapped[int] = mapped_column(Integer, ForeignKey("students.id", ondelete="CASCADE"), nullable=False)
    from_class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"), nullable=False)
    to_class_id: Mapped[int] = mapped_column(Integer, ForeignKey("classes.id"), nullable=False)
    transferred_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    by_user_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Relationships
    student: Mapped["Student"] = relationship("Student", back_populates="transfers", foreign_keys=[student_id])
    by_user: Mapped["User"] = relationship("User", back_populates="transfers_made", foreign_keys=[by_user_id])
