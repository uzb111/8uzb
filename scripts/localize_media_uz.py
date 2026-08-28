"""Media manifestidagi foydalanuvchi ko'radigan matnlarni o'zbekchalashtiradi.

Asl ``title`` va ``license`` maydonlari manba auditi uchun saqlanadi. Frontend
``title_uz`` va ``license_uz`` ni birinchi o'rinda ko'rsatadi.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data" / "media_manifest.json"


TITLE_UZ_BY_ID = {
    "gen_t01_xorazm_siyosiy": "XIII asr boshidagi Xorazm siyosiy muhiti",
    "gen_t02_xorazm_mongol_munosabat": "Xorazm va Mo'g'ullar davlati munosabatlari",
    "gen_t02_otror_voqeasi": "O'tror voqeasi",
    "gen_t03_mudofaa_oqibat": "Xorazm mudofaasi va uning oqibatlari",
    "gen_t03_buxoro_samarqand": "Buxoro va Samarqand mudofaasi",
    "gen_t04_jaloliddin_qahramonligi": "Jaloliddin Manguberdining qahramonligi",
    "gen_t04_parvon": "Parvon jangi",
    "gen_t05_jaloliddin_yurishlari": "Jaloliddin Manguberdining harbiy yurishlari",
    "gen_t06_chigatoy_tashkil": "Chig'atoy ulusining tashkil topishi",
    "gen_t06_chigatoy_savdo": "Chig'atoy ulusidagi savdo hayoti",
    "gen_t07_chigatoy_bolinish": "Chig'atoy ulusining bo'linishi",
    "gen_t07_moguliston_hayot": "Mo'g'ulistondagi ijtimoiy hayot",
    "gen_t08_ilm_fan": "XIII–XIV asrlarda ilm-fan va adabiyot",
    "gen_t08_rashididdin": "Rashididdin va tarixnavislik",
    "gen_t09_turon_siyosiy": "XIV asr o'rtalaridagi Turon siyosiy muhiti",
    "gen_t09_sarbadorlar": "Samarqand sarbadorlari",
    "gen_t10_temur_hokimiyat": "Amir Temurning hokimiyatga kelishi",
    "gen_t10_samarqand": "Amir Temur davridagi Samarqand",
    "src_t01_001": "Najmiddin Kubro va Muhammad Xorazmshoh",
    "src_t01_002": "Xorazmshohlar davlati va Mo'g'ullar ittifoqi xaritasi, taxminan 1200-yil",
    "src_t01_003": "Xorazmshohlar davlati va Mo'g'ullar ittifoqi xaritasi, taxminan 1200-yil",
    "src_t01_004": "Xorazmshohlar davlatining eng keng hududi",
    "src_t01_005": "Xorazmshohlar davlatining eng keng hududi",
    "src_t01_006": "Muhammad II Xorazmshohning 1430-yilgi qo'lyozmadagi tasviri",
    "src_t01_007": "Muhammad Xorazmshohning vafoti",
    "src_t01_008": "Afrosiyobdagi taxtda o'tirgan shahzoda, Samarqand, 1170–1220-yillar",
    "src_t01_009": "Muhammad II Xorazmshohning 1430-yilgi qo'lyozmadagi tasviri",
    "src_t02_001": "Chingizxonning Urganchga yurishi",
    "src_t02_002": "Buxoro qamali, 1220-yil",
    "src_t02_003": "Xorazmliklar yig'ini",
    "src_t03_001": "Xorazmshohlar davlati xaritasi va bayrog'i, 1218-yil",
    "src_t03_002": "Buxorodagi To'pchiboshi madrasasi",
    "src_t03_003": "O'tror xarobalarining havodan ko'rinishi, 2018-yil",
    "src_t03_004": "O'tror xarobalarining havodan ko'rinishi, 2018-yil",
    "src_t04_001": "Jaloliddin Manguberdining Sind daryosidan kechib o'tishi",
    "src_t04_002": "Sind daryosi bo'yidagi Jaloliddin Manguberdi, 1221-yil noyabr",
    "src_t04_003": "Jaloliddin Manguberdi va Chingizxonning Sind bo'yidagi to'qnashuvi",
    "src_t04_004": "Jaloliddin Manguberdi va Chingizxonning Sind bo'yidagi to'qnashuvi",
    "src_t04_005": "Sind daryosi bo'yidagi Jaloliddin Manguberdi, 1221-yil noyabr",
    "src_t04_006": "Chingizxon va Jaloliddin qo'shinlarining Sind bo'yidagi jangi",
    "src_t04_007": "Sind jangi tasviri",
    "src_t05_001": "Jaloliddin Manguberdi va Chingizxon Sind daryosi bo'yida",
    "src_t05_002": "Bolnisi jangi",
    "src_t06_001": "Chig'atoy ulusi xaritasi, taxminan 1300-yil",
    "src_t06_002": "Chig'atoy ulusi xaritasi",
    "src_t06_003": "Chig'atoyxon tasviri",
    "src_t06_004": "Katalon atlasidagi Chig'atoy ulusi",
    "src_t06_005": "Chig'atoy ulusi xaritasi",
    "src_t06_006": "Katalon atlasidagi Chig'atoy saltanati, 1375-yil",
    "src_t06_007": "Chig'atoy ulusi xaritasi",
    "src_t07_001": "Mo'g'ullar hukmronligi davridagi Osiyo, 1290-yil",
    "src_t07_002": "Mo'g'uliston xaritasi, 1372-yil",
    "src_t07_003": "Mo'g'uliston xaritasi, 1372-yil",
    "src_t07_004": "Mo'g'uliston xaritasi, 1372-yil",
    "src_t07_005": "Mo'g'uliston xaritasi, 1372-yil",
    "src_t07_006": "Sharqiy Chig'atoy hududi, 1372-yil",
    "src_t07_007": "Mo'g'uliston xaritasi, 1372-yil",
    "src_t07_008": "Osiyo xaritasi, 1335-yil",
    "src_t07_009": "Mo'g'ullar hukmronligi davridagi Osiyo, 1290-yil",
    "src_t08_001": "Sa'diy Sheroziyning «Guliston» asari",
    "src_t08_002": "Sa'diyning «Guliston» qo'lyozmasi, XVII asr o'rtalari",
    "src_t08_003": "Jaloliddin Rumiyning «Masnaviy» qo'lyozmasi",
    "src_t08_004": "Jaloliddin Rumiyning «Masnaviy» qo'lyozmasi",
    "src_t08_005": "Islomiy qo'lyozma va miniatyura namunasi",
    "src_t08_006": "«Guliston bit-turkiy» qo'lyozmasi",
    "src_t08_007": "Amir Xusrav dostonlaridan birining miniatyurali qo'lyozmasi",
    "src_t09_001": "Xuroson, Movarounnahr va Xorazm xaritasi",
    "src_t09_002": "Amir Temur va Amir Husaynning Mengli Buqaga qarshi jangi",
    "src_t09_003": "Amir Temur va Amir Husaynning Mengli Buqaga qarshi jangi",
    "src_t09_004": "Amir Temurning Balxga yurishi, 1370-yil",
    "src_t10_001": "XV asr Temuriylar–mo'g'ullar shajarasi",
    "src_t10_002": "Amir Temur davlati xaritasi, 1400-yil",
    "src_t10_003": "Amir Temur davlati xaritasi, 1400-yil",
    "src_t10_004": "Amir Temur davlati xaritasi, 1400-yil",
    "src_t10_005": "Amir Temur va To'xtamishxon qo'shinlari jangi",
    "src_t10_006": "Amir Temur davlati xaritasi",
    "src_t10_007": "Amir Temur vafotiga motam, 1405-yil",
    "src_t10_008": "XV asr Temuriylar–mo'g'ullar shajarasi",
}


LICENSE_UZ = {
    "AI-generated for TARIX360": "TARIX360 uchun yaratilgan sun'iy intellekt rekonstruksiyasi",
    "TARIX360 AI educational reconstruction": "TARIX360 uchun yaratilgan ta'limiy sun'iy intellekt rekonstruksiyasi",
    "Public domain": "Jamoat mulki",
    "Public Domain · The Met Open Access": "Jamoat mulki · Met muzeyining ochiq kolleksiyasi",
    "No restrictions": "Foydalanish cheklovi yo'q",
}


def localize_media_manifest(path: Path = MANIFEST) -> int:
    records = json.loads(path.read_text(encoding="utf-8"))
    changed = 0
    for record in records:
        title_uz = TITLE_UZ_BY_ID.get(record.get("id"))
        if title_uz and record.get("title_uz") != title_uz:
            record["title_uz"] = title_uz
            changed += 1
        elif record.get("title") and not record.get("title_uz"):
            # 11–15-mavzularda sarlavhalar avvaldan o'zbekcha yaratilgan.
            record["title_uz"] = record["title"]
            changed += 1

        license_uz = LICENSE_UZ.get(record.get("license"), record.get("license"))
        if license_uz and record.get("license_uz") != license_uz:
            record["license_uz"] = license_uz
            changed += 1

    path.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return changed


if __name__ == "__main__":
    print(f"MEDIA_UZ_UPDATED={localize_media_manifest()}")
