"""Admin handlerlari - to'liq versiya."""
import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext

from core.db import get_session
from core.security.access import check_admin_access
from services.user import UserService
from services.class_service import ClassService
from services.report_service import ReportService
from bot.states import AdminStates
from bot.keyboards.inline import (
    get_back_button,
    get_classes_list_keyboard,
    get_class_actions_keyboard,
    get_confirm_keyboard,
    get_staff_list_keyboard,
    get_assigned_staff_keyboard,
    get_cancel_keyboard,
    get_reports_menu_keyboard,
    get_report_classes_keyboard,
)

logger = logging.getLogger(__name__)
router = Router()


# ============= SINFLAR BOSHQARUVI =============

@router.callback_query(F.data == "a:menu:classes")
async def admin_classes_menu(callback: CallbackQuery):
    """Admin - Sinflar menyusi."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Barcha sinflarni olish
        class_service = ClassService(session)
        classes = await class_service.get_all_classes()
        
        if not classes:
            text = "📚 Sinflar\n\nHozircha sinflar yo'q. Yangi sinf yarating."
        else:
            text = f"📚 Sinflar ({len(classes)} ta)\n\nSinfni tanlang:"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_classes_list_keyboard(classes),
        )
        await callback.answer()


@router.callback_query(F.data == "a:cls:list")
async def admin_classes_list(callback: CallbackQuery):
    """Sinflar ro'yxatiga qaytish."""
    await admin_classes_menu(callback)


@router.callback_query(F.data == "a:cls:create")
async def admin_create_class_start(callback: CallbackQuery, state: FSMContext):
    """Yangi sinf yaratish - boshlash."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        await state.set_state(AdminStates.waiting_class_name)
        await callback.message.edit_text(
            "📝 Yangi sinf yaratish\n\n"
            "Sinf nomini kiriting (masalan: 10-A, 11-B):",
            reply_markup=get_cancel_keyboard(),
        )
        await callback.answer()


@router.message(AdminStates.waiting_class_name)
async def admin_create_class_finish(message: Message, state: FSMContext):
    """Yangi sinf yaratish - yakunlash."""
    class_name = message.text.strip()
    
    if not class_name:
        await message.answer("❌ Sinf nomi bo'sh bo'lishi mumkin emas. Qaytadan kiriting:")
        return
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await message.answer(error_msg)
            await state.clear()
            return
        
        # Sinf yaratish
        class_service = ClassService(session)
        class_obj, error = await class_service.create_class(class_name)
        
        if error:
            await message.answer(error)
            return
        
        await state.clear()
        
        # Sinflar ro'yxatini ko'rsatish
        classes = await class_service.get_all_classes()
        await message.answer(
            f"✅ '{class_name}' sinfi muvaffaqiyatli yaratildi!\n\n"
            f"📚 Sinflar ({len(classes)} ta)\n\nSinfni tanlang:",
            reply_markup=get_classes_list_keyboard(classes),
        )


@router.callback_query(F.data.regexp(r"^a:cls:(\d+)$"))
async def admin_class_detail(callback: CallbackQuery):
    """Sinf tafsilotlari."""
    class_id = int(callback.data.split(":")[-1])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        if not class_obj:
            await callback.answer("❌ Sinf topilmadi.", show_alert=True)
            return
        
        # O'quvchilar
        from services.student_service import StudentService
        student_service = StudentService(session)
        students = await student_service.get_students_by_class(class_id)
        
        # Bugungi davomat
        from datetime import date
        from services.attendance_service import AttendanceService
        attendance_service = AttendanceService(session)
        
        from sqlalchemy import select, and_
        from core.db.models import AttendanceDay
        
        today = date.today()
        result = await session.execute(
            select(AttendanceDay).where(
                and_(
                    AttendanceDay.class_id == class_id,
                    AttendanceDay.date == today
                )
            )
        )
        attendance_day = result.scalar_one_or_none()
        
        # Biriktirilgan xodimlar
        staff_assignments = await class_service.get_staff_for_class(class_id)
        
        text = f"📚 {class_obj.name}\n\n"
        
        # O'quvchilar
        text += f"👥 O'quvchilar: {len(students)} ta\n"
        if students:
            text += "\n"
            for i, student in enumerate(students[:10], 1):  # Faqat 10 ta ko'rsatish
                text += f"{i}. {student.full_name}\n"
            if len(students) > 10:
                text += f"... va yana {len(students) - 10} ta\n"
        
        # Bugungi davomat
        if attendance_day:
            summary = await attendance_service.get_attendance_summary(attendance_day.id)
            text += f"\n📊 Bugungi davomat:\n"
            text += f"  ✅ Keldi: {summary['present']}\n"
            text += f"  🟡 Kechikdi: {summary['late']}\n"
            text += f"  ❌ Kelmadi: {summary['absent']}\n"
            if summary['not_marked'] > 0:
                text += f"  ⚪ Belgilanmagan: {summary['not_marked']}\n"
        else:
            text += f"\n📊 Bugungi davomat: Hali belgilanmagan\n"
        
        # Xodimlar
        text += f"\n👨‍🏫 Xodimlar:\n"
        if staff_assignments:
            for assignment in staff_assignments:
                text += f"  • {assignment.staff_user.full_name}\n"
        else:
            text += "  Hozircha biriktirilmagan\n"
        
        text += "\nNima qilmoqchisiz?"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_class_actions_keyboard(class_id),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"a:cls:(\d+):delete$"))
async def admin_delete_class_confirm(callback: CallbackQuery):
    """Sinfni o'chirish - tasdiqlash."""
    class_id = int(callback.data.split(":")[2])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        if not class_obj:
            await callback.answer("❌ Sinf topilmadi.", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"⚠️ Tasdiqlash\n\n"
            f"'{class_obj.name}' sinfini o'chirmoqchimisiz?\n\n"
            f"Bu amal qaytarib bo'lmaydi!",
            reply_markup=get_confirm_keyboard(
                callback_yes=f"a:cls:{class_id}:delete:yes",
                callback_no=f"a:cls:{class_id}"
            ),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"a:cls:(\d+):delete:yes$"))
