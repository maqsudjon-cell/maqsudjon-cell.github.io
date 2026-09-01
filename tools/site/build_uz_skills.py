# -*- coding: utf-8 -*-
"""Builds /uz/listening/, /uz/reading/, /uz/writing/ and /uz/speaking/.

Why: /uz/ was the only Uzbek page on the domain, so it had to rank on its own
for every Uzbek query at once — "IELTS listening test", "reading test onlayn",
"writing task 2 qanday yoziladi", "speaking savollari". One page cannot do
that, and the 129 practice pages it links to are all in English.

Each page here answers one query properly: the format, the question types, the
raw-score table, the mistakes that cost bands, and a crawlable list of the
actual tests on the site for that skill. The raw-score tables are the same
arrays /band-calculator/ uses, so the two pages cannot disagree.

Run:  python3 tools/site/build_uz_skills.py
"""
import json, os, sys
from html import escape

sys.path.insert(0, os.path.dirname(__file__))
import shell
from build_tests_index import load
from build_uz import STYLE

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), '..', '..'))
BASE = 'https://flarestamina.com'

# Same arrays as /band-calculator/ — one source of truth for the conversion.
RAW = {
    'listening': [(39, 9), (37, 8.5), (35, 8), (32, 7.5), (30, 7), (26, 6.5),
                  (23, 6), (18, 5.5), (16, 5), (13, 4.5), (10, 4)],
    'reading':   [(39, 9), (37, 8.5), (35, 8), (33, 7.5), (30, 7), (27, 6.5),
                  (23, 6), (19, 5.5), (15, 5), (13, 4.5), (10, 4)],
}


def band_table(kind):
    rows, prev = [], 41
    for lo, b in RAW[kind]:
        hi = prev - 1
        rows.append((f'{lo}–{hi}' if lo != hi else f'{lo}', f'{b:g}'))
        prev = lo
    return rows


def table_html(kind):
    rows = band_table(kind)
    body = ''.join(f'<tr><td>{r}</td><td>{b}</td></tr>' for r, b in rows)
    return ('<div class="tblwrap"><table class="bandtbl">'
            '<caption>40 talik xom balldan band ballga — Academic</caption>'
            '<thead><tr><th scope="col">To‘g‘ri javoblar</th><th scope="col">Band</th></tr></thead>'
            f'<tbody>{body}</tbody></table></div>')


EXTRA_STYLE = '''
.tblwrap{overflow-x:auto;margin-top:1.2rem}
.bandtbl{border-collapse:collapse;width:100%;max-width:26rem;font-size:.9rem}
.bandtbl caption{text-align:left;font-family:var(--mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:var(--subtle);padding-bottom:.6rem}
.bandtbl th,.bandtbl td{text-align:left;padding:.45rem .9rem .45rem 0;border-bottom:1px solid var(--line)}
.bandtbl th{font-family:var(--mono);font-size:.7rem;text-transform:uppercase;letter-spacing:.06em;color:var(--subtle);font-weight:400}
.bandtbl td:last-child{font-family:var(--mono)}
.steps{list-style:none;counter-reset:s;margin-top:1.2rem;display:grid;gap:.9rem}
.steps li{counter-increment:s;display:grid;grid-template-columns:1.6rem 1fr;gap:.9rem;font-size:.92rem;line-height:1.7;color:var(--muted)}
.steps li::before{content:counter(s);font-family:var(--mono);font-size:.75rem;color:var(--subtle);padding-top:.2rem}
.steps li strong{color:var(--ink,inherit);font-weight:600}
.testlist{list-style:none;display:grid;gap:.05rem;margin-top:1.2rem;border-top:1px solid var(--line)}
.testlist li{border-bottom:1px solid var(--line)}
.testlist a{display:flex;justify-content:space-between;gap:1rem;padding:.6rem 0;font-size:.9rem;text-decoration:none;color:inherit}
.testlist a:hover{color:var(--accent,inherit)}
.testlist .t{flex:1;min-width:0}
.testlist a>span+span{font-family:var(--mono);font-size:.72rem;color:var(--subtle);white-space:nowrap}
'''

PAGES = {}

