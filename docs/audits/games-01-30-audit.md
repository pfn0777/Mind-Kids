# 1–30-o'yinlar logik auditi (1-bosqich)

Sana: 2026-09-28. Spec: [games-01-30-audit-fixes.md](../specs/games-01-30-audit-fixes.md). `mind-kids.html` o'zgartirilmadi. Natija: **BLOCKER 0, MAJOR 20, MINOR 23**. 30 ta o'yindan 4 tasida (13, 14, 16, 27) topilma yo'q.

### Usul

- Kod to'liq o'qildi (qator raqamlari `mind-kids.html` dan, ~ belgisi taxminiy). Sinov: `python -m http.server 8765`, Playwright MCP (Chromium), `page.evaluate`. Yordamchi: `wait = ms => new Promise(r => setTimeout(r, ms))`, `await openGame(id); await wait(300)`, daraja: `S.level = L; startRound()`.
- `[PW]` — Playwright bilan takrorlandi (CONFIRMED). `[kod]` — faqat kod o'qildi. Takrorlanmagan BLOCKER/MAJOR "PLAUSIBLE" deb belgilandi.
- Umumiy sinovlar:
  - Barcha 16 `gen` o'yini × 10 daraja × 150 marta chaqirildi: istisno 0, variantlar takrorlanmaydi, eng uzun `gen` 2.1 ms (chiqish chegarasiz `for(;;)`/`do..while` sikllari amalda tugaydi).
  - Mustaqil yechuvchilar (1, 4, 5, 7, 13, 14, 23) × 10 daraja × 200 marta: to'g'ri javob har doim to'g'ri va yagona. Noto'g'ri baholanadigan savol topilmadi.
  - 1–30 har biri 3 raund (L1–3) tasodifiy bosishlar bilan, vaqt 30× tezlashtirilgan: konsol xatosi 0, qotib qolgan raund 0 (barcha raund `S.answered===true` ga yetdi).
  - Ma'lumot to'qnashuvi: `CATS`, `COLOR_OBJ`, `SHAPE_OBJ` da toifalararo umumiy emoji yo'q, `NEEDS` da takror yo'q.

### Jiddiylik va C5 chegarasi

- BLOCKER topilmadi: noto'g'ri baholangan javob ham, qotib qolgan raund ham topilmadi.
- C5 (taxmin qilinadigan javob) uchun o'lchov: bitta sodda qoida bilan (masalan "2-eng kichik son") raundlarning necha foizi yutiladi. Tasodif = 25% (4 variant). **≥ 60% yoki 100% deterministik qoida → MAJOR**, 40–60% → MINOR.
- C4 (nohaq jon): bitta raundda `S.rl > 1`, ya'ni 1 tadan ortiq jon ketishi → MAJOR (spec qoidasi).

### Umumiy kuzatuv: `gen` o'yinlari va engine

`playChoice` (qator 394–405) birinchi bosishdan keyin `S.answered` bilan qulflaydi, `a.miss()` ishlatmaydi, taymer `tok`-himoyalangan. Shuning uchun barcha `gen` o'yinlarida C3, C4, C7, C9 qoplangan (faqat 29 ning `after()` qismi bundan mustasno). Quyida bu bandlar "playChoice" deb yoziladi.

---

## 1 Sonni top (4-6, gen)
- [C5] MINOR — `numOpts(n,[n-1,n+1,n-2,n+2],4,1)` nomzodlari simmetrik: to'g'ri son hech qachon eng kichik yoki eng katta variant emas. Qator ~447. [PW] `G[0].gen(L)` 400×10: chetda 0%, 2- yoki 3-o'rinda 100% (50/50). Tuzatish taklifi: nomzodlarni assimetrik `[n-3..n+3]` dan tasodifiy tanlab, to'g'ri javob o'rnini tekislash.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C6 (n: L1 2–5, L10 9–14), C8 ([PW] mustaqil sanash 2000 gen, 0 xato), C10.

