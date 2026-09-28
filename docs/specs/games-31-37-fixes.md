# Spec: 31–37-o'yinlar logikasini tuzatish

## Maqsad
Oxirgi qo'shilgan 7 ta o'yindagi (31–37) logik xatolarni tuzatish. Xato bosilgan katak bosilmay qolmasin. Xotira o'yinlarida tavakkal bosib topishning iloji bo'lmasin. "Chivin yo'li" 10–12 yoshda sekinroq bo'lsin va ketma-ket kelgan bir xil qadamlar ko'rinsin. "Og'zaki hisob" murakkabligi darajaga qarab o'ssin.

## Nega kerak
- **31 Schulte:** noto'g'ri bosilgan son `bad` holatida qolib ketadi va handler uni boshqa qabul qilmaydi. Navbat o'sha songa yetganda o'yin qotib qoladi va faqat vaqt tugashi bilan tugaydi.
- **36 Chivin yo'li:** xatodan keyin "Yana urinib ko'ring" chiqadi va o'sha taxtada qayta bosish mumkin bo'ladi. Shunda bola chivinni xotiradan emas, tavakkal bosib topadi. Raund qaytadan boshlanmaydi.
- **34 Sonlar joyi:** xuddi shu muammo bor, xatodan keyin qolgan kataklarni tavakkal bosib chiqish mumkin.
- **36, 10–12 yosh:** har qadam 500 ms va 15 tagacha qadam bor. Bu juda tez.
- **36, ketma-ket bir xil yo'nalish (⬆️⬆️):** katakdagi matn o'zgarmaydi, shuning uchun ikkita qadam bo'lgani ko'rinmaydi.
- **36, o'lik kod:** yo'l yasalayotganda `if(!moved)path.push(dirs[0])` qatori chivinni surmasdan strelka qo'shadi. Markazdan boshlanganda bu holat hech qachon yuz bermaydi, lekin kodni o'qiganni chalg'itadi.
- **37 Og'zaki hisob:** 10–12 yoshda bo'lish trivial (bo'linuvchi ≤ 10, masalan `10 ÷ 5`). 7–9 va 10–12 yoshda sonlar diapazoni darajaga (L) qarab o'smaydi.

## Qamrov ICHIDA

**F1 — Schulte (31): xato son qayta bosiladigan bo'ladi**
- Noto'g'ri son bosilganda unga `bad` klassi qo'yiladi va `SCHULTE_BAD_MS` (400 ms) dan keyin olib tashlanadi. Olib tashlash `a.later` orqali bo'ladi (tok-guard bilan).
- Handler'dagi `bad` tekshiruvi QOLADI: bu tez ikki marta bosishda ikkita jon ketishidan himoya qiladi. `bad` klassi olib tashlangach katak yana bosiladigan bo'ladi. O'zgaradigan yagona narsa shu klassni vaqt o'tgach olib tashlash.
- Jon logikasi o'zgarmaydi: `a.miss()`, 3-xatoda `done(false)`.

**F2 — Chivin (36) va Sonlar joyi (34): bitta xato raundni tugatadi**
- Javob bosqichida noto'g'ri katak bosilsa, raund darhol tugaydi:
  - aniq 1 ta jon ketadi;
  - to'g'ri javob ko'rsatiladi: 36 da chivin katagi `ok` klassi va 🪰 bilan, 34 da qolgan sonlar `ok` bilan (bu hozirgi `miss` shoxidagi ko'rsatish);
  - `a.done(false, {msg})` chaqiriladi, keyin mavjud `WRONG_ADVANCE_MS` avto-o'tishi yangi raundni (yangi yo'l yoki yangi joylashuv bilan) boshlaydi.
- "Yana urinib ko'ring" hint'i va shu taxtada qayta bosish bu ikki o'yindan olib tashlanadi.
- Bir jondan ortiq ketmasligi kerak. Buning uchun `a.done(false)` o'zi chaqiriladi (`S.rl=0` bo'lgani uchun `finishRound` jonni o'zi oladi), yoki `a.miss()` + `a.done(false)` birga ishlatiladi (`S.rl` ikkinchi marta olishga yo'l qo'ymaydi). Qaysi biri tanlansa ham natija: 1 ta jon.

