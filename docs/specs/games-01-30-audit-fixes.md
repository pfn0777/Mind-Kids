# Spec: 1–30-o'yinlar logikasini audit qilish va tuzatish

## Maqsad
1–30-o'yinlarning har birini o'yin logikasi jihatidan tekshirish. Bola sezmay qoladigan, tavakkal bilan yutadigan, qotib qoladigan yoki nohaq jon yo'qotadigan holatlarni topib tuzatish. Ish ikki bosqichda bajariladi: **1-bosqich — audit (kod yozilmaydi)**, **2-bosqich — tasdiqlangan topilmalarni tuzatish**.

## Nega kerak
- 31–37-o'yinlar auditida ([games-31-37-fixes.md](games-31-37-fixes.md)) bir xil turdagi xatolar topildi: ketma-ket kelgan bir xil stimul sezilmaydi, xatodan keyin tavakkal bosish mumkin, o'yin qotib qoladi, murakkablik darajaga qarab o'smaydi. 1–30-o'yinlar oldinroq yozilgan va hech qachon bunday tekshiruvdan o'tmagan.
- **Ma'lum xato — 26 Brain Speed:** ketma-ket ikkita bir xil rasm (masalan ⭐ → ⭐) chiqqanda foydalanuvchi ikkinchi rasm chiqqanini sezmaydi. Sababi: `show()` da rasmlar orasidagi bo'sh vaqt atigi `220` ms va rasm paydo bo'lishida hech qanday animatsiya yo'q (`mind-kids.html` ~706). Bu n-back o'yini, shuning uchun "bir xil rasm" holati aynan asosiy savol. Bola uni sezmasa, o'yinning mohiyati buziladi.

## 1-bosqich — Audit

**Natija:** `docs/audits/games-01-30-audit.md` fayli. Kod o'zgartirilmaydi. Audit tugagach, ish to'xtatiladi va topilmalar tasdiqlanadi.

**Har bir o'yin (1–30) uchun quyidagi checklist bo'yicha tekshiriladi:**

| # | Tekshiruv | Misol (31–37 dan) |
|---|---|---|
| C1 | **Ko'rinmas o'zgarish:** ketma-ket kelgan bir xil stimul (rasm, strelka, son, rang, ovoz) bola uchun sezilarli ajraladimi? Bo'sh vaqt ≥ 300 ms va/yoki paydo bo'lish animatsiyasi bormi? | 36 ⬆️⬆️, 26 ⭐⭐ |
| C2 | **Qotib qolish (softlock):** o'yinni to'g'ri javob berib bo'lmaydigan holatga keltirish mumkinmi? Faqat vaqt tugashi bilan chiqiladigan holat bormi? | 31: `bad` katak bosilmay qoladi |
| C3 | **Tavakkal bilan yutish:** xatodan keyin o'sha taxtada bosishni davom ettirib, javobni tanlab topish mumkinmi? | 34, 36 |
| C4 | **Nohaq jon yo'qotish:** double-tap, ko'rsatish bosqichidagi bosish yoki animatsiya paytidagi bosish bir necha jon oladimi? Bitta raundda 1 tadan ortiq jon ketadimi (`S.rl` hisobga olinmagan)? | 31 double-tap |
| C5 | **Oldindan ma'lum javob:** javob pozitsiyasi, qiymati yoki shakli naqsh bo'yicha taxmin qilinadimi? Masalan, doim bir xil javob, `fixed` variantlarda to'g'risi doim bitta joyda yoki variantlar takrorlangan. | 37 L1 da `÷` javobi doim 2 |
| C6 | **Murakkablik:** qiyinlik `L` (1–10) bo'yicha seziladigan darajada o'sadimi? L1 yosh guruhi uchun juda qiyin, L10 esa juda osonmi? Tezlik va vaqt yosh uchun realmi? | 36 10–12 yoshda 500 ms |
| C7 | **Timer va token:** barcha kechiktirilgan callback'lar `a.later`/`a.every`/`S.timers` orqali o'tadimi yoki `tok!==S.tok` bilan himoyalanganmi? Xom `setTimeout` bormi? | 29: `after()` ichida xom `setTimeout` |
| C8 | **Generator to'g'riligi:** `gen(L)` / `mount` noto'g'ri yoki bir nechta to'g'ri javobli savol yarata oladimi? Cheksiz `while`/`do` sikli (chiqish chegarasisiz) bormi? `key` takrorlanishni to'g'ri ushlaydimi? | — |
| C9 | **Holat oqimi:** `a.done` bir raundda bir martadan ko'p chaqirilishi mumkinmi (timer + bosish poygasi)? `done` dan keyin bosish yana qabul qilinadimi? | — |
| C10 | **Til:** uz/ru da o'yin logikasi farq qiladimi (masalan, `LX[lang]` ro'yxati qisqa bo'lib, generator yetarlicha variant topolmaydi)? | — |

**Audit fayli formati:**
```
## <id> <nomi> (age, gen|mount)
- [C1] <jiddiylik: BLOCKER|MAJOR|MINOR> — <muammo 1 jumla>. Qator ~NNN. Qanday takrorlanadi: <qadamlar>. Tuzatish taklifi: <1 jumla>.
- Muammo topilmadi: <tekshirilgan checklist bandlari>
```
Oxirida jadval: `id | nom | BLOCKER | MAJOR | MINOR`.

**Jiddiylik:**
- **BLOCKER** — o'yin qotadi, noto'g'ri javob to'g'ri deb baholanadi yoki raund to'g'ri yakunlanmaydi.
- **MAJOR** — bola o'yinning maqsadini bajara olmaydi (C1, C3, C4, C5) yoki qiyinlik yoshga umuman mos emas.
- **MINOR** — o'lik kod, sezilmaydigan nomuvofiqlik.

**Audit qoidalari:**
- Har bir topilma kodda qator raqami bilan ko'rsatiladi. BLOCKER va MAJOR topilmalar Playwright'da (`page.evaluate`) takrorlanib tasdiqlanadi. Takrorlanmasa, "PLAUSIBLE" deb belgilanadi.
- Taxmin yozilmaydi. Tekshirilmagan narsa "tekshirilmadi" deb yoziladi.
- Dizayn didiga oid fikrlar (rang, matn uslubi) auditga kirmaydi.

