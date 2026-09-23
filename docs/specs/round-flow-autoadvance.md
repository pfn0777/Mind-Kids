# Spec: Xatodan keyin avto-o'tish + ovozni bir marta aytish

## Maqsad
Xato javobdan keyin o'yin "Davom etish / Продолжить" tugmasini kutib to'xtab qolmasin. Jon kamaysin, to'g'ri javob va tushuntirish qisqa vaqt ko'rinib tursin, keyin o'yin o'zi keyingi savolga o'tsin. Ovozli topshiriq bitta o'yin davomida bir xil matnni faqat bir marta o'qisin.

## Nega kerak
- Hozir xato qilinganda o'yin to'xtaydi. Bola tugmani bosmasa, o'yin davom etmaydi ("Матрица узоров" skrinshoti). Bu to'g'ri javobdagi oqimga zid: u yerda o'yin 1.2 soniyada o'zi o'tadi.
- 4–6 yosh o'yinlarida bir xil savol matni ("Qaysi biri ortiqcha?" va h.k.) har raundda qayta o'qiladi. Bu bolani charchatadi.

## Qamrov ICHIDA
- **Umumiy dvijok** (`finishRound`, `playChoice`, `setPrompt`). Bu barcha `gen` (savol-variant) o'yinlarga va `mount` o'yinlariga (`a.done(false, …)`) bir xil ta'sir qiladi.
- **Xato javob / vaqt tugashi / mount o'yinda `a.done(false)`:**
  - jon 1 taga kamayadi (bu mexanizm allaqachon bor: `S.rl` orqali ikki marta kamaymaydi);
  - to'g'ri variant yashil bilan ko'rsatiladi, `#fb` da tushuntirish chiqadi (mavjud);
  - `WRONG_ADVANCE_MS` (2800 ms) o'tgach, o'yin o'zi `nextRound()` ni chaqiradi.
- **To'g'ri javob:** mavjud 1200 ms avto-o'tish saqlanadi. Bu raqam `OK_ADVANCE_MS` konstantasiga chiqariladi (magic number bo'lmasin).
- **Oxirgi raund** (jon 0 ga tushdi yoki 10-daraja): tugma chiqmaydi. Mos kechikishdan keyin (to'g'ri javobda `OK_ADVANCE_MS`, xatoda `WRONG_ADVANCE_MS`) o'yin o'zi `endGame()` ga o'tadi. `nextRound()` buni allaqachon qiladi.
- **`#next` tugmasi olib tashlanadi:** DOM elementi, `onclick` handler, `cleanup()` dagi yashirish qatori va ishlatilmay qolgan `next_btn` / `finish_btn` i18n kalitlari (uz/ru/en). Buni faqat `node scripts/check-i18n.js` o'tsa qilamiz.
- **Ovoz — bir marta:** `setPrompt(h, say)` avtomatik o'qishni (faqat 4–6 yosh) shunday qiladi: shu o'yin sessiyasida `lang + '|' + say` kaliti oldin o'qilmagan bo'lsagina o'qiydi. O'qilgan kalitlar `S.spoken` (Set) da saqlanadi. `openGame()` da (jumladan "Qayta o'ynash" bosilganda) u tozalanadi.
- **🗣 (`#speak`) tugmasi** har doim o'qiydi. Qo'lda bosish cheklanmaydi va `S.spoken` ga ta'sir qilmaydi.

## Qamrov TASHQARISIDA (bularni qilma!)
- Xatoda shu savolni qayta berish. Tanlangan xulq: keyingi savolga o'tish.
- Jonlar soni (3), ball formulasi, darajalar soni (10) va `endGame` natija ekrani o'zgarmaydi.
- Statistika/saqlash logikasi (`saveStats`, `per`, `Store`) o'zgarmaydi.
- Mount o'yinlarining ichki "2–3 urinish" (`miss>=N`, `hint`) logikasi o'zgarmaydi. Faqat raund yakunidagi tugma avto-o'tishga almashadi.
- Xato tushuntirishini ovozda o'qish. Bu keyingi versiyaga qoldiriladi.
- "Tezroq o'tish uchun bosing" funksiyasi. Kerak bo'lsa keyin qo'shiladi.
- Boshqa o'yinlardagi kontent/generator xatolari.