**F3 — Chivin (36): tezlik va qadamlar orasidagi tanaffus**
- `AGE_CFG.fly` ning har bir yoshiga yangi `gap: 250` (ms) kaliti qo'shiladi.
- `10-12`: `speed: 500 → 700`, `c2: 15 → 12`.
- `7-9` va `4-6`: `speed` va `c2` o'zgarmaydi.
- Ko'rsatish sikli: strelka `speed` ms ko'rinib turadi, keyin katak `gap` ms bo'sh turadi, keyin keyingi strelka chiqadi. Oxirgi strelkadan keyin katak bo'shatiladi va javob bosqichi boshlanadi.
- Sikldan oldingi boshlang'ich kutish (chivin markazda ko'rinib turadi) avvalgidek `speed` ms.
- "Pop" animatsiya ixtiyoriy. Qo'shilsa, faqat CSS tokenlari bilan va mavjud animatsiya uslubida qilinadi.

**F4 — Chivin (36): o'lik kod**
- Yo'l generatsiyasidagi `moved` o'zgaruvchisi va `if(!moved)path.push(dirs[0])` olib tashlanadi. Tsikl birinchi mos yo'nalishni olib `break` qiladi. Markazdan boshlanib n ≥ 3 bo'lganda har doim kamida bitta mos yo'nalish bo'ladi.

**F5 — Og'zaki hisob (37): darajaga bog'langan murakkablik**
- 7–9 va 10–12 yoshlar uchun har bir amal konfigiga `max1` (L=1 dagi yuqori chegara) qo'shiladi. `max` L=10 dagi yuqori chegara bo'lib qoladi. Samarali yuqori chegara: `lerp(max1, max, L)`. `max1` yo'q bo'lsa `max` ishlatiladi, shuning uchun 4–6 yosh o'zgarmaydi.
- Bo'lish (10–12): `div:{min:2,max:10,a1:3,a2:12}`. Bo'luvchi `y = ri(min,max)`, javob `ans = ri(2, lerp(a1,a2,L))`, bo'linuvchi `x = y*ans`. L=1 da javob 2..3, L=10 da 2..12.
- 7–9 da ko'paytirish faqat `mulFromL` (6) dan boshlab chiqadi. Shuning uchun amalda samarali chegara L6 da `lerp(3,7,6)=5` dan L10 da `7` gacha o'sadi, L1 dagi `max1:3` hech qachon ishlatilmaydi. Bu ataylab qilingan: L6 dagi 5 eski qiymatga teng.
- Taklif qilingan qiymatlar (barchasi `AGE_CFG.mental` ichida):
  - `7-9`: `add:{min:10,max1:40,max:100}`, `sub:{min:10,max1:40,max:100}`, `mul:{min:2,max1:3,max:7}`, `mulFromL:6`, `time:8`
  - `10-12`: `add:{min:10,max1:50,max:99}`, `sub:{min:10,max1:50,max:99}`, `mul:{min:2,max1:5,max:10}`, `div:{min:2,max:10,a1:3,a2:12}`, `time:6`
- 7–9 da qo'shish natijasi samarali `max` bilan cheklanadi (mavjud formula: `x=ri(min,mx-min)`, `y=ri(min,mx-x)`).

**F6 — `scripts/check-age-cfg.js`**
- fly: `Number.isInteger(c.gap) && c.gap >= 100 && c.gap <= c.speed`. Bundan tashqari har L uchun qadamlar soni ≤ `FLY_MAX_STEPS` (12) bo'lishi tekshiriladi.
- mental: `max1` bor bo'lsa, `min <= max1 <= max`. 7–9 da har L uchun `lerp(max1,max,L) - min >= min` (capped-sum formulasi uchun).
- mental div: `a1 >= 3`, `a1 <= a2`, `min >= 2`.