## 2-bosqich — Tuzatish

Faqat tasdiqlangan BLOCKER va MAJOR topilmalar tuzatiladi. MINOR — tasdiqlanganlari.

**F1 — 26 Brain Speed: har bir rasm sezilarli paydo bo'ladi (oldindan tasdiqlangan)**
- Rasmlar orasidagi bo'sh vaqt `220` ms dan `NB_GAP_MS` (400 ms) ga oshiriladi. Konstanta Games bo'limida, `NB` yonida.
- Har yangi rasm mavjud `@keyframes pop` bilan paydo bo'ladi. `.nbbox.in{animation:pop .25s}` qo'shiladi. Klass olib tashlanadi va reflow'dan keyin (`void box.offsetWidth`) qayta qo'shiladi, shunda bir xil rasm uchun ham animatsiya qayta ishlaydi.
- `T` (javob vaqti) o'zgarmaydi. Umumiy raund uzunligi `(trials+nb)*180` ms ga oshadi, bu qabul qilinadi.
- Eslab qolish bosqichidagi (`i<nb`) rasmlarga ham xuddi shu gap + animatsiya qo'llanadi.

### Ijro tartibi (audit natijasi bo'yicha tasdiqlangan qarorlar, 2026-09-28)

Audit: [games-01-30-audit.md](../audits/games-01-30-audit.md) (BLOCKER 0, MAJOR 20, MINOR 23). Ish 2 partiyada bajariladi, har partiya alohida commit:
- **1-partiya (mexanik tuzatishlar): F1–F6.** Commit: `Fix 1-30 audit batch 1: round life budget, pad gap, stale beats, memory reveal`.
- **2-partiya (generatorlar, statistik AC bilan): F7–F10.** Commit: `Fix 1-30 audit batch 2: numeric option ranks, distractor design, balanced n-back`.
- Ichki tartib: 1-partiya tugab, qabul qilinib, commit qilinmaguncha 2-partiya boshlanmaydi (F1 va F10 ikkalasi ham 26-o'yin `mount` ini o'zgartiradi).
- **Kiritilmaydi:** 20-o'yin tezligi (audit C6), va MINOR lardan F6 da nomlanmaganlari (1, 3, 4, 5, 7, 8, 10, 11, 12, 15, 19, 21, 24, 30 dagi C5/C6/C8 MINOR lar). Ular auditda qoladi.

### F2 — Raund byudjeti: bitta raundda aniq 1 jon (2, 6, 15, 17, 20, 22, 24, 25, 28) [1-partiya]

**Muammo (audit C4, MAJOR, 9/9 CONFIRMED):** bu 9 o'yin har xatoda `a.miss()` chaqiradi va `miss>=N` da raundni tugatadi: bitta raundda N ta jon ketadi (N=2 yoki 3, 17/20/22/24 da 3 ta xato = butun o'yin tugaydi). Bir xil noto'g'ri elementni qayta bosish ham xato hisoblanadi (2, 17, 22, 24).

**Tuzatish ("raund byudjeti"):**
- Har o'yinda mavjud xato chegarasi `N` saqlanadi. `a.miss()` chaqiruvi shu 9 o'yindan olib tashlanadi. 1..N−1-xatoda faqat mavjud hint chiqadi, jon ketmaydi. N-xatoda `a.done(false,{msg})` chaqiriladi; `S.rl===0` bo'lgani uchun `finishRound` aniq 1 jon oladi (engine o'zgarmaydi).
- Allaqachon xato deb belgilangan element qayta bosilsa e'tiborsiz qoldiriladi: xato hisoblagichi, hint va `S.lives` o'zgarmaydi.
- Jadval:

