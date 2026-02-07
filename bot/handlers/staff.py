"""Staff handlerlari - to'liq versiya."""
import logging
from datetime import date
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from core.db import get_session
from core.security.access import check_staff_access
from services.user import UserService
from services.class_service import ClassService
from services.attendance_service import AttendanceService
from services.student_service import StudentService
from utils.dates import format_date, get_weekday_name
from bot.states import StaffStates
from bot.keyboards.inline import (
    get_back_button,
    get_staff_classes_keyboard,
    get_students_attendance_keyboard,
    get_attendance_status_keyboard,
    get_staff_classes_keyboard,
    get_students_list_keyboard,
    get_student_actions_keyboard,
    get_transfer_students_keyboard,
    get_transfer_target_classes_keyboard,
    get_confirm_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()


# ============= DAVOMAT =============

@router.callback_query(F.data == "s:menu:attendance")
async def staff_attendance_menu(callback: CallbackQuery):
    """Xodim - Bugungi davomat - sinflarni tanlash."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Xodimning sinflarini olish
        from repositories.class_repo import ClassRepository
        class_repo = ClassRepository(session)
        
        # Faol biriktirilganlarni olish
        from core.db.models import ClassStaff
        from sqlalchemy import select, and_
        
        result = await session.execute(
            select(ClassStaff).where(
                and_(
                    ClassStaff.staff_user_id == user.id,
                    ClassStaff.active_to.is_(None)
                )
            )
        )
        class_assignments = list(result.scalars().all())
        
        active_assignments = []
        for assignment in class_assignments:
            class_obj = await class_repo.get_by_id(assignment.class_id)
            if class_obj:
                assignment.class_ = class_obj
                active_assignments.append(assignment)
        
        if not active_assignments:
            await callback.message.edit_text(
                "❌ Sizga hech qanday sinf biriktirilmagan.\n\n"
                "Iltimos, administrator bilan bog'laning.",
                reply_markup=get_back_button("back_to_menu"),
            )
            await callback.answer()
            return
        
        today = date.today()
        weekday = get_weekday_name(today.weekday())
        date_str = format_date(today)
        
        await callback.message.edit_text(
            f"✅ Bugungi davomat\n\n"
            f"📅 {weekday}, {date_str}\n\n"
            f"Sinfni tanlang:",
            reply_markup=get_staff_classes_keyboard(active_assignments),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:att:class:(\d+)$"))
async def staff_select_class(callback: CallbackQuery):
    """Sinf tanlash va o'quvchilar ro'yxatini ko'rsatish."""
    class_id = int(callback.data.split(":")[-1])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Sinfni tekshirish
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        if not class_obj:
            await callback.answer("❌ Sinf topilmadi.", show_alert=True)
            return
        
        # Davomat olish
        attendance_service = AttendanceService(session)
        attendance_day, students_data = await attendance_service.get_today_attendance(
            class_id=class_id,
            user_id=user.id,
        )
        
        if not students_data:
            await callback.message.edit_text(
                f"📚 {class_obj.name}\n\n"
                f"❌ Bu sinfda o'quvchilar yo'q.\n\n"
                f"Iltimos, administrator bilan bog'laning.",
                reply_markup=get_back_button("s:menu:attendance"),
            )
            await callback.answer()
            return
        
        today = date.today()
        weekday = get_weekday_name(today.weekday())
        date_str = format_date(today)
        
        # Xulosa
        summary = await attendance_service.get_attendance_summary(attendance_day.id)
        
        text = f"📚 {class_obj.name}\n"
        text += f"📅 {weekday}, {date_str}\n\n"
        text += f"👥 Jami: {summary['total']} ta o'quvchi\n"
        text += f"✅ Keldi: {summary['present']}\n"
        text += f"🟡 Kechikdi: {summary['late']}\n"
        text += f"❌ Kelmadi: {summary['absent']}\n"
        
        if summary['not_marked'] > 0:
            text += f"⚪ Belgilanmagan: {summary['not_marked']}\n"
        
        text += f"\n👇 O'quvchini tanlang:"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_students_attendance_keyboard(
                students_data,
                attendance_day.id,
                class_id,
            ),
        )
        await callback.answer()


@router.callback_query(F.data == "s:att:refresh")
async def staff_refresh_attendance(callback: CallbackQuery):
    """Davomat ro'yxatini yangilash."""
    # Bu callback data hozircha ishlatilmaydi
    await callback.answer("🔄 Yangilanmoqda...")