## Qamrov TASHQARISIDA (bularni qilma!)
- 32 Rang chalg'itadi, 33 Yodda qo'sh, 35 Qora kataklar — auditda jiddiy xato topilmadi, ularga tegilmaydi.
- 35 dagi "xatodan keyin davom etish" xulqi o'zgarmaydi. U yerda bir nechta nishon bor, bitta xato raundni tugatmaydi.
- 37 da `time` darajaga qarab qisqarmaydi (keyinroq ko'rib chiqiladi).
- 4–6 yosh uchun `AGE_CFG.mental` va `AGE_CFG.fly` qiymatlari (`gap`dan tashqari) o'zgarmaydi.
- Jonlar soni, `finishRound` / `nextRound` oqimi, ball formulasi, statistika o'zgarmaydi.
- 1–30-o'yinlar.
- Yangi i18n kalitlari qo'shilmaydi. Hint'lar olib tashlanadi, mavjud `msg` matnlari qoladi.

## Texnik
- Fayl: `mind-kids.html` (yagona fayl, zich uslub saqlanadi, qayta formatlanmaydi)
  - `AGE_CFG` (~758): `fly` ga `gap`, `10-12` ga `speed`/`c2`; `mental` ga `max1`, `div` ga `a1/a2`.
  - Yangi konstanta `SCHULTE_BAD_MS=400` (Age-scaled difficulty bo'limida, `AGE_CFG` dan oldin).
  - 31 (~773–775): `bad` tekshiruvi va `a.later` bilan olib tashlash.
  - 34 (~817–821): xato shoxi → darhol ko'rsatish + `done(false)`. `bad` tekshiruvi shu raundda ortiqcha bo'lib qoladi, lekin zarari yo'q.
  - 36 (~836–849): yo'l generatsiyasi (F4), `showArrow` sikli `gap` bilan (F3), xato shoxi (F2).
  - 37 (~852–860): `gen` ichida samarali max va yangi `div` formulasi.
- `scripts/check-age-cfg.js`: F6 dagi tekshiruvlar. `FLY_MAX_STEPS=12` skriptdagi konstanta.
- DB / migration / config: yo'q.
- Locale: yangi kalit yo'q. `node scripts/check-i18n.js` o'tishi kerak.

## Qoidalar (EARS)
- QACHON Schulte'da noto'g'ri son bosilsa, TIZIM unga `bad` qo'yishi va 400 ms dan keyin olib tashlashi SHART. VA o'sha son keyinroq navbati kelganda bosilsa, to'g'ri deb qabul qilishi SHART.
- AGAR `bad` katak 400 ms ichida qayta bosilsa, TIZIM uni e'tiborsiz qoldirishi SHART (`S.lives` o'zgarmaydi). AGAR o'sha katak 400 ms dan keyin qayta bosilsa va u hali ham navbatdagi son bo'lmasa, TIZIM 1 ta jon olishi SHART.
- QACHON Schulte'da `dim` katak bosilsa, TIZIM hech narsa qilmasligi SHART (jon ketmaydi).
- QACHON Chivin yoki Sonlar joyida javob bosqichida noto'g'ri katak bosilsa, TIZIM aniq 1 ta jon olishi, to'g'ri javobni `ok` bilan ko'rsatishi va raundni `done(false)` bilan tugatishi SHART. VA shu raundda boshqa bosishlarni qabul qilmasligi SHART.
- QACHON raund xato bilan tugasa VA jon qolgan bo'lsa, TIZIM `WRONG_ADVANCE_MS` dan keyin yangi yo'l (yoki joylashuv) bilan yangi raund boshlashi SHART.
- QACHON Chivin strelkalarni ko'rsatayotgan bo'lsa, TIZIM har ikki strelka orasida katakni `gap` ms bo'sh qoldirishi SHART, yo'nalishlar bir xil bo'lsa ham.
- AGAR ko'rsatish bosqichida katak bosilsa, TIZIM uni e'tiborsiz qoldirishi SHART (javob handler'i hali o'rnatilmagan).
- QACHON 37 da bo'lish misoli yaratilsa, TIZIM `x % y === 0`, `2 <= y <= 10` va `2 <= x/y <= lerp(3,12,L)` shartlarini bajarishi SHART.

## Acceptance criteria (tugadi deganda)
Barchasi `python -m http.server 8765` → `http://localhost:8765/mind-kids.html` sahifasida Playwright `page.evaluate` bilan tekshiriladi. Yordamchi funksiyalar: `wait = ms => new Promise(r => setTimeout(r, ms))`; raund ochish: `await openGame(id,'10-12'); await wait(300)`; ma'lum darajani ochish: `S.level = L; startRound()`.

**Umumiy**
- [ ] `node scripts/check-age-cfg.js` va `node scripts/check-i18n.js` OK chiqaradi.
- [ ] Inline `<script>` ajratib olinib `node --check` dan o'tadi.
- [ ] 31–37 har birini `openGame(id,age)` bilan 3 ta yosh uchun ochib, 1 soniya kutganda konsolda xato yo'q.

**F1 Schulte**
- [ ] `openGame(31,'7-9')` dan keyin: `2` qiymatli katakka `pointerdown` yuboriladi (`new PointerEvent('pointerdown',{bubbles:true})`). Natija: katakda `bad` bor, `S.lives===2`.
- [ ] 400 ms ichida (masalan 100 ms dan keyin) o'sha katakni qayta bosish `S.lives` ni o'zgartirmaydi (`===2`).
- [ ] 500 ms dan keyin o'sha katakda `bad` yo'q.
- [ ] Keyin `1`, so'ng `2` bosiladi. Ikkalasida ham `dim` bor, `S.lives===2`, `#prompt` matnida `3` ko'rinadi.
- [ ] `dim` katakni qayta bosish `S.lives` ni o'zgartirmaydi.
- [ ] Alohida raundda (`openGame(31,'7-9')` qayta): `2` bosiladi, 500 ms kutiladi, `2` yana bosiladi. Natija: `S.lives===1`.

**F2 Chivin (36)**
- [ ] `openGame(36,'10-12'); S.level=1; startRound()`. `#prompt` "qayerda"/"Где" matnini ko'rsatguncha kutiladi. Keyin `#board .tc` dan birinchi katakka `pointerdown` yuboriladi. Agar u to'g'ri bo'lib chiqsa (`S.lives===3 && S.answered`), test boshqa raund bilan takrorlanadi.
- [ ] Noto'g'ri bosishdan keyin: `S.answered===true`, `S.lives===2`, aniq bitta `.tc.ok` bor va uning matni `🪰`.
- [ ] Shu raundda boshqa katakni bosish `S.lives` ni o'zgartirmaydi.
- [ ] `WRONG_ADVANCE_MS + 300` ms dan keyin `S.level===2` va `S.answered===false` (yangi raund boshlangan).

**F2 Sonlar joyi (34)**
- [ ] `openGame(34,'4-6')`, `AGE_CFG.numpos['4-6'].show + 200` ms kutiladi. Bo'sh (`textContent===''`) kataklardan biri noto'g'ri bo'lishi kafolatlanmaydi, shuning uchun F2 dagi "to'g'ri chiqsa takrorlash" usuli qo'llanadi. Noto'g'ri bosishdan keyin: `S.answered===true`, `S.lives===2`, `.tc.ok` kataklar soni qolgan sonlar soniga teng.
- [ ] Shu raundda yana bosish `S.lives` ni o'zgartirmaydi.

**F3 Chivin tezligi va tanaffus**
- [ ] `AGE_CFG.fly['10-12']` qiymatlari: `speed===700`, `c2===12`, `gap===250`. `AGE_CFG.fly['7-9'].speed===850`. `4-6` va `7-9` da `gap===250`.
- [ ] `openGame(36,'10-12'); S.level=10; startRound()` qilinadi. Markaziy katakka `MutationObserver` (`childList, characterData, subtree`) ulanadi va har o'zgarishda `[performance.now(), textContent]` yoziladi. Javob bosqichigacha kutiladi. Natija:
  - bo'sh bo'lmagan va 🪰 bo'lmagan yozuvlar (strelkalar) soni `12` ga teng;
  - har ikki ketma-ket strelka orasida `''` yozuvi bor va u keyingi strelkagacha ≥ 200 ms turadi;
  - har strelka ≥ 650 ms ko'rinadi.
- [ ] `S.level=1; startRound()` bilan 10–12 da strelkalar soni `AGE_CFG.fly['10-12'].c1` ga teng.

**F4 O'lik kod**
- [ ] `mind-kids.html` da `moved` so'zi 36-o'yin blokida yo'q (`grep`).

**F5 Og'zaki hisob**
- [ ] 10–12 da `S.level=10` qilinadi va 300 marta `startRound()` chaqirilib, har safar `#prompt` matni `/(\d+) ([+−×÷]) (\d+)/` bilan o'qiladi. Barcha `÷` misollarda: `x%y===0`, `2<=y<=10`, `2<=x/y<=12`. Kamida bitta misolda `x/y>=8` bor.
- [ ] 10–12, `S.level=1`, 300 ta raund: barcha `÷` misollarda `x/y ∈ {2,3}` va ikkala qiymat ham kamida bir marta uchraydi. Barcha `+`/`−` misollarda operandlar ≤ `50`. `×` misollarda operandlar ≤ `5`.
- [ ] 7–9, `S.level=1`, 300 ta raund: `+` natijasi ≤ `40`, `×` chiqmaydi. `S.level=10`: `+` natijasi ≤ `100`, kamida bittasi > `40`. `×` operandlari ≤ `7`.
- [ ] 4–6 yosh: `AGE_CFG.mental['4-6']` o'zgarmagan (git diff'da yo'q).