PAGES['listening'] = dict(
    slug='listening', cat='Listening',
    kicker='O‘zbekcha · Listening',
    h1='IELTS Listening test — bepul onlayn mashq',
    title_t='IELTS Listening test onlayn — {n} ta bepul test javoblari bilan',
    desc_t=('{n} ta IELTS Listening mashq testi bepul: to‘rt bo‘lim, 40 ta savol, audio bir marta. '
            'Haqiqiy imtihon vaqti, darhol band ball, javob kaliti va audio matni.'),
    lede=('Saytdagi {n} ta Listening testi haqiqiy imtihondagidek ishlaydi: audio bir marta yangraydi, '
          'to‘rt bo‘lim ketma-ket keladi va vaqt to‘xtamaydi. Tugatganingizda 40 talik xom ball, '
          'uning band qiymati, har bir savol bo‘yicha tahlil va audio matni chiqadi.'),
    facts=[('Bo‘limlar', 'To‘rtta. 1 va 2 — kundalik hayot, 3 va 4 — ta’lim va akademik mavzular.'),
           ('Savollar', '40 ta. Har bir to‘g‘ri javob 1 ball.'),
           ('Vaqt', 'Audio taxminan 30 daqiqa. Qog‘ozda javoblarni ko‘chirish uchun 10 daqiqa qo‘shiladi, kompyuterda 2 daqiqa.'),
           ('Audio', 'Bir marta yangraydi. Ortga qaytarib bo‘lmaydi — imtihonda ham, bu yerdagi testlarda ham.'),
           ('Aksent', 'Britan, avstraliya, amerika, yangi zelandiya aksentlari aralash keladi.')],
    types=[('Form / Note / Table completion', 'Bo‘sh joyga eshitgan so‘zingizni yozasiz. So‘z chegarasiga qat’iy rioya qiling: “NO MORE THAN TWO WORDS” yozilgan bo‘lsa, uch so‘z yozgan javob noto‘g‘ri hisoblanadi.'),
           ('Multiple choice', 'Uch yoki undan ortiq variantdan tanlaysiz. Spiker ko‘pincha avval noto‘g‘ri variantni aytib, keyin uni rad etadi — oxirigacha tinglang.'),
           ('Matching', 'Ro‘yxatdagi elementlarni bir-biriga moslashtirasiz. Variantlar audio tartibida kelmasligi mumkin.'),
           ('Map / Plan / Diagram labelling', 'Xarita yoki chizmadagi joylarni belgilaysiz. Boshlanishidan oldin yo‘nalish so‘zlarini — left, opposite, next to, beyond — ko‘z bilan bir bor o‘qib chiqing.'),
           ('Sentence completion', 'Gapni to‘ldirasiz. Grammatikaga qarang: bo‘sh joydan keyin ko‘plik kelsa, javob ham ko‘plikda bo‘ladi.'),
           ('Short answer', 'Qisqa savolga qisqa javob. So‘z chegarasi bu yerda ham amal qiladi.')],
    mistakes=[('Imlo', 'Ma’nosi to‘g‘ri, imlosi xato javob ball olmaydi. Raqam va sanalarni ham xuddi eshitilganidek yozing.'),
              ('Ko‘plik qo‘shimchasi', '“ticket” va “tickets” — ikki xil javob. Gap tuzilishiga qarab qaror qiling.'),
              ('So‘z chegarasi', 'ONE WORD ONLY yozilgan joyda “a ticket” deb yozish — noto‘g‘ri javob.'),
              ('Bitta savolda qotib qolish', 'Bir savolni o‘tkazib yuborsangiz, keyingisiga o‘ting. Audio sizni kutmaydi va bitta savol uchun uchtasini yo‘qotish mumkin.'),
              ('Javobni ko‘chirmaslik', 'Qog‘oz formatda javoblar answer sheet’ga ko‘chirilmasa, hisobga olinmaydi.')],
    steps=[('Test ishlang', 'Bitta to‘liq testni vaqtni to‘xtatmasdan, audio bir marta bilan ishlang. Bu sizning boshlang‘ich ballingiz.'),
           ('Xatolarni ajrating', 'Har bir xatoni ikki turga bo‘ling: eshitmadim yoki eshitdim-u noto‘g‘ri yozdim. Ikkinchisi imlo va grammatika masalasi, uni bir haftada tuzatish mumkin.'),
           ('Audio matnini o‘qing', 'Javobni topolmagan joyingizni matndan toping va o‘sha jumlani qayta tinglang. Spiker qaysi so‘z bilan javobni belgilaganini eslab qoling.'),
           ('Takrorlang', 'Haftasiga ikkita test, yaxshilab tahlil qilingani, shoshib ishlangan yettitadan ko‘proq foyda beradi.')],
    faq=[('IELTS Listening testini bepul onlayn qayerdan topsam bo‘ladi?',
          'Shu sahifadagi ro‘yxatdan. Barcha Listening testlari bepul va ro‘yxatdan o‘tishni talab qilmaydi — testni ochib, darhol boshlashingiz mumkin.'),
         ('Listening’da 30 ta to‘g‘ri javob necha band?',
          '30 ta to‘g‘ri javob — 7.0 band. Jadval shu sahifada, kalkulyator esa band kalkulyatori sahifasida.'),
         ('Audioni ikki marta tinglasam bo‘ladimi?',
          'Imtihonda yo‘q — audio faqat bir marta yangraydi. Shuning uchun bu yerdagi testlarda ham audio bir marta ishlaydi. Tugatgandan keyin esa audio va uning matni ochiladi, tahlil uchun xohlagancha tinglashingiz mumkin.'),
         ('Javoblarni katta harfda yozish kerakmi?',
          'Shart emas, lekin zarar ham qilmaydi. Kompyuter formatda odatdagidek yozavering; qog‘ozda ko‘pchilik bosh harfni afzal ko‘radi, chunki imlo aniqroq o‘qiladi.')],
)