| o'yin | xato birligi | N | qayta bosish e'tiborsiz |
|---|---|---|---|
| 2 | noto'g'ri harf katagi | 2 | `bad` katak (`ok` bilan birga tekshiriladi) |
| 6 | to'liq noto'g'ri terilgan so'z (urinish) | 2 | N/A (elementi yo'q) |
| 15 | noto'g'ri "Tekshirish" (urinish) | 2 (xotira rejimida 1, F5) | N/A: belgilangan kataklarni qayta bo'yash xato emas |
| 17 | farqsiz katak indeksi | 3 | shu indeks (`Set`), A va B panelda ikkalasida |
| 20 | noto'g'ri hayvon bosildi | 3 | hayvon bosilganda yo'qoladi (`hide()`), qo'shimcha qoida kerak emas |
| 22 | (katak, belgi) juftligi | 3 | shu juftlik (`Set`) |
| 24 | noto'g'ri son qiymati | 3 | shu qiymat (`Set`). Keyin navbati kelganda to'g'ri bosilsa qabul qilinadi va `bad` klassi olib tashlanadi (CSS da `.tc.bad` `.tc.ok` dan keyin turadi, aks holda to'g'ri son qizil qoladi) |
| 25 | yonmagan katak | 2 | `bad` katak (mavjud guard) |
| 28 | muvaffaqiyatsiz ishga tushirish (urinish) | 2 | N/A |

- Qabul qilingan oqibat: non-final xatoda `S.streak` uzilmaydi (avval `loseLife` uzardi). Xato bilan yutilgan raundda bonus 0 bo'lib qoladi (mavjud `bonus: miss?0:…`).
- 25 ko'p nishonli o'yin: 1-xatodan keyin davom etish qoladi (35 dagi kabi).

**EARS:**
- QACHON bu 9 o'yinning birida raundda N-xato yuz bersa, TIZIM aniq 1 jon olishi (`a.done(false)` orqali) VA raundni tugatishi SHART.
- QACHON xato soni N dan kam bo'lsa, TIZIM jon olmasligi SHART.
- QACHON allaqachon xato deb belgilangan element qayta bosilsa, TIZIM xato hisoblagichini oshirmasligi SHART.

**AC** (qadamlar: audit faylidagi tegishli o'yin bo'limi; `wait`, `openGame` yordamchilari yuqoridagidek):
- [ ] N=3 o'yinlar (17, 20, 22, 24): 1-xatodan keyin `S.lives===3 && !S.answered`; 2-xatodan keyin `S.lives===3 && !S.answered`; 3-xatodan keyin `S.lives===2 && S.answered && S.rl===0`.
- [ ] N=2 o'yinlar (2, 6, 15, 25, 28): 1-xatodan keyin `S.lives===3 && !S.answered`; 2-xatodan keyin `S.lives===2 && S.answered`.
- [ ] 2, 17, 22, 24: bir xil noto'g'ri elementni 3 marta bosish → faqat 1 xato hisoblanadi (`S.lives===3`, `!S.answered`); keyin boshqa noto'g'ri elementlar bilan N-xatoga yetkazilganda `S.lives===2`.
- [ ] 24: noto'g'ri bosilgan son keyin navbatiga yetganda bosilsa qabul qilinadi (`ok`+`dim`), katakda `bad` klassi yo'q, `S.lives` o'zgarmaydi.
- [ ] Tasodifiy bosish smoke (audit usuli, 9 o'yin × L1–3): har raundda `S.lives` ning kamayishi ≤ 1.

### F3 — 21 Ritmni takrorla: qorong'i oraliq va pop animatsiya (C1) [1-partiya]

**Muammo (audit C1, MAJOR, CONFIRMED):** ketma-ket bir xil tugma yonganda qorong'i oraliq faqat `gap*.3` = 221 ms (L1), ~125 ms (L10) va animatsiya yo'q. Qaror: `seq` dagi takrorlar TAQIQLANMAYDI, oraliq kattalashtiriladi.

**Tuzatish:**
- Yangi konstanta `PAD_DARK_MS=300`, `PADS` yonida. Yonish davomiyligi o'zgarmaydi: `lit=Math.round(gap*.7)`. Qadam davri `step=lit+PAD_DARK_MS`. Ko'rsatish jadvali `600+k*step`, kiritish bosqichiga o'tish `600+len*step` (hozir `gap` ishlatilgan joylarda).
- CSS: `.pad.lit{animation:pop .25s}` qo'shiladi (mavjud `@keyframes pop`; yangi animatsiya yaratilmaydi). Klass har yonishda olib tashlanib qayta qo'shilgani uchun animatsiya har tugmada qayta ishlaydi.
- `flash()` dagi xom `setTimeout` (`classList.remove('lit')`) `S.timers` ga tushadigan va `tok` tekshiradigan variantga almashtiriladi (`const tk=S.tok` mount boshida; `S.timers.push(setTimeout(()=>{if(tk===S.tok)…},d))`). `a.later` ishlatilmaydi: u raund tugagach ishlamaydi va oxirgi bosilgan tugma yonib qolardi.
- Oqibat: raund ko'rsatish qismi uzayadi (L1: 2.09 s → 2.24 s, L10: 3.18 s → 4.21 s). Qabul qilinadi.

**EARS:** QACHON 21-o'yinda ketma-ket ikki tugma yonsa (bir xil bo'lsa ham), TIZIM ular orasida tugmani kamida `PAD_DARK_MS` ms o'chiq qoldirishi VA har yonishda `pop` animatsiyasini ishlatishi SHART.

**AC:**
- [ ] `R=()=>0` (hamma tugma bir xil) bilan `openGame(21,'4-6'); S.level=L; startRound()`, `.pad` ga `MutationObserver` (`class`): L1 va L10 uchun ketma-ket yonishlar orasidagi o'chiq vaqt ≥ 300 ms (barcha oraliqlar).
- [ ] Yonganda `getComputedStyle(pad).animationName==='pop'`.
- [ ] Kiritish bosqichi (`#prompt` "Endi siz takrorlang" chiqishi) oxirgi yonish tugagandan keyin boshlanadi.
- [ ] To'g'ri ketma-ketlikni bosish: `S.answered && S.ok===1`. Noto'g'ri bosish: `S.answered && S.lives===2`.
- [ ] Raund tugagach yoki `closeGame()` dan keyin `.pad.lit` holati o'zgarish keltirib chiqarmaydi (xatosiz, konsolda xato yo'q).

### F4 — 29 Beat & Brain: xom `setTimeout` (C7) [1-partiya]

**Muammo (audit C7, MAJOR, CONFIRMED):** `after()` ichidagi xom `setTimeout` lar raund tugagach ham, o'yindan chiqqach ham ritm zarbalarini chalaveradi va keyingi raund ritmi bilan aralashadi (750 ms da to'g'ri javob: eski raundning 5 zarbasidan 3 tasi yangi raundga o'tdi).

**Tuzatish:**
- Zarbalarni rejalashtirish (`Snd.tone` chaqiruvi) va "Tinglash" tugmasini qayta yoqish `a.later` orqali. (`a.later` `live()` bilan qo'riqlangan: raund tugagach ishlamaydi.)
- `pulse` ni o'chirish `S.timers` ga tushadigan va `tok` tekshiradigan xom variantda (raund tugaganda ham vizual o'chadi). `Snd.tone` bu timerda chaqirilmaydi.
- `plays` chegarasi (3) va `btn` matnlari o'zgarmaydi.

**EARS:** QACHON 29-o'yinda raund tugasa yoki o'yin yopilsa, TIZIM keyin hech qanday zarba ovozini chalmasligi SHART.

