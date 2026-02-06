"""Telefon raqamlarni normalizatsiya qilish."""
import re


def normalize_phone(phone: str) -> str:
    """
    Telefon raqamni standart formatga keltirish.
    
    Misol:
        +998901234567 -> 998901234567
        998 90 123 45 67 -> 998901234567
        +7 (900) 123-45-67 -> 79001234567
    """
    # Faqat raqamlarni qoldirish
    digits = re.sub(r'\D', '', phone)
    
    # Agar + bilan boshlansa, uni olib tashlash
    if phone.startswith('+'):
        return digits
    
    # Agar 998 bilan boshlanmasa, 998 qo'shish (O'zbekiston)
    if not digits.startswith('998') and len(digits) == 9:
        return '998' + digits
    
    return digits


def format_phone_display(phone: str) -> str:
    """
    Telefon raqamni ko'rsatish uchun formatlash.
    
    Misol:
        998901234567 -> +998 90 123 45 67
    """
    normalized = normalize_phone(phone)
    
    if normalized.startswith('998') and len(normalized) == 12:
        return f"+{normalized[:3]} {normalized[3:5]} {normalized[5:8]} {normalized[8:10]} {normalized[10:]}"
    
    return f"+{normalized}"


def is_valid_uzbek_phone(phone: str) -> bool:
    """
    O'zbekiston telefon raqamini tekshirish.
    
    Format: 998XXXXXXXXX (12 ta raqam)
    """
    normalized = normalize_phone(phone)
    return normalized.startswith('998') and len(normalized) == 12
