"""Report generator - hisobotlar yaratish."""
from datetime import date
from typing import Optional


class ReportGenerator:
    """Hisobotlar yaratish."""
    
    @staticmethod
    def generate_daily_summary(
        date_val: date,
        class_name: str,
        total: int,
        present: int,
        late: int,
        absent: int,
        not_marked: int,
    ) -> str:
        """
        Kunlik xulosa yaratish.
        
        Args:
            date_val: Sana
            class_name: Sinf nomi
            total: Jami o'quvchilar
            present: Kelganlar
            late: Kechikkanlar
            absent: Kelmaganlar
            not_marked: Belgilanmaganlar
        
        Returns:
            Formatlangan hisobot matni
        """
        from utils.dates import format_date, get_weekday_name
        
        weekday = get_weekday_name(date_val.weekday())
        date_str = format_date(date_val)
        
        text = f"📊 Kunlik Davomat Hisoboti\n\n"
        text += f"📚 Sinf: {class_name}\n"
        text += f"📅 Sana: {weekday}, {date_str}\n\n"
        text += f"👥 Jami o'quvchilar: {total}\n\n"
        text += f"✅ Keldi: {present}\n"
        text += f"🟡 Kechikdi: {late}\n"
        text += f"❌ Kelmadi: {absent}\n"
        
        if not_marked > 0:
            text += f"⚪ Belgilanmagan: {not_marked}\n"
        
        # Foizlar
        if total > 0:
            present_percent = (present / total) * 100
            late_percent = (late / total) * 100
            absent_percent = (absent / total) * 100
            
            text += f"\n📈 Statistika:\n"
            text += f"  • Kelganlar: {present_percent:.1f}%\n"
            text += f"  • Kechikkanlar: {late_percent:.1f}%\n"
            text += f"  • Kelmaganlar: {absent_percent:.1f}%\n"
        
        return text
    
    @staticmethod
    def generate_class_report(
        class_name: str,
        total_students: int,
        active_students: int,
        staff_count: int,
        staff_names: list[str],
    ) -> str:
        """
        Sinf hisoboti yaratish.
        
        Args:
            class_name: Sinf nomi
            total_students: Jami o'quvchilar
            active_students: Faol o'quvchilar
            staff_count: Xodimlar soni
            staff_names: Xodimlar nomlari
        
        Returns:
            Formatlangan hisobot matni
        """
        text = f"📚 Sinf Hisoboti\n\n"
        text += f"📖 Sinf: {class_name}\n\n"
        text += f"👥 O'quvchilar:\n"
        text += f"  • Jami: {total_students}\n"
        text += f"  • Faol: {active_students}\n"
        
        if total_students != active_students:
            text += f"  • Nofaol: {total_students - active_students}\n"
        
        text += f"\n👨‍🏫 Xodimlar ({staff_count} ta):\n"
        
        if staff_names:
            for name in staff_names:
                text += f"  • {name}\n"
        else:
            text += f"  • Hozircha xodimlar biriktirilmagan\n"
        
        return text
    
    @staticmethod
    def format_students_list(students: list, show_status: bool = False) -> str:
        """
        O'quvchilar ro'yxatini formatlash.
        
        Args:
            students: O'quvchilar ro'yxati
            show_status: Statusni ko'rsatish
        
        Returns:
            Formatlangan ro'yxat
        """
        if not students:
            return "O'quvchilar yo'q."
        
        text = ""
        for i, student in enumerate(students, 1):
            if show_status and hasattr(student, 'status_emoji'):
                text += f"{i}. {student.status_emoji} {student.full_name}\n"
            else:
                text += f"{i}. {student.full_name}\n"
        
        return text
