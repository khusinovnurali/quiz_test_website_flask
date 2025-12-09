# Quiz Master

Online test platformasi - o'qituvchilar uchun test yaratish va o'quvchilar uchun testlarni yechish imkoniyati.

## Imkoniyatlar

- Test yaratish va tahrirlash
- Testlarni fan/bo'lim/mavzu bo'yicha turkumlash
- Foydalanuvchilarni ro'yxatdan o'tkazish va boshqarish
- Test natijalarini saqlash va ko'rish
- Admin panel orqali tizimni boshqarish

## O'rnatish

1. Python 3.8+ versiyasini o'rnating
2. Loyihani clone qiling:
```bash
git clone https://github.com/yourusername/quiz_master.git
cd quiz_master
```
3. Virtual muhit yarating va faollashtiring:
```bash
python -m venv venv
# Windows uchun
venv\Scripts\activate
# Linux/Mac uchun
source venv/bin/activate
```
4. Kerakli kutubxonalarni o'rnating:
```bash
pip install -r requirements.txt
```

## Database yaratish

1. Dastlab ma'lumotlar bazasini yarating:
```bash
python scripts/create_admin.py --init-db
```
2. Admin foydalanuvchini yarating:
```bash
python scripts/create_admin.py
```

## Ishga tushirish

1. Development server:
```bash
python run.py
```
2. Browser orqali http://localhost:5000 ga kiring

## Foydalanish

### Administrator uchun
- Admin login: admin@quiz.com
- Standart parol: admin123
- Admin panel orqali fanlar, bo'limlar va testlarni boshqarish mumkin
- Foydalanuvchilarni boshqarish

### O'qituvchi uchun
- Ro'yxatdan o'ting
- Test yarating va tahrirlang
- Natijalarni ko'ring

### O'quvchi uchun
- Ro'yxatdan o'ting
- Testlarni yeching
- Natijalarni ko'ring

## Texnik ma'lumotlar

- Framework: Flask
- Database: SQLite
- Authentication: Flask-Login
- Forms: Flask-WTF
- ORM: SQLAlchemy

## Fayllar strukturasi

```
quiz_master/
├── app/
│   ├── models/         # Database modellari
│   ├── controllers/    # Route kontrollerlar
│   ├── templates/      # HTML shablonlar
│   └── static/         # CSS, JS, rasmlar
├── scripts/           # Utility skriptlar
├── config/           # Konfiguratsiya fayllari
└── instance/         # Database va maxfiy ma'lumotlar
```

## Litsenziya

MIT
