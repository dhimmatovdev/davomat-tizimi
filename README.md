# 🎓 Davomat Tizimi - Maktab Davomat Boshqaruvi

Professional Telegram bot maktablar uchun davomat yuritish va boshqarish tizimi.

## ✨ Asosiy Imkoniyatlar

### 👨‍💼 Admin Panel
- ✅ Sinflarni boshqarish (yaratish, ko'rish, o'chirish)
- ✅ Xodimlarni boshqarish (qo'shish, sinfga biriktirish)
- ✅ O'quvchilar ro'yxati va statistika
- ✅ Excel formatida export (CSV)
- ✅ Bugungi davomat xulosasi
- ✅ Kunlik va sinf bo'yicha hisobotlar

### 👨‍🏫 Xodim Panel
- ✅ Bugungi davomatni belgilash
- ✅ O'quvchilarni boshqarish (qo'shish, o'chirish)
- ✅ O'quvchilarni sinflar o'rtasida ko'chirish (transfer)
- ✅ Sinfim - o'z sinflari haqida ma'lumot
- ✅ Davomat xulosasi

## 🛠 Texnologiyalar

- **Python**: 3.11+
- **Bot Framework**: aiogram 3.x
- **Database**: SQLite (SQLAlchemy ORM)
- **Migrations**: Alembic
- **Architecture**: Clean Architecture (Repository + Service pattern)

## 📦 O'rnatish

### 1. Repositoriyani klonlash
```bash
git clone https://github.com/dhimmatovdev/davomat-tizimi.git
cd davomat-tizimi
```

### 2. Virtual environment yaratish
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# Linux/Mac
python3 -m venv venv
source venv/bin/activate
```

### 3. Dependencylarni o'rnatish
```bash
pip install -r requirements.txt
```

### 4. Environment sozlash
```bash
# Windows
copy .env.example .env

# Linux/Mac
cp .env.example .env
```

`.env` faylida quyidagilarni o'rnating:
```env
BOT_TOKEN=your_telegram_bot_token_here
DATABASE_URL=sqlite:///./davomat.db
```

### 5. Birinchi adminni yaratish
```bash
python scripts/create_admin.py
```

Telefon raqam va to'liq ismni kiriting.

### 6. Botni ishga tushirish
```bash
python main.py
```

## 📁 Loyiha Strukturasi

```
davomat-tizimi/
├── core/                   # Asosiy modullar
│   ├── config.py          # Sozlamalar
│   ├── db/                # Database
│   │   ├── base.py
│   │   ├── engine.py
│   │   └── models.py      # SQLAlchemy modellar
│   └── security/          # Access control
│       └── access.py
├── bot/                   # Bot modullari
│   ├── handlers/          # Message/callback handlers
│   │   ├── start.py       # Start va auth
│   │   ├── admin.py       # Admin funksiyalari
│   │   └── staff.py       # Xodim funksiyalari
│   ├── keyboards/         # Inline keyboards
│   │   └── inline.py
│   └── states.py          # FSM states
├── services/              # Biznes mantiq
│   ├── user.py
│   ├── class_service.py
│   ├── student_service.py
│   ├── attendance_service.py
│   └── report_service.py
├── repositories/          # Database CRUD
│   ├── user.py
│   ├── class_repo.py
│   ├── student.py
│   └── attendance.py
├── reports/               # Hisobotlar
│   └── generator.py
├── utils/                 # Yordamchi funksiyalar
│   ├── phone.py           # Telefon normalizatsiya
│   ├── dates.py           # Sana formatlash
│   └── excel.py           # Excel export
├── scripts/               # Yordamchi scriptlar
│   └── create_admin.py
├── main.py                # Entry point
├── requirements.txt
├── pyproject.toml
└── .env.example
```

## 👥 Rollar va Huquqlar

### Admin
- Sinflarni yaratish va boshqarish
- Xodimlarni qo'shish va sinfga biriktirish
- Barcha o'quvchilarni ko'rish
- Hisobotlarni ko'rish va yuklab olish
- Excel formatida export

### Xodim
- Faqat biriktirilgan sinflarda ishlash
- Bugungi davomatni belgilash
- O'quvchilarni qo'shish/o'chirish
- O'quvchilarni ko'chirish (transfer)

## 🗄 Database Schema

### Asosiy Jadvallar
- `users` - Foydalanuvchilar (admin, xodim)
- `classes` - Sinflar
- `class_staff` - Xodim-sinf biriktirilishi
- `students` - O'quvchilar
- `attendance_days` - Davomat kunlari
- `attendance_items` - Davomat yozuvlari
- `transfers` - O'quvchilar transferi tarixi

## 🚀 Ishlatish

### Birinchi kirish
1. Botni ishga tushiring: `/start`
2. Telefon raqamingizni ulashing
3. Tizim sizni avtomatik aniqlaydi

### Admin uchun
1. **Sinflar** → Yangi sinf yaratish
2. **Xodimlar** → Yangi xodim qo'shish
3. Xodimni sinfga biriktirish
4. **Hisobotlar** → Kunlik yoki sinf hisobotini ko'rish

### Xodim uchun
1. **Bugungi davomat** → Sinfni tanlash
2. Har bir o'quvchi uchun status belgilash:
   - ✅ Keldi
   - 🟡 Kechikdi
   - ❌ Kelmadi
3. **O'quvchilar** → Yangi o'quvchi qo'shish

## 📊 Hisobotlar

- **Kunlik hisobot**: Bugungi barcha sinflar bo'yicha
- **Sinf hisoboti**: Tanlangan sinf uchun batafsil
- **Excel export**: O'quvchilar ro'yxati CSV formatida

## 🔒 Xavfsizlik

- Role-based access control (RBAC)
- Telefon raqam orqali autentifikatsiya
- Har bir amal uchun huquqlar tekshiruvi
- Soft delete (o'quvchilar arxivlanadi)

## 🐛 Muammolarni hal qilish

### Bot ishlamayapti
```bash
# Virtual environment faollashtirilganini tekshiring
# Windows
venv\Scripts\activate

# Botni qayta ishga tushiring
python main.py
```

### Database xatosi
```bash
# Database faylini o'chiring va qayta yarating
rm davomat.db
python scripts/create_admin.py
```

### ModuleNotFoundError
```bash
# Dependencylarni qayta o'rnating
pip install -r requirements.txt
```

## 📝 Development

### Yangi migration yaratish
```bash
alembic revision --autogenerate -m "migration_nomi"
alembic upgrade head
```

### Code style
- Type hints ishlatish
- Docstrings yozish
- Clean Architecture tamoyillariga rioya qilish

## 🤝 Hissa qo'shish

1. Fork qiling
2. Feature branch yarating (`git checkout -b feature/AmazingFeature`)
3. Commit qiling (`git commit -m 'Add some AmazingFeature'`)
4. Push qiling (`git push origin feature/AmazingFeature`)
5. Pull Request oching

## 📄 Litsenziya

MIT License

## 👨‍💻 Muallif

**Dhimmatov Dev**
- GitHub: [@dhimmatovdev](https://github.com/dhimmatovdev)
- Telegram: [@dhimmatovdev](https://t.me/dilshodhimmatov)

## 🙏 Minnatdorchilik

- [aiogram](https://github.com/aiogram/aiogram) - Telegram Bot framework
- [SQLAlchemy](https://www.sqlalchemy.org/) - ORM
- [Alembic](https://alembic.sqlalchemy.org/) - Database migrations

---

⭐ Agar loyiha foydali bo'lsa, GitHub'da star qoldiring!
