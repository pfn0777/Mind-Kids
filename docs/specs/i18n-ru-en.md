# Spec: Rus tili (barcha o'yinlar) + ingliz tili ("Rang chalg'itadi") + til almashtirish tugmasi

## Maqsad
Mind Kids'ning butun interfeysi va 37 ta o'yinining hammasi rus tilida ishlashi kerak. "Rang chalg'itadi" o'yini qo'shimcha ravishda ingliz tilida ham o'ynaladi. Tilni bosh ekranning yuqori panelidagi tugma orqali almashtirish mumkin bo'ladi.

## Nega kerak
- Rus tilida gaplashadigan oilalar ham ilovadan foydalana olsin (auditoriya kengayadi).
- "Rang chalg'itadi" (Stroop) inglizcha rang nomlarini yodlashga ham yordam beradi.
- Eslatma: `new-games-integration.md` da ru/en qamrovdan chiqarilgan edi. Endi foydalanuvchi qarori bilan qamrovga qo'shildi.

## Qamrov ICHIDA
- **Tillar:** `uz` (asosiy, default) va `ru`. Barcha o'yinlar uchun ishlaydi. `en` faqat "Rang chalg'itadi" (id 32) ichida bo'ladi.
- **Global til tugmasi:** bosh ekrandagi `.top` panelida, `themeBtn` yonida `UZ` / `RU` yozuvli `iconbtn` turadi. Bosilganda til almashadi va sahifa qayta yuklanmasdan qayta chiziladi.
- **Default:** birinchi ochilishda har doim `uz`. Tanlov `mk_lang` kalitida saqlanadi (`Store` orqali: localStorage + Telegram CloudStorage).
- **Stroop til tugmasi:** "Rang chalg'itadi" o'yinining `sbar` panelida qo'shimcha tugma bor. U `UZ → RU → EN` bo'yicha aylanadi va faqat shu o'yin tilini o'zgartiradi. Tanlov `mk_lang_stroop` ga saqlanadi. Hali tanlanmagan bo'lsa, global til ishlatiladi. Boshqa o'yinlarda bu tugma ko'rinmaydi.
- **Tarjima qilinadigan UI:** bosh ekran (salomlashuv, chiplar, hisoblagich, kartalar, CTA, footer), o'yin ekrani (HUD, "Davom etish", natija ekrani, yosh tanlash oynasi), ota-ona paneli, `aria-label`lar, `<html lang>`.
- **Har bir o'yin:** `name`, `desc`, topshiriqlar (`prompt`, `say`), `hint`, `explain`, `fb` xabarlari.
- **Kontent lokalizatsiyasi (ru uchun faqat tarjima emas, alohida kontent):**
  - `ABC` va `SIMILAR`: kirill alifbosi va o'xshash harflar juftlari (Ш/Щ, И/Й, Е/Ё, П/Н, Б/В, З/Э va h.k.). "Harfni top" da ishlatiladi.
  - `WORDS`: ruscha so'zlar + emoji. Uzunlik bo'yicha guruhlar uz dagidek bo'ladi (≤4, 5–6, ≥6 harf), har guruhda kamida uz dagi kabi so'z soni. `toks()` ru uchun har bir harfni alohida token qiladi.
  - `COLORS`: `{uz, ru, en}` nomlari. Ru uchun rodga qarab shakllar ham saqlanadi (m/f/n: красный/красная/красное).
  - `SHAPE_N`: `{uz, ru}` + ru uchun rod (`круг` m, `звезда` f, ...). "Rang + Son" o'yinida sifat shakl rodiga moslashadi.
  - `CATS` guruh nomlari, `PRAISE`, `WRULES` qoida tavsiflari.
- **Ruscha grammatika:** son bilan kelishikdan qochish uchun iboralar shunday tuziladi: "Сколько 🍎?", "Ответ: 5", "Было: 5".
- **Ovoz (4–6 yosh):** `Voice` ovozni joriy tilga qarab tanlaydi: `uz` → uz/tr ovozi, `ru` → ru ovozi, `en` (faqat Stroop) → en ovozi. Mos ovoz topilmasa, `#speak` tugmasi yashiriladi (mavjud xatti-harakat).