PAGES['reading'] = dict(
    slug='reading', cat='Reading',
    kicker='O‘zbekcha · Reading',
    h1='IELTS Reading test — bepul onlayn mashq',
    title_t='IELTS Reading test onlayn — {n} ta bepul mashq javoblari bilan',
    desc_t=('{full} ta to‘liq IELTS Academic Reading testi va {single} ta bitta matnli qisqa mashq — bepul. '
            'Uchta matn, 40 ta savol, 60 daqiqa; darhol band ball va javob tahlili.'),
    lede=('Saytda {full} ta to‘liq Academic Reading testi — uchta matn, 40 ta savol, 60 daqiqa — va '
          '{single} ta bitta matnli qisqa mashq bor. Yuborganingizdan keyin xom ball, band qiymati va '
          'har bir javobning matnning qaysi qismidan chiqqani ko‘rsatiladi.'),
    facts=[('Matnlar', 'Uchta. Odatda ilmiy-ommabop maqola, tarix yoki tadqiqot matni.'),
           ('Savollar', '40 ta. Har bir to‘g‘ri javob 1 ball.'),
           ('Vaqt', '60 daqiqa. Javoblarni ko‘chirish uchun alohida vaqt berilmaydi.'),
           ('Vaqt taqsimoti', 'Taxminan 17 – 20 – 23 daqiqa: birinchi matn eng oson, oxirgisi eng qiyin.'),
           ('Academic va General', 'Matnlar va xom balldan bandga o‘tish jadvali har xil. Bu sahifadagi jadval — Academic uchun.')],
    types=[('True / False / Not Given', 'Eng ko‘p ball yo‘qotiladigan tur. False — matn aksini aytadi; Not Given — matn bu haqda umuman gapirmaydi. Bilimingizga emas, faqat matnga tayaning.'),
           ('Yes / No / Not Given', 'Xuddi shunday, lekin faktlar emas, muallifning fikri haqida.'),
           ('Matching headings', 'Har bir paragrafga sarlavha tanlaysiz. Avval paragrafni o‘qing, keyin sarlavhalarga qarang — teskarisi emas.'),
           ('Matching information', 'Ma’lumot qaysi paragrafda ekanini topasiz. Bir paragraf bir necha marta javob bo‘lishi mumkin.'),
           ('Sentence / Summary completion', 'Matndagi so‘z bilan to‘ldirasiz. So‘zni o‘zgartirmang — matnda qanday bo‘lsa, shundayligicha ko‘chiring.'),
           ('Multiple choice', 'Variantlar matn tartibida keladi, shuning uchun oldingi javobingiz qayerda bo‘lsa, keyingisi undan pastda.')],
    mistakes=[('Not Given o‘rniga False', 'Matn bu haqda gapirmagan bo‘lsa — Not Given. “Menimcha bu noto‘g‘ri” degan fikr javob emas.'),
              ('Birinchi matnda ortiqcha vaqt', 'Birinchi matnga 25 daqiqa ketsa, uchinchisiga 12 daqiqa qoladi — o‘sha yerda 13 ta savol turadi.'),
              ('Har bir so‘zni o‘qish', 'Matnni boshdan oxir o‘qishga vaqt yetmaydi. Savolni o‘qing, kalit so‘zni toping, o‘sha joyni diqqat bilan o‘qing.'),
              ('Sinonimni sezmaslik', 'Savoldagi so‘z matnda deyarli hech qachon aynan takrorlanmaydi. Matn “decline” desa, savol “fall” deb yozadi.'),
              ('Javobni o‘zgartirib yozish', 'Completion turida matndagi so‘zning shaklini o‘zgartirsangiz, javob noto‘g‘ri hisoblanadi.')],
    steps=[('Vaqt bilan ishlang', 'Bitta to‘liq testni 60 daqiqada, to‘xtatmasdan ishlang. Vaqtsiz ishlangan test haqiqiy ballni ko‘rsatmaydi.'),
           ('Xatoni matndan toping', 'Har bir noto‘g‘ri javob uchun to‘g‘ri javob matnning qayerida turganini toping. Javobni emas, joyni toping.'),
           ('Savol turini yozib boring', 'Xatolaringiz qaysi turda ko‘proq ekanini sanang. Ko‘pincha hammasi bitta turdan chiqadi — o‘sha turni alohida mashq qiling.'),
           ('Vaqt taqsimotini mashq qiling', 'Har bir matnga soat qo‘ying: 17, 20, 23 daqiqa. Vaqt tugasa, javob berilmagan savolni tashlab, keyingi matnga o‘ting.')],
    faq=[('IELTS Reading testini bepul onlayn qayerdan ishlasam bo‘ladi?',
          'Shu sahifadagi ro‘yxatdan. Barcha Reading testlari bepul, ro‘yxatdan o‘tish talab qilinmaydi.'),
         ('Reading’da 30 ta to‘g‘ri javob necha band?',
          'Academic Reading’da 30 ta to‘g‘ri javob — 7.0 band. To‘liq jadval shu sahifada.'),
         ('Academic va General Reading farqi nimada?',
          'Matnlar turi va xom balldan bandga o‘tish jadvali farq qiladi. General Training’da bir xil band uchun ko‘proq to‘g‘ri javob kerak bo‘ladi.'),
         ('Javobni katta harfda yozsam bo‘ladimi?',
          'Ha, bo‘ladi. Baholashda harf katta-kichikligi hisobga olinmaydi, imlo esa hisobga olinadi.')],
)

