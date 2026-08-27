"""Enrich TARIX360 FIRST10 city records and topic links.

This is a deterministic content migration, not a test.  It keeps the existing
topic_config -> showFeatureIds -> master_all_features runtime contract intact.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"

UNESCO_OTRAR = "https://whc.unesco.org/en/tentativelists/6568/"
UNESCO_KUNYA = "https://whc.unesco.org/en/list/1199"
UNESCO_SHAHRISABZ = "https://whc.unesco.org/en/list/885/"
IRANICA_CENTRAL_ASIA = "https://www.iranicaonline.org/articles/central-asia-v/"
IRANICA_CHAGHATAY = "https://www.iranicaonline.org/articles/chaghatayid-dynasty/"
IRANICA_JALAL = "https://www.iranicaonline.org/articles/jalal-al-din-kvarazmsahi-mengbirni/"
IRANICA_SAMARQAND = "https://www.iranicaonline.org/articles/samarqand-i/"
IRANICA_LITERATURE = "https://www.iranicaonline.org/articles/iran-viii2-classical-persian-literature/"


def relation(state_id: str, kind: str, note: str) -> dict:
    return {"state_id": state_id, "kind": kind, "note_uz": note}


CITY_META = {
    "CITY_001": dict(name_uz="Samarqand", historical_name_uz="Samarqand", modern_name_uz="Samarqand", modern_country_uz="O‘zbekiston", modern_region_uz="Samarqand viloyati", summary_uz="Movarounnahrning yirik siyosiy, savdo va ilmiy markazi; Amir Temur davrida saltanat poytaxtiga aylandi.", topic_ids=[1,2,3,6,7,9,10], source_refs=[IRANICA_CENTRAL_ASIA, IRANICA_SAMARQAND]),
    "CITY_002": dict(name_uz="Buxoro", historical_name_uz="Buxoro", modern_name_uz="Buxoro", modern_country_uz="O‘zbekiston", modern_region_uz="Buxoro viloyati", summary_uz="Zarafshon vohasidagi qadimiy savdo va ilm markazi; Chig‘atoy ulusining g‘arbiy shaharlari qatorida bo‘lgan.", topic_ids=[1,2,3,6,7,9,10], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_003": dict(name_uz="Toshkent", historical_name_uz="Choch / Shosh", modern_name_uz="Toshkent", modern_country_uz="O‘zbekiston", modern_region_uz="Toshkent shahri", summary_uz="Choch vohasining markazi; Movarounnahr va Yettisuv oralig‘idagi strategik tugun.", topic_ids=[7,9,10], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_004": dict(name_uz="Kesh / Shahrisabz", historical_name_uz="Kesh", modern_name_uz="Shahrisabz", modern_country_uz="O‘zbekiston", modern_region_uz="Qashqadaryo viloyati", summary_uz="Barlos urug‘ining tayanch markazi va Amir Temurning tug‘ilgan hududi bilan bog‘liq shahar.", topic_ids=[9,10], source_refs=[UNESCO_SHAHRISABZ, IRANICA_CENTRAL_ASIA]),
    "CITY_005": dict(name_uz="Termiz", historical_name_uz="Termiz", modern_name_uz="Termiz", modern_country_uz="O‘zbekiston", modern_region_uz="Surxondaryo viloyati", summary_uz="Amudaryo kechuvi va Movarounnahr–Baqtriya yo‘lidagi strategik shahar.", topic_ids=[9,10], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_006": dict(name_uz="Balx", historical_name_uz="Balx", modern_name_uz="Balkh", modern_country_uz="Afg‘oniston", modern_region_uz="Balx viloyati", summary_uz="Xuroson va Toxariston oralig‘idagi yirik siyosiy-madaniy markaz; 1370-yil voqealarida muhim o‘rin tutadi.", topic_ids=[1,9,10], source_refs=[IRANICA_CENTRAL_ASIA, IRANICA_LITERATURE]),
    "CITY_007": dict(name_uz="Hirot", historical_name_uz="Hirot", modern_name_uz="Herat", modern_country_uz="Afg‘oniston", modern_region_uz="Hirot viloyati", summary_uz="Xurosonning yirik markazi; keyinchalik Temuriylar davrida kuchli madaniy poytaxtga aylangan.", topic_ids=[1,9], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_008": dict(name_uz="Marv", historical_name_uz="Marv", modern_name_uz="Mary yaqinidagi Qadimgi Marv", modern_country_uz="Turkmaniston", modern_region_uz="Mary viloyati", summary_uz="Buyuk Ipak yo‘li va Xurosondagi yirik voha shahri; Xorazm, Buxoro va Eron yo‘llarini bog‘lagan.", topic_ids=[1,3], source_refs=[UNESCO_OTRAR]),
    "CITY_009": dict(name_uz="Gurganj / Ko‘hna Urganch", historical_name_uz="Gurganj (Urganch)", modern_name_uz="Ko‘hna Urganch", modern_country_uz="Turkmaniston", modern_region_uz="Dashoguz viloyati", summary_uz="Xorazmshohlar davlatining asosiy poytaxtlaridan biri. Nuqta zamonaviy O‘zbekistonning Urganchiga emas, Ko‘hna Urganch yodgorligiga to‘g‘ri keladi.", topic_ids=[1,2,3,4], source_refs=[UNESCO_KUNYA, IRANICA_JALAL]),
    "CITY_010": dict(name_uz="O‘tror / Forob", historical_name_uz="O‘tror (Forob, Tarband)", modern_name_uz="O‘trartobe arxeologik shaharchasi", modern_country_uz="Qozog‘iston", modern_region_uz="Turkiston viloyati, O‘tror tumani", summary_uz="Sirdaryo yo‘lidagi voha poytaxti; 1218-yilgi O‘tror voqeasi va mo‘g‘ullar yurishining boshlanish nuqtasi.", topic_ids=[1,2,3], source_refs=[UNESCO_OTRAR]),
    "CITY_011": dict(name_uz="Xo‘jand", historical_name_uz="Xo‘jand", modern_name_uz="Khujand", modern_country_uz="Tojikiston", modern_region_uz="Sug‘d viloyati", summary_uz="Sirdaryo bo‘yidagi chegara va savdo shahri; Farg‘ona bilan Movarounnahrni bog‘lagan.", topic_ids=[1,3,9,10], source_refs=[UNESCO_OTRAR, IRANICA_CENTRAL_ASIA]),
    "CITY_012": dict(name_uz="Farg‘ona", historical_name_uz="Farg‘ona vohasi", modern_name_uz="Farg‘ona", modern_country_uz="O‘zbekiston", modern_region_uz="Farg‘ona viloyati", summary_uz="Tarixiy Farg‘ona vohasining umumlashtirilgan tayanch nuqtasi; aniq bitta o‘rta asr shahri chegarasini anglatmaydi.", topic_ids=[6,7,9,10], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_013": dict(name_uz="Andijon", historical_name_uz="Andijon", modern_name_uz="Andijon", modern_country_uz="O‘zbekiston", modern_region_uz="Andijon viloyati", summary_uz="Farg‘ona vodiysining sharqiy siyosiy va savdo markazlaridan biri.", topic_ids=[7,9,10], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_014": dict(name_uz="O‘sh", historical_name_uz="O‘sh", modern_name_uz="Osh", modern_country_uz="Qirg‘iziston", modern_region_uz="Osh shahri", summary_uz="Farg‘ona vodiysidan Qashg‘ar tomonga o‘tuvchi tog‘ yo‘llaridagi qadimiy markaz.", topic_ids=[6,7,9], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_015": dict(name_uz="Olmaliq", historical_name_uz="Olmaliq", modern_name_uz="Huocheng yaqinidagi tarixiy Olmaliq hududi", modern_country_uz="Xitoy", modern_region_uz="Shinjon-Uyg‘ur avtonom rayoni, Ili vodiysi", summary_uz="Sharqiy Chig‘atoy va Mo‘g‘uliston hukmdorlarining muhim qarorgohlaridan biri; nuqta taxminiy tarixiy hududni ko‘rsatadi.", topic_ids=[6,7], source_refs=[IRANICA_CHAGHATAY, IRANICA_CENTRAL_ASIA]),
    "CITY_016": dict(name_uz="Talas / Taroz", historical_name_uz="Talas–Taroz vohasi", modern_name_uz="Taraz", modern_country_uz="Qozog‘iston", modern_region_uz="Jambil viloyati", summary_uz="Yettisuv va Movarounnahr oralig‘idagi savdo hamda yaylov yo‘llari markazi.", topic_ids=[6,7], source_refs=[UNESCO_OTRAR, IRANICA_CENTRAL_ASIA]),
    "CITY_017": dict(name_uz="Qashg‘ar", historical_name_uz="Qashg‘ar", modern_name_uz="Kashgar", modern_country_uz="Xitoy", modern_region_uz="Shinjon-Uyg‘ur avtonom rayoni", summary_uz="Tarim havzasining g‘arbiy darvozasi va Mo‘g‘ulistonning muhim siyosiy-savdo markazi.", topic_ids=[6,7], source_refs=[IRANICA_CHAGHATAY, IRANICA_CENTRAL_ASIA]),
    "CITY_018": dict(name_uz="Aqsu", historical_name_uz="Aqsu", modern_name_uz="Aksu", modern_country_uz="Xitoy", modern_region_uz="Shinjon-Uyg‘ur avtonom rayoni", summary_uz="Tarim havzasining shimoliy yo‘lidagi shahar; keyingi Mo‘g‘uliston xonlari qarorgohlaridan biri.", topic_ids=[6,7], source_refs=[IRANICA_CHAGHATAY]),
    "CITY_019": dict(name_uz="Yorkand", historical_name_uz="Yorkand", modern_name_uz="Yarkant (Shache)", modern_country_uz="Xitoy", modern_region_uz="Shinjon-Uyg‘ur avtonom rayoni", summary_uz="Janubiy Tarim yo‘lidagi voha shahri va Qashg‘ariya siyosiy markazlaridan biri.", topic_ids=[7], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_020": dict(name_uz="Xo‘tan", historical_name_uz="Xo‘tan", modern_name_uz="Hotan", modern_country_uz="Xitoy", modern_region_uz="Shinjon-Uyg‘ur avtonom rayoni", summary_uz="Janubiy Tarim havzasidagi qadimiy voha va karvon savdosi markazi.", topic_ids=[7], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_021": dict(name_uz="Kucha", historical_name_uz="Kucha", modern_name_uz="Kuqa", modern_country_uz="Xitoy", modern_region_uz="Shinjon-Uyg‘ur avtonom rayoni", summary_uz="Tarim havzasining shimoliy Ipak yo‘li bo‘yidagi yirik voha shahri.", topic_ids=[7], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_022": dict(name_uz="Turfon", historical_name_uz="Turfon", modern_name_uz="Turpan", modern_country_uz="Xitoy", modern_region_uz="Shinjon-Uyg‘ur avtonom rayoni", summary_uz="Sharqiy Tarim va Uyg‘ur vohalarini bog‘lovchi markaz; Chig‘atoy hududlari bilan aloqador.", topic_ids=[7], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_023": dict(name_uz="Beshbaliq", historical_name_uz="Beshbaliq", modern_name_uz="Jimsar yaqinidagi tarixiy hudud", modern_country_uz="Xitoy", modern_region_uz="Shinjon-Uyg‘ur avtonom rayoni", summary_uz="Tyanshan shimolidagi Uyg‘ur va Chig‘atoy davri siyosiy markazlaridan biri; joylashuv arxeologik hudud bo‘yicha taxminiy.", topic_ids=[6,7], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_024": dict(name_uz="Hami", historical_name_uz="Komul / Hami", modern_name_uz="Hami", modern_country_uz="Xitoy", modern_region_uz="Shinjon-Uyg‘ur avtonom rayoni", summary_uz="Tarim yo‘llarining sharqiy darvozasi va Mo‘g‘ulistonning sharqiy ta’sir hududlaridan biri.", topic_ids=[7], source_refs=[IRANICA_CENTRAL_ASIA]),
    "CITY_025": dict(name_uz="Kobul", historical_name_uz="Kobul", modern_name_uz="Kabul", modern_country_uz="Afg‘oniston", modern_region_uz="Kobul viloyati", summary_uz="Hindukush yo‘llaridagi strategik markaz; Jaloliddin qo‘shinlarining G‘azni va Hind vodiysi harakatlari bilan bog‘liq.", topic_ids=[4,5], source_refs=[IRANICA_JALAL]),
    "CITY_026": dict(name_uz="Dehli", historical_name_uz="Dehli", modern_name_uz="Delhi", modern_country_uz="Hindiston", modern_region_uz="Milliy poytaxt hududi", summary_uz="Dehli sultonligi markazi; Jaloliddinning Hindistondagi siyosiy aloqalari kontekstida muhim.", topic_ids=[4,5,8], source_refs=[IRANICA_JALAL, IRANICA_LITERATURE]),
    "CITY_027": dict(name_uz="Tabriz", historical_name_uz="Tabriz", modern_name_uz="Tabriz", modern_country_uz="Eron", modern_region_uz="Sharqiy Ozarbayjon viloyati", summary_uz="Ozarbayjonning siyosiy-savdo markazi; Jaloliddin 1225-yilda bu hududda hokimiyat o‘rnatgan.", topic_ids=[5,8], source_refs=[IRANICA_JALAL, IRANICA_LITERATURE]),
    "CITY_028": dict(name_uz="Bag‘dod", historical_name_uz="Bag‘dod", modern_name_uz="Baghdad", modern_country_uz="Iroq", modern_region_uz="Bag‘dod gubernatorligi", summary_uz="Abbosiy xalifaligi poytaxti; Jaloliddin davridagi Yaqin Sharq siyosiy muvozanatining markazi.", topic_ids=[5], source_refs=[IRANICA_JALAL]),
    "CITY_029": dict(name_uz="Halab", historical_name_uz="Halab", modern_name_uz="Aleppo", modern_country_uz="Suriya", modern_region_uz="Halab gubernatorligi", summary_uz="Shimoliy Suriya savdo va siyosiy markazi; XIII asr mintaqaviy kuchlari kontekstida.", topic_ids=[5], source_refs=[IRANICA_JALAL]),
    "CITY_030": dict(name_uz="Damashq", historical_name_uz="Damashq", modern_name_uz="Damascus", modern_country_uz="Suriya", modern_region_uz="Damashq", summary_uz="Shomning yirik siyosiy va ilmiy markazi.", topic_ids=[5,8], source_refs=[IRANICA_LITERATURE]),
    "CITY_031": dict(name_uz="Anqara", historical_name_uz="Anqara", modern_name_uz="Ankara", modern_country_uz="Turkiya", modern_region_uz="Anqara viloyati", summary_uz="Anadolu ichki yo‘llaridagi shahar; XIII asr siyosiy-madaniy makoni kontekstida.", topic_ids=[5,8], source_refs=[IRANICA_LITERATURE]),
    "CITY_032": dict(name_uz="Isfahon", historical_name_uz="Isfahon", modern_name_uz="Isfahan", modern_country_uz="Eron", modern_region_uz="Isfahon viloyati", summary_uz="Markaziy Eronning yirik shahri; Jaloliddinning 1220-yillardagi harbiy-siyosiy tayanchlaridan biri.", topic_ids=[1,5], source_refs=[IRANICA_JALAL]),
    "CITY_033": dict(name_uz="Sheroz", historical_name_uz="Sheroz", modern_name_uz="Shiraz", modern_country_uz="Eron", modern_region_uz="Fors viloyati", summary_uz="Fors viloyatining madaniy markazi; Sa’diy hayoti va klassik adabiyot bilan bog‘liq.", topic_ids=[5,8], source_refs=[IRANICA_JALAL, IRANICA_LITERATURE]),
    "CITY_034": dict(name_uz="Mashhad", historical_name_uz="Tus / Mashhad hududi", modern_name_uz="Mashhad", modern_country_uz="Eron", modern_region_uz="Razaviy Xuroson viloyati", summary_uz="Xurosonning keyingi davrlardagi yirik diniy va savdo markazi; tarixiy Tus shahri yaqinida.", topic_ids=[1,8], source_refs=[IRANICA_LITERATURE]),
    "CITY_035": dict(name_uz="O‘tror / Forob (takroriy yozuv)", historical_name_uz="Forob", modern_name_uz="O‘trartobe", modern_country_uz="Qozog‘iston", modern_region_uz="Turkiston viloyati", summary_uz="CITY_010 bilan bir joyni ifodalovchi eski takroriy yozuv; sahnalarda ishlatilmaydi.", topic_ids=[], source_refs=[UNESCO_OTRAR], deprecated_duplicate_of="CITY_010"),
}


NEW_CITIES = [
    ("CITY_036", "Ghazni", [68.42, 33.5539], dict(name_uz="G‘azni", historical_name_uz="G‘azna", modern_name_uz="Ghazni", modern_country_uz="Afg‘oniston", modern_region_uz="G‘azni viloyati", summary_uz="Jaloliddin Manguberdining Afg‘onistondagi asosiy harbiy tayanchi; Parvon g‘alabasi oldidan qo‘shin shu hududda jamlangan.", topic_ids=[4], source_refs=[IRANICA_JALAL])),
    ("CITY_037", "Nasa", [58.212, 37.965], dict(name_uz="Naso", historical_name_uz="Naso", modern_name_uz="Qadimgi Niso yodgorligi", modern_country_uz="Turkmaniston", modern_region_uz="Ahal viloyati, Ashxobod yaqinida", summary_uz="Jaloliddinning Xorazmdan Xurosonga harakati bilan bog‘liq qadimiy shahar va qal’a hududi.", topic_ids=[4], source_refs=[IRANICA_JALAL], coordinate_quality="archaeological_site approximate")),
    ("CITY_038", "Kerman", [57.0834, 30.2839], dict(name_uz="Kirmon", historical_name_uz="Kirmon", modern_name_uz="Kerman", modern_country_uz="Eron", modern_region_uz="Kirmon viloyati", summary_uz="Jaloliddin Hindistondan qaytgach kirgan Eron viloyati va siyosiy tayanchlardan biri.", topic_ids=[5], source_refs=[IRANICA_JALAL])),
    ("CITY_039", "Tbilisi", [44.8271, 41.7151], dict(name_uz="Tbilisi", historical_name_uz="Tiflis", modern_name_uz="Tbilisi", modern_country_uz="Gruziya", modern_region_uz="Tbilisi shahri", summary_uz="Jaloliddinning Kavkaz yurishlari va 1226-yil voqealari bilan bog‘liq markaz.", topic_ids=[5], source_refs=[IRANICA_JALAL])),
    ("CITY_040", "Ahlat", [42.4814, 38.7526], dict(name_uz="Ahlat", historical_name_uz="Ahlat / Xilot", modern_name_uz="Ahlat", modern_country_uz="Turkiya", modern_region_uz="Bitlis viloyati", summary_uz="Van ko‘li bo‘yidagi qal’a-shahar; Jaloliddinning so‘nggi g‘arbiy yurishlaridagi muhim nishon.", topic_ids=[5], source_refs=[IRANICA_JALAL])),
    ("CITY_041", "Lahore", [74.3587, 31.5204], dict(name_uz="Lahor", historical_name_uz="Lahor", modern_name_uz="Lahore", modern_country_uz="Pokiston", modern_region_uz="Panjob viloyati", summary_uz="Hind vodiysi va Dehli sultonligi oralig‘idagi yirik markaz; Jaloliddinning Hindistondagi faoliyati kontekstida.", topic_ids=[4,5], source_refs=[IRANICA_JALAL])),
    ("CITY_042", "Konya", [32.4932, 37.8746], dict(name_uz="Konya", historical_name_uz="Quniya / Konya", modern_name_uz="Konya", modern_country_uz="Turkiya", modern_region_uz="Konya viloyati", summary_uz="Jaloliddin Rumiy yashab ijod qilgan Saljuqiy Anadolu madaniy markazi.", topic_ids=[8], source_refs=[IRANICA_LITERATURE])),
    ("CITY_043", "Hamadan", [48.515, 34.7989], dict(name_uz="Hamadon", historical_name_uz="Hamadon", modern_name_uz="Hamadan", modern_country_uz="Eron", modern_region_uz="Hamadon viloyati", summary_uz="G‘arbiy Eronning qadimiy yo‘l tuguni; Jaloliddinning Eron va Ozarbayjon harakatlari kontekstida.", topic_ids=[5], source_refs=[IRANICA_JALAL])),
    ("CITY_044", "Nishapur", [58.7961, 36.2141], dict(name_uz="Nishopur", historical_name_uz="Nishopur", modern_name_uz="Neyshabur", modern_country_uz="Eron", modern_region_uz="Razaviy Xuroson viloyati", summary_uz="Xurosonning yirik ilmiy va savdo markazi; Marv, Hirot va O‘tror yo‘llari bilan bog‘langan.", topic_ids=[1,3,8], source_refs=[UNESCO_OTRAR, IRANICA_LITERATURE])),
    ("CITY_045", "Rayy", [51.4386, 35.6006], dict(name_uz="Ray", historical_name_uz="Ray", modern_name_uz="Rey (Tehron metropoliyasi)", modern_country_uz="Eron", modern_region_uz="Tehron viloyati", summary_uz="Shimoliy Eronning qadimiy shahri; Xurosondan Iroq va Ozarbayjonga boruvchi yo‘lda joylashgan.", topic_ids=[1,5], source_refs=[IRANICA_JALAL])),
]


STATE_RELATIONS = {
    "CITY_001": [relation("P00_KHWARAZM_1218", "yirik_markaz", "Muhammad Xorazmshoh davrida Movarounnahr markazi"), relation("P01_CHAGATAI_EARLY", "asosiy_shahar", "Chig‘atoy ulusining g‘arbiy qismi"), relation("P02_CHAGATAI_UNIFIED", "asosiy_shahar", "Movarounnahr markazi"), relation("P05_SAMARKAND", "siyosiy_markaz", "Samarqand siyosiy markazi"), relation("P06_TIMUR_1370", "poytaxt", "Amir Temurning boshlang‘ich hokimiyat markazi")],
    "CITY_002": [relation("P00_KHWARAZM_1218", "yirik_markaz", "Xorazmshohlar nazoratidagi Movarounnahr shahri"), relation("P01_CHAGATAI_EARLY", "asosiy_shahar", "Chig‘atoy ulusining g‘arbiy shahri"), relation("P02_CHAGATAI_UNIFIED", "asosiy_shahar", "Movarounnahr markazi"), relation("P05_BUKHARA", "siyosiy_markaz", "Buxoro–g‘arbiy Movarounnahr zonasi"), relation("P06_TIMUR_1370", "nazorat_markazi", "1370-yildagi boshlang‘ich nazorat hududi")],
    "CITY_003": [relation("P04_WEST_CHAGATAI", "chegara_markazi", "Choch vohasi"), relation("P06_TIMUR_1370", "nazorat_markazi", "Temurning kuchi Chochgacha yoyilgan")],
    "CITY_004": [relation("P05_BARLAS", "tayanch_markaz", "Barlos urug‘i va Kesh tayanchi"), relation("P06_TIMUR_1370", "tayanch_markaz", "Amir Temurning tug‘ilgan hududi")],
    "CITY_005": [relation("P05_QARAUNAS", "strategik_shahar", "Amudaryo kechuvi va janubiy yo‘l"), relation("P06_TIMUR_1370", "strategik_shahar", "Movarounnahrning janubiy darvozasi")],
    "CITY_006": [relation("P05_QARAUNAS", "siyosiy_markaz", "Qaraunas va Amir Husayn ta’siri"), relation("P06_TIMUR_1370", "hal_qiluvchi_markaz", "1370-yil Balx voqealari")],
    "CITY_009": [relation("P00_KHWARAZM_1218", "poytaxt", "Xorazmshohlar davlatining asosiy poytaxtlaridan biri")],
    "CITY_010": [relation("P00_KHWARAZM_1218", "chegara_savdo_markazi", "Xorazm bilan bog‘langan Sirdaryo vohasi va 1218-yil voqeasi")],
    "CITY_011": [relation("P00_KHWARAZM_1218", "chegara_qalasi", "Sirdaryo bo‘yidagi mudofaa va savdo markazi"), relation("P04_WEST_CHAGATAI", "shahar", "G‘arbiy Chig‘atoy / Movarounnahr sharqiy chekkasi"), relation("P06_TIMUR_1370", "nazorat_markazi", "Movarounnahrning sharqiy yo‘li")],
    "CITY_012": [relation("P05_FERGHANA", "voha_markazi", "Farg‘ona siyosiy zonasi")],
    "CITY_013": [relation("P05_FERGHANA", "shahar", "Farg‘ona vodiysi sharqi")],
    "CITY_014": [relation("P05_FERGHANA", "yo‘l_markazi", "Farg‘ona–Qashg‘ar yo‘li")],
    "CITY_015": [relation("P03_MOGHULISTAN_1372", "qarorgoh", "Sharqiy Chig‘atoy / Mo‘g‘uliston siyosiy markazi")],
    "CITY_016": [relation("P01_CHAGATAI_EARLY", "yo‘l_markazi", "Chig‘atoy ulusining Yettisuv qismi"), relation("P03_MOGHULISTAN_1372", "voha_markazi", "Talas–Chu hududi")],
    "CITY_017": [relation("P01_CHAGATAI_EARLY", "sharqiy_markaz", "Chig‘atoy ulusining Tarim yo‘li"), relation("P03_MOGHULISTAN_1372", "asosiy_shahar", "Mo‘g‘ulistonning janubiy savdo markazi")],
    "CITY_018": [relation("P03_MOGHULISTAN_1372", "qarorgoh", "Keyingi Mo‘g‘uliston siyosiy markazlaridan biri")],
    "CITY_019": [relation("P03_MOGHULISTAN_1372", "voha_shahri", "Janubiy Tarim vohasi")],
    "CITY_020": [relation("P03_MOGHULISTAN_1372", "voha_shahri", "Janubiy Tarim vohasi")],
    "CITY_021": [relation("P03_MOGHULISTAN_1372", "voha_shahri", "Shimoliy Tarim yo‘li")],
    "CITY_022": [relation("P03_MOGHULISTAN_1372", "voha_shahri", "Sharqiy Tarim vohasi")],
    "CITY_023": [relation("P01_CHAGATAI_EARLY", "sharqiy_markaz", "Tyanshan shimolidagi siyosiy markaz"), relation("P03_MOGHULISTAN_1372", "chegara_markazi", "Sharqiy ta’sir hududi")],
    "CITY_024": [relation("P03_MOGHULISTAN_1372", "sharqiy_darvoza", "Komul/Hami sharqiy yo‘l tuguni")],
}


TOPIC_ADDITIONS = {
    1: ["CITY_006", "CITY_007", "CITY_032", "CITY_044", "CITY_045"],
    3: ["CITY_006", "CITY_007", "CITY_044"],
    4: ["CITY_036", "CITY_037", "CITY_041"],
    5: ["CITY_027", "CITY_033", "CITY_038", "CITY_039", "CITY_040", "CITY_041", "CITY_043", "CITY_045"],
    6: ["CITY_012", "CITY_014", "CITY_018", "CITY_023"],
    7: ["CITY_003", "CITY_004", "CITY_012", "CITY_013", "CITY_014", "CITY_016", "CITY_018", "CITY_019", "CITY_020", "CITY_021", "CITY_022", "CITY_023", "CITY_024"],
    8: ["CITY_006", "CITY_026", "CITY_027", "CITY_033", "CITY_042"],
    9: ["CITY_002", "CITY_005", "CITY_006", "CITY_011", "CITY_012", "CITY_013", "CITY_014"],
    10: ["CITY_003", "CITY_005", "CITY_011", "CITY_012"],
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def enrich_feature(feature: dict) -> dict:
    feature_id = feature["properties"]["id"]
    if feature_id in CITY_META:
        feature["properties"].update(CITY_META[feature_id])
    feature["properties"].setdefault("feature_class", "city")
    feature["properties"].setdefault("source_layer", "cities")
    feature["properties"].setdefault("location_precision", feature["properties"].get("coordinate_quality", "modern city centre approximate"))
    feature["properties"]["state_relations"] = STATE_RELATIONS.get(feature_id, [])
    return feature


def new_feature(feature_id: str, name: str, coordinates: list[float], metadata: dict) -> dict:
    properties = {
        "id": feature_id,
        "name": name,
        "role": "historical_city/route_anchor",
        "coordinate_quality": metadata.pop("coordinate_quality", "modern city centre approximate"),
        "feature_class": "city",
        "source_layer": "cities",
        **metadata,
        "state_relations": STATE_RELATIONS.get(feature_id, []),
    }
    properties["location_precision"] = properties["coordinate_quality"]
    return {"type": "Feature", "id": feature_id, "properties": properties, "geometry": {"type": "Point", "coordinates": coordinates}}


def main() -> None:
    cities_path = DATA / "cities_master_v2.geojson"
    master_path = DATA / "master_all_features.geojson"
    topics_path = DATA / "topic_config_10.json"
    cities = read_json(cities_path)
    master = read_json(master_path)
    topics = read_json(topics_path)

    enriched = {item["properties"]["id"]: enrich_feature(item) for item in cities["features"]}
    for feature_id, name, coordinates, metadata in NEW_CITIES:
        if feature_id not in enriched:
            enriched[feature_id] = new_feature(feature_id, name, coordinates, dict(metadata))
    cities["features"] = list(enriched.values())

    master_non_cities = [item for item in master["features"] if item.get("properties", {}).get("id") not in enriched and item.get("properties", {}).get("source_layer") != "cities"]
    master["features"] = master_non_cities + cities["features"]

    for topic in topics["topics"]:
        for feature_id in TOPIC_ADDITIONS.get(topic["id"], []):
            if feature_id not in topic["showFeatureIds"]:
                topic["showFeatureIds"].append(feature_id)

    source_index = {
        "schema_version": "1.0",
        "note_uz": "MVP-1 shahar boyitishida ishlatilgan asosiy ilmiy va meros manbalari. Chegaralar va shahar-davlat aloqalari tarixiy taxmin bo‘lib, zamonaviy siyosiy chegara sifatida talqin qilinmaydi.",
        "sources": [
            {"id": "UNESCO_OTRAR", "title": "Silk Roads: Fergana–Syrdarya Corridor — Otrar", "url": UNESCO_OTRAR},
            {"id": "UNESCO_KUNYA", "title": "Kunya-Urgench", "url": UNESCO_KUNYA},
            {"id": "UNESCO_SHAHRISABZ", "title": "Historic Centre of Shakhrisyabz", "url": UNESCO_SHAHRISABZ},
            {"id": "IRANICA_CENTRAL_ASIA", "title": "Central Asia in the Mongol and Timurid Periods", "url": IRANICA_CENTRAL_ASIA},
            {"id": "IRANICA_CHAGHATAY", "title": "Chaghatayid Dynasty", "url": IRANICA_CHAGHATAY},
            {"id": "IRANICA_JALAL", "title": "Jalal-al-Din Khwarazmshah Mengubirni", "url": IRANICA_JALAL},
            {"id": "IRANICA_SAMARQAND", "title": "Samarqand: History and Archaeology", "url": IRANICA_SAMARQAND},
            {"id": "IRANICA_LITERATURE", "title": "Classical Persian Literature", "url": IRANICA_LITERATURE},
        ],
    }

    write_json(cities_path, cities)
    write_json(master_path, master)
    write_json(topics_path, topics)
    write_json(DATA / "city_sources_first10.json", source_index)
    print(f"Updated {len(cities['features'])} city records and {len(topics['topics'])} topics.")


if __name__ == "__main__":
    main()