## Texnik
- Fayl: `mind-kids.html` (yagona fayl)
  - `S` obyekti (~355-qator): `spoken: new Set()` maydoni qo'shiladi.
  - Konstantalar: `OK_ADVANCE_MS = 1200`, `WRONG_ADVANCE_MS = 2800` (Engine bo'limi boshida).
  - `setPrompt` (~362): dedupe logikasi qo'shiladi.
  - `cleanup` (~373): `#next` qatori olib tashlanadi.
  - `finishRound` (~384–392): `else` shoxidagi tugma o'rniga `S.timers` ga tok-guard bilan `setTimeout(nextRound, delay)` qo'shiladi.
  - `openGame` (~410): `S.spoken = new Set()`.
  - ~915-qator: `$('#next').onclick` olib tashlanadi. `#next` HTML elementi va CSS'i ham olib tashlanadi.
  - i18n lug'atlaridan `next_btn`, `finish_btn` olib tashlanadi.
- DB / migration / config: yo'q.

## Qoidalar (EARS)
- QACHON foydalanuvchi noto'g'ri variantni tanlasa
  TIZIM jonni 1 taga kamaytirishi, to'g'ri variantni yashil qilishi va tushuntirishni ko'rsatishi SHART
  VA `WRONG_ADVANCE_MS` dan keyin tugma bosilmasa ham keyingi raundni boshlashi SHART.
- QACHON raund vaqti tugasa yoki mount o'yin `done(false)` chaqirsa
  TIZIM xuddi shu avto-o'tish oqimini bajarishi SHART.
- AGAR avto-o'tish kutilayotganda o'yin yopilsa, qayta ochilsa yoki boshqa o'yinga o'tilsa
  TIZIM eski taymerni ishga tushirMASLIGI SHART (`S.tok` tekshiruvi + `cleanup()` dagi `S.timers` tozalash).
- AGAR bu raundda jon 0 ga tushsa yoki 10-daraja bo'lsa
  TIZIM kechikishdan keyin natija ekraniga (`endGame`) o'tishi SHART va hech qanday tugma ko'rsatMASLIGI SHART.
- QACHON 4–6 yosh o'yinida `setPrompt` ovozli matn bilan chaqirilsa
  VA shu matn shu tilda joriy o'yin sessiyasida allaqachon o'qilgan bo'lsa
  TIZIM uni qayta o'qiMASLIGI SHART (lekin `S.say` yangilanadi, 🗣 bosilsa o'qiladi).
- QACHON foydalanuvchi 🗣 tugmasini bossa
  TIZIM joriy `S.say` ni har doim o'qishi SHART.
- AGAR xato raundda jon bir marta kamaygan bo'lsa (`S.rl > 0`)
  TIZIM `finishRound` da uni ikkinchi marta kamaytirMASLIGI SHART (mavjud xulq saqlanadi).

## Acceptance criteria
- [ ] "Матрица узоров" da xato variant bosilsa: jon 3→2, to'g'ri variant yashil, tushuntirish ko'rinadi, ~2.8 soniyadan keyin keyingi daraja o'zi boshlanadi. Tugma chiqmaydi.
- [ ] 3 ta xatodan keyin natija ekrani o'zi ochiladi ("Не завершено" / "Tugallanmadi"), tugma bosish shart emas.
- [ ] 10-darajadagi to'g'ri javobdan keyin natija ekrani o'zi ochiladi.
- [ ] Taymerli o'yinda vaqt tugasa, jon kamayadi va o'yin o'zi o'tadi.
- [ ] Mount o'yinda (masalan Memory Match yoki "Farqni top PRO") raund yutqazilsa, o'yin o'zi o'tadi.
- [ ] Avto-o'tish kutilayotganda ✕ bilan yopib, boshqa o'yin ochilsa, eski o'yin "o'tib ketmaydi" (konsolda xato yo'q, yangi o'yin buzilmaydi).
- [ ] 4–6 yosh "Qaysi biri ortiqcha?" o'yinida savol matni faqat 1-raundda ovozda o'qiladi, 2–10-raundlarda o'qilmaydi. 🗣 bosilsa o'qiladi. "Qayta o'ynash" dan keyin yana 1 marta o'qiladi.
- [ ] `#next` elementi va `next_btn`/`finish_btn` kalitlari kodda qolmagan (`grep` bo'sh).
- [ ] `node scripts/check-i18n.js` va `node scripts/check-age-cfg.js` o'tadi.
- [ ] Brauzer konsolida yangi xato yo'q.

## Test
Pul/xavfsizlikka tegmaydi, shuning uchun alohida test fayli majburiy emas. Tekshiruv brauzerda (Playwright/DevTools) acceptance criteria bo'yicha qilinadi, mavjud `scripts/check-*.js` ham ishga tushiriladi.