PAGES['writing'] = dict(
    slug='writing', cat='Writing',
    kicker='O‘zbekcha · Writing',
    h1='IELTS Writing — Task 1 va Task 2 bepul mashq',
    title_t='IELTS Writing Task 1 va Task 2 — bepul mashq va band bahosi',
    desc_t=('IELTS Academic Writing Task 1 va Task 2: format, to‘rtta baholash mezoni, tuzilma va '
            'ko‘p uchraydigan xatolar. Writing Lab’da yozib, darhol band bo‘yicha izoh oling — bepul.'),
    lede=('Writing — eng ko‘p ball yo‘qotiladigan bo‘lim, chunki uni o‘zingiz tekshira olmaysiz. '
          'Bu sahifada ikkala topshiriqning formati, to‘rtta baholash mezoni va eng ko‘p uchraydigan '
          'xatolar bor. Writing Lab’da esa yozgan matningizga darhol band bo‘yicha izoh olasiz.'),
    facts=[('Task 1', 'Academic: grafik, jadval, diagramma yoki jarayonni tasvirlaysiz. Kamida 150 so‘z, taxminan 20 daqiqa.'),
           ('Task 2', 'Esse. Kamida 250 so‘z, taxminan 40 daqiqa.'),
           ('Og‘irligi', 'Task 2 umumiy Writing ballining uchdan ikki qismini tashkil qiladi.'),
           ('Umumiy vaqt', '60 daqiqa, ikkala topshiriq uchun birgalikda.'),
           ('So‘z chegarasi', 'Kam yozilgan ish uchun ball tushiriladi. Ko‘p yozganlik o‘zi jarima emas, lekin vaqt va aniqlikni yeydi.')],
    types=[('Task Achievement / Task Response', 'Savolga to‘liq javob berdingizmi. Task 2’da savolning har bir qismiga javob bo‘lishi shart — ikki qismli savolga bir qismli javob 6 dan yuqoriga chiqmaydi.'),
           ('Coherence and Cohesion', 'Fikr oqimi va bog‘lovchilar. Har bir paragrafda bitta asosiy fikr bo‘lsin; bog‘lovchini ko‘p ishlatish ball qo‘shmaydi, aksincha sun’iy ko‘rinadi.'),
           ('Lexical Resource', 'So‘z boyligi va uni to‘g‘ri ishlatish. Noto‘g‘ri joyda ishlatilgan “murakkab” so‘z oddiy so‘zdan ko‘ra ko‘proq zarar keltiradi.'),
           ('Grammatical Range and Accuracy', 'Grammatik xilma-xillik va aniqlik. Faqat sodda gaplar bilan yozilgan ish 6 dan yuqoriga chiqishi qiyin.')],
    mistakes=[('Task 1’da fikr bildirish', 'Academic Task 1 — tasvir, tahlil emas. “Bu yomon tendensiya” degan jumla ball qo‘shmaydi, aksincha mezonga zid.'),
              ('Raqamsiz Task 1', 'Grafikdagi eng katta, eng kichik va o‘zgarish nuqtalari raqam bilan ko‘rsatilishi kerak.'),
              ('Savolni qayta yozish', 'Kirish qismida savol so‘zma-so‘z ko‘chirilsa, u so‘z sanog‘iga kirmaydi.'),
              ('Misolsiz paragraf', 'Har bir asosiy fikr misol yoki izoh bilan qo‘llab-quvvatlanishi kerak — aks holda paragraf da’vodan iborat bo‘lib qoladi.'),
              ('Yodlangan jumlalar', 'Tayyor kirish shablonlari tanib olinadi va Lexical Resource bo‘yicha ball qo‘shmaydi.')],
    steps=[('Savolni ajrating', 'Task 2 savolini o‘qib, unda nechta savol borligini sanang. Ikkitasi bo‘lsa, ikkalasiga ham alohida paragraf kerak.'),
           ('Rejani yozing', 'Besh daqiqa reja — ikkita asosiy fikr va har biriga bitta misol. Rejasiz yozilgan esse Coherence bo‘yicha ball yo‘qotadi.'),
           ('Vaqt bilan yozing', '20 va 40 daqiqa. Vaqtsiz yozilgan ish imtihonda qanday yozishingizni ko‘rsatmaydi.'),
           ('Izohni oling va qayta yozing', 'Writing Lab bahosini o‘qing, keyin o‘sha esseni qaytadan yozing. Qayta yozish — eng tez band ko‘taruvchi mashq.')],
    faq=[('IELTS Writing’ni bepul tekshirtirsam bo‘ladimi?',
          'Ha. Writing Lab’da Task 1 va Task 2 yozib, to‘rtta mezon bo‘yicha izoh olasiz — bepul va ro‘yxatdan o‘tmasdan.'),
         ('Task 2 uchun necha so‘z yozish kerak?',
          'Kamida 250 so‘z. Amalda 260–290 so‘z qulay: chegaradan o‘tadi, lekin vaqtni yeb qo‘ymaydi.'),
         ('Task 1 va Task 2 dan qaysi biri muhimroq?',
          'Task 2. U Writing ballining uchdan ikki qismini beradi, shuning uchun vaqt yetmay qolsa, Task 2 tugallangan bo‘lishi kerak.'),
         ('Qanday qilib 6.0 dan 7.0 ga ko‘tarilaman?',
          'Odatda ikkita narsa hal qiladi: savolning har bir qismiga javob berish va grammatik aniqlik. 7.0 uchun gaplaringizning ko‘pchiligi xatosiz bo‘lishi kutiladi.')],
)