## 2 Harfni top (4-6, mount)
- [C4] MAJOR — har noto'g'ri katakda `a.miss()` jon oladi, `miss>=2` raundni tugatadi: bitta raundda 2 jon. Noto'g'ri (`bad`) katakni qayta bosish ham xato hisoblanadi, chunki faqat `ok` katak bloklanadi. Qator ~459. Qanday takrorlanadi: `await openGame(2,'4-6'); await wait(300)`; `.tgt` dagi harfdan farqli 2 ta `#board .tc` ni `click()` → `S.lives` 3→2→1, `S.rl===2`, `S.answered===true`. **CONFIRMED [PW]**. Tuzatish taklifi: 1-xatoda faqat hint, `miss>=2` da `a.done(false)` (engine aynan 1 jon oladi).
- Muammo topilmadi: C1 (N/A), C2 (taymer yo'q), C3, C5, C6 (12/16/20 katak, 2–4 nishon), C7, C8 [kod], C9, C10 (uz 28 / ru 30 harf, `SIMILAR` kalitlari `ABC` da [PW]).

## 3 Qaysi biri ortiqcha? (4-6, gen)
- [C6] MINOR — `L` faqat variantlar sonini 4→5 ga o'zgartiradi (`n=L<5?4:5`), qolgan darajalar bir xil. Qator ~464. Tuzatish taklifi: yuqori darajada yaqinroq toifalar.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C5, C8 ([PW] toifalar orasida umumiy emoji yo'q, variantlar takrorlanmaydi), C10.

## 4 Tez hisobla (7-9, gen)
- [C5] MINOR — `numOpts` nomzodlari (±1, ±2, ±10, ±3) tufayli to'g'ri javob 2-eng kichik variant bo'lish ulushi 49–56% (tasodif 25%). Qator ~471. [PW] 400×10; chetda 13–19%. Tuzatish taklifi: distraktorlarni javobning ikki tomonidan tasodifiy taqsimlash.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice, taymer `tok`-himoyalangan), C6 (vaqt 12→5 s; L8–10 da 2 xonali qo'shish 5 s — bola sinovisiz baholanmadi, tekshirilmadi), C8 ([PW] arifmetika va `explain` mos), C10.

## 5 Sonlar zanjiri (7-9, gen)
- [C5] MINOR — nomzodlar `[ans±step, ans±1]` simmetrik: to'g'ri javob L3–10 da 99–100% chetda emas. Qator ~476. [PW] 400×10. Tuzatish taklifi: 4-o'yindagi kabi.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C6 (qadam 1..2+L, L>5 da manfiy), C8 ([PW] zanjir chiziqli, javob to'g'ri, 2000 gen 0 xato), C10.

## 6 So‘zni tuz (7-9, mount)
- [C4] MAJOR — noto'g'ri terishda `a.miss()` (1-urinish 1 jon) + `tries>=2` (2-urinishda yana 1 jon) = 2 jon. Qator ~487. Qanday takrorlanadi: `await openGame(6,'7-9'); await wait(300)`; `#board .tile:not(.used)` ni ketma-ket bosib terish (har bosishda DOM qayta chiziladi, elementni qayta so'rash kerak) → `S.lives` 3→2 (3 ta `.slot.bad`); 900 ms kutib qayta terish → `S.lives===1`, `S.answered`. **CONFIRMED [PW]**. Tuzatish taklifi: 2-omadsizlikda `a.done(false)`, 1-urinishda jon olinmasin.
- [C9] MINOR — xatodan keyin `a.later(()=>{slots.fill(-1);draw()},700)` bola boshlagan tuzatishni ham o'chiradi. Qator ~488. [PW] 1-xatodan 150 ms keyin `.slot[data-s="2"]` bosildi (`.slot.f`=2), 800 ms dan keyin `.slot.f`=0. Tuzatish taklifi: bola bosganda kechiktirilgan tozalashni bekor qilish.
- Muammo topilmadi: C1 (N/A), C2 (`[data-s]` bilan qaytarish mumkin), C3, C5, C6 (n≤4 / 5–6 / ≥6 belgi), C7 (faqat `a.later`), C8, C10 ([PW] havzalar uz 20/27/23, ru 27/28/28).

## 7 Matematik jumboq (10-12, gen)
- [C5] MAJOR — `numOpts(ans,[ans+1,ans-1,ans+2,ans+x,|ans-x|])`: to'g'ri javob 2-eng kichik variant 61–67% (10 daraja o'rtachasi 64%, tasodif 25%). Qator ~498. Qanday takrorlanadi: `G[6].gen(L)` 400×10, `options[0]` ning saralangan o'rnini hisoblash. **CONFIRMED [PW]**. Tuzatish taklifi: distraktorlarni javob atrofida ikki tomonlama tasodifiy tanlash.
- [C6] MINOR — L1–4 bir xil pog'ona (bitta noma'lum, 2 tenglama): 10–12 yosh uchun juda oson bo'lishi mumkin. Qator ~494. Bola sinovisiz baholanmadi, tekshirilmadi.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C8 ([PW] mustaqil yechuvchi: yechim yagona va javobga teng, 2000 gen), C10.

## 8 Xatoni top (10-12, gen)
- [C5] MINOR — `idx=ri(1,5)`: birinchi son hech qachon xato emas, 6 joydan faqat 5 tasi ishlatiladi. Qator ~507. [kod] Ehtimol ataylab (1-son qoidani belgilaydi). Tuzatish taklifi: ataylab bo'lmasa `ri(0,5)`.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C6, C8 ([PW] variantlar takrorlanmaydi; `do..while` chegarasiz, lekin 1500 gen'da eng uzun 1 ms), C10.