**AC** (`Snd.tone` ni kuzatib, `S.level=9; startRound()` → 6 zarba):
- [ ] To'g'ri variantni 750 ms da bosish: `S.answered` dan keyin `'square'` tonlar 0 ta.
- [ ] Keyingi raund boshlangach ilk 600 ms da 0 ta zarba; keyingi raundning avto-ijrosida aynan naqsh uzunligicha (6) zarba.
- [ ] 750 ms da `closeGame()`: undan keyin 4.5 s davomida 0 ta zarba.
- [ ] To'xtatilmagan ijro: 6 zarba to'liq chalinadi, "Tinglash" tugmasi qayta yoqiladi (`plays<3` bo'lsa), 3-ijrodan keyin `disabled`.

### F5 — 15 Figurani yig': xotira rejimida 1-xato raundni tugatadi (C3) [1-partiya]

**Muammo (audit C3, MAJOR, CONFIRMED):** xotira rejimida (L≥6, `hide`) 1-xato tekshiruvdan keyin namuna ko'rsatilmasa ham xato kataklar belgilanadi va raund davom etadi: bo'sh taxtada 1-tekshiruv 16 katakdan 11 tasini belgilab yashirin shakl siluetini oshkor qildi.

**Tuzatish:** xato chegarasi `maxTries = hide ? 1 : 2` (F2 dagi `tries>=maxTries`). Xotira rejimida 1-noto'g'ri tekshiruv: `showT=true; draw(wrong); a.done(false,{msg})` (mavjud xabar "N ta katak xato edi. Namuna ko'rsatildi."), aniq 1 jon. Xotirasiz rejimda (L<6) F2 dagi ikki urinish qoladi, 1-urinishda xato kataklar belgilanadi va hint chiqadi (namuna ko'rinib turgani uchun oshkor qilish yo'q).

**EARS:**
- QACHON 15-o'yinda xotira rejimida noto'g'ri tekshiruv bosilsa, TIZIM aniq 1 jon olishi, namunani ko'rsatishi va raundni tugatishi SHART, boshqa tekshiruvga yo'l qo'ymasligi SHART.
- QACHON xotira rejimida bo'lmagan raundda 1-noto'g'ri tekshiruv bosilsa, TIZIM jon olmasligi VA raundni davom ettirishi SHART.

**AC:**
- [ ] `openGame(15,'7-9'); S.level=6; startRound()`, 5.2 s kutib bo'sh taxtada `[data-chk]` bosiladi: `S.answered===true`, `S.lives===2`, `#board .ro` soni > 0 (namuna ko'rinadi), `.pc.bad` soni = noto'g'ri kataklar soni. Shu raundda yana bosish `S.lives` ni o'zgartirmaydi.
- [ ] `S.level=1; startRound()`: bo'sh taxtada 1-tekshiruv: `S.answered===false`, `S.lives===3`, `.pc.bad`>0. 2-tekshiruv: `S.answered===true`, `S.lives===2`.
- [ ] To'g'ri chizilgan taxta (L1, namunadan aynan ko'chirilgan) tekshirilsa: `S.ok===1`, `S.lives===3`.

### F6 — Kichik mexanik tuzatishlar: 18 izoh, 19 limit, 6 tozalash, 28 poyga [1-partiya]

(21 dagi xom `setTimeout` F3 ichida.) 6 va 28 F2 dagi o'zgarishlarga tayanadi.

**F6a — 18 Naqsh matritsasi: `explain` matni (C8).** L<7 da izoh ("Har qator va ustunda shakl va rang bir martadan uchraydi") 800/800 gen'da noto'g'ri. Yangi matnlar (uz+ru, mavjud `loc({uz,ru})` shaklida, I18N kalit emas):
- L<4 (mode 0): uz `Har qatorda shakl bir xil, har ustunda rang bir xil.` ru `В каждой строке форма одна и та же, в каждом столбце — один цвет.`
- L4–6 (mode 1): uz `Har qator va ustunda shakl bir martadan uchraydi, rang esa ustun bo‘yicha bir xil.` ru `В каждой строке и столбце форма встречается по одному разу, а цвет одинаков в столбце.`
- L≥7 (mode 2): matn o'zgarmaydi.

**F6b — 19 Memory Match: limit har yurishda tekshiriladi (C8).** Hozir `moves>=limit` faqat noto'g'ri juftlikda tekshiriladi, promptda "yurish 10/9" chiqadi. Tuzatish: har yurishdan keyin (mos yoki mos emas), agar barcha juftlar topilmagan bo'lsa va `moves>=limit` bo'lsa, kartalar ochib ko'rsatiladi va `a.done(false,{msg:'Yurishlar tugadi.'})` (mavjud matn). Oxirgi juft aynan `moves===limit` da topilsa `done(true)` ustuvor. Mos yurishda ko'rsatish darhol, mos emasda mavjud 700 ms kechikish bilan.

**F6c — 6 So'zni tuz: tozalash bekor qilinadi (C9).** 1-xatodan keyingi `a.later(()=>{slots.fill(-1);draw()},700)` bola 700 ms ichida katakni bossa ham hamma narsani o'chiradi. Tuzatish: lokal hisoblagich (`let wipe=0`): tozalash `my=++wipe` bilan rejalashtiriladi va faqat `my===wipe` bo'lsa bajariladi; `[data-s]` yoki `[data-t]` bosilganda `wipe++` (kutilayotgan tozalash bekor). Bosishsiz 700 ms dan keyin avvalgidek tozalanadi.

**F6d — 28 Robotni boshqar: poyga (C9).** 1-omadsizlikdan keyingi `a.later(()=>{rpos=s;cur=-1;draw()},900)` 900 ms ichida ▶ bosilsa animatsiya o'rtasida robotni boshlang'ichga qaytaradi va to'g'ri dasturni ham xato baholaydi (3/3 CONFIRMED). Tuzatish: xuddi shu hisoblagich usuli (`let rst=0`): `fail()` `my=++rst` bilan rejalaydi, `my===rst` bo'lsa bajaradi; `run()` boshida `rst++; rpos=s; cur=-1; draw()` (kutilayotgan tozalash bekor va taxta darhol boshlang'ich holatga qaytadi).

**EARS:**
- QACHON 18-o'yinda xato javobdan keyin izoh ko'rsatilsa, TIZIM o'sha darajadagi matritsa qoidasiga mos matnni ko'rsatishi SHART.
- QACHON 19-o'yinda `moves` `limit` ga yetsa va barcha juftlar topilmagan bo'lsa, TIZIM raundni `done(false)` bilan tugatishi VA promptda `moves>limit` ko'rsatmasligi SHART.
- QACHON 6-o'yinda kutilayotgan tozalash davrida bola katak/harf bossa, TIZIM tozalashni bajarmasligi SHART.
- QACHON 28-o'yinda ▶ bosilsa, TIZIM oldingi omadsizlikdan qolgan kutilayotgan tozalashni bekor qilishi SHART.