PAGES['speaking'] = dict(
    slug='speaking', cat='Speaking',
    kicker='O‘zbekcha · Speaking',
    h1='IELTS Speaking — savollar, format va mashq',
    title_t='IELTS Speaking savollari — Part 1, 2, 3 formati va bepul mashq',
    desc_t=('IELTS Speaking Part 1, Part 2 va Part 3 formati, to‘rtta baholash mezoni, cue card '
            'strategiyasi va ko‘p uchraydigan xatolar. Speaking Lab’da ovozingizni yozib mashq qiling.'),
    lede=('Speaking — 11–14 daqiqalik jonli suhbat, uchta qismdan iborat. Bu sahifada har bir '
          'qismning formati, nimaga qarab baholanishi va cue card bilan qanday ishlash kerakligi '
          'yozilgan. Speaking Lab’da savollarga ovozingizni yozib javob berib mashq qilasiz.'),
    facts=[('Part 1', '4–5 daqiqa. O‘zingiz, uyingiz, ishingiz yoki o‘qishingiz haqida oddiy savollar.'),
           ('Part 2', '1 daqiqa tayyorgarlik, 1–2 daqiqa gapirish. Cue card bo‘yicha monolog.'),
           ('Part 3', '4–5 daqiqa. Part 2 mavzusining kengroq, mavhumroq tomonlari haqida suhbat.'),
           ('Umumiy vaqt', '11–14 daqiqa. Suhbat yozib olinadi.'),
           ('Format', 'Jonli imtihonchi bilan. Kompyuterda topshirilganda ham Speaking odam bilan o‘tadi.')],
    types=[('Fluency and Coherence', 'Ravonlik va fikr izchilligi. Uzoq pauza va o‘zini tez-tez tuzatish ball tushiradi; sekin, lekin tekis gapirish esa tushirmaydi.'),
           ('Lexical Resource', 'So‘z boyligi. Mavzuga xos so‘z va iboralarni to‘g‘ri ishlatish — yodlangan “ilg‘or” iboralarni tiqishtirishdan muhimroq.'),
           ('Grammatical Range and Accuracy', 'Grammatik xilma-xillik va aniqlik. Zamonlarni aralashtirmaslik 6.5 dan yuqoriga chiqishda ko‘pincha hal qiluvchi bo‘ladi.'),
           ('Pronunciation', 'Talaffuz. Aksent muammo emas — tushunarlilik, urg‘u va ohang muhim.')],
    mistakes=[('Bir so‘zli javob', '“Do you like reading?” — “Yes.” Bu Fluency uchun eng zarar javob. Har doim sabab yoki misol qo‘shing.'),
              ('Yodlangan javob', 'Yod olingan matn ohangidan bilinadi va ball qo‘shmaydi.'),
              ('Cue card’ning bir qismini o‘tkazib yuborish', 'Kartadagi to‘rtta punktning hammasiga tegib o‘tish kerak.'),
              ('Pauzani “um” bilan to‘ldirish', 'O‘ylash uchun vaqt kerak bo‘lsa, tayyor jumla ishlating: “That’s an interesting question, let me think.”'),
              ('Part 3’da qisqa javob', 'Part 3 fikr va sabab talab qiladi. Bir jumlali javob bu qismda yetarli emas.')],
    steps=[('Mavzular bilan tanishing', 'Speaking mavzular sahifasida Part 2 cue card oilalari va Part 1 savollari yig‘ilgan. Javobni emas, mavzuni tayyorlang.'),
           ('Ovozingizni yozing', 'Speaking Lab’da savolga javob berib, o‘zingizni tinglang. Ko‘pchilik xatosini birinchi marta shu yerda eshitadi.'),
           ('Bir daqiqani mashq qiling', 'Cue card uchun 1 daqiqada to‘rtta kalit so‘z yozishni o‘rganing — jumla emas, kalit so‘z.'),
           ('Takrorlab gapiring', 'Bir cue card’ni uch marta gapiring: birinchisi tarqoq, uchinchisi ravon chiqadi. Farqni eshitish o‘zi mashq.')],
    faq=[('IELTS Speaking’ni yolg‘iz qanday mashq qilaman?',
          'Savolga ovozingizni yozib javob bering va o‘zingizni tinglang. Speaking Lab shu uchun qilingan: savol bankasi, yozib olish va izoh bir joyda.'),
         ('Speaking necha daqiqa davom etadi?',
          '11–14 daqiqa: Part 1 uchun 4–5, Part 2 uchun tayyorgarlik bilan 3–4, Part 3 uchun 4–5 daqiqa.'),
         ('Cue card’da nima yozish kerak?',
          'Jumla emas, to‘rtta kalit so‘z — kartadagi har bir punkt uchun bittadan. Gapirayotganda ko‘z tashlab olasiz.'),
         ('Aksentim ball tushiradimi?',
          'Yo‘q. Pronunciation mezoni tushunarlilik, urg‘u va ohangga qaraydi, aksentga emas.')],
)