## Qamrov TASHQARISIDA (bularni qilma!)
- Qolgan 36 ta o'yinni ingliz tiliga o'tkazish. Stroop'dan boshqa o'yinlarda `en` yo'q.
- Telegram tilidan avtomatik aniqlash. Default doim `uz` (foydalanuvchi qarori).
- O'zbek kirill yozuvi.
- Logotip va `a1`–`a6` rasmlaridagi matnni o'zgartirish. Brend nomi "Mind Kids" o'zgarmaydi.
- Statistikani til bo'yicha ajratish. `mk_stats` o'yin id bo'yicha umumiy qoladi.
- Alohida tarjima fayllari yoki build tizimi. Hammasi `mind-kids.html` ichida qoladi.
- Telegram bot xabarlari (agar bo'lsa).

## Texnik
- Fayl: `mind-kids.html` (bitta fayl, build yo'q).
- Yangi: `LANGS=['uz','ru']`, `let LANG='uz'`, `I18N={uz:{...},ru:{...}}` lug'ati va `tr(key,params)` funksiyasi (`{n}` kabi placeholder'lar bilan). Statik HTML matnlari `data-i18n` atributi orqali `applyI18n()` bilan to'ldiriladi.
- O'yin registri: `def({name:{uz,ru},desc:{uz,ru},...})`. Ko'rsatishda `loc(g.name)` ishlatiladi.
- Kontent: `LX={uz:{ABC,SIMILAR,WORDS,...},ru:{...}}`. O'yinlar `LX[LANG].WORDS` kabi o'qiydi. `COLORS`/`SHAPE_N` nomlari til bo'yicha obyektga aylanadi, rang kodlari (`#ef4444`) umumiy qoladi.
- Stroop: `mount(a)` ichida til `a.lang` dan olinadi. `makeApi()` ga `lang` qo'shiladi: id 32 uchun `mk_lang_stroop || LANG`, qolganlar uchun `LANG`.
- Til almashtirilganda: `applyI18n()` + `renderHome()`. Ochiq o'yin bo'lmaydi, chunki global tugma faqat bosh ekranda.
- Stroop ichida til almashtirilganda: yangi til **keyingi savoldan** qo'llanadi. Jon, ball va daraja o'zgarmaydi.
- `mk_seen_*` kalitlari o'zgarmaydi (ru so'zlari boshqa `key` bo'lgani uchun to'qnashuv yo'q).
- Storage: yangi kalitlar `mk_lang`, `mk_lang_stroop`. DB / migration: yo'q.
- Tekshiruv skripti: `scripts/check-i18n.js` (`check-age-cfg.js` naqshida).

## Qoidalar (EARS)
- QACHON ilova birinchi marta ochilsa
  TIZIM `uz` tilida ko'rsatishi SHART.

- QACHON `mk_lang` da saqlangan til bo'lsa
  TIZIM ilovani shu tilda ochishi SHART
  VA ilova avval `uz` da ko'rinib, keyin tilga "sakrab" o'tMASLIGI SHART (til `Store.get` tugagach birinchi render qilinadi).

- QACHON foydalanuvchi global til tugmasini bossa
  TIZIM barcha UI va kartalarni yangi tilda qayta chizishi SHART
  VA `<html lang>` ni yangilashi SHART
  VA tanlovni `mk_lang` ga saqlashi SHART
  VA statistika, yulduzlar va filtrni o'zgartirMASLIGI SHART.

- QACHON foydalanuvchi "Rang chalg'itadi" o'yinini ochsa
  TIZIM `sbar` panelida Stroop til tugmasini ko'rsatishi SHART
  VA boshqa o'yinlarda bu tugmani yashirishi SHART.

- QACHON Stroop'da til `en` bo'lsa
  TIZIM rang so'zlari, topshiriq va xabarlarni inglizcha ko'rsatishi SHART
  VA 4–6 yoshda topshiriqni ingliz ovozida o'qishi SHART (en ovozi bo'lsa).

- QACHON Stroop o'yini davomida til almashtirilsa
  TIZIM joriy savolni o'zgartirmasligi, yangi tilni keyingi savoldan qo'llashi SHART
  VA jon olMASLIGI SHART.

- QACHON til `ru` bo'lsa va "Rang + Son" o'yinida rang + shakl nomi chiqsa
  TIZIM sifatni shakl rodiga moslashtirishi SHART (красный круг, красная звезда).

- AGAR biror kalit uchun `ru` tarjimasi topilmasa
  TIZIM `uz` matnini ko'rsatishi SHART
  VA `console.warn` bilan kalit nomini yozishi SHART (silent fallback emas).

- AGAR joriy til uchun TTS ovozi topilmasa
  TIZIM `#speak` tugmasini yashirishi SHART
  VA boshqa tildagi ovoz bilan o'qiMASLIGI SHART (masalan, ruscha matnni turkcha ovoz bilan o'qimaslik).

## Acceptance criteria (tugadi deganda)
- [ ] Bosh ekranda `UZ`/`RU` tugmasi bor. Bosilganda hamma matn (chiplar, kartalar, CTA, footer, ota-ona paneli) tarjima bo'ladi, sahifa qayta yuklanmaydi.
- [ ] Ilova yopilib qayta ochilganda oxirgi tanlangan til saqlanib qoladi. Birinchi ochilishda `uz`.
- [ ] 37 ta o'yinning har biri `ru` da ochiladi. Topshiriq, xato xabarlari va natija ekranida o'zbekcha so'z qolmaydi.
- [ ] "Harfni top" `ru` da kirill harflarini, "So'zni tuz" ruscha so'zlarni ko'rsatadi.
- [ ] "Rang + Son" `ru` da rod to'g'ri moslashadi (kamida 1 ta erkak va 1 ta ayol rodidagi shakl tekshiriladi).
- [ ] "Rang chalg'itadi" da `UZ → RU → EN` tugmasi ishlaydi, `en` da rang so'zlari inglizcha (RED, BLUE, ...), tanlov saqlanadi.
- [ ] 4–6 yoshda `ru` topshiriqlari ruscha ovozda o'qiladi (qurilmada ru ovozi bo'lsa).
- [ ] 360px kenglikda ruscha uzun matnlar (kartalar, tugmalar) sig'adi, gorizontal scroll yo'q.
- [ ] `scripts/check-i18n.js` o'tadi: `uz` dagi har bir kalit `ru` da bor, `LX.ru` massivlari bo'sh emas, `WORDS.ru` da har uzunlik guruhi to'lgan.
- [ ] Eski statistika (`mk_stats`) va o'yin id'lari o'zgarmagan. Konsolda xato yo'q.

## Test
Pul yoki xavfsizlikka tegmaydi, shuning uchun test majburiy emas. Minimal tekshiruv:
- `scripts/check-i18n.js` (Node): kalitlar to'liqligi, placeholder'lar (`{n}`) ikkala tilda bir xil, `COLORS`/`SHAPE_N` da `ru` rod shakllari mavjud.
- Playwright smoke: `ru` ga o'tish → har bir o'yinni ochish → `#prompt` va `#board` matnida lotin o'zbek harflari (`o‘`, `g‘`, `sh` + o'zbekcha so'zlar ro'yxati) yo'qligini tekshirish.