async def admin_delete_class_execute(callback: CallbackQuery):
    """Sinfni o'chirish - bajarish."""
    class_id = int(callback.data.split(":")[2])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        class_service = ClassService(session)
        success, error = await class_service.delete_class(class_id)
        
        if not success:
            await callback.answer(error, show_alert=True)
            return
        
        # Sinflar ro'yxatini ko'rsatish
        classes = await class_service.get_all_classes()
        await callback.message.edit_text(
            f"✅ Sinf muvaffaqiyatli o'chirildi!\n\n"
            f"📚 Sinflar ({len(classes)} ta)\n\nSinfni tanlang:",
            reply_markup=get_classes_list_keyboard(classes),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"a:cls:(\d+):excel$"))
async def admin_export_students_excel(callback: CallbackQuery):
    """O'quvchilarni Excel faylda yuklab olish."""
    class_id = int(callback.data.split(":")[2])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        if not class_obj:
            await callback.answer("❌ Sinf topilmadi.", show_alert=True)
            return
        
        # O'quvchilarni olish
        from services.student_service import StudentService
        student_service = StudentService(session)
        students = await student_service.get_students_by_class(class_id)
        
        if not students:
            await callback.answer("❌ Bu sinfda o'quvchilar yo'q.", show_alert=True)
            return
        
        # Excel yaratish
        from utils.excel import generate_students_excel
        excel_file = generate_students_excel(class_obj.name, students)
        
        # Faylni yuborish
        from aiogram.types import BufferedInputFile
        from datetime import date
        
        filename = f"{class_obj.name}_oquvchilar_{date.today().strftime('%Y%m%d')}.csv"
        file = BufferedInputFile(excel_file.read(), filename=filename)
        
        await callback.message.answer_document(
            document=file,
            caption=f"📊 {class_obj.name} - O'quvchilar ro'yxati\n\n"
                    f"👥 Jami: {len(students)} ta o'quvchi"
        )
        
        await callback.answer("✅ Fayl yuborildi!")