def skill_tests(tests, cat, limit=24):
    rows = [t for t in tests if t.get('category') == cat
            and (t.get('url') or '').startswith(BASE)
            and not (t.get('url') or '').rstrip('/').endswith(('/tests', '/ielts-hub'))]
    rows.sort(key=lambda t: t.get('date') or '', reverse=True)
    return rows[:limit], len(rows)


def split_counts(tests, cat):
    """Reading holds both full 40-question papers and single-passage drills.
    The page says which is which rather than calling all of them 'tests'."""
    rows = [t for t in tests if t.get('category') == cat
            and (t.get('url') or '').startswith(BASE)]
    single = sum(1 for t in rows if '1 passage' in (t.get('difficulty') or ''))
    two = sum(1 for t in rows if '2 passages' in (t.get('difficulty') or ''))
    return {'single': single + two, 'full': len(rows) - single - two}


def build(key, tests):
    p = PAGES[key]
    rows, n = skill_tests(tests, p['cat'])
    url = f"{BASE}/uz/{p['slug']}/"
    counts = dict(n=n, **split_counts(tests, p['cat']))
    title = p['title_t'].format(**counts)
    desc = p['desc_t'].format(**counts)
    lede = p['lede'].format(**counts)

    ld = {"@context": "https://schema.org", "@graph": [
        {"@type": "WebPage", "@id": url + "#page", "url": url, "name": title,
         "description": desc, "inLanguage": "uz",
         "isPartOf": {"@id": f"{BASE}/#website"},
         "publisher": {"@id": f"{BASE}/#org"}},
        {"@type": "FAQPage", "inLanguage": "uz", "mainEntity": [
            {"@type": "Question", "name": q,
             "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in p['faq']]},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "Flarestamina", "item": BASE + '/'},
            {"@type": "ListItem", "position": 2, "name": "O‘zbekcha", "item": BASE + '/uz/'},
            {"@type": "ListItem", "position": 3, "name": p['h1'], "item": url}]}]}

    alt = (f'<link rel="alternate" hreflang="uz" href="{url}">\n'
           f'<link rel="alternate" hreflang="en" href="{BASE}/ielts-{p["slug"]}-test/">\n'
           if key in ('listening', 'reading') else
           f'<link rel="alternate" hreflang="uz" href="{url}">\n')

    sib = [(f'/uz/{k}/', PAGES[k]['h1'].split(' — ')[0]) for k in PAGES if k != key]
    tools = [('/convert/', 'Ball konverteri'), ('/band-calculator/', 'Band kalkulyatori'),
             ('/plan/', 'O‘quv rejasi'), ('/uz/', 'O‘zbekcha bosh sahifa')]

    if key in ('listening', 'reading'):
        table = table_html('listening' if key == 'listening' else 'reading')
        table_sec = f'''
    <section class="sec">
      <h2>Xom balldan band ballga</h2>
      <p>40 talik xom ball rasmiy jadval bo‘yicha bandga aylantiriladi. Quyidagi jadval — Academic {p['cat']} uchun; kalkulyator <a href="/band-calculator/">band kalkulyatori</a> sahifasida.</p>
      {table}
    </section>
'''
        list_head = 'Testlar'
        list_note = (f'Saytda {n} ta {p["cat"]} sahifasi bor. Quyida eng yangi {len(rows)} tasi; '
                     f'to‘liq ro‘yxat <a href="/tests/">barcha testlar</a> sahifasida.')
    else:
        table_sec = ''
        list_head = 'Mashq sahifalari'
        list_note = f'{p["cat"]} bo‘yicha saytdagi sahifalar.'

    listing = '\n'.join(
        f'        <li><a href="{escape((t.get("url") or "").replace(BASE, ""))}">'
        f'<span class="t">{escape(t.get("title") or "")}</span>'
        f'<span>{escape(t.get("date") or "")}</span></a></li>' for t in rows)

    body = f'''
<section class="page-head">
  <div class="wrap">
    <p class="kicker">{escape(p['kicker'])}</p>
    <h1>{escape(p['h1'])}</h1>
    <p class="lede">{escape(lede)}</p>
    <div class="cta-row">
      <a class="btn solid" href="{'/ielts-' + p['slug'] + '-test/' if key in ('listening', 'reading') else ('/writing/' if key == 'writing' else '/pangea8-speaking/')}">Mashqni boshlash</a>
      <a class="btn ghost" href="/uz/">O‘zbekcha bosh sahifa</a>
    </div>
  </div>
</section>

<section>
  <div class="wrap">
    <section class="sec">
      <h2>Format</h2>
      <ul class="facts">
{chr(10).join(f'        <li><b>{escape(k)}</b><span>{escape(v)}</span></li>' for k, v in p['facts'])}
      </ul>
    </section>

    <section class="sec">
      <h2>{'Savol turlari' if key in ('listening', 'reading') else 'Nimaga qarab baholanadi'}</h2>
      <div class="qa">
{chr(10).join(f'        <details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q, a in p['types'])}
      </div>
    </section>
{table_sec}
    <section class="sec">
      <h2>Ko‘p uchraydigan xatolar</h2>
      <ul class="facts">
{chr(10).join(f'        <li><b>{escape(k)}</b><span>{escape(v)}</span></li>' for k, v in p['mistakes'])}
      </ul>
    </section>

    <section class="sec">
      <h2>Qanday mashq qilish kerak</h2>
      <ol class="steps">
{chr(10).join(f'        <li><strong>{escape(h)}</strong> {escape(d)}</li>' for h, d in p['steps'])}
      </ol>
    </section>
'''

    if rows:
        body += f'''
    <section class="sec">
      <h2>{list_head}</h2>
      <p>{list_note}</p>
      <ul class="testlist">
{listing}
      </ul>
    </section>
'''

    body += f'''
    <section class="sec">
      <h2>Ko‘p so‘raladigan savollar</h2>
      <div class="qa">
{chr(10).join(f'        <details><summary>{escape(q)}</summary><p>{escape(a)}</p></details>' for q, a in p['faq'])}
      </div>
    </section>

    <section class="sec">
      <h2>Boshqa bo‘limlar</h2>
      <div class="linkrow">
{chr(10).join(f'        <a class="chip" href="{h}">{escape(t)}</a>' for h, t in sib + tools)}
      </div>
    </section>
  </div>
</section>
'''

    en_switch = '''<script>
(function(){
  var b=document.querySelector('[data-lang="en"]');
  if(b) b.addEventListener('click',function(e){e.stopPropagation();location.href='/';},true);
})();
</script>
'''

    html = (shell.head(escape(title), escape(desc), url,
                       f'{BASE}/og-image.png?v=2',
                       extra_head=alt + '<script type="application/ld+json">\n'
                       + json.dumps(ld, ensure_ascii=False) + '\n</script>\n<style>\n'
                       + STYLE.strip() + '\n' + EXTRA_STYLE.strip() + '\n</style>\n', lang='uz')
            + shell.header() + body
            + shell.footer(json.dumps(dict(shell.CHROME_UZ), ensure_ascii=False, indent=1),
                           extra_scripts=en_switch))

    d = os.path.join(ROOT, 'uz', p['slug'])
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, 'index.html'), 'w', encoding='utf-8').write(html)
    return p['slug'], len(html), len(rows), n


def main():
    tests = load()
    for key in PAGES:
        slug, size, shown, total = build(key, tests)
        print(f'/uz/{slug}/ built — {size} bytes, {shown} of {total} tests linked')


if __name__ == '__main__':
    main()