@router.callback_query(F.data.regexp(r"s:att:(\d+):list$"))
async def staff_attendance_list_back(callback: CallbackQuery):
    """O'quvchilar ro'yxatiga qaytish."""
    class_id = int(callback.data.split(":")[2])
    
    # staff_select_class kodini to'g'ridan-to'g'ri chaqirish
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Sinfni tekshirish
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        if not class_obj:
            await callback.answer("❌ Sinf topilmadi.", show_alert=True)
            return
        
        # Davomat olish
        attendance_service = AttendanceService(session)
        attendance_day, students_data = await attendance_service.get_today_attendance(
            class_id=class_id,
            user_id=user.id,
        )
        
        if not students_data:
            await callback.message.edit_text(
                f"📚 {class_obj.name}\n\n"
                f"❌ Bu sinfda o'quvchilar yo'q.\n\n"
                f"Iltimos, administrator bilan bog'laning.",
                reply_markup=get_back_button("s:menu:attendance"),
            )
            await callback.answer()
            return
        
        today = date.today()
        weekday = get_weekday_name(today.weekday())
        date_str = format_date(today)
        
        # Xulosa
        summary = await attendance_service.get_attendance_summary(attendance_day.id)
        
        text = f"📚 {class_obj.name}\n"
        text += f"📅 {weekday}, {date_str}\n\n"
        text += f"👥 Jami: {summary['total']} ta o'quvchi\n"
        text += f"✅ Keldi: {summary['present']}\n"
        text += f"🟡 Kechikdi: {summary['late']}\n"
        text += f"❌ Kelmadi: {summary['absent']}\n"
        
        if summary['not_marked'] > 0:
            text += f"⚪ Belgilanmagan: {summary['not_marked']}\n"
        
        text += f"\n👇 O'quvchini tanlang:"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_students_attendance_keyboard(
                students_data,
                attendance_day.id,
                class_id,
            ),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:att:(\d+):(\d+)$"))