@router.callback_query(F.data.regexp(r"a:cls:(\d+):staff$"))
async def admin_assign_staff_list(callback: CallbackQuery):
    """Xodimni sinfga biriktirish - xodimlar ro'yxati."""
    class_id = int(callback.data.split(":")[2])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        class_service = ClassService(session)
        class_obj = await class_service.get_class_by_id(class_id)
        
        if not class_obj:
            await callback.answer("❌ Sinf topilmadi.", show_alert=True)
            return
        
        # Barcha xodimlarni olish
        user_repo = user_service.repo
        all_staff = await user_repo.get_all_staff()
        
        if not all_staff:
            await callback.answer("❌ Tizimda xodimlar yo'q.", show_alert=True)
            return
        
        await callback.message.edit_text(
            f"👥 Xodimni '{class_obj.name}' sinfiga biriktirish\n\n"
            f"Xodimni tanlang:",
            reply_markup=get_staff_list_keyboard(all_staff, class_id),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"a:cls:(\d+):staff:(\d+)$"))
async def admin_assign_staff_execute(callback: CallbackQuery):
    """Xodimni sinfga biriktirish - bajarish."""
    parts = callback.data.split(":")
    class_id = int(parts[2])
    staff_user_id = int(parts[4])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        class_service = ClassService(session)
        success, error = await class_service.assign_staff_to_class(class_id, staff_user_id)
        
        if not success:
            await callback.answer(error, show_alert=True)
            return
        
        # Sinf tafsilotlarini ko'rsatish
        class_obj = await class_service.get_class_by_id(class_id)
        staff_assignments = await class_service.get_staff_for_class(class_id)
        
        text = f"✅ Xodim muvaffaqiyatli biriktirildi!\n\n"
        text += f"📚 {class_obj.name}\n\n"
        
        if staff_assignments:
            text += "👥 Biriktirilgan xodimlar:\n"
            for assignment in staff_assignments:
                text += f"  • {assignment.staff_user.full_name}\n"
        
        text += "\nNima qilmoqchisiz?"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_class_actions_keyboard(class_id),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"a:staff:(\d+):remove:(\d+)$"))
async def admin_remove_staff_execute(callback: CallbackQuery):
    """Xodimni sinfdan olib tashlash."""
    parts = callback.data.split(":")
    class_id = int(parts[2])
    staff_user_id = int(parts[4])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        class_service = ClassService(session)
        success, error = await class_service.remove_staff_from_class(class_id, staff_user_id)
        
        if not success:
            await callback.answer(error, show_alert=True)
            return
        
        # Sinf tafsilotlarini ko'rsatish
        class_obj = await class_service.get_class_by_id(class_id)
        staff_assignments = await class_service.get_staff_for_class(class_id)
        
        text = f"✅ Xodim muvaffaqiyatli olib tashlandi!\n\n"
        text += f"📚 {class_obj.name}\n\n"
        
        if staff_assignments:
            text += "👥 Biriktirilgan xodimlar:\n"
            for assignment in staff_assignments:
                text += f"  • {assignment.staff_user.full_name}\n"
        else:
            text += "👥 Hozircha xodimlar biriktirilmagan.\n"
        
        text += "\nNima qilmoqchisiz?"
        
        await callback.message.edit_text(
            text,
            reply_markup=get_class_actions_keyboard(class_id),
        )
        await callback.answer()


# ============= XODIMLAR BOSHQARUVI =============

