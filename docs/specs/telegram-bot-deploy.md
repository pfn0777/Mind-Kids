# Spec: Telegram bot + Mini App deploy (Vercel + Hetzner)

## Maqsad
Mind Kids uchun aiogram botini yaratish. Bot `/start` bosilganda rasm, o'zbekcha salomlashuv va mini appni ochadigan tugmani yuboradi. Admin uchun `/stats` buyrug'i bo'ladi. Mini app (`mind-kids.html`) Vercel'da statik sahifa sifatida, bot esa Hetzner serverida (178.104.103.113) systemd servisi sifatida ishlaydi.

## Nega kerak
- Hozir mini app faqat lokal faylda turibdi. Telegram'da ochish uchun unga https manzil va uni ochadigan bot kerak.
- Egasi (admin) botdan nechta odam foydalanayotganini bilishi kerak.

## Qamrov ICHIDA
- **Bot (`bot/bot.py`, aiogram 3, long polling):**
  - `/start` bosilganda `WELCOME_PHOTO_PATH` dagi rasm yuboriladi. Uning caption'i o'zbekcha salomlashuv matni, ostida esa inline `web_app` tugmasi ("🧠 O'yinlarni ochish") bo'ladi. Tugma `WEBAPP_URL` ni ochadi.
  - Bot ishga tushganda `setChatMenuButton` orqali default Menu Button'ni ham `WEBAPP_URL` ga o'rnatadi.
  - `/start` bosgan foydalanuvchi SQLite'ga yoziladi: `user_id`, `first_seen`, `last_seen` (UTC). Takroriy `/start` yangi qator qo'shmaydi, faqat `last_seen` ni yangilaydi.
  - `/stats` faqat `ADMIN_ID` uchun ishlaydi va quyidagilarni ko'rsatadi: jami noyob foydalanuvchilar, bugun qo'shilgan yangilar (Toshkent vaqti, UTC+5), oxirgi 7 kunda qo'shilgan yangilar, oxirgi 7 kunda faol bo'lganlar (`last_seen`).
  - Boshqa har qanday xabarga qisqa matn va o'sha mini app tugmasi bilan javob beriladi.
  - Rasmning `file_id` si birinchi yuklashdan keyin xotirada keshlanadi (Dunyo Hotel `WelcomePhoto` naqshi).
- **Config (`.env`, faqat serverda):** `BOT_TOKEN`, `WEBAPP_URL` (https), `ADMIN_ID` (8264870741), `WELCOME_PHOTO_PATH`, `DB_PATH` (default `data/users.db`), `LOG_LEVEL`. Repo'da faqat `bot/.env.example` turadi.
- **Vercel:** repo ildizida `vercel.json` bo'ladi. U `/` ni `mind-kids.html` ga rewrite qiladi (fayl nomi o'zgarmaydi, check-skriptlar buzilmasin). Bot fayllari deploy'ga kirmasligi uchun `.vercelignore` qo'shiladi. Deploy'ni va domenni egasining o'zi qiladi, keyin URL'ni beradi.
- **Hetzner deploy:**
  - Bot kodi `/opt/mindkids-bot` ga joylanadi. Python venv va `requirements.txt` (aiogram, python-dotenv, aiosqlite) o'rnatiladi.
  - systemd unit: `mindkids-bot.service`, `Restart=always`, alohida (root emas) `mindkids` foydalanuvchisi nomidan ishlaydi.
  - `deploy/deploy.ps1` skripti Windows'dan fayllarni scp orqali serverga ko'chiradi, venv/requirements'ni yangilaydi va servisni qayta ishga tushiradi. `.env` va `data/` ga tegmaydi.
  - Serverda boshqa botlar bo'lsa, ularga tegilmaydi (boshqa unit nomi, boshqa papka).
- **Test:** `bot/test_bot.py` (pytest). U admin tekshiruvi, stats hisobi va user upsert'ni tekshiradi.