## 9 Sirli ketma-ketlik (10-12, gen)
- [C5] MAJOR — nomzodlar `[lin, ans±1, ans+(ans-last)]`: to'g'ri javob hech qachon eng kichik/eng katta emas (barcha 10 darajada 0%) va 2-eng kichik ulushi 56–77% (o'rtacha 65%). Qator ~524. Qanday takrorlanadi: `G[8].gen(L)` 400×10, `options[0]` ning saralangan o'rnini hisoblash. **CONFIRMED [PW]**. Tuzatish taklifi: 7-o'yindagi kabi.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C6 (qoidalar `m` bo'yicha L1→L9 gacha ochiladi), C8 ([PW] variantlar takrorlanmaydi), C10.

## 10 Ranglar olami (4-6, gen)
- [C8] MINOR — yaqin ranglar (sariq, to'q sariq, jigarrang) bir savolda variant bo'lganda ba'zi emojilar bir nechta javobga mos (pishloq, basketbol to'pi, tulki; soyabon va kapalak rangi platformaga bog'liq). Qator ~526, ~529. PLAUSIBLE: emoji ko'rinishi platformaga bog'liq, tekshirilmadi. Tuzatish taklifi: noaniq emojilarni olib tashlash.
- [C6] MINOR — `gen(L)` `L` dan foydalanmaydi: 10 daraja bir xil qiyinlikda. Qator ~529.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C5, C10 (til mustaqil), C8 ([PW] ranglar ro'yxatida umumiy emoji yo'q).

## 11 Shaklni top (4-6, gen)
- [C8] MINOR — kvadrat va to'rtburchak variantlari 3/4 ehtimol bilan birga chiqadi, rasm ramkasi/quti/sovg'a qutisi kvadrat deb belgilangan, lekin to'rtburchakka ham mos. Qator ~532. PLAUSIBLE: ko'rinish platformaga bog'liq, tekshirilmadi. Tuzatish taklifi: noaniq emojilarni olib tashlash yoki kvadrat/to'rtburchakni bir savolga qo'ymaslik.
- [C6] MINOR — `gen(L)` `L` dan foydalanmaydi. Qator ~535.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C5, C10, C8 ([PW] shakllar ro'yxatida umumiy emoji yo'q).

## 12 Kimga nima kerak? (4-6, gen)
- [C5] MAJOR — distraktorlar doim boshqa turdan (`x[2]!==p[2]`): hayvon uchun to'g'ri javob (ovqat) 3 ta buyum orasida yagona ovqat, buyum uchun to'g'ri javob 3 ta ovqat orasida yagona buyum. Savolni tushunmasdan tur bo'yicha topiladi. Qator ~540. Qanday takrorlanadi: `G[11].gen(1)` 3000 marta, variantlarni `NEEDS` bo'yicha turga o'girish → to'g'ri javob o'z turidan yagona: 3000/3000. **CONFIRMED [PW]**. Tuzatish taklifi: distraktorlarni ayni turdan tanlash (boshqa hayvonlarning ovqati / boshqa buyumlarning juftlari).
- [C8] MINOR — tovadagi tuxum emojisi uchun ovqat distraktorlari (baliq, sabzi, asal) ham pishirilishi mumkin. Qator ~538. PLAUSIBLE, tekshirilmadi.
- [C6] MINOR — `gen(L)` `L` dan foydalanmaydi. Qator ~540.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C10.

## 13 Ko‘zgudagi shakl (7-9, gen)
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C5 (javob boshqa variantlardan qonuniyat bilan ajralmaydi, tekshirilmadi), C6 (3×3 → 4×4, L7+ da vertikal aks), C8 ([PW] mustaqil aks-transformatsiya: 2000 gen 0 xato, aynan 1 to'g'ri variant; `for(;;)` chegarasiz, eng uzun 0.7 ms), C10.

## 14 Aylantirib top (7-9, gen)
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C5 (tekshirilmadi), C6 (90° → 90/180/270), C8 ([PW] mustaqil burish: 2000 gen 0 xato, aynan 1 to'g'ri variant; `for(;;)` chegarasiz, eng uzun 0.6 ms), C10.

## 15 Figurani yig‘ (7-9, mount)
- [C4] MAJOR — "Tekshirish" da `a.miss()||tries>=2`: 1-noto'g'ri tekshiruv 1 jon, 2-si yana 1 jon = 2 jon. Qator ~573. Qanday takrorlanadi: `await openGame(15,'7-9'); await wait(300)`; `#board [data-chk]` ni bo'sh taxtada 2 marta `click()` → `S.lives` 3→2→1, `S.answered===true`. **CONFIRMED [PW]**. Tuzatish taklifi: 2-omadsizlikda `a.done(false)`, 1-tekshiruvda jon olinmasin.
- [C3] MAJOR — xotira rejimida (L≥6, `hide`) 1-xatodan keyin raund davom etadi va xato kataklar belgilanadi (`draw(wrong)`), namuna yashirin turgan bo'lsa ham. Bo'sh taxtada 1-tekshiruv 16 katakdan 11 tasini `bad` qildi = yashirin shakl silueti bepul oshkor bo'ldi, qolgani faqat rang tanlash (3–4 rang). Qator ~572–573. Qanday takrorlanadi: `await openGame(15,'7-9'); S.level=6; startRound()`; 5.2 s kutib (xotira bosqichi 4900 ms), `[data-chk]` bosiladi → `.pc.bad`=11 (16 dan), `.ro`=0 (namuna ko'rinmaydi), `S.answered===false`, `S.lives===2`. **CONFIRMED [PW]**. Tuzatish taklifi: xotira rejimida 1-xato raundni tugatadi va namunani ko'rsatadi (`done(false)`), 31–37 spec'dagi C3 tamoyili.
- [C6] MINOR — L8–10: 5×5, 4 rang, xotirada atigi 5.5 s (`2500+n*600`): 7–9 yosh uchun og'ir bo'lishi mumkin. Qator ~562, ~568. Bola sinovisiz baholanmadi, tekshirilmadi.
- Muammo topilmadi: C1 (N/A), C2 (taymer yo'q), C5, C7 (`a.later`), C8, C9, C10.

## 16 Aqlli labirint (10-12, mount)
- Muammo topilmadi: C1 (N/A: emoji har qadamda katak almashtiradi, ko'rinadi), C2 (DFS mukammal labirint, BFS yo'li doim bor [kod]; taymer tugasa `done(false)`), C3, C4 (`a.miss()` ishlatilmaydi, taymer tugashi 1 jon), C5, C6 (5×5/40 s → 10×10/85 s), C7 (`a.on`, `a.timer`, tok-himoya), C8, C9 (`live()` va `t.stop()`), C10. [PW] smoke: xatosiz, L1–3 da raund tugadi.

## 17 Farqni top PRO (10-12, mount)
- [C4] MAJOR — `a.miss()||miss>=3`: uch xato = 3 jon = bitta raundda o'yin tugashi. Bir xil farqsiz katakni qayta bosish ham hisoblanadi, chunki `got` faqat topilganlarni bloklaydi. Qator ~600. Qanday takrorlanadi: `await openGame(17,'10-12'); await wait(300)`; A va B panelda matni bir xil bo'lgan katakni 3 marta `click()` → `S.lives` 3→2→1→0, `S.answered===true`. Tasodifiy smoke: 3 bosishda 0 jon (3/3 raund). **CONFIRMED [PW]**. Tuzatish taklifi: `miss>=3` da `a.done(false)`, oldingi xatolarda jon olinmasin; `bad` katakni bloklash.
- Muammo topilmadi: C1 (N/A), C2, C3, C5, C6 (25+k·8 s, 2–4 farq), C7, C8, C9, C10.

## 18 Naqsh matritsasi (10-12, gen)
- [C5] MAJOR — distraktorlar to'g'ri javobning 1–2 belgisini o'zgartirib yasaladi, shu sababli to'g'ri variant boshqa 3 tasi bilan eng ko'p umumiy belgi (shakl/rang/son) ulashadigan **yagona** variant. Matritsaga qaramay topiladi. Qator ~609. Qanday takrorlanadi: `G[17].gen(L)` (L=1,5,9) × 400, variantlarni `svg` bo'yicha (shakl, `fill`, soni) belgilarga ajratib juftma-juft moslikni sanash → to'g'ri variant yagona maksimum: 1200/1200. **CONFIRMED [PW]**. Tuzatish taklifi: distraktorlarni matritsaning qo'shni kataklaridan (qator/ustun qo'shnisi) yasash.
- [C8] MINOR — L<7 da `explain` "Har qator va ustunda shakl va rang bir martadan uchraydi" noto'g'ri: mode 0 da shakl qatorda, rang ustunda o'zgarmaydi. Qator ~612. [PW] 800/800 gen'da da'vo yolg'on. Tuzatish taklifi: mode 0/1 uchun to'g'ri izoh.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C6 (mode L4 va L7 da o'zgaradi), C10.

## 19 Memory Match (4-6, mount)
- [C8] MINOR — yurish limiti faqat noto'g'ri juftlikdan keyin tekshiriladi, mos juftlikda tekshirilmaydi: `moves>=limit` dan keyin ham mos juftliklar davom etadi. Qator ~627. [PW] L1 (limit 9): 8 ta xato + mos juft → prompt "yurish 9/9", keyingi mos juft "10/9", "11/9", raund `done(true)`. Tuzatish taklifi: limitni har yurishdan keyin tekshirish.
- [C6] MINOR — 4–6 yosh uchun L8–10 da 16 karta (8 juft, limit 24), L5+ da qarash vaqti 1500 ms (12–16 karta). Qator ~616, ~622. Bola sinovisiz baholanmadi, tekshirilmadi.
- Muammo topilmadi: C1 (N/A), C2, C3 (xotira o'yini, limit bor), C4 (`done(false)` 1 jon, `busy` oynasi 700 ms), C5, C7 (`a.later`), C9, C10.

## 20 Top va bos (4-6, mount)
- [C4] MAJOR — har noto'g'ri hayvonda `a.miss()`, `bad>=3` → bitta raundda 3 jon (o'yin tugaydi). Qator ~639. Qanday takrorlanadi: `await openGame(20,'4-6')`; `#prompt` dagi hayvondan farqli, katakda paydo bo'lgan hayvonga `pointerdown` yuborish (3 marta) → `S.lives` 3→2→1→0, `S.rl===3`, `S.answered`. **CONFIRMED [PW]**. Tuzatish taklifi: `bad>=3` da `a.done(false)`, oldingi xatolarda jon olinmasin.
- [C6] MAJOR — 4–6 yosh uchun `show=max(650,1500-L*85)`: L8 820 ms, L9 735 ms, L10 650 ms, tanaffus 250 ms. Bola 9 katak orasidan hayvonni topib, target/decoy ni ajratib, bosishi kerak. Qator ~631. Qanday takrorlanadi: `await openGame(20,'4-6'); S.level=L; startRound()`, 9 ta `#board .tc` ga `MutationObserver` (`childList, characterData, subtree`) ulab, matn paydo bo'lishidan yo'qolishigacha o'lchash: [PW] L1 da ~1420 ms (davr ~1665 ms), L10 da ~655 ms (davr ~900 ms) — raqamlar tasdiqlandi. **PLAUSIBLE**: Playwright bola reaksiyasini o'lchay olmaydi, shuning uchun "yoshga mos emas" xulosasi tasdiqlanmagan (31–37 auditida 36-o'yindagi 500 ms shu sababli tuzatilgan). Tuzatish taklifi: `show` pastki chegarasini oshirish (masalan ≥ 1000 ms, qiymat sinovda aniqlanadi).
- Muammo topilmadi: C1 (har paydo bo'lish boshqa katakda, `i!==last`), C2, C3, C5, C7 (`a.later`/`a.every`), C8, C9 (`t.stop()` + tok-himoya), C10.

## 21 Ritmni takrorla (4-6, mount)
- [C1] MAJOR — ketma-ket bir xil tugma yonganda qorong'i oraliq faqat `gap*.3`, animatsiya yo'q; `seq` da ketma-ket takrorga cheklov yo'q. Qator ~644, ~647. Qanday takrorlanadi: `R=()=>0` (hamma tugma bir xil) → `await openGame(21,'4-6'); S.level=L; startRound()`, `.pad` ga `MutationObserver` (`class`): L1 da yonish 526 ms, qorong'i **221 ms**; L10 da yonish ~303 ms, qorong'i **122–131 ms**. **CONFIRMED [PW]**. Tuzatish taklifi: `seq` ni ketma-ket takrorsiz yasash (27-o'yindagidek) yoki qorong'i oraliqni ≥ 300 ms qilish.
- [C7] MINOR — `flash` da xom `setTimeout` (`classList.remove('lit')`). Qator ~647. [kod] Faqat eski elementga tegadi, holatga ta'sir qilmaydi.
- [C6] MINOR — 4–6 yosh uchun L9–10 da 6 belgi, 430 ms qadam. Qator ~644. Bola sinovisiz baholanmadi, tekshirilmadi.
- Muammo topilmadi: C2, C3 (1 xato raundni tugatadi), C4 (`a.done(false)` → 1 jon), C5, C8, C9 (`phase` guard), C10.

## 22 Smart Puzzle (7-9, mount)
- [C4] MAJOR — noto'g'ri belgida `a.miss()||miss>=3` → 3 jon. Bir xil noto'g'ri belgini qayta bosish ham hisoblanadi. Qator ~669. Qanday takrorlanadi: `await openGame(22,'7-9'); await wait(300)`; tanlangan katakning qatorida allaqachon bor belgini paletdan 3 marta bosish → `S.lives` 3→2→1→0, `S.answered`. Tasodifiy smoke: L1–3 da barcha raundlar 0 jon bilan tugadi. **CONFIRMED [PW]**. Tuzatish taklifi: `miss>=3` da `a.done(false)`.
- Muammo topilmadi: C1 (N/A), C2 (yechim yagona, `sdkCount` kafolatlaydi [kod]), C3, C5, C6 (4→11 bo'sh katak), C7, C8, C9, C10.

## 23 Rang + Son (7-9, gen)
- [C5] MAJOR — `numOpts(k,[k-1,k+1,k+2],4,0)`: nomzodlar aynan 3 ta va hammasi yaroqli (k≥1), shuning uchun variantlar doim `{k-1,k,k+1,k+2}`, to'g'ri javob doim 2-eng kichik. Qator ~676. Qanday takrorlanadi: `G[22].gen(L)` 400×10, `options[0]` o'rni: har darajada 2-o'rin 100%. **CONFIRMED [PW]**. Tuzatish taklifi: nomzodlarni kengaytirish (`k±1..3`) va ikki tomonlama tasodifiy tanlash.
- Muammo topilmadi: C1 (N/A), C2–C4, C7, C9 (playChoice), C6, C8 ([PW] mustaqil sanash 2000 gen, 0 xato), C10.

## 24 Tezkor kombinatsiya (7-9, mount)
- [C4] MAJOR — `a.miss()||miss>=3` → 3 jon. Bir xil noto'g'ri sonni qayta bosish ham hisoblanadi (`v<next` faqat topilganlarni o'tkazadi). Qator ~684. Qanday takrorlanadi: `await openGame(24,'7-9'); await wait(300)`; `3` qiymatli katakka (navbat `1`) `pointerdown` 3 marta → `S.lives` 3→2→1→0, `S.answered`. Tasodifiy smoke: 3 bosishda 0 jon (3/3 raund). **CONFIRMED [PW]**. Tuzatish taklifi: `miss>=3` da `a.done(false)` (31 dagi `bad` debounce qolsin).
- [C6] MINOR — L8–10 da 5×5 (25 son), har songa 2.0→1.7 s (50/47/43 s). Qator ~685. 7–9 yosh uchun qattiq bo'lishi mumkin, tekshirilmadi.
- Muammo topilmadi: C1 (N/A), C2, C3, C5, C7, C8, C9, C10.

## 25 Brain Builder (10-12, mount)
- [C4] MAJOR — `a.miss()||miss>=2` → 2 jon. Qator ~694. Qanday takrorlanadi: `await openGame(25,'10-12')`; yonganlar (`.lit`) yodda saqlanadi, 2.6 s dan keyin yonmagan 2 xil katakka `click()` → `S.lives` 3→2→1, 1-xatodan keyin `S.answered===false`, 2-dan keyin `true`. **CONFIRMED [PW]**. Tuzatish taklifi: `miss>=2` da `a.done(false)`, 1-xatoda jon olinmasin. Ko'p nishonli o'yin bo'lgani uchun 1-xatodan keyin davom etish qoladi (35 dagi kabi).
- Muammo topilmadi: C1 (N/A), C2, C3 (ko'p nishonli, qabul), C5, C6 (k 3→8, ko'rsatish 2.0–2.8 s), C7, C8, C9 (`phase` guard; `bad` katak qayta bosilmaydi), C10.

## 26 Brain Speed (10-12, mount)
- [C1] MAJOR — ketma-ket bir xil rasm orasida bo'sh vaqt `220` ms va paydo bo'lish animatsiyasi yo'q. Qator ~706. Qanday takrorlanadi: `R=()=>0` (hamma rasm bir xil), `await openGame(26,'10-12'); S.level=1; startRound()`, `.nbbox` ga `MutationObserver` (`childList, characterData, subtree`), "Ha" bosib borish → har rasm oldida bo'sh oraliq 222–237 ms, `getComputedStyle(box).animationName==='none'`. **CONFIRMED [PW]**. Spec F1 da oldindan tasdiqlangan; `i<nb` rasmlari ham shu spec'da.
- [C5] MAJOR — mos kelish ehtimoli 38%, o'tish chegarasi `ceil(8*.75)=6`: har doim "Yo'q" bosgan bola raundni 33–38% da yutadi (tasodifiy bosish 14–15%). Qator ~699, ~704. Qanday takrorlanadi: vaqt 60× tezlashtirilib (`setTimeout`/`setInterval`/`Date.now`), har raundda faqat `[data-a="0"]` bosildi: L1 50/150 (33%), L6 57/150 (38%); tasodifiy 15/100 va 14/100; nazariy 35.9% va 14.5%. **CONFIRMED [PW]**. Tuzatish taklifi: 8 urinishdan aynan 4 tasi mos (aralashtirilgan), o'tish shartini ikkala javob turi bo'yicha qo'yish (har turdan ≥ 3/4).
- Muammo topilmadi: C2, C3, C4 (`a.miss()` yo'q, `done(false)` → 1 jon), C6 (T 2850→1500 ms, L6+ da 2-back), C7 (`a.later`, `a.on`), C8, C9 (`waiting` guard, `answer(null)` taymeri poygada xavfsiz), C10.

## 27 Super Memory (10-12, mount)
- Muammo topilmadi: C1 (ketma-ket bir xil belgi `seq` da taqiqlangan, belgilar orasida 220 ms bo'sh), C2, C3 (1 xato raundni tugatadi), C4 (`a.done(false)` → 1 jon), C5, C6 (3→7 belgi, 910→550 ms), C7 (`a.later`), C8 (`while` chiqishi kafolatli: `rep=false` da len ≤ 5 ≤ havza 6/8 [kod]), C9 (`phase` guard), C10. [PW] smoke: xatosiz.

## 28 Robotni boshqar (10-12, mount)
- [C4] MAJOR — `fail()` da `a.miss()||tries>=2` → bitta raundda 2 jon. Qator ~735. Qanday takrorlanadi: `await openGame(28,'10-12'); await wait(300)`; 1 qadamli dastur (`[data-d="0"]`) + `[data-run]`, xatodan keyin qayta `[data-run]` → `S.lives` 3→2→1, `S.rl` 1→2. **CONFIRMED [PW]**. Tuzatish taklifi: 2-omadsizlikda `a.done(false)`, 1-omadsizlikda jon olinmasin.
- [C9] MINOR — 1-omadsizlikdan keyin `a.later(()=>{rpos=s;cur=-1;draw()},900)` bekor qilinmaydi: 900 ms ichida ▶ qayta bosilsa, animatsiya o'rtasida robot boshlang'ichga qaytadi va to'g'ri dastur ham xato baholanadi. Qator ~735. Qanday takrorlanadi: 1 qadamli dastur ishga tushiriladi, `S.rl===1` bo'lishi bilan BFS bilan hisoblangan optimal dastur kiritilib ▶ bosiladi (xatodan ~10 ms keyin) → 3/3 sinovda `ok:0, bad:1`, 2 jon ketdi; nazorat (1100 ms kutib) 3/3 `ok:1`. **CONFIRMED [PW]**, lekin oyna tor (≤ 900 ms) va bola uchun kam uchraydi, shuning uchun MINOR. Tuzatish taklifi: kechiktirilgan tozalashni `run()` da bekor qilish.
- Muammo topilmadi: C1 (N/A), C2 (dasturni ⌫ bilan tozalash mumkin, yo'l `bfs` bilan kafolatli, zaxira bo'sh maydon bor [kod]), C3, C5 (prompt `opt` ni ochiq aytadi, qabul), C6, C7, C10.

## 29 Beat & Brain (10-12, gen)
- [C7] MAJOR — `after()` ichida xom `setTimeout` (zarba va `pulse` o'chirish): raund tugagach ham, o'yindan chiqqach ham ritm chalinaveradi va keyingi raund ritmi bilan aralashadi. Qator ~750. Qanday takrorlanadi: `Snd.tone` (`'square'`) ni kuzatib, `S.level=9; startRound()` (6 zarba); 750 ms da to'g'ri variantni bosish → keyingi raund 1973 ms da boshlandi; eski raundning 5 zarbasidan 3 tasi (2407, 2795, 3166 ms) yangi raund ichida chalindi va yangi raundning o'z zarbalari (2565, 2954, 3667, ...) bilan aralashdi. Alohida: 750 ms da `closeGame()` → undan keyin 5 zarba (987–2849 ms) Bosh sahifada chalindi. **CONFIRMED [PW]**. Tuzatish taklifi: `setTimeout` ni `a.later` ga almashtirish (`live()` + `S.timers` tozalanadi).
- Muammo topilmadi: C1 (N/A: zarbalar ritmning o'zi), C2–C4, C9 (playChoice), C6, C8 ([PW] variantlar takrorlanmaydi), C10. Tekshirilmadi: C5 (distraktorlar javobning mutatsiyasi, 18-dagi kabi "eng o'xshash variant" naqshi bo'lishi mumkin).

## 30 Brain Challenge (10-12, gen)
- [C6] MINOR — `pick([3,4,5,7,8,9,13,14,23])`: 9 tadan 1 tasi 4–6 yosh o'yini (3), 5 tasi 7–9 yosh (4, 5, 13, 14, 23), 10–12 ga mos faqat 7, 8, 9. `Math.max(L,3)` past darajani ko'taradi. Qator ~754. Tuzatish taklifi: ro'yxatni 10–12 mos o'yinlar bilan cheklash yoki yoshga mos daraja oshirish.
- [C5] MINOR — sub-o'yinlarning naqshlari meros bo'lib o'tadi: 23 (100%), 7 va 9 (~64%) 9 tadan 3 ta tanlovda. Qator ~754. Tuzatish 7, 9, 23 dagi tuzatish bilan o'z-o'zidan hal bo'ladi.
- Muammo topilmadi: C1 (N/A), C2–C4, C7 (`time` orqali, playChoice), C9, C8 ([PW] `gen` ishlaydi, `key` `'c'+id` bilan farqlanadi), C10.

---

### Xulosa jadvali

| id | nom | BLOCKER | MAJOR | MINOR |
|---|---|---|---|---|
| 1 | Sonni top | 0 | 0 | 1 |
| 2 | Harfni top | 0 | 1 | 0 |
| 3 | Qaysi biri ortiqcha? | 0 | 0 | 1 |
| 4 | Tez hisobla | 0 | 0 | 1 |
| 5 | Sonlar zanjiri | 0 | 0 | 1 |
| 6 | So‘zni tuz | 0 | 1 | 1 |
| 7 | Matematik jumboq | 0 | 1 | 1 |
| 8 | Xatoni top | 0 | 0 | 1 |
| 9 | Sirli ketma-ketlik | 0 | 1 | 0 |
| 10 | Ranglar olami | 0 | 0 | 2 |
| 11 | Shaklni top | 0 | 0 | 2 |
| 12 | Kimga nima kerak? | 0 | 1 | 2 |
| 13 | Ko‘zgudagi shakl | 0 | 0 | 0 |
| 14 | Aylantirib top | 0 | 0 | 0 |
| 15 | Figurani yig‘ | 0 | 2 | 1 |
| 16 | Aqlli labirint | 0 | 0 | 0 |
| 17 | Farqni top PRO | 0 | 1 | 0 |
| 18 | Naqsh matritsasi | 0 | 1 | 1 |
| 19 | Memory Match | 0 | 0 | 2 |
| 20 | Top va bos | 0 | 2 | 0 |
| 21 | Ritmni takrorla | 0 | 1 | 2 |
| 22 | Smart Puzzle | 0 | 1 | 0 |
| 23 | Rang + Son | 0 | 1 | 0 |
| 24 | Tezkor kombinatsiya | 0 | 1 | 1 |
| 25 | Brain Builder | 0 | 1 | 0 |
| 26 | Brain Speed | 0 | 2 | 0 |
| 27 | Super Memory | 0 | 0 | 0 |
| 28 | Robotni boshqar | 0 | 1 | 1 |
| 29 | Beat & Brain | 0 | 1 | 0 |
| 30 | Brain Challenge | 0 | 0 | 2 |
| | **Jami** | **0** | **20** | **23** |

### Tuzatish guruhlari (taklif)

| Guruh | Mazmun | O'yinlar | Jiddiylik |
|---|---|---|---|
| A | C4: `a.miss()` + ko'p xato = raundda 1 tadan ortiq jon (bitta naqsh, bir xil tuzatish) | 2, 6, 15, 17, 20, 22, 24, 25, 28 | MAJOR × 9 |
| B | C5: taxmin qilinadigan javob (12, 18, 23 — 100%; 26 — "har doim Yo'q"; 7, 9 — ~65%) | 7, 9, 12, 18, 23, 26 (+ MINOR: 1, 4, 5, 8, 30) | MAJOR × 6 |
| C | C1: ketma-ket bir xil stimul ko'rinmaydi (26 — spec F1 allaqachon tasdiqlangan) | 21, 26 | MAJOR × 2 |
| D | C7: xom `setTimeout` | 29 (+ MINOR: 21) | MAJOR × 1 |
| E | C3: xotira rejimida xato katak oshkor bo'ladi | 15 | MAJOR × 1 |
| F | C6: 4–6 yosh uchun tezlik (20) | 20 (+ MINOR: 7, 15, 19, 21, 24, 30 va `L` ishlatilmaydigan 3, 10, 11, 12) | MAJOR × 1 |
| G | MINOR to'plami: 19 limit, 18 izoh, 6 tozalash, 28 poyga, 10/11/12 noaniq emojilar, 8 `idx` | 6, 8, 10, 11, 12, 18, 19, 28 | MINOR |