@router.callback_query(F.data == "a:menu:staff")
async def admin_staff_menu(callback: CallbackQuery):
    """Admin - Xodimlar menyusi."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Barcha xodimlarni olish
        user_repo = user_service.repo
        all_staff = await user_repo.get_all_staff()
        
        if not all_staff:
            text = "👥 Xodimlar\n\nHozircha xodimlar yo'q. Yangi xodim qo'shing."
        else:
            text = f"👥 Xodimlar ({len(all_staff)} ta)\n\n"
            for staff in all_staff:
                text += f"👤 {staff.full_name}\n"
                text += f"   📱 {staff.phone}\n\n"
        
        from bot.keyboards.inline import InlineKeyboardBuilder, InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="➕ Yangi xodim", callback_data="a:staff:add")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_menu")
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup(),
        )
        await callback.answer()


@router.callback_query(F.data == "a:staff:add")
async def admin_add_staff_start(callback: CallbackQuery, state: FSMContext):
    """Yangi xodim qo'shish - boshlash."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        await state.set_state(AdminStates.waiting_staff_phone)
        await callback.message.edit_text(
            "📝 Yangi xodim qo'shish\n\n"
            "Xodimning telefon raqamini kiriting\n"
            "(masalan: +998901234567 yoki 998901234567):",
            reply_markup=get_cancel_keyboard(),
        )
        await callback.answer()


@router.message(AdminStates.waiting_staff_phone)
async def admin_add_staff_phone(message: Message, state: FSMContext):
    """Yangi xodim - telefon raqam."""
    from utils.phone import normalize_phone
    
    phone = normalize_phone(message.text)
    
    if not phone:
        await message.answer("❌ Noto'g'ri telefon raqam. Qaytadan kiriting:")
        return
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await message.answer(error_msg)
            await state.clear()
            return
        
        # Telefon raqam allaqachon mavjudligini tekshirish
        existing_user = await user_service.get_user_by_phone(phone)
        if existing_user:
            await message.answer(
                f"❌ Bu telefon raqam allaqachon ro'yxatdan o'tgan.\n"
                f"Foydalanuvchi: {existing_user.full_name} ({existing_user.role})"
            )
            return
        
        # Telefon raqamni saqlash va ismni so'rash
        await state.update_data(phone=phone)
        await state.set_state(AdminStates.waiting_staff_name)
        
        await message.answer(
            f"✅ Telefon: {phone}\n\n"
            f"Xodimning to'liq ismini kiriting:"
        )


@router.message(AdminStates.waiting_staff_name)
async def admin_add_staff_finish(message: Message, state: FSMContext):
    """Yangi xodim - ism va yakunlash."""
    full_name = message.text.strip()
    
    if not full_name:
        await message.answer("❌ Ism bo'sh bo'lishi mumkin emas. Qaytadan kiriting:")
        return
    
    data = await state.get_data()
    phone = data.get("phone")
    
    if not phone:
        await message.answer("❌ Xato yuz berdi. Qaytadan urinib ko'ring.")
        await state.clear()
        return
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await message.answer(error_msg)
        # Xodim yaratish
        new_staff = await user_service.create_user(
            telegram_id=0,  # Xodim hali botga kirmagan
            phone=phone,
            full_name=full_name,
            role="xodim",
        )
        
        await state.clear()
        
        # Barcha xodimlarni ko'rsatish
        user_repo = user_service.repo
        all_staff = await user_repo.get_all_staff()
        
        text = f"✅ '{full_name}' muvaffaqiyatli qo'shildi!\n\n"
        text += f"👥 Xodimlar ({len(all_staff)} ta)\n\n"
        for staff in all_staff:
            text += f"👤 {staff.full_name}\n"
            text += f"   📱 {staff.phone}\n\n"
        
        from bot.keyboards.inline import InlineKeyboardBuilder, InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="➕ Yangi xodim", callback_data="a:staff:add")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_menu")
        )
        
        await message.answer(
            text,
            reply_markup=builder.as_markup(),
        )


