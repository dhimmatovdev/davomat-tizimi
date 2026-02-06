# Davomat Bot - Maktab Davomat Tizimi

Professional Telegram bot maktab davomatini yuritish uchun.

## Stack
- Python 3.11
- aiogram 3.x
- SQLite (local, keyinchalik PostgreSQL)
- SQLAlchemy + Alembic

## O'rnatish

1. Virtual environment yaratish:
```bash
python -m venv venv
venv\Scripts\activate  # Windows
```

2. Dependencylarni o'rnatish:
```bash
pip install -r requirements.txt
```

3. `.env` faylini yaratish:
```bash
copy .env.example .env
```

`.env` faylida `BOT_TOKEN` ni o'rnating.

4. Birinchi adminni yaratish:
```bash
python scripts/create_admin.py
```

5. Botni ishga tushirish:
```bash
python main.py
```

## Loyiha Strukturasi

```
davomat-bot/
├── core/
│   ├── config.py          # Sozlamalar
│   ├── db/                # Database
│   │   ├── base.py
│   │   ├── engine.py
│   │   └── models.py
│   └── security/          # Access control
│       └── access.py
├── bot/
│   ├── handlers/          # Message/callback handlers
│   │   ├── start.py
│   │   ├── admin.py
│   │   └── staff.py
│   └── keyboards/         # Inline keyboards
│       └── inline.py
├── services/              # Biznes mantiq
│   └── user.py
├── repositories/          # Database CRUD
│   └── user.py
├── utils/                 # Yordamchi funksiyalar
│   ├── phone.py
│   └── dates.py
├── scripts/               # Yordamchi scriptlar
│   └── create_admin.py
├── main.py                # Entry point
├── requirements.txt
└── .env.example
```

## Rollar

- **Admin**: To'liq huquq (sinflar, xodimlar, hisobotlar)
- **Xodim**: Faqat o'z sinflari uchun davomat

## Fazalar

- [x] FAZA-1: Loyiha strukturasi va auth
- [ ] FAZA-2: Admin CRUD
- [ ] FAZA-3: Staff attendance
- [ ] FAZA-4: Students + transfer
- [ ] FAZA-5: Reports
