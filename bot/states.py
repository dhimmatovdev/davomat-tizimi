"""FSM states - bot holatlari."""
from aiogram.fsm.state import State, StatesGroup


class AdminStates(StatesGroup):
    """Admin FSM holatlari."""
    
    # Sinf yaratish
    waiting_class_name = State()
    
    # Xodim qo'shish
    waiting_staff_phone = State()
    waiting_staff_name = State()


class StaffStates(StatesGroup):
    """Staff FSM holatlari."""
    
    # O'quvchi qo'shish
    waiting_student_name = State()
