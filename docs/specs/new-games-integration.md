# Spec: 7 ta yangi o'yinni Mind Kids'ga qo'shish (yoshga moslashuvchi qiyinlik bilan)

## Maqsad
7 ta alohida HTML o'yinni `mind-kids.html` ichiga `def()` modul sifatida ko'chirish, Mind Kids uslubiga keltirish, 3 ta jon tizimiga ulash va qiyinligini tanlangan yoshga (4-6 / 7-9 / 10-12) qarab belgilash.

## Nega kerak
- Hozir yangi o'yinlar alohida fayllarda turibdi va `shared/*.js` fayllari yo'qligi sabab umuman ishlamaydi.
- Ularning dizayni boshqacha (header, til tugmalari, boshqa ranglar), bitta xatoda o'yin tugaydi — bolaga og'ir.
- Bitta o'yin uchala yosh guruhiga xizmat qiladi: katalog 30 tadan 37 taga o'sadi, har bir yosh filtrida esa +7 ta o'yin qo'shiladi.

## Qamrov ICHIDA
- 7 ta o'yin `mind-kids.html` ichida, mavjud dvigatel orqali qayta yoziladi (id 31–37, oxiriga qo'shiladi, shunda eski statistika id'lari buzilmaydi):

| # | Manba fayl | Mind Kids nomi | Kategoriya |
|---|---|---|---|
| 31 | schulte_table.html | Schulte jadvali | super |
| 32 | colors_game.html | Rang chalg'itadi | super |
| 33 | math_game.html | Yodda qo'sh | logic |
| 34 | iq_game.html | Sonlar joyi | super |
| 35 | pattern_game.html | Qora kataklar | creative |
| 36 | fly_game.html | Chivin yo'li | creative |
| 37 | mental_math.html | Og'zaki hisob | logic |

- Yangi maydon: `age:'all'` — o'yin 4-6, 7-9 va 10-12 filtrlarining har birida ko'rinadi. Kartada "4–12 yosh" deb yoziladi.
- Samarali yosh (`S.age`):
  - Filtr yosh chipida turgan bo'lsa (`4-6`/`7-9`/`10-12`), yosh shu chipdan olinadi.
  - Filtr `all` yoki kategoriya bo'lsa, o'yin boshlanishidan oldin 3 ta tugmali yosh tanlash oynasi chiqadi. Oxirgi tanlangan yosh `mk_age` kalitida saqlanadi va oynada belgilangan holda turadi.