## Qamrov TASHQARISIDA (bularni qilma!)
- Rus/ingliz tili — 1-versiyada bot faqat o'zbekcha. Keyinroq qo'shiladi.
- Mini appni ochganlarni sanash (HTTP endpoint, domen, SSL) — `/start` bosmay ochganlar sanalmaydi, bu qabul qilingan cheklov.
- Ota-onaga eslatma, progress hisoboti, broadcast — 2-versiya.
- Telegram Stars / to'lov — 2-versiya.
- Mini app ichidagi o'yin statistikasini botga yuborish (`sendData`, API) — qilinmaydi.
- `mind-kids.html` ni o'zgartirish — qilinmaydi (faqat `vercel.json` rewrite qilinadi).
- Webhook, Docker, CI/CD — long polling va deploy skripti yetarli.
- Foydalanuvchi ismi, username yoki telefonini saqlash — saqlanmaydi (bolalar ilovasi, minimal ma'lumot: faqat `user_id`).

## Texnik
- Yangi fayllar:
  - `bot/bot.py`: Settings, TEXTS (uz), handlerlar, `main()`.
  - `bot/db.py`: SQLite (aiosqlite) — `init`, `upsert_user`, `stats`.
  - `bot/requirements.txt`, `bot/.env.example`, `bot/test_bot.py`.
  - `bot/media/welcome.jpg`: egasi beradigan rasm.
  - `deploy/mindkids-bot.service`, `deploy/deploy.ps1`.
  - `vercel.json`, `.vercelignore`, `.gitignore` (`.env`, `*.db`, `__pycache__`, `.venv`, `.playwright-mcp/`).
- DB: `users(user_id INTEGER PRIMARY KEY, first_seen TEXT, last_seen TEXT)`. Migration kerak emas, jadval `CREATE TABLE IF NOT EXISTS` bilan yaratiladi.
- Konstantalar: `TASHKENT = UTC+5`, `STATS_WINDOW_DAYS = 7` (magic number yo'q).
- Locale: faqat `uz`, `TEXTS` lug'atida (keyin `ru` qo'shish oson bo'lsin).

## Qoidalar (EARS)
- QACHON foydalanuvchi `/start` yuborsa
  TIZIM uni DB'ga upsert qilishi SHART
  VA rasm, caption va `web_app` tugmasini yuborishi SHART.

- AGAR rasm yuborilmasa (fayl yo'q, Telegram xatosi)
  TIZIM xuddi shu matn va tugmani oddiy xabar sifatida yuborishi SHART
  VA xatoni log qilishi SHART (silent catch yo'q).

- AGAR DB'ga yozishda xato bo'lsa
  TIZIM xatoni log qilishi SHART
  VA foydalanuvchiga baribir salomlashuv va tugmani yuborishi SHART (stats uchun foydalanuvchi bloklanmaydi).

- QACHON `/stats` ni `ADMIN_ID` yuborsa
  TIZIM 4 ta raqamni (jami, bugun, 7 kun yangi, 7 kun faol) yuborishi SHART.

- AGAR `/stats` ni boshqa foydalanuvchi yuborsa
  TIZIM uni oddiy "boshqa xabar" deb ko'rib, fallback javobini berishi SHART
  VA statistika raqamlarini ko'rsatmasligi SHART
  VA buyruq mavjudligini oshkor qilmasligi SHART.

- AGAR `.env` da `BOT_TOKEN`, `WEBAPP_URL`, `ADMIN_ID` yo'q bo'lsa yoki `WEBAPP_URL` https bilan boshlanmasa
  TIZIM ishga tushmasligi va qaysi qiymat noto'g'ri ekanini aniq aytishi SHART.

- QACHON bot qayta ishga tushsa
  TIZIM navbatdagi eski update'larni tashlab yuborishi SHART (`drop_pending_updates`).

## Acceptance criteria
- [ ] `https://<vercel-domen>/` ochilganda Mind Kids home ekrani chiqadi, konsolda xato yo'q.
- [ ] Telegram'da `/start` bosilganda rasm, o'zbekcha matn va tugma keladi. Tugma mini appni Telegram ichida ochadi, salomlashuvda ism chiqadi (`initDataUnsafe` ishlaydi).
- [ ] Bot chatidagi Menu Button ham mini appni ochadi.
- [ ] Admin (8264870741) `/stats` yuborganda to'g'ri raqamlar keladi. Ikkinchi akkauntdan `/start` bosilgach, jami son 1 taga oshadi.
- [ ] Admin bo'lmagan akkaunt `/stats` yuborganda statistika emas, fallback javobi keladi.
- [ ] Serverda `systemctl status mindkids-bot` holati `active (running)`, `reboot` dan keyin bot o'zi ko'tariladi.
- [ ] Servis root emas, `mindkids` foydalanuvchisi nomidan ishlaydi. `.env` ning huquqi `600`.
- [ ] `.env` va `*.db` git'da yo'q (`git status` toza).
- [ ] `pytest bot/` o'tadi. `node scripts/check-i18n.js` va `node scripts/check-age-cfg.js` avvalgidek o'tadi.

## Test (admin huquqi va token xavfsizligi tufayli MAJBURIY)
- `is_admin`: `ADMIN_ID` → true, boshqa ID → false, `from_user` yo'q → false.
- `/stats` handleri admin bo'lmagan foydalanuvchi uchun raqamlarni qaytarmaydi.
- `upsert_user`: birinchi chaqiruv qator qo'shadi, ikkinchisi `first_seen` ni o'zgartirmay faqat `last_seen` ni yangilaydi.
- `stats`: "bugun" Toshkent vaqti bo'yicha hisoblanadi (UTC 20:00 da qo'shilgan foydalanuvchi Toshkentda ertangi kunga tushadi).
- `load_settings`: token yo'q → `ConfigError`, `WEBAPP_URL=http://...` → `ConfigError`, `ADMIN_ID=abc` → `ConfigError`.