@router.callback_query(F.data == "a:menu:reports")
async def admin_reports_menu(callback: CallbackQuery):
    """Admin - Hisobotlar menyusi."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        await callback.message.edit_text(
            "📊 Hisobotlar\n\n"
            "Qaysi hisobotni ko'rmoqchisiz?",
            reply_markup=get_reports_menu_keyboard(),
        )
        await callback.answer()


@router.callback_query(F.data == "a:reports:daily")
async def admin_daily_report(callback: CallbackQuery):
    """Admin - Bugungi hisobot."""
    from datetime import date
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Barcha sinflarni olish
        class_service = ClassService(session)
        classes = await class_service.get_all_classes()
        
        if not classes:
            await callback.message.edit_text(
                "❌ Hozircha sinflar yo'q.",
                reply_markup=get_back_button("a:menu:reports"),
            )
            await callback.answer()
            return
        
        # Har bir sinf uchun bugungi hisobot
        report_service = ReportService(session)
        today = date.today()
        
        reports = []
        for class_obj in classes:
            report, success = await report_service.get_daily_report(class_obj.id, today)
            if success:
                reports.append(report)
        
        if not reports:
            await callback.message.edit_text(
                "❌ Bugun hech qanday davomat topilmadi.",
                reply_markup=get_back_button("a:menu:reports"),
            )
            await callback.answer()
            return
        
        # Hisobotlarni birlashtirish
        full_report = "\n\n" + "="*30 + "\n\n".join(reports)
        
        await callback.message.edit_text(
            full_report,
            reply_markup=get_back_button("a:menu:reports"),
        )
        await callback.answer()


@router.callback_query(F.data == "a:reports:classes")
async def admin_class_reports_menu(callback: CallbackQuery):
    """Admin - Sinf hisobotlari - sinfni tanlash."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Barcha sinflarni olish
        class_service = ClassService(session)
        classes = await class_service.get_all_classes()
        
        if not classes:
            await callback.message.edit_text(
                "❌ Hozircha sinflar yo'q.",
                reply_markup=get_back_button("a:menu:reports"),
            )
            await callback.answer()
            return
        
        await callback.message.edit_text(
            "📚 Sinf Hisoboti\n\n"
            "Sinfni tanlang:",
            reply_markup=get_report_classes_keyboard(classes),
        )
        await callback.answer()


@router.callback_query(F.data.regexp(r"a:reports:class:(\d+)$"))
async def admin_class_report(callback: CallbackQuery):
    """Admin - Sinf hisoboti."""
    class_id = int(callback.data.split(":")[-1])
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Sinf hisoboti
        report_service = ReportService(session)
        report, success = await report_service.get_class_report(class_id)
        
        if not success:
            await callback.answer(report, show_alert=True)
            return
        
        await callback.message.edit_text(
            report,
            reply_markup=get_back_button("a:reports:classes"),
        )
        await callback.answer()


@router.callback_query(F.data == "a:menu:settings")
async def admin_settings_menu(callback: CallbackQuery):
    """Admin - Sozlamalar menyusi."""
    await callback.message.edit_text(
        "⚙️ Sozlamalar\n\n"
        "Bu bo'lim keyingi fazada ishlab chiqiladi.",
        reply_markup=get_back_button("back_to_menu"),
    )
    await callback.answer()


@router.callback_query(F.data == "cancel")
async def cancel_action(callback: CallbackQuery, state: FSMContext):
    """Bekor qilish."""
    await state.clear()
    await callback.answer("❌ Bekor qilindi.")
    
    # Admin menyuga qaytish
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        if user:
            from bot.keyboards.inline import get_admin_menu_keyboard
            await callback.message.edit_text(
                "Admin panel",
                reply_markup=get_admin_menu_keyboard(),
            )


# ============= ADMINLAR BOSHQARUVI =============