- `makeApi()` ga `age` qo'shiladi, o'yinlar qiyinlikni `api.age` va `api.L` (1–10) orqali hisoblaydi.
- Jon: mavjud tizim (3 ❤️). Har bir xato bosish `api.miss()` orqali 1 jon oladi. Vaqt tugasa `api.done(false)` chaqiriladi (raundda jon hali olinmagan bo'lsa, 1 jon ketadi). Jon 0 bo'lsa, o'yin tugaydi (`endGame`).
- Mind Kids uslubi: `#prompt`, `#board`, `#opts`, `#timer`, `#fb` elementlari, `:root` tokenlari (`--brand`, `--ok`, `--bad`, ...), light/dark tema. Alohida header, til tugmalari va ichki score paneli bo'lmaydi.
- Ovoz: 4-6 yosh uchun topshiriq ovozda o'qiladi. `setPrompt` shartida `S.g.age==='4-6'` o'rniga samarali yosh (`S.age`) tekshiriladi.
- Barcha matn faqat o'zbekcha (lotin).
- Qiyinlik parametrlari har bir o'yin uchun bitta `AGE_CFG` obyektida saqlanadi, kod ichida magic number bo'lmaydi.
- Tekshiruvdan keyin 7 ta manba fayl o'chiriladi.

## Qiyinlik jadvali (L = daraja 1–10)

| O'yin | 4-6 | 7-9 | 10-12 |
|---|---|---|---|
| Schulte jadvali | 3×3 (L1–5), 4×4 (L6+); 45 s | 4×4, keyin 5×5; 40 s | 5×5, keyin 6×6; 35 s |
| Rang chalg'itadi | O'qishsiz variant: rangli shakl/emoji, javob sifatida rang doirachalari; 3→4 rang | So'z boshqa rangda yozilgan, tugmalar oddiy; 4→5 rang | 6 rang, tugmalar ham chalkash rangda; vaqt qisqaroq |
| Yodda qo'sh | 1–5 sonlari, 2→4 ta son, har biri 1.5 s, 3 ta javob varianti | 1–9 sonlari, 2→6 ta son, 1.1 s, 4 ta variant | 1–20, 3→8 ta son, 0.8 s, 4 ta variant |
| Sonlar joyi | 3×3 to'r, 2→5 ta son, 3 s ko'rinadi | 4×4, 3→7 ta son, 2.5 s | 5×5, 4→9 ta son, 2 s |
| Qora kataklar | 3×3, 2→4 ta katak | 4×4, 3→7 ta katak | 5×5, 4→10 ta katak |
| Chivin yo'li | 3×3, 2→5 ta strelka, 1100 ms | 5×5, 3→8 ta strelka, 850 ms | 5×5, 5→15 ta strelka, 500 ms |
| Og'zaki hisob | + 10 gacha, L6 dan − (20 gacha) | +, − 100 gacha, L6 dan × (2–5 jadvali) | +, −, ×, ÷ (10 gacha jadval), ikki xonali sonlar |

Oraliq qiymatlar daraja bo'yicha chiziqli oshadi (`lerp(min,max,(L-1)/9)`, butun songacha yaxlitlanadi).
Rang chalg'itadi va Og'zaki hisob o'yinlarida bitta daraja 5 ta savoldan iborat mini-seriya bo'ladi, har bir xato `api.miss()` chaqiradi.

## Qamrov TASHQARISIDA (bularni qilma!)
- Eski 30 ta o'yinga yoshga qarab qiyinlik qo'shish. Keyingi versiyada, yangi 7 tasi sinovdan o'tgach.
- ru/en tillari va til almashtirish tugmalari. Mind Kids faqat uz.
- `shared/*.js` (telegram, theme, audio, scoreManager) ni tiklash. Mind Kids'ning o'z `Store`, `Snd`, `hap`, tema tizimi ishlatiladi.
- Yulduz/statistikani har bir yosh uchun alohida saqlash. Hozircha statistika o'yin id bo'yicha umumiy.
- Yangi `art` rasmlari. Mavjud `a1`–`a6` sinflari qayta ishlatiladi.
- O'xshash o'yinlarni birlashtirish (#24 va Schulte, #4 va Og'zaki hisob). Foydalanuvchi qarori bilan ikkalasi ham qoladi.

## Texnik
- Fayl: `mind-kids.html` (bitta fayl, build yo'q).
- O'yin registri: `def({...})`, 31–37-o'yinlar `/* 30 */` blokidan keyin qo'shiladi.
- Filtr: `renderHome()` va `nextGame()` ichidagi `g.age===filter` sharti `g.age===filter||g.age==='all'&&AGES.includes(filter)` ga o'zgaradi.
- Karta: `g.age.replace('-','–')` o'rniga `ageLabel(g)` ishlatiladi (`all` bo'lsa "4–12").
- `openGame(id)`: `g.age==='all'` bo'lsa, samarali yosh aniqlanadi (filtrdan yoki yosh tanlash oynasidan), keyin `S.age` o'rnatiladi. Qolgan o'yinlar uchun `S.age=g.age`.
- `makeApi()`: `age:S.age` maydoni qo'shiladi.
- Config: `AGE_CFG` obyekti, masalan `{schulte:{'4-6':{...},'7-9':{...},'10-12':{...}}, ...}`.
- Storage: yangi kalit `mk_age` (localStorage + Telegram CloudStorage, `Store` orqali).
- DB / migration: yo'q.

## Qoidalar (EARS)
- QACHON foydalanuvchi yosh chipi (4-6/7-9/10-12) tanlangan holatda `age:'all'` o'yinni ochsa
  TIZIM o'yinni shu yosh parametrlari bilan darhol boshlashi SHART
  VA yosh tanlash oynasini ko'rsatmasligi SHART.

- QACHON foydalanuvchi `all` yoki kategoriya filtrida `age:'all'` o'yinni ochsa
  TIZIM 3 ta yosh tugmasini ko'rsatishi SHART
  VA `mk_age` dagi oxirgi tanlovni belgilangan holda ko'rsatishi SHART
  VA tanlovdan keyin uni `mk_age` ga saqlashi SHART.

- QACHON o'yinchi noto'g'ri katak, son yoki tugmani bossa
  TIZIM 1 ta jonni olishi SHART (`api.miss()`)
  VA jon qolgan bo'lsa, raundni davom ettirishi SHART (o'yin tugamaydi).

- AGAR raund vaqti tugasa
  TIZIM raundni xato deb yakunlashi SHART (`api.done(false)`)
  VA shu raundda allaqachon jon olingan bo'lsa, ikkinchi jonni olMASLIGI SHART.

- AGAR jon 0 ga tushsa
  TIZIM o'yinni `endGame()` bilan yakunlashi SHART
  VA qolgan taymerlarni `cleanup()` orqali to'xtatishi SHART.

- QACHON samarali yosh `4-6` bo'lsa
  TIZIM topshiriqni ovozda o'qishi SHART
  VA "Rang chalg'itadi" o'yinida o'qishni talab qiladigan so'zlarni ko'rsatMASLIGI SHART.

- QACHON o'yinchi 10-darajani tugatsa
  TIZIM o'yinni g'alaba bilan yakunlashi SHART (mavjud `S.level>=10` mantig'i).

## Acceptance criteria (tugadi deganda)
- [ ] 4-6, 7-9 va 10-12 filtrlarining har birida 7 ta yangi o'yin ko'rinadi, kartada "4–12 yosh" yozuvi bor.
- [ ] `Barchasi` filtrida yangi o'yin ochilganda yosh so'raladi, keyingi safar oxirgi tanlov belgilangan turadi.
- [ ] Bitta o'yin 4-6 va 10-12 yoshda ochilganda qiyinlik farqi ko'rinib turadi (to'r o'lchami, sonlar soni, tezlik).
- [ ] Har bir o'yinda xato bosilganda 1 ta ❤️ ketadi, silkinish animatsiyasi va ovoz ishlaydi, 3 ta xatodan keyin o'yin tugaydi.
- [ ] Vaqt tugaganda bir raundda 2 ta jon ketmaydi.
- [ ] Light va dark temada yangi o'yinlar Mind Kids uslubida ko'rinadi, 360px kenglikda gorizontal scroll yo'q.
- [ ] Eski 30 ta o'yin va ularning statistikasi o'zgarmagan (id 1–30 joyida).
- [ ] Brauzer konsolida xato yo'q.
- [ ] 7 ta manba fayl o'chirilgan.

## Test
Pul yoki xavfsizlikka tegmaydi, shuning uchun test majburiy emas. Minimal tekshiruv:
- `AGE_CFG` uchun Node skripti: har bir o'yin × 3 yosh × L1..10 kombinatsiyasida parametrlar chegarada (to'r ichiga sig'adi, sonlar soni to'r kataklaridan oshmaydi, vaqt > 0).
- Playwright bilan qo'lda smoke test: har bir o'yinni 3 yoshda ochish, 3 marta xato bosish, natijada o'yin tugashini ko'rish.