**AC:**
- [ ] 18: `G[17].gen(1).explain.uz`, `gen(5).explain.uz`, `gen(9).explain.uz` uchtasi o'zaro farqli; `.ru` ham farqli va bo'sh emas; L≥7 matni oldingi bilan bir xil. 400×3 gen'da mode 0 va 1 uchun to'ldirilgan 3×3 (options[0] bilan) xuddi shu matn aytgan xossani bajaradi (mode 0: shakl qatorda o'zgarmas va qatorlararo farqli, rang ustunda o'zgarmas va ustunlararo farqli; mode 1: shakl har qator/ustunda 3 xil, rang ustunda o'zgarmas).
- [ ] 19 (L1, limit 9): 8 ta mos emas + 1 ta mos juft (moves=9, juftlar tugamagan) → `S.answered===true`, `S.ok===0`, `S.bad===1`. `#prompt` hech qachon `yurish X/9` da X>9 ko'rsatmaydi. Oxirgi juft moves=9 da topilsa → `S.ok===1`.
- [ ] 6: 1-xatodan 150 ms keyin `.slot[data-s="2"]` bosiladi → 900 ms dan keyin `.slot.f` soni 2 (o'chirilmagan). Bosishsiz variantda 800 ms dan keyin `.slot.f`=0.
- [ ] 28: BFS bilan hisoblangan optimal dastur xatodan ≤ 100 ms keyin kiritilib ▶ bosiladi → `S.ok===1`, `S.lives===3` (1-omadsizlik jon olmaydi, F2). Nazorat (1100 ms kutib) ham `S.ok===1`. 3 marta takrorlanadi.

### F7 — Umumiy `numOpts`: to'g'ri javob o'rni tekis (C5; 1, 4, 5, 7, 9, 23 + 33, 37) [2-partiya]

**Muammo (audit C5, CONFIRMED):** `numOpts` (qator ~232) nomzodlarni tasodifiy tanlaydi, lekin ular javobga nisbatan simmetrik/kam: 23-o'yinda variantlar doim `{k-1,k,k+1,k+2}` (javob 100% "2-eng kichik"), 9 da o'rtacha 65%, 7 da 64%, 4 da 54%; 1 va 5 da javob deyarli hech qachon eng kichik/eng katta emas. `numOpts` 8 joyda ishlatiladi: 1, 4, 5, 7, 9, 23, 33, 37. Tuzatish o'yinma-o'yin emas, umumiy funksiyada qilinadi.

**Tuzatish (imzo o'zgarmaydi: `numOpts(ans,cands,n=4,min=0)`):**
1. `cands` dan yaroqlilari (butun, `>=min`, `!==ans`, takrorsiz) `lo` (`<ans`) va `hi` (`>ans`) ga ajratiladi.
2. Maqsadli rank `r` = to'g'ri javobdan kichik variantlar soni. `rmax=Math.min(n-1, ans-min)` (`ans-min` = `[min, ans-1]` dagi butun sonlar soni). `r=ri(0,rmax)` tekis.
3. Kichiklar: `lo` dan tasodifiy `r` ta; yetmasa `ans-1, ans-2, …` dan eng yaqin ishlatilmagan (`>=min`) bilan to'ldiriladi. Kattalar: `hi` dan tasodifiy `n-1-r` ta; yetmasa `ans+1, ans+2, …` bilan to'ldiriladi.
4. Qaytariladi `[ans, ...kichiklar, ...kattalar]`: **`ans` 0-o'rinda qoladi** (`playChoice` `answer` default 0 ga tayanadi). Tartibni o'yinlar o'zlari aralashtiradi (mavjud).
- `R`/`ri`/`shuffle` mavjud yordamchilar ishlatiladi (test uchun `R` stub qilinadi).
- 30-o'yin (4, 5, 7, 9, 23 ni chaqiradi) o'z-o'zidan foyda ko'radi.

**EARS:**
- QACHON `numOpts` chaqirilsa, TIZIM aynan `n` ta noyob, `>=min` butun son qaytarishi VA `ans` ni 0-o'rinda qoldirishi SHART.
- QACHON `ans-min >= n-1` bo'lsa, TIZIM `ans` ning saralangan o'rnini `0..n-1` dan tekis tanlashi SHART.
- QACHON `ans-min < n-1` bo'lsa, TIZIM o'rinni `0..ans-min` dan tekis tanlashi SHART.

**AC:** (`page.evaluate`; `G[id-1].gen(L)` 400×10, `options[0]` javobning saralangan o'rni; n=4 uchun)
- [ ] Birlik: `numOpts` ni 20000 marta tasodifiy `ans∈[0,60]`, `min∈{0,1}`, `n∈{3,4}`, `cands` (bo'sh, kichik, simmetrik, uzoq qiymatli) bilan chaqirish: uzunlik `n`, hammasi butun va `>=min`, noyob, `[0]===ans`.
- [ ] 1, 4, 5, 7, 9, 23: shartli ulush (faqat `ans-min>=3` savollari) har rank uchun 15–35% (n=4). Shartsiz ulush har rank ≥ 10%. "2-eng kichik" qoidasi (rank 1 ulushi) ≤ 40%. (Qo'lda hisob: 23 da shartsiz rank 3 ≈ 14%, rank 1 ≈ 32%; kichik `k` da yuqori rank mumkin emas, shuning uchun shartsiz chegara 10%.)
- [ ] 33: `AGE_CFG.mathmem[age]` bo'yicha (har yosh uchun 400×10) `sum` yasab `numOpts(sum,[sum±1,±2,±3],c.opts,1)` chaqiriladi: shartli ulush har rank uchun `1/n ± 10` punkt (n=3 da 23–43%, n=4 da 15–35%), shartsiz ≥ 10%, o'rta rank (n=4 da rank 1, n=3 da rank 1) ≤ 40%.
- [ ] 37: har yosh uchun `S.g=G[36]; S.age=age; S.level=L; startRound()` 400×10. Misol `#prompt` ning `innerHTML.split('<br>')[1]` dan o'qiladi (`textContent` "Savol 1/5" ni sonlar bilan yopishtirib yuboradi), javob hisoblanib `#board [data-v]` variantlari bilan solishtiriladi: n=4 uchun yuqoridagi shartli/shartsiz/o'rta rank chegaralari. Variantlar `>=0`, noyob, to'g'ri javob aynan 1 ta.
- [ ] Prototip o'lchovi (yangi `numOpts` sahifada vaqtincha e'lon qilinib, 4000 gen har biri; % ko'rinishida rank 0/1/2/3): 1: 28/27/23/21; 4: 26/25/25/24; 5: 25/26/25/24; 7: 28/28/24/20; 9: 26/25/25/24; 23: 32/33/22/13 (shartli 25/26/26/24); 33 (4–6, n=3): 32/34/34, (7–9): 25/25/26/24, (10–12): 24/24/26/26; 37 (4–6): 29/26/24/22, (7–9): 28/26/24/23, (10–12): 27/25/25/24. Hammasida yaroqsiz qator 0. Eski `numOpts` da 23 da rank 1 = 100%. Shu sababli AC chegaralari: shartli 15–35%, shartsiz ≥ 10%, o'rta rank ≤ 40%.
- [ ] 37 ning games-31-37-fixes.md dagi F5 AC lari (÷ shartlari, diapazonlar) o'zgarishsiz o'tadi.
- [ ] Audit mustaqil yechuvchilari (1, 4, 5, 7, 23) × 10 daraja × 200: `options[0]` hamon mustaqil yechimga teng (javob qiymati o'zgarmagan). 8 va 13/14 ning `numOpts`ga aloqasi yo'q.
- [ ] `git diff`: faqat `numOpts` funksiyasi (qator ~232) o'zgargan; 1, 4, 5, 7, 9, 23, 33, 37 o'yin kodlari o'zgarmagan.

### F8 — 12 Kimga nima kerak?: distraktorlar ayni turdan (C5) [2-partiya]

**Muammo (audit C5, MAJOR, CONFIRMED 3000/3000):** distraktorlar doim boshqa turdan (`x[2]!==p[2]`), shuning uchun to'g'ri javob o'z turidan yagona variant va savolsiz topiladi.

**Tuzatish:** `ds=sample(NEEDS.filter(x=>x[2]===p[2]&&x!==p&&!NEEDS_CONFUSE(p,x)).map(x=>x[1]),3)`. Ayni tur ichida noaniqlik oshgani uchun (ayiq baliq yeydi, maymun yong'oq yeydi) `CONFUSE` (3-o'yin) uslubida qo'shimcha ziddiyat ro'yxati kiritiladi. Boshlang'ich ro'yxat (subyekt → taqiqlangan distraktor): ayiq→baliq, maymun→yong'oq, mashina→batareya, tort→tuxum. Qolgan juftlar tekshirilgandan keyin ro'yxatga qo'shilishi mumkin. `a`-tur 9 ta, `o`-tur 14 ta juft: har subyekt uchun kamida 3 distraktor qoladi.

**EARS:** QACHON 12-o'yinda savol yasalsa, TIZIM barcha 3 distraktorni to'g'ri javob bilan bir turdan (`a` yoki `o`) tanlashi VA ziddiyat ro'yxatidagi juftni birga chiqarmasligi SHART.

**AC:**
- [ ] `G[11].gen(1)` 3000 marta: 4 variantning hammasi `NEEDS` bo'yicha bir xil turda; to'g'ri javob o'z turidan yagona bo'lgan holat 0 ta. Variantlar noyob.
- [ ] `gen` 20000 marta; subyekt `q.board` dagi emojidan olinadi: ziddiyat ro'yxatidagi distraktor 0 marta chiqadi, `NEEDS` ning 23 subyektining hammasi kamida bir marta uchraydi, har savolda aynan 4 ta variant.
- [ ] `openGame(12,'4-6')` 3 raund tasodifiy bosish: xatosiz, `S.answered`.

### F9 — 18 Naqsh matritsasi: variantlar muvozanatli (C5) [2-partiya]

**Muammo (audit C5, MAJOR, CONFIRMED 1200/1200):** distraktorlar to'g'ri javobning 1–2 belgisini o'zgartirib yasaladi, to'g'ri variant boshqa uchtasi bilan eng ko'p umumiy belgi (shakl/rang/son) ulashadigan yagona variant bo'ladi.

**Tuzatish:** variantlar to'g'ri javob `ans=(s,c,k)` atrofidagi juft-paritetli qism-kub tepalaridan yasaladi, shunda har juft variant bir xil sondagi belgi ulashadi:
- Almashtiruvchi qiymatlar matritsada ko'rinadigan qiymatlardan: `s'` ∈ `sh∖{s}`, `c'` ∈ `co∖{c}` (tasodifiy), mode 2 da `k'` ∈ `{1,2,3}∖{k}`.
- Mode 0 va 1: variantlar `(s,c)`, `(s',c)`, `(s,c')`, `(s',c')` (2×2). Mode 2: `(s,c,k)`, `(s',c',k)`, `(s',c,k')`, `(s,c',k')`.
- Qidiruv sikli va `extraS`/`extraC` (endi ishlatilmaydi) olib tashlanadi. `key`, `explain` (F6a dan keyin) va taxta o'zgarmaydi.
- Izoh: faqat "qo'shni katak" nusxalari yetarli emas: satr/ustun qo'shnisidan yasalgan distraktorlarda ham to'g'ri javob yana eng ko'p umumiy belgili variant bo'lib qoladi. Shuning uchun muvozanatli tuzilma tanlandi.

Xossa: har variantning boshqa uchtasi bilan umumiy belgilari yig'indisi (ball) hamma 4 variant uchun teng (mode 0/1 da 2 + umumiy `k`, mode 2 da 3). Shuning uchun "eng ko'p umumiy belgi" evristikasi to'g'ri javobni ajrata olmaydi (kutilgan aniqlik 25%).

**EARS:** QACHON 18-o'yinda savol yasalsa, TIZIM to'g'ri javob va 3 ta noto'g'ri variantni yuqoridagi qism-kub tepalaridan yasashi VA barcha variantlarni (shakl, rang, son) bo'yicha noyob qilishi SHART.

**AC:** (`G[17].gen(L)`, L=1,5,9, har biri 400)
- [ ] Har savolda 4 variantning ballari (boshqalar bilan umumiy belgilar yig'indisi; variantlar `svg` bo'yicha shakl/`fill`/soniga ajratiladi) o'zaro teng.
- [ ] "Eng ko'p umumiy belgi" evristikasining aniqligi = `mean(1/g)` (g = maksimum ballli variantlar soni; to'g'ri javob ular orasida bo'lsa, aks holda 0): har mode uchun ≤ 40%.
- [ ] Variantlar noyob (shakl, rang, son); `options[0]` to'g'ri katak: to'ldirilgan 3×3 mode qoidasini bajaradi (F6a AC dagi xossalar + mode 2 da soni qator bo'yicha o'zgarmas va qatorlararo farqli).
- [ ] Barcha variantlar `sh`/`co` dagi qiymatlardan; hamma `k∈{1,2,3}`.
- [ ] `openGame(18,'10-12')` L1/5/9 smoke: xatosiz, `S.answered`.

### F10 — 26 Brain Speed: muvozanatli urinishlar va tur bo'yicha o'tish sharti (C5) [2-partiya]

**Muammo (audit C5, MAJOR, CONFIRMED):** mos kelish ehtimoli 38%, o'tish `right>=6/8`: har doim "Yo'q" bosgan bola raundlarning 33–38% ini yutadi (tasodifiy bosish 14–15%).

**Tuzatish:**
- 8 urinishdan **aynan 4 tasi** mos (n-back: `seq[i]===seq[i-nb]`), qolgan 4 tasi mos emas. Joylar `sample(range(trials),4)` bilan tanlanadi. Mos emas urinishda qiymat `sy` dan `seq[i-nb]` chiqarib tashlangan ro'yxatdan olinadi (qayta urinish sikli `++g<10` olib tashlanadi). `i<nb` rasmlari (eslab qolish) o'zgarishsiz.
- O'tish sharti: mos urinishlardan ≥ 3/4 VA mos emaslardan ≥ 3/4 (`hitsM>=3 && hitsN>=3`, bu jami ≥ 6 ni ham kafolatlaydi). `need` o'zgaruvchisi olib tashlanadi. Bonus `(right-6)*30` saqlanadi.
- Muvaffaqiyatsizlik matni yangilanadi (uz+ru, inline `loc`): uz `Mos kelganlardan {a}/4, mos kelmaganlardan {b}/4 topildi — har biridan kamida 3 ta kerak edi.` ru `Совпадений найдено {a}/4, несовпадений {b}/4 — нужно минимум по 3.` Muvaffaqiyat matni (`{right}/{trials} to'g'ri.`) o'zgarmaydi.

**EARS:**
- QACHON 26-o'yin raundi yasalsa, TIZIM 8 ta savol urinishida aynan 4 tasini mos qilishi SHART.
- QACHON raund oxirida mos yoki mos emas urinishlarning birida 3/4 dan kam to'g'ri bo'lsa, TIZIM raundni `done(false)` bilan tugatishi SHART.

**AC:** (vaqt tezlashtirilib: `setTimeout`/`setInterval`/`Date.now` 60×; har raundda `S.level=L; S.lives=3; startRound()`, tugagach `cleanup(); S.tok++`)
- [ ] L1 va L6 uchun 150 raunddan: har doim "Yo'q" → 0 ta o'tish; har doim "Ha" → 0 ta o'tish; tasodifiy → ≤ 15%; mukammal o'yinchi (`.nbbox` matn tarixidan `nb` orqadagi rasm bilan solishtirib javob beradi) → 100% o'tish.
- [ ] 300 raundda `.nbbox` tarixidan hisoblangan mos urinishlar soni har raundda aynan 4.
- [ ] 6/8 = 4 mos (3 topilgan) + 2 mos emas → `done(false)` va yangi matn; 3 mos + 3 mos emas topilgan (jami 6) → `done(true)`.
- [ ] F1 AC lari (bo'sh oraliq ≥ 380 ms, `pop`) o'zgarishsiz o'tadi.

**Tuzatish tamoyillari (31–37 dan olingan):**
- **C1:** stimul orasidagi bo'sh vaqt + `pop` animatsiya. Yangi animatsiya yaratilmaydi, mavjud `pop` ishlatiladi.
- **C2:** vaqtinchalik holat klasslari (`bad`) `a.later` bilan olib tashlanadi. Rad etish tekshiruvi o'sha oyna davomida debounce sifatida qoladi.
- **C3:** xotira o'yinlarida bitta xato raundni tugatadi: to'g'ri javob `ok` bilan ko'rsatiladi, `done(false)`. Bir nechta nishonli o'yinlarda (35 kabi) davom etish qoladi.
- **C4:** raundda 1 tadan ortiq jon ketmaydi. Audit qarori: "raund byudjeti" (F2): oxirgi xatogacha `a.miss()` chaqirilmaydi, N-xatoda `a.done(false)` aniq 1 jon oladi. (`a.miss()` + `a.done(false)` juftligi 31–37 dagi kabi faqat `a.miss()` allaqachon 1 tadan ortiq chaqirilmaydigan o'yinlarda qoladi.)
- **C7:** xom `setTimeout` o'rniga `a.later` yoki token tekshiruvi.
- Yangi raqamlar — konstanta sifatida. 1–30 uchun `AGE_CFG` ga ko'chirilmaydi (ular bitta yoshga bog'langan).

## Qamrov TASHQARISIDA (bularni qilma!)
- 31–37-o'yinlar (alohida spec bilan tuzatilgan). Istisno: 33 va 37 umumiy `numOpts` ni ishlatadi, shuning uchun F7 ularga ta'sir qiladi. Ularning o'z kodi o'zgarmaydi, F7 AC lari ularni ham tekshiradi.
- 20-o'yin tezligi (audit C6, "F" guruhi) va auditning F2–F10 da nomlanmagan MINOR lari.
- `hint()` va boshqa engine yordamchilaridagi xom `setTimeout` (`hint`, `Store.get`).
- Engine: `finishRound`, `nextRound`, jonlar soni, ball formulasi, `S.level` ning xatodan keyin ham oshishi.
- O'yin qo'shish, olib tashlash yoki qayta tartiblash (id = `G` dagi o'rin, statistika shunga bog'langan).
- Vizual qayta dizayn, yangi ranglar (faqat mavjud CSS tokenlar).
- Yangi i18n kalitlari. Agar tuzatish uchun yangi matn kerak bo'lsa, u F-bandda alohida ko'rsatiladi va uz+ru ikkalasi qo'shiladi.
- 1–30 ni `age:'all'` ga yoki `AGE_CFG` ga o'tkazish.
- Kodni qayta formatlash (zich uslub saqlanadi).

## Texnik
- Fayl: `mind-kids.html` (yagona fayl).
  - 26 Brain Speed: ~696–709 (`show()`, `seq` yasash, `advance`), CSS ~115–116 (`.nbbox`). F1 va F10.
  - F2: 2 (~459), 6 (~487), 15 (~573), 17 (~600), 20 (~639), 22 (~669), 24 (~684), 25 (~694), 28 (~735).
  - F3: 21 (~642–653), CSS ~108 (`.pad.lit`), yangi konstanta `PAD_DARK_MS` `PADS` yonida.
  - F4: 29 (~750). F5: 15 (~562–573). F6: 18 (~612), 19 (~627), 6 (~488), 28 (~735).
  - F7: `numOpts` (~232). F8: 12 (~538–541, yangi ziddiyat ro'yxati). F9: 18 (~605–612).
  - Boshqa o'yinlar va engine (`makeApi`, `startRound`, `finishRound`, `nextRound`) o'zgarmaydi.
- Yangi fayl: `docs/audits/games-01-30-audit.md`.
- DB / migration / config: yo'q.
- `scripts/check-i18n.js` va `scripts/check-age-cfg.js` o'tishi shart.

## Qoidalar (EARS)
- QACHON 26-o'yinda yangi rasm ko'rsatilsa, TIZIM oldin qutini kamida `NB_GAP_MS` ms bo'sh qoldirishi VA rasmni `pop` animatsiya bilan chiqarishi SHART, rasm oldingisi bilan bir xil bo'lsa ham.
- QACHON 1–30-o'yinlardan birida bir xil stimul ketma-ket ko'rsatilsa, TIZIM ikkinchi stimulning paydo bo'lishini ko'rinadigan qilishi SHART (bo'sh oraliq ≥ 300 ms yoki animatsiya).
- QACHON raundda istalgan tartibda bosishlar bo'lsa, TIZIM bitta raundda 1 tadan ortiq jon olmasligi SHART.
- QACHON xotira o'yinida noto'g'ri javob bosilsa, TIZIM o'sha taxtada qayta tanlashga yo'l qo'ymasligi SHART.
- AGAR o'yin holatida to'g'ri javob berishning iloji qolmasa, TIZIM bunday holatga tushmasligi SHART (softlock yo'q).
- QACHON raund tugasa (`done`), TIZIM shu raundda boshqa bosishlarni qabul qilmasligi VA `done` ni qayta chaqirmasligi SHART.
- F2–F10 qoidalari (raund byudjeti, pad oralig'i, zarba timerlari, xotira rejimi, izoh/limit/tozalash/poyga, `numOpts` rank, 12/18/26 variantlari) o'z bandlarida yozilgan.

## Acceptance criteria (tugadi deganda)
Sinov muhiti: `python -m http.server 8765` → `http://localhost:8765/mind-kids.html`, Playwright `page.evaluate`. Yordamchilar: `wait = ms => new Promise(r => setTimeout(r, ms))`; `await openGame(id, age); await wait(300)`; daraja: `S.level = L; startRound()`.

**1-bosqich**
- [ ] `docs/audits/games-01-30-audit.md` mavjud va 1–30 ning har bir o'yini uchun bo'lim bor (30 ta `## ` sarlavha).
- [ ] Har bir o'yinda C1–C10 ning qaysilari tekshirilgani yozilgan.
- [ ] Har bir BLOCKER/MAJOR topilmada qator raqami va takrorlash qadamlari bor, holati CONFIRMED yoki PLAUSIBLE.
- [ ] `mind-kids.html` da o'zgarish yo'q (`git diff --stat` faqat `docs/` ni ko'rsatadi).

**F1 Brain Speed**
- [ ] `openGame(26,'10-12')` → `.nbbox` ga `MutationObserver` (`childList, characterData, subtree`) ulanadi va har o'zgarishda `[performance.now(), textContent]` yoziladi. Raund oxirigacha "Ha" tugmasi bilan javob beriladi. Natija: har ikki rasm orasida `''` yozuvi bor va u keyingi rasmgacha ≥ 380 ms turadi.
- [ ] Har rasm paydo bo'lganda `.nbbox` da `in` klassi bor va `getComputedStyle(box).animationName === 'pop'`.
- [ ] `seq` da ketma-ket bir xil ikki rasm bo'lgan raundda (`R` ni stub qilib yoki 20 raundgacha takrorlab topiladi) ikkala rasm uchun ham alohida `''` → rasm o'tishi yozilgan.
- [ ] 8 ta javobdan keyin raund `done` bilan tugaydi, `S.answered === true`.

**Umumiy (2-bosqich oxirida)**
- [ ] Har bir F-band uchun spec'ga yozilgan AC o'tadi.
- [ ] `node scripts/check-i18n.js` va `node scripts/check-age-cfg.js` OK.
- [ ] Inline `<script>` ajratib olinib `node --check` dan o'tadi.
- [ ] 1–30 har birini o'z yoshida `openGame(id)` bilan ochib, 3 ta raundni tasodifiy bosishlar bilan o'ynaganda konsolda xato yo'q va har raund `S.answered===true` ga yetadi (softlock yo'q).
- [ ] `git diff` da 31–37-o'yinlar va engine funksiyalari (`finishRound`, `nextRound`, `startRound`, `makeApi`) o'zgarmagan. Faqat 2-partiyada umumiy `numOpts` (~232) o'zgaradi va u 33/37 ga ta'sir qiladi (F7 AC).
- [ ] F2–F10 AC lari o'z bandlarida. Har partiya oxirida yuqoridagi umumiy AC lar (skriptlar, `node --check`, 1–30 smoke) qayta o'tkaziladi va faqat shu partiyaning o'yinlari `git diff` da o'zgargan bo'ladi.
- [ ] Har partiya alohida commit (batch 1: F1–F6, batch 2: F7–F10). `git push` qilinmaydi.
