"""Inline keyboard builderlar."""
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder


def get_contact_share_keyboard() -> ReplyKeyboardMarkup:
    """Telefon raqamni ulashish uchun keyboard."""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="📱 Raqamni ulashish", request_contact=True))
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def get_admin_menu_keyboard() -> InlineKeyboardMarkup:
    """Admin asosiy menyu."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📚 Sinflar", callback_data="a:menu:classes"),
        InlineKeyboardButton(text="👥 Xodimlar", callback_data="a:menu:staff"),
    )
    builder.row(
        InlineKeyboardButton(text="📊 Hisobotlar", callback_data="a:menu:reports"),
        InlineKeyboardButton(text="👨‍💼 Adminlar", callback_data="a:menu:admins"),
    )
    builder.row(
        InlineKeyboardButton(text="⚙️ Sozlamalar", callback_data="a:menu:settings"),
    )
    return builder.as_markup()


def get_staff_menu_keyboard() -> InlineKeyboardMarkup:
    """Xodim asosiy menyu."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="✅ Bugungi davomat", callback_data="s:menu:attendance"),
    )
    builder.row(
        InlineKeyboardButton(text="👨‍🎓 O'quvchilar", callback_data="s:menu:students"),
        InlineKeyboardButton(text="🔄 Transfer", callback_data="s:menu:transfer"),
    )
    builder.row(
        InlineKeyboardButton(text="📖 Sinfim", callback_data="s:menu:myclass"),
    )
    return builder.as_markup()


def get_back_button(callback_data: str = "back") -> InlineKeyboardMarkup:
    """Orqaga qaytish tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="◀️ Orqaga", callback_data=callback_data))
    return builder.as_markup()


def get_cancel_keyboard() -> InlineKeyboardMarkup:
    """Bekor qilish tugmasi."""
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="cancel"))
    return builder.as_markup()


def get_classes_list_keyboard(classes: list, show_create: bool = True) -> InlineKeyboardMarkup:
    """Sinflar ro'yxati keyboard."""
    builder = InlineKeyboardBuilder()
    
    # Sinflar ro'yxati
    for class_obj in classes:
        builder.add(InlineKeyboardButton(
            text=f"📚 {class_obj.name}",
            callback_data=f"a:cls:{class_obj.id}"
        ))
    
    # 2 ta ustun
    builder.adjust(2)
    
    # Yangi sinf yaratish tugmasi
    if show_create:
        builder.row(
            InlineKeyboardButton(text="➕ Yangi sinf", callback_data="a:cls:create")
        )
    
    # Orqaga
    builder.row(
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


def get_class_actions_keyboard(class_id: int) -> InlineKeyboardMarkup:
    """Sinf harakatlari keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="👥 Xodim biriktirish", callback_data=f"a:cls:{class_id}:staff")
    )
    builder.row(
        InlineKeyboardButton(text="📊 Excel yuklab olish", callback_data=f"a:cls:{class_id}:excel")
    )
    builder.row(
        InlineKeyboardButton(text="🗑 O'chirish", callback_data=f"a:cls:{class_id}:delete")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="a:cls:list")
    )
    
    return builder.as_markup()


def get_confirm_keyboard(callback_yes: str, callback_no: str = "cancel") -> InlineKeyboardMarkup:
    """Tasdiqlash keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="✅ Ha", callback_data=callback_yes),
        InlineKeyboardButton(text="❌ Yo'q", callback_data=callback_no),
    )
    
    return builder.as_markup()


def get_staff_list_keyboard(staff_list: list, class_id: int) -> InlineKeyboardMarkup:
    """Xodimlar ro'yxati keyboard (sinfga biriktirish uchun)."""
    builder = InlineKeyboardBuilder()
    
    for staff in staff_list:
        builder.add(InlineKeyboardButton(
            text=f"👤 {staff.full_name}",
            callback_data=f"a:cls:{class_id}:staff:{staff.id}"
        ))
    
    builder.adjust(1)
    
    builder.row(
        InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"a:cls:{class_id}")
    )
    
    return builder.as_markup()


def get_assigned_staff_keyboard(staff_assignments: list, class_id: int) -> InlineKeyboardMarkup:
    """Sinfga biriktirilgan xodimlar ro'yxati."""
    builder = InlineKeyboardBuilder()
    
    for assignment in staff_assignments:
        builder.add(InlineKeyboardButton(
            text=f"👤 {assignment.staff_user.full_name}",
            callback_data=f"a:staff:{class_id}:remove:{assignment.staff_user_id}"
        ))
    
    builder.adjust(1)
    
    builder.row(
        InlineKeyboardButton(text="◀️ Orqaga", callback_data=f"a:cls:{class_id}")
    )
    
    return builder.as_markup()


