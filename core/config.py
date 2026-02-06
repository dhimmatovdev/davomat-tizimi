"""Konfiguratsiya sozlamalari."""
import os
from pathlib import Path
from dotenv import load_dotenv

# .env faylini yuklash
env_path = Path(__file__).parent.parent / ".env"
load_dotenv(dotenv_path=env_path)


class Settings:
    """Asosiy sozlamalar."""
    
    # Bot
    BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")
    SUPER_ADMIN_ID: int = int(os.getenv("SUPER_ADMIN_ID", "0"))

    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./davomat.db")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    # Rollar
    ROLE_ADMIN = "admin"
    ROLE_STAFF = "xodim"
    # Davomat statuslari
    STATUS_PRESENT = 1
    STATUS_LATE = 2
    STATUS_ABSENT = 3
    
    def validate(self) -> None:
        """Sozlamalarni tekshirish."""
        if not self.BOT_TOKEN:
            raise ValueError("BOT_TOKEN o'rnatilmagan!")


settings = Settings()
