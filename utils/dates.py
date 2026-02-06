"""Sana bilan ishlash uchun yordamchi funksiyalar."""
from datetime import datetime, date, timedelta
from typing import Optional


def today() -> date:
    """Bugungi sanani qaytarish."""
    return date.today()


def format_date(dt: date, format_str: str = "%d.%m.%Y") -> str:
    """Sanani formatlash."""
    return dt.strftime(format_str)


def parse_date(date_str: str, format_str: str = "%Y%m%d") -> Optional[date]:
    """String'dan sanani parse qilish."""
    try:
        return datetime.strptime(date_str, format_str).date()
    except ValueError:
        return None


def get_week_dates(start_date: Optional[date] = None) -> list[date]:
    """Haftaning sanalarini olish (dushanbadan yakshanbagacha)."""
    if start_date is None:
        start_date = today()
    
    # Haftaning boshiga o'tish (dushanba)
    weekday = start_date.weekday()
    monday = start_date - timedelta(days=weekday)
    
    # 7 kunni qaytarish
    return [monday + timedelta(days=i) for i in range(7)]


def get_month_name(month: int) -> str:
    """Oy nomini olish (o'zbekcha)."""
    months = {
        1: "Yanvar",
        2: "Fevral",
        3: "Mart",
        4: "Aprel",
        5: "May",
        6: "Iyun",
        7: "Iyul",
        8: "Avgust",
        9: "Sentabr",
        10: "Oktabr",
        11: "Noyabr",
        12: "Dekabr",
    }
    return months.get(month, "")


def get_weekday_name(weekday: int) -> str:
    """Hafta kuni nomini olish (o'zbekcha)."""
    weekdays = {
        0: "Dushanba",
        1: "Seshanba",
        2: "Chorshanba",
        3: "Payshanba",
        4: "Juma",
        5: "Shanba",
        6: "Yakshanba",
    }
    return weekdays.get(weekday, "")
