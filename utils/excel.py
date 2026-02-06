"""Excel export - o'quvchilar ro'yxatini Excel faylda yaratish."""
import io
from datetime import date


def generate_students_excel(class_name: str, students: list) -> io.BytesIO:
    """
    O'quvchilar ro'yxatini CSV formatida yaratish (Excel ochishi mumkin).
    
    Args:
        class_name: Sinf nomi
        students: O'quvchilar ro'yxati
    
    Returns:
        BytesIO obyekti (fayl)
    """
    # CSV yaratish (Excel ochishi mumkin)
    output = io.BytesIO()
    
    # UTF-8 BOM qo'shish (Excel uchun)
    output.write(b'\xef\xbb\xbf')
    
    # Header
    header = f"{class_name} - O'quvchilar ro'yxati\n"
    header += f"Sana: {date.today().strftime('%d.%m.%Y')}\n\n"
    header += "№,Ism Familiya,Status\n"
    
    output.write(header.encode('utf-8'))
    
    # O'quvchilar
    for i, student in enumerate(students, 1):
        status = "Faol" if student.is_active else "Nofaol"
        line = f"{i},{student.full_name},{status}\n"
        output.write(line.encode('utf-8'))
    
    output.seek(0)
    return output