@router.callback_query(F.data == "a:menu:admins")
async def admin_admins_menu(callback: CallbackQuery):
    """Admin - Adminlar menyusi."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        # Barcha adminlarni olish
        user_repo = user_service.repo
        all_admins = await user_repo.get_all_admins()
        
        if not all_admins:
            text = "👨‍💼 Adminlar\n\nHozircha adminlar yo'q."
        else:
            text = f"👨‍💼 Adminlar ({len(all_admins)} ta)\n\n"
            for admin in all_admins:
                text += f"👤 {admin.full_name}\n"
                text += f"   📱 {admin.phone}\n\n"
        
        from bot.keyboards.inline import InlineKeyboardBuilder, InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="➕ Yangi admin", callback_data="a:admins:add")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_menu")
        )
        
        await callback.message.edit_text(
            text,
            reply_markup=builder.as_markup(),
        )
        await callback.answer()


@router.callback_query(F.data == "a:admins:add")
async def admin_add_admin_start(callback: CallbackQuery, state: FSMContext):
    """Yangi admin qo'shish - boshlash."""
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(callback.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await callback.answer(error_msg, show_alert=True)
            return
        
        await state.set_state(AdminStates.waiting_admin_phone)
        await callback.message.edit_text(
            "📝 Yangi admin qo'shish\n\n"
            "Adminning telefon raqamini kiriting\n"
            "(masalan: +998901234567 yoki 998901234567):",
            reply_markup=get_cancel_keyboard(),
        )
        await callback.answer()


@router.message(AdminStates.waiting_admin_phone)
async def admin_add_admin_phone(message: Message, state: FSMContext):
    """Yangi admin - telefon raqam."""
    from utils.phone import normalize_phone
    
    phone = normalize_phone(message.text)
    
    if not phone:
        await message.answer("❌ Noto'g'ri telefon raqam. Qaytadan kiriting:")
        return
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await message.answer(error_msg)
            await state.clear()
            return
        
        # Telefon raqam allaqachon mavjudligini tekshirish
        existing_user = await user_service.get_user_by_phone(phone)
        if existing_user:
            # Agar mavjud bo'lsa, rolini yangilash mumkin
            if existing_user.role == "admin":
                await message.answer(
                    f"❌ Bu foydalanuvchi allaqachon admin.\n"
                    f"Foydalanuvchi: {existing_user.full_name}"
                )
                return
            else:
                # Mavjud user rolini admin qilish
                existing_user.role = "admin"
                await session.commit()
                await message.answer(
                    f"✅ {existing_user.full_name} endi admin bo'ldi!",
                )
                await state.clear()
                # Admins menu ga qaytishni taklif qilish? Yoki avto qaytish?
                # Hozircha shu yerda to'xtaymiz, user menu dan ko'rsa bo'ladi.
                return
        
        # Telefon raqamni saqlash va ismni so'rash
        await state.update_data(phone=phone)
        await state.set_state(AdminStates.waiting_admin_name)
        
        await message.answer(
            f"✅ Telefon: {phone}\n\n"
            f"Adminning to'liq ismini kiriting:"
        )


@router.message(AdminStates.waiting_admin_name)
async def admin_add_admin_finish(message: Message, state: FSMContext):
    """Yangi admin - ism va yakunlash."""
    full_name = message.text.strip()
    
    if not full_name:
        await message.answer("❌ Ism bo'sh bo'lishi mumkin emas. Qaytadan kiriting:")
        return
    
    data = await state.get_data()
    phone = data.get("phone")
    
    if not phone:
        await message.answer("❌ Xato yuz berdi. Qaytadan urinib ko'ring.")
        await state.clear()
        return
    
    async for session in get_session():
        user_service = UserService(session)
        user = await user_service.get_user_by_telegram_id(message.from_user.id)
        
        has_access, error_msg = await check_admin_access(user)
        if not has_access:
            await message.answer(error_msg)
        
        # Admin yaratish
        new_admin = await user_service.create_user(
            telegram_id=0,
            phone=phone,
            full_name=full_name,
            role="admin",
        )
        
        await state.clear()
        
        # Barcha adminlarni ko'rsatish
        user_repo = user_service.repo
        all_admins = await user_repo.get_all_admins()
        
        text = f"✅ '{full_name}' muvaffaqiyatli admin etib tayinlandi!\n\n"
        text += f"👨‍💼 Adminlar ({len(all_admins)} ta)\n\n"
        for admin in all_admins:
            text += f"👤 {admin.full_name}\n"
            text += f"   📱 {admin.phone}\n\n"
        
        from bot.keyboards.inline import InlineKeyboardBuilder, InlineKeyboardButton
        builder = InlineKeyboardBuilder()
        
        builder.row(
            InlineKeyboardButton(text="➕ Yangi admin", callback_data="a:admins:add")
        )
        builder.row(
            InlineKeyboardButton(text="◀️ Orqaga", callback_data="back_to_menu")
        )
        
        await message.answer(
            text,
            reply_markup=builder.as_markup(),
        )