def get_staff_classes_keyboard(class_assignments: list, prefix: str = "s:att") -> InlineKeyboardMarkup:
    """Xodimning sinflari keyboard."""
    builder = InlineKeyboardBuilder()
    
    for assignment in class_assignments:
        builder.add(InlineKeyboardButton(
            text=f"📚 {assignment.class_.name}",
            callback_data=f"{prefix}:class:{assignment.class_id}"
        ))
    
    builder.adjust(2)
    
    builder.row(
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


def get_students_attendance_keyboard(
    students_data: list,
    attendance_day_id: int,
    class_id: int,
) -> InlineKeyboardMarkup:
    """O'quvchilar davomat keyboard."""
    builder = InlineKeyboardBuilder()
    
    for data in students_data:
        student = data["student"]
        emoji = data["status_emoji"]
        
        builder.add(InlineKeyboardButton(
            text=f"{emoji} {student.full_name}",
            callback_data=f"s:att:{class_id}:{student.id}"
        ))
    
    builder.adjust(1)
    
    # Xulosa tugmasi
    builder.row(
        InlineKeyboardButton(
            text="📊 Xulosa",
            callback_data=f"s:att:{class_id}:summary"
        )
    )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="s:menu:attendance")
    )
    
    return builder.as_markup()


def get_attendance_status_keyboard(
    attendance_day_id: int,
    student_id: int,
    class_id: int,
) -> InlineKeyboardMarkup:
    """Status tanlash keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="✅ Keldi",
            callback_data=f"s:att:set:{attendance_day_id}:{student_id}:1"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🟡 Kechikdi",
            callback_data=f"s:att:set:{attendance_day_id}:{student_id}:2"
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="❌ Kelmadi",
            callback_data=f"s:att:set:{attendance_day_id}:{student_id}:3"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data=f"s:att:{class_id}:list"
        )
    )
    
    return builder.as_markup()


def get_students_list_keyboard(
    students: list,
    class_id: int,
    show_add: bool = True,
) -> InlineKeyboardMarkup:
    """O'quvchilar ro'yxati keyboard."""
    builder = InlineKeyboardBuilder()
    
    for student in students:
        builder.add(InlineKeyboardButton(
            text=f"👤 {student.full_name}",
            callback_data=f"s:students:{student.id}:actions"
        ))
    
    builder.adjust(1)
    
    if show_add:
        builder.row(
            InlineKeyboardButton(
                text="➕ Yangi o'quvchi",
                callback_data=f"s:students:{class_id}:add"
            )
        )
    
    builder.row(
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="s:menu:students")
    )
    
    return builder.as_markup()


def get_student_actions_keyboard(student_id: int) -> InlineKeyboardMarkup:
    """O'quvchi harakatlari keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(
            text="🗑 O'chirish",
            callback_data=f"s:students:{student_id}:delete"
        )
    )
    
    builder.row(
        InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data="s:students:back"
        )
    )
    
    return builder.as_markup()


def get_transfer_students_keyboard(
    students: list,
    class_id: int,
) -> InlineKeyboardMarkup:
    """Transfer uchun o'quvchilar ro'yxati."""
    builder = InlineKeyboardBuilder()
    
    for student in students:
        builder.add(InlineKeyboardButton(
            text=f"👤 {student.full_name}",
            callback_data=f"s:transfer:{class_id}:student:{student.id}"
        ))
    
    builder.adjust(1)
    
    builder.row(
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="s:menu:transfer")
    )
    
    return builder.as_markup()


def get_transfer_target_classes_keyboard(
    classes: list,
    student_id: int,
    current_class_id: int,
) -> InlineKeyboardMarkup:
    """Transfer maqsad sinflar keyboard."""
    builder = InlineKeyboardBuilder()
    
    for class_obj in classes:
        # Joriy sinfni chiqarib tashlash
        if class_obj.id == current_class_id:
            continue
        
        builder.add(InlineKeyboardButton(
            text=f"📚 {class_obj.name}",
            callback_data=f"s:transfer:{student_id}:to:{class_obj.id}"
        ))
    
    builder.adjust(2)
    
    builder.row(
        InlineKeyboardButton(
            text="◀️ Orqaga",
            callback_data="s:menu:transfer"
        )
    )
    
    return builder.as_markup()


def get_reports_menu_keyboard() -> InlineKeyboardMarkup:
    """Hisobotlar menyusi keyboard."""
    builder = InlineKeyboardBuilder()
    
    builder.row(
        InlineKeyboardButton(text="📅 Bugungi hisobot", callback_data="a:reports:daily")
    )
    builder.row(
        InlineKeyboardButton(text="📚 Sinf hisoboti", callback_data="a:reports:classes")
    )
    builder.row(
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_menu")
    )
    
    return builder.as_markup()


def get_report_classes_keyboard(classes: list) -> InlineKeyboardMarkup:
    """Hisobot uchun sinflar keyboard."""
    builder = InlineKeyboardBuilder()
    
    for class_obj in classes:
        builder.add(InlineKeyboardButton(
            text=f"📚 {class_obj.name}",
            callback_data=f"a:reports:class:{class_obj.id}"
        ))
    
    builder.adjust(2)
    
    builder.row(
        InlineKeyboardButton(text="◀️ Orqaga", callback_data="a:menu:reports")
    )
    
    return builder.as_markup()