async def staff_mark_attendance_select(callback: CallbackQuery):
    """O'quvchi tanlash - status belgilash."""
    parts = callback.data.split(":")
    class_id = int(parts[2])
    student_id = int(parts[3])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # O'quvchini topish
        from repositories.student import StudentRepository
        student_repo = StudentRepository(session)
        student = await student_repo.get_by_id(student_id)
        
        if not student:
            await callback.answer("❌ O'quvchi topilmadi.", show_alert=True)
            return
        
        # Davomat kunini olish
        attendance_service = AttendanceService(session)
        attendance_day, _ = await attendance_service.get_today_attendance(
            class_id=class_id,
            user_id=user.id,
        )
        
        await callback.message.edit_text(
            f"👤 {student.full_name}\n\n"
            f"Statusni tanlang:",
            reply_markup=get_attendance_status_keyboard(
                attendance_day.id,
                student_id,
                class_id,
            ),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:att:set:(\d+):(\d+):(\d+)$"))
async def staff_mark_attendance_execute(callback: CallbackQuery):
    """Status belgilash - bajarish."""
    parts = callback.data.split(":")
    attendance_day_id = int(parts[3])
    student_id = int(parts[4])
    status = int(parts[5])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Status belgilash
        attendance_service = AttendanceService(session)
        success, error = await attendance_service.mark_attendance(
            attendance_day_id=attendance_day_id,
            student_id=student_id,
            status=status,
        )
        
        if not success:
            await callback.answer(error, show_alert=True)
            return
        
        # Davomat kunini olish
        from repositories.attendance import AttendanceRepository
        attendance_repo = AttendanceRepository(session)
        attendance_day = await attendance_repo.get_attendance_day_by_id(attendance_day_id)
        
        if not attendance_day:
            await callback.answer("❌ Xato yuz berdi.", show_alert=True)
            return
        
        # Muvaffaqiyat xabari
        status_text = attendance_service._get_status_text(status)
        await callback.answer(f"✅ {status_text} deb belgilandi.")
        
        # O'quvchilar ro'yxatiga qaytish - yangi callback yaratish
        from aiogram.types import CallbackQuery as CQ
        new_callback = CQ(
            id=callback.id,
            from_user=callback.from_user,
            message=callback.message,
            chat_instance=callback.chat_instance,
            data=f"s:att:class:{attendance_day.class_id}"
        )
        await staff_select_class(new_callback)


@router.callback_query(F.data.regexp(r"s:att:(\d+):summary$"))
async def staff_attendance_summary(callback: CallbackQuery):
    """Davomat xulosasi."""
    class_id = int(callback.data.split(":")[2])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Sinfni tekshirish
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        if not class_obj:
            await callback.answer("❌ Sinf topilmadi.", show_alert=True)
            return
        
        # Davomat olish
        attendance_service = AttendanceService(session)
        attendance_day, students_data = await attendance_service.get_today_attendance(
            class_id=class_id,
            user_id=user.id,
        )
        
        # Xulosa
        summary = await attendance_service.get_attendance_summary(attendance_day.id)
        
        today = date.today()
        weekday = get_weekday_name(today.weekday())
        date_str = format_date(today)
        
        text = f"📊 Davomat Xulosasi\n\n"
        text += f"📚 Sinf: {class_obj.name}\n"
        text += f"📅 Sana: {weekday}, {date_str}\n\n"
        text += f"👥 Jami o'quvchilar: {summary['total']}\n\n"
        text += f"✅ Keldi: {summary['present']}\n"
        text += f"🟡 Kechikdi: {summary['late']}\n"
        text += f"❌ Kelmadi: {summary['absent']}\n"
        
        if summary['not_marked'] > 0:
            text += f"⚪ Belgilanmagan: {summary['not_marked']}\n"
        
        # Foizlar
        if summary['total'] > 0:
            present_percent = (summary['present'] / summary['total']) * 100
            text += f"\n📈 Kelganlar: {present_percent:.1f}%"
        
        from bot.keyboards.inline import InlineKeyboardBuilder, InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        
        # Yakunlash tugmasi (agar yakunlanmagan bo'lsa)
        if not summary.get('is_finalized', False):
            builder.row(
                InlineKeyboardButton(
                    text="🔒 Davomatni yakunlash",
                    callback_data=f"s:att:finalize:{attendance_day.id}"
                )
            )
        else:
            builder.row(
                InlineKeyboardButton(
                    text="✅ Davomat yakunlangan",
                    callback_data="noop"
                )
            )
            
        builder.row(
            InlineKeyboardButton(
                text="◀️ Orqaga",
                callback_data=f"s:att:class:{class_id}"
            )
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup(),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:att:finalize:(\d+)$"))
async def staff_finalize_attendance(callback: CallbackQuery):
    """Davomatni yakunlash."""
    attendance_day_id = int(callback.data.split(":")[-1])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        attendance_service = AttendanceService(session)
        
        # Yakunlashga urinish
        success, error = await attendance_service.finalize_attendance(attendance_day_id)
        
        if not success:
            await callback.answer(error, show_alert=True)
            return
        
        await callback.answer("✅ Davomat muvaffaqiyatli yakunlandi!", show_alert=True)
        
        # Ekranni yangilash
        day = await attendance_service.attendance_repo.get_attendance_day_by_id(attendance_day_id)
        if day:
            # Summary handlerini chaqirish uchun yangi callback yasash
            from aiogram.types import CallbackQuery as CQ
            new_callback = CQ(
                id=callback.id,
                from_user=callback.from_user,
                message=callback.message,
                chat_instance=callback.chat_instance,
                data=f"s:att:{day.class_id}:summary"
            )
            await staff_attendance_summary(new_callback)


# ============= O'QUVCHILAR =============

@router.callback_query(F.data == "s:menu:students")
async def staff_students_menu(callback: CallbackQuery):
    """Xodim - O'quvchilar - sinfni tanlash."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Xodimning sinflarini olish
        class_service = ClassService(session)
        from repositories.class_repo import ClassRepository
        class_repo = ClassRepository(session)
        
        # Faol biriktirilganlarni olish
        from core.db.models import ClassStaff
        from sqlalchemy import select, and_
        
        result = await session.execute(
            select(ClassStaff).where(
                and_(
                    ClassStaff.staff_user_id == user.id,
                    ClassStaff.active_to.is_(None)
                )
            )
        )
        class_assignments = list(result.scalars().all())
        
        active_assignments = []
        for assignment in class_assignments:
            class_obj = await class_repo.get_by_id(assignment.class_id)
            if class_obj:
                assignment.class_ = class_obj
                active_assignments.append(assignment)
        
        if not active_assignments:
            await callback.message.edit_text(
                "❌ Sizga hech qanday sinf biriktirilmagan.\n\n"
                "Iltimos, administrator bilan bog'laning.",
                reply_markup=get_back_button("back_to_menu"),
            )
            await callback.answer()
            return
        
        await callback.message.edit_text(
            "👨‍🎓 O'quvchilar\n\n"
            "Sinfni tanlang:",
            reply_markup=get_staff_classes_keyboard(active_assignments, prefix="s:students"),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:att:class:(\d+)$"))
async def staff_students_class_selected(callback: CallbackQuery):
    """Sinf tanlanganda o'quvchilar ro'yxatini ko'rsatish."""
    # Bu handler allaqachon mavjud - davomat uchun
    pass


@router.callback_query(F.data.regexp(r"s:students:class:(\d+)$"))
async def staff_students_class_list(callback: CallbackQuery):
    """O'quvchilar - sinf tanlanganda ro'yxatni ko'rsatish."""
    class_id = int(callback.data.split(":")[-1])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # O'quvchilarni olish
        student_service = StudentService(session)
        students = await student_service.get_students_by_class(class_id)
        
        # Sinfni topish
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        if not class_obj:
            await callback.answer("❌ Sinf topilmadi.", show_alert=True)
            return
        
        if not students:
            await callback.message.edit_text(
                f"📚 {class_obj.name}\n\n"
                f"❌ Bu sinfda o'quvchilar yo'q.\n\n"
                f"Yangi o'quvchi qo'shing:",
                reply_markup=get_students_list_keyboard([], class_id, show_add=True),
            )
            await callback.answer()
            return
        
        await callback.message.edit_text(
            f"📚 {class_obj.name} - O'quvchilar ({len(students)} ta)\n\n"
            f"O'quvchini tanlang:",
            reply_markup=get_students_list_keyboard(students, class_id),
        )
        await callback.answer()


@router.callback_query(F.data == "s:students:back")
async def staff_students_back(callback: CallbackQuery, state: FSMContext):
    """O'quvchilar ro'yxatiga qaytish."""
    await state.clear()
    
    # O'quvchilar menyusiga qaytish
    await staff_students_menu(callback)


@router.callback_query(F.data.regexp(r"s:students:(\d+):add$"))
async def staff_add_student_start(callback: CallbackQuery, state: FSMContext):
    """Yangi o'quvchi qo'shish - boshlash."""
    class_id = int(callback.data.split(":")[2])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        await state.set_state(StaffStates.waiting_student_name)
        await state.update_data(class_id=class_id)
        
        from bot.keyboards.inline import get_cancel_keyboard
        await callback.message.edit_text(
            "📝 Yangi o'quvchi qo'shish\n\n"
            "O'quvchining to'liq ismini kiriting:",
            reply_markup=get_cancel_keyboard(),
        )
        await callback.answer()


@router.message(StaffStates.waiting_student_name)
async def staff_add_student_finish(message: Message, state: FSMContext):
    """Yangi o'quvchi qo'shish - yakunlash."""
    full_name = message.text.strip()
    
    if not full_name:
        await message.answer("❌ Ism bo'sh bo'lishi mumkin emas. Qaytadan kiriting:")
        return
    
    data = await state.get_data()
    class_id = data.get("class_id")
    
    if not class_id:
        await message.answer("❌ Xato yuz berdi. Qaytadan urinib ko'ring.")
        await state.clear()
        return
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await message.answer(error_msg)
            await state.clear()
            return
        
        # O'quvchi qo'shish
        student_service = StudentService(session)
        student, error = await student_service.add_student(class_id, full_name)
        
        if error:
            await message.answer(error)
            return
        
        await state.clear()
        
        # O'quvchilar ro'yxatini ko'rsatish
        students = await student_service.get_students_by_class(class_id)
        
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        await message.answer(
            f"✅ '{full_name}' muvaffaqiyatli qo'shildi!\n\n"
            f"📚 {class_obj.name} - O'quvchilar ({len(students)} ta)\n\n"
            f"O'quvchini tanlang:",
            reply_markup=get_students_list_keyboard(students, class_id),
        )


@router.callback_query(F.data.regexp(r"s:students:(\d+):actions$"))
async def staff_student_actions(callback: CallbackQuery):
    """O'quvchi harakatlari."""
    student_id = int(callback.data.split(":")[2])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # O'quvchini topish
        from repositories.student import StudentRepository
        student_repo = StudentRepository(session)
        student = await student_repo.get_by_id(student_id)
        
        if not student:
            await callback.answer("❌ O'quvchi topilmadi.", show_alert=True)
            return
        
        # Sinfni topish
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(student.class_id)
        
        await callback.message.edit_text(
            f"👤 {student.full_name}\n"
            f"📚 Sinf: {class_obj.name if class_obj else 'Noma\'lum'}\n\n"
            f"Nima qilmoqchisiz?",
            reply_markup=get_student_actions_keyboard(student_id),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:students:(\d+):delete$"))
async def staff_delete_student_confirm(callback: CallbackQuery):
    """O'quvchini o'chirish - tasdiqlash."""
    student_id = int(callback.data.split(":")[2])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # O'quvchini topish
        from repositories.student import StudentRepository
        student_repo = StudentRepository(session)
        student = await student_repo.get_by_id(student_id)
        
        if not student:
            await callback.answer("❌ O'quvchi topilmadi.", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"⚠️ Tasdiqlash\n\n"
            f"'{student.full_name}' o'quvchisini o'chirmoqchimisiz?\n\n"
            f"Bu amal qaytarib bo'lmaydi!",
            reply_markup=get_confirm_keyboard(
                callback_yes=f"s:students:{student_id}:delete:yes",
                callback_no=f"s:students:{student_id}:actions"
            ),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:students:(\d+):delete:yes$"))
async def staff_delete_student_execute(callback: CallbackQuery):
    """O'quvchini o'chirish - bajarish."""
    student_id = int(callback.data.split(":")[2])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # O'quvchini topish
        from repositories.student import StudentRepository
        student_repo = StudentRepository(session)
        student = await student_repo.get_by_id(student_id)
        
        if not student:
            await callback.answer("❌ O'quvchi topilmadi.", show_alert=True)
            return
        
        class_id = student.class_id
        
        # O'chirish
        student_service = StudentService(session)
        success, error = await student_service.remove_student(student_id)
        
        if not success:
            await callback.answer(error, show_alert=True)
            return
        
        # O'quvchilar ro'yxatini ko'rsatish
        students = await student_service.get_students_by_class(class_id)
        
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        await callback.message.edit_text(
            f"✅ O'quvchi muvaffaqiyatli o'chirildi!\n\n"
            f"📚 {class_obj.name} - O'quvchilar ({len(students)} ta)\n\n"
            f"O'quvchini tanlang:",
            reply_markup=get_students_list_keyboard(students, class_id),
        )
        await callback.answer()


# ============= TRANSFER =============

@router.callback_query(F.data == "s:menu:transfer")
async def staff_transfer_menu(callback: CallbackQuery):
    """Xodim - Transfer - sinfni tanlash."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Xodimning sinflarini olish
        from repositories.class_repo import ClassRepository
        class_repo = ClassRepository(session)
        
        from core.db.models import ClassStaff
        from sqlalchemy import select, and_
        
        result = await session.execute(
            select(ClassStaff).where(
                and_(
                    ClassStaff.staff_user_id == user.id,
                    ClassStaff.active_to.is_(None)
                )
            )
        )
        class_assignments = list(result.scalars().all())
        
        active_assignments = []
        for assignment in class_assignments:
            class_obj = await class_repo.get_by_id(assignment.class_id)
            if class_obj:
                assignment.class_ = class_obj
                active_assignments.append(assignment)
        
        if not active_assignments:
            await callback.message.edit_text(
                "❌ Sizga hech qanday sinf biriktirilmagan.\n\n"
                "Iltimos, administrator bilan bog'laning.",
                reply_markup=get_back_button("back_to_menu"),
            )
            await callback.answer()
            return
        
        await callback.message.edit_text(
            "🔄 Transfer\n\n"
            "Qaysi sinfdan o'quvchini ko'chirmoqchisiz?",
            reply_markup=get_staff_classes_keyboard(active_assignments),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:transfer:class:(\d+)$"))
async def staff_transfer_select_class(callback: CallbackQuery):
    """Transfer - sinf tanlash."""
    class_id = int(callback.data.split(":")[-1])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # O'quvchilarni olish
        student_service = StudentService(session)
        students = await student_service.get_students_by_class(class_id)
        
        if not students:
            await callback.answer("❌ Bu sinfda o'quvchilar yo'q.", show_alert=True)
            return
        
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        await callback.message.edit_text(
            f"🔄 Transfer\n\n"
            f"📚 {class_obj.name}\n\n"
            f"Qaysi o'quvchini ko'chirmoqchisiz?",
            reply_markup=get_transfer_students_keyboard(students, class_id),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:transfer:(\d+):student:(\d+)$"))
async def staff_transfer_select_student(callback: CallbackQuery):
    """Transfer - o'quvchi tanlash."""
    parts = callback.data.split(":")
    class_id = int(parts[2])
    student_id = int(parts[4])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # O'quvchini topish
        from repositories.student import StudentRepository
        student_repo = StudentRepository(session)
        student = await student_repo.get_by_id(student_id)
        
        if not student:
            await callback.answer("❌ O'quvchi topilmadi.", show_alert=True)
            return
        
        # Barcha sinflarni olish
        class_service = ClassService(session)
        all_classes = await class_service.get_all_classes()
        
        if len(all_classes) <= 1:
            await callback.answer("❌ Boshqa sinflar yo'q.", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"🔄 Transfer\n\n"
            f"👤 O'quvchi: {student.full_name}\n\n"
            f"Qaysi sinfga ko'chirmoqchisiz?",
            reply_markup=get_transfer_target_classes_keyboard(
                all_classes,
                student_id,
                student.class_id,
            ),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:transfer:(\d+):to:(\d+)$"))
async def staff_transfer_confirm(callback: CallbackQuery):
    """Transfer - tasdiqlash."""
    parts = callback.data.split(":")
    student_id = int(parts[2])
    to_class_id = int(parts[4])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # O'quvchi va sinflarni topish
        from repositories.student import StudentRepository
        student_repo = StudentRepository(session)
        student = await student_repo.get_by_id(student_id)
        
        if not student:
            await callback.answer("❌ O'quvchi topilmadi.", show_alert=True)
            return
        
        class_service = ClassService(session)
        from_class = await class_service.get_class_by_id(student.class_id)
        to_class = await class_service.get_class_by_id(to_class_id)
        
        if not from_class or not to_class:
            await callback.answer("❌ Sinf topilmadi.", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"⚠️ Transfer Tasdiqlash\n\n"
            f"👤 O'quvchi: {student.full_name}\n"
            f"📚 {from_class.name} → {to_class.name}\n\n"
            f"Tasdiqlaysizmi?",
            reply_markup=get_confirm_keyboard(
                callback_yes=f"s:transfer:confirm:{student_id}:{to_class_id}",
                callback_no="s:menu:transfer"
            ),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"s:transfer:confirm:(\d+):(\d+)$"))
async def staff_transfer_execute(callback: CallbackQuery):
    """Transfer - bajarish."""
    parts = callback.data.split(":")
    student_id = int(parts[3])
    to_class_id = int(parts[4])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Transfer qilish
        student_service = StudentService(session)
        success, error = await student_service.transfer_student(
            student_id=student_id,
            to_class_id=to_class_id,
            by_user_id=user.id,
        )
        
        if not success:
            await callback.answer(error, show_alert=True)
            return
        
        # O'quvchi va sinflarni topish
        from repositories.student import StudentRepository
        student_repo = StudentRepository(session)
        student = await student_repo.get_by_id(student_id)
        
        class_service = ClassService(session)
        to_class = await class_service.get_class_by_id(to_class_id)
        
        await callback.message.edit_text(
            f"✅ Transfer muvaffaqiyatli bajarildi!\n\n"
            f"👤 {student.full_name}\n"
            f"📚 Yangi sinf: {to_class.name}",
            reply_markup=get_back_button("back_to_menu"),
        )
        await callback.answer()


@router.callback_query(F.data == "s:menu:myclass")
async def staff_myclass_menu(callback: CallbackQuery):
    """Xodim - Sinfim."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_staff_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Xodimning sinflarini olish
        from repositories.class_repo import ClassRepository
        class_repo = ClassRepository(session)
        
        from core.db.models import ClassStaff
        from sqlalchemy import select, and_
        
        result = await session.execute(
            select(ClassStaff).where(
                and_(
                    ClassStaff.staff_user_id == user.id,
                    ClassStaff.active_to.is_(None)
                )
            )
        )
        class_assignments = list(result.scalars().all())
        
        if not class_assignments:
            await callback.message.edit_text(
                "❌ Sizga hech qanday sinf biriktirilmagan.\n\n"
                "Iltimos, administrator bilan bog'laning.",
                reply_markup=get_back_button("back_to_menu"),
            )
            await callback.answer()
            return
        
        # Har bir sinf uchun ma'lumot
        text = "📚 Mening Sinflarim\n\n"
        
        for assignment in class_assignments:
            class_obj = await class_repo.get_by_id(assignment.class_id)
            if not class_obj:
                continue
            
            # O'quvchilar soni
            student_service = StudentService(session)
            students = await student_service.get_students_by_class(class_obj.id)
            
            text += f"📚 {class_obj.name}\n"
            text += f"  👥 O'quvchilar: {len(students)} ta\n\n"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_back_button("back_to_menu"),
        )
        await callback.answer()
