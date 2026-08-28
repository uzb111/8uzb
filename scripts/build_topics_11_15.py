#!/usr/bin/env python3
"""Build the TARIX360 topic 11–15 scene data from the authoritative datasets.

This migration is intentionally idempotent: records are updated by ID and the
first ten topic definitions remain untouched.
"""

from __future__ import annotations

import json
from pathlib import Path

from localize_media_uz import localize_media_manifest


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
BOOK_DRIVE_ID = "1MBVkyq1JJmz3WtFZDjpW4vQeKKoJ2ddY"

TEXTBOOK_REF = {
    "title": "O‘zbekiston tarixi, 8-sinf (2023)",
    "drive_file_id": BOOK_DRIVE_ID,
}
IRANICA_CENTRAL_ASIA = "https://www.iranicaonline.org/articles/central-asia-v/"
UNESCO_TIMUR = "https://es.unesco.org/silkroad/sites/default/files/knowledge-bank-article/vol_IVa%20silk%20road_central%20asia%20under%20timur.pdf"
MET_TIMURID = "https://www.metmuseum.org/toah/hd/timu/hd_timu.htm"


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def upsert_feature(collection: dict, feature: dict) -> None:
    feature_id = feature["properties"]["id"]
    feature["id"] = feature_id
    for index, current in enumerate(collection["features"]):
        if current.get("properties", {}).get("id") == feature_id:
            collection["features"][index] = feature
            return
    collection["features"].append(feature)


def add_unique(values: list, additions: list) -> list:
    return list(dict.fromkeys([*values, *additions]))


def polygon_feature(feature_id: str, start: int, end: int, snapshot: int, phase: str, coordinates: list) -> dict:
    return {
        "type": "Feature",
        "properties": {
            "id": feature_id,
            "period_id": "P07",
            "polity_uz": "Amir Temur davlati",
            "polity_en": "Timurid realm under Timur",
            "start_date": str(start),
            "end_date": str(end),
            "snapshot_year": snapshot,
            "phase": phase,
            "status": "reconstructed",
            "boundary_type": "historical_control_and_influence",
            "boundary_kind": "reconstructed_control_extent",
            "confidence": 0.54,
            "geometry_quality": "textbook-georeferenced generalized reconstruction",
            "boundary_quality": "generalized control area; campaign reach is shown separately as routes",
            "source_ids": ["TARIX360_BOOK_P111", "IRANICA_CENTRAL_ASIA", "UNESCO_TIMUR_CHAPTER"],
            "notes": "Davlatning tayanch nazorat hududi umumlashtirilgan. Qisqa muddatli yurishlar poligonga qo‘shilmay, alohida yo‘nalish qatlamida ko‘rsatiladi.",
            "uncertainty_note": "XIV–XV asrlarda qat’iy chiziqli chegara bo‘lmagan; kontur siyosiy nazorat va ta’sir makonining o‘quv rekonstruksiyasidir.",
            "crs_note": "WGS84 longitude/latitude (EPSG:4326).",
            "source_refs": [
                {**TEXTBOOK_REF, "pages": [94, 100, 111]},
                {"title": "Encyclopaedia Iranica — Central Asia in the Mongol and Timurid Periods", "url": IRANICA_CENTRAL_ASIA},
                {"title": "UNESCO — Central Asia under Timur", "url": UNESCO_TIMUR},
            ],
        },
        "geometry": {"type": "Polygon", "coordinates": coordinates},
    }


def point_feature(feature_id: str, coordinates: list, **properties) -> dict:
    return {
        "type": "Feature",
        "properties": {"id": feature_id, **properties},
        "geometry": {"type": "Point", "coordinates": coordinates},
    }


def line_feature(feature_id: str, coordinates: list, **properties) -> dict:
    return {
        "type": "Feature",
        "properties": {"id": feature_id, **properties},
        "geometry": {"type": "LineString", "coordinates": coordinates},
    }


def build_topics() -> None:
    path = DATA / "topic_config_10.json"
    config = read_json(path)
    topics = {int(item["id"]): item for item in config["topics"]}
    additions = [
        {
            "id": 11,
            "title": "Amir Temur markazlashgan davlat tuzish yo‘lida",
            "pages": [94, 99],
            "years": [1370, 1393],
            "focusYear": 1385,
            "showFeatureIds": [
                "P06_TIMUR_1370", "P07_TIMUR_1381_1387", "P07_TIMUR_1388_1393",
                "EV_1372_KHWARAZM", "EV_1381_HERAT", "EV_1387_ISFAHAN",
                "CAM_1372_1379_MOGHUL_KHWARAZM", "CAM_1380_1387_KHORASAN_IRAN",
                "CITY_001", "CITY_002", "CITY_003", "CITY_004", "CITY_006", "CITY_007",
                "CITY_009", "CITY_010", "CITY_012", "CITY_013", "CITY_027", "CITY_032",
                "CITY_033", "CITY_034", "CITY_044", "CITY_045", "CITY_046", "CITY_047",
                "CITY_048", "CITY_049", "CITY_053", "CITY_054",
            ],
            "mapStory": "1370-yildagi Movarounnahr tayanch hududidan Xorazm, Xuroson va Eron tomon bosqichma-bosqich kengayish; yurish yo‘llari davlat poligonidan alohida ko‘rsatiladi.",
            "generatedImages": ["gen_t11_balkh_qurultay.png", "gen_t11_herat_1381.png"],
        },
        {
            "id": 12,
            "title": "Amir Temurning davlat chegaralarini mustahkamlashi",
            "pages": [100, 111],
            "years": [1376, 1405],
            "focusYear": 1402,
            "showFeatureIds": [
                "P06_TIMUR_1370", "P07_TIMUR_1381_1387", "P07_TIMUR_1388_1393",
                "P07_TIMUR_1394_1397", "P07_TIMUR_1397_1399", "P07_TIMUR_1399_1401",
                "P07_TIMUR_1401_1402", "P07_TIMUR_1403_1405",
                "EV_1391_KONDURCHA", "EV_1395_TEREK", "EV_1398_DELHI", "EV_1400_ALEPPO",
                "EV_1401_DAMASCUS", "EV_1401_BAGHDAD", "EV_1402_ANKARA", "EV_1405_OTRAR",
                "CAM_1394_95_GOLDEN_HORDE", "CAM_1398_INDIA", "CAM_1400_01_SYRIA",
                "CAM_1402_ANATOLIA", "CAM_1404_05_CHINA_START",
                "CITY_001", "CITY_003", "CITY_007", "CITY_010", "CITY_025", "CITY_026",
                "CITY_027", "CITY_028", "CITY_029", "CITY_030", "CITY_031", "CITY_041",
                "CITY_046", "CITY_049", "CITY_050", "CITY_051", "CITY_052", "CITY_053",
            ],
            "mapStory": "To‘xtamish bilan shimoliy to‘qnashuvlar, Dehli, Suriya–Iroq, Anqara va Xitoy yurishi arafasi vaqt bo‘yicha jonlanadi.",
            "generatedImages": ["gen_t12_terek_1395.png", "gen_t12_ankara_1402.png"],
        },
        {
            "id": 13,
            "title": "Amir Temurning tashqi siyosati",
            "pages": [112, 116],
            "years": [1402, 1404],
            "focusYear": 1404,
            "showFeatureIds": [
                "P07_TIMUR_1401_1402", "P07_TIMUR_1403_1405",
                "EV_1402_FRANCE_LETTER", "EV_1403_CLAVIJO", "EV_1404_MING_ENVOYS",
                "ROUTE_CLAVIJO_1403_1404", "ROUTE_TIMUR_WESTERN_DIPLOMACY_1402",
                "CITY_001", "CITY_054", "CITY_055", "CITY_056", "CITY_057", "CITY_058",
                "TH_DIPLOMACY_SAMARKAND", "TH_MING_DIPLOMACY_SAMARKAND",
            ],
            "mapStory": "Samarqanddan Fransiya va Angliyaga maktublar hamda Kastiliya elchisi Klavixoning 1403–1404-yillardagi yo‘li bitta diplomatik sahnada.",
            "generatedImages": ["gen_t13_clavijo_samarkand.png", "gen_t13_western_couriers.png", "gen_t13_ming_envoys.png"],
        },
        {
            "id": 14,
            "title": "Amir Temur davlatida qo‘shin tuzilishi",
            "pages": [117, 126],
            "years": [1370, 1405],
            "focusYear": 1395,
            "showFeatureIds": [
                "P06_TIMUR_1370", "P07_TIMUR_1381_1387", "P07_TIMUR_1388_1393",
                "P07_TIMUR_1394_1397", "P07_TIMUR_1397_1399", "P07_TIMUR_1399_1401",
                "P07_TIMUR_1401_1402", "P07_TIMUR_1403_1405",
                "CAM_1394_95_GOLDEN_HORDE", "CAM_1398_INDIA", "CAM_1400_01_SYRIA",
                "CAM_1402_ANATOLIA", "CAM_1404_05_CHINA_START",
                "EV_1395_TEREK", "EV_1398_DELHI", "EV_1402_ANKARA",
                "CITY_001", "CITY_004", "CITY_010", "CITY_026", "CITY_030", "CITY_031",
                "TH_ARMY_MUSTER_SAMARKAND", "TH_ARMY_EASTERN_STAGE_OTRAR",
            ],
            "mapStory": "Qo‘shin yig‘ilishi, yetti qo‘l tamoyili, ta’minot tugunlari va asosiy yurish yo‘nalishlari xaritada bog‘lanadi.",
            "generatedImages": ["gen_t14_seven_corps.png", "gen_t14_logistics.png"],
        },
        {
            "id": 15,
            "title": "Amir Temur davlatining boshqaruvi",
            "pages": [127, 131],
            "years": [1370, 1405],
            "focusYear": 1404,
            "showFeatureIds": [
                "P06_TIMUR_1370", "P07_TIMUR_1381_1387", "P07_TIMUR_1388_1393",
                "P07_TIMUR_1394_1397", "P07_TIMUR_1397_1399", "P07_TIMUR_1399_1401",
                "P07_TIMUR_1401_1402", "P07_TIMUR_1403_1405",
                "CITY_001", "CITY_002", "CITY_003", "CITY_004", "CITY_006", "CITY_007",
                "CITY_008", "CITY_009", "CITY_010", "CITY_027", "CITY_028", "CITY_032",
                "CITY_033", "CITY_034", "CITY_044", "CITY_046", "CITY_047", "CITY_053",
                "TH_DIWAN_SAMARKAND", "TH_JUSTICE_SAMARKAND",
            ],
            "mapStory": "Samarqanddagi markaziy boshqaruv, mahalliy viloyat markazlari va sud-adolat tizimi saltanat makoni bilan bog‘lanadi.",
            "generatedImages": ["gen_t15_central_divan.png", "gen_t15_justice_court.png"],
        },
    ]
    for topic in additions:
        topics[topic["id"]] = topic
    config["topics"] = [topics[key] for key in sorted(topics)]
    config["book"]["note"] = "Browser faqat joriy yengil WebP sahifani yuklaydi; 145 MB asl PDF foydalanuvchi so‘ragandagina Drive orqali ochiladi."
    write_json(path, config)


def build_states() -> None:
    path = DATA / "states_master_v2.geojson"
    states = read_json(path)
    caspian_hole = [[46.4, 36.8], [47.0, 40.2], [48.8, 43.8], [51.3, 45.7], [53.7, 43.2], [53.8, 39.0], [52.2, 36.8], [49.0, 36.2], [46.4, 36.8]]
    upsert_feature(states, polygon_feature(
        "P07_TIMUR_1381_1387", 1381, 1387, 1385, "Xuroson va Eron tomon kengayish",
        [[
            [46.0, 31.0], [46.0, 37.5], [49.0, 41.5], [54.0, 43.5], [61.0, 44.0],
            [68.0, 44.0], [73.5, 42.2], [76.0, 39.0], [74.0, 34.0], [70.0, 30.0],
            [65.0, 27.5], [59.0, 25.5], [53.0, 26.5], [49.0, 28.0], [46.0, 31.0],
        ], caspian_hole],
    ))
    upsert_feature(states, polygon_feature(
        "P07_TIMUR_1388_1393", 1388, 1393, 1391, "Eron, Kavkaz va Dashti Qipchoq yurishlari davri",
        [[
            [42.5, 31.0], [42.5, 37.5], [45.0, 41.5], [49.0, 44.0], [54.0, 46.0],
            [61.0, 45.5], [68.0, 44.5], [73.5, 42.5], [76.0, 39.0], [74.5, 34.0],
            [70.5, 29.0], [65.0, 26.5], [59.0, 25.0], [53.0, 26.0], [47.0, 28.0],
            [42.5, 31.0],
        ], caspian_hole],
    ))

    intervals = {
        "P07_TIMUR_1394_1397": (1394, 1397, 1395),
        "P07_TIMUR_1397_1399": (1398, 1399, 1399),
        "P07_TIMUR_1399_1401": (1400, 1401, 1401),
        "P07_TIMUR_1401_1402": (1402, 1402, 1402),
        "P07_TIMUR_1403_1405": (1403, 1405, 1404),
    }
    for feature in states["features"]:
        properties = feature.get("properties", {})
        feature_id = properties.get("id")
        if feature_id not in intervals:
            continue
        start, end, snapshot = intervals[feature_id]
        properties.update({
            "start_date": str(start), "end_date": str(end), "snapshot_year": snapshot,
            "boundary_kind": "reconstructed_control_extent", "status": "reconstructed", "confidence": 0.54,
            "geometry_quality": "textbook-georeferenced generalized reconstruction",
            "boundary_quality": "generalized control area; campaign reach is shown separately as routes",
            "notes": "Tayanch nazorat hududi va qisqa muddatli siyosiy ta’sir umumlashtirilgan; Dehli, Suriya, Anqara va Dashti Qipchoq yurishlari alohida chiziqlarda ko‘rsatiladi.",
            "uncertainty_note": "Kontur zamonaviy davlat chegarasi emas. Yurishdagi g‘alaba doimiy ma’muriy qo‘shib olish degani emas.",
            "source_refs": [
                {**TEXTBOOK_REF, "pages": [100, 111]},
                {"title": "Encyclopaedia Iranica — Central Asia in the Mongol and Timurid Periods", "url": IRANICA_CENTRAL_ASIA},
                {"title": "UNESCO — Central Asia under Timur", "url": UNESCO_TIMUR},
            ],
        })
    write_json(path, states)


def build_cities() -> None:
    path = DATA / "cities_master_v2.geojson"
    cities = read_json(path)
    additions = [
        ("CITY_046", [68.2690, 43.2973], "Yassi / Turkiston", "Turkiston", "Qozog‘iston", "Turkiston viloyati", "Sirdaryo bo‘yidagi chegara va ziyorat markazi; Amir Temur davrida sharqiy tayanch nuqtalardan biri."),
        ("CITY_047", [69.7583, 42.3044], "Sayram / Isfijob", "Sayram", "Qozog‘iston", "Turkiston viloyati", "Movarounnahrning shimoli-sharqiy darvozasi va karvon yo‘li tuguni."),
        ("CITY_048", [57.6819, 36.2126], "Sabzavor", "Sabzavor", "Eron", "Razaviy Xuroson", "Xurosondagi Sarbadorlar markazi; 1380-yillar kengayish sahnasidagi muhim nuqta."),
        ("CITY_049", [65.7101, 31.6289], "Qandahor", "Qandahor", "Afg‘oniston", "Qandahor viloyati", "Xuroson–Hindiston oralig‘idagi strategik yo‘l tuguni."),
        ("CITY_050", [71.5249, 30.1575], "Multon", "Multon", "Pokiston", "Panjob", "1398-yilgi Hindiston yurishi yo‘lidagi tayanch shahar."),
        ("CITY_051", [47.4440, 47.1750], "Saroy Berka / Saroy al-Jadid", "Selitrennoe atrofi", "Rossiya", "Astraxan viloyati", "Oltin O‘rda siyosiy-savdo markazi; aniq arxeologik identifikatsiya bo‘yicha ilmiy bahslar mavjud."),
        ("CITY_052", [39.4233, 47.1121], "Tana / Azov", "Azov", "Rossiya", "Rostov viloyati", "Don dengiz yo‘li bo‘yidagi savdo markazi; 1395-yil yurishi oqibatlarini tushuntiruvchi nuqta."),
        ("CITY_053", [47.1500, 40.2800], "Boylaqon", "Boylaqon xarobasi", "Ozarbayjon", "Mil dashti", "Qorabog‘ yaqinidagi tarixiy shahar va qurultoy-kanal bunyodkorligi bilan bog‘liq nuqta."),
        ("CITY_054", [48.7981, 36.4351], "Sultoniya", "Soltaniyeh", "Eron", "Zanjon", "Eron va Kavkaz yo‘llari tutashgan siyosiy-diplomatik markaz."),
        ("CITY_055", [39.7181, 41.0050], "Trabzon", "Trabzon", "Turkiya", "Trabzon", "Klavixo elchiligi Qora dengizdan Samarqandga o‘tgan yo‘ldagi muhim port."),
        ("CITY_056", [2.3522, 48.8566], "Parij", "Parij", "Fransiya", "Île-de-France", "Karl VI saroyi va Amir Temurning 1402-yilgi diplomatik maktubi bilan bog‘liq ramziy nuqta."),
        ("CITY_057", [-0.1276, 51.5072], "London", "London", "Angliya", "Buyuk London", "Genrix IV saroyi bilan yozishmalarni ko‘rsatadigan diplomatik nuqta."),
        ("CITY_058", [-4.0273, 39.8628], "Toledo / Kastiliya saroyi", "Toledo", "Ispaniya", "Kastiliya-La Mancha", "Genrix III yuborgan Klavixo elchiligining Kastiliyadagi ramziy boshlanish nuqtasi; qirollik saroyi ko‘chma bo‘lgan."),
    ]
    topics_by_city = {
        "CITY_001": [11, 12, 13, 14, 15], "CITY_002": [11, 15], "CITY_003": [11, 12, 15],
        "CITY_004": [11, 14, 15], "CITY_006": [11, 15], "CITY_007": [11, 12, 15],
        "CITY_008": [15], "CITY_009": [11, 15], "CITY_010": [11, 12, 14, 15],
        "CITY_012": [11], "CITY_013": [11], "CITY_025": [12], "CITY_026": [12, 14],
        "CITY_027": [11, 12, 15], "CITY_028": [12, 15], "CITY_029": [12], "CITY_030": [12, 14],
        "CITY_031": [12, 14], "CITY_032": [11, 15], "CITY_033": [11, 15], "CITY_034": [11, 15],
        "CITY_041": [12], "CITY_044": [11, 15], "CITY_045": [11],
    }
    existing = {feature["properties"]["id"]: feature for feature in cities["features"]}
    for city_id, coordinates, historical, modern, country, region, summary in additions:
        upsert_feature(cities, point_feature(
            city_id, coordinates,
            name=historical, name_uz=historical, historical_name_uz=historical,
            modern_name_uz=modern, modern_country_uz=country, modern_region_uz=region,
            role="historical_anchor/control_point", coordinate_quality="modern/historical-site approximate",
            location_precision="modern/historical-site approximate", summary_uz=summary,
            topic_ids=[topic for topic in range(11, 16) if city_id in {
                11: {"CITY_046", "CITY_047", "CITY_048", "CITY_049", "CITY_053", "CITY_054"},
                12: {"CITY_046", "CITY_049", "CITY_050", "CITY_051", "CITY_052", "CITY_053"},
                13: {"CITY_054", "CITY_055", "CITY_056", "CITY_057", "CITY_058"},
                14: set(), 15: {"CITY_046", "CITY_047", "CITY_053"},
            }[topic]],
            source_refs=[IRANICA_CENTRAL_ASIA, UNESCO_TIMUR], state_relations=[],
        ))
    for feature in cities["features"]:
        properties = feature.get("properties", {})
        city_id = properties.get("id")
        if city_id in topics_by_city:
            properties["topic_ids"] = add_unique(properties.get("topic_ids", []), topics_by_city[city_id])

    state_ids = [
        "P07_TIMUR_1381_1387", "P07_TIMUR_1388_1393", "P07_TIMUR_1394_1397",
        "P07_TIMUR_1397_1399", "P07_TIMUR_1399_1401", "P07_TIMUR_1401_1402", "P07_TIMUR_1403_1405",
    ]
    roles = {
        "CITY_001": ("poytaxt", "Saltanatning markaziy poytaxti"),
        "CITY_004": ("sulolaviy_markaz", "Amir Temurning vatani va sulolaviy markaz"),
        "CITY_006": ("tayanch_markaz", "Amudaryo janubidagi tayanch markaz"),
        "CITY_007": ("yirik_markaz", "Xurosonning yirik ma’muriy markazi"),
        "CITY_010": ("chegara_qalasi", "Sharqiy yurishlar va qo‘shin yig‘ilishi tuguni"),
    }
    for feature in cities["features"]:
        city_id = feature.get("properties", {}).get("id")
        if city_id not in roles:
            continue
        relations = feature["properties"].setdefault("state_relations", [])
        current = {item.get("state_id"): item for item in relations}
        kind, note = roles[city_id]
        for state_id in state_ids:
            current[state_id] = {"state_id": state_id, "kind": kind, "note_uz": note}
        feature["properties"]["state_relations"] = list(current.values())
    write_json(path, cities)


def build_events() -> None:
    path = DATA / "events_master_v2.geojson"
    events = read_json(path)
    records = [
        point_feature("EV_1372_KHWARAZM", [60.55, 41.55], date="1372", title_uz="Xorazmga yurishlar bosqichining boshlanishi", category="campaign", period_id="P07", topic_refs="11", coordinate_quality="Gurganj vohasi bo‘yicha taxminiy", source_refs=[{**TEXTBOOK_REF, "pages": [94, 95, 96]}]),
        point_feature("EV_1387_ISFAHAN", [51.6776, 32.6546], date="1387", title_uz="Isfahonning bo‘ysundirilishi", category="campaign", period_id="P07", topic_refs="11", coordinate_quality="city-fixed", source_refs=[IRANICA_CENTRAL_ASIA]),
        point_feature("EV_1402_FRANCE_LETTER", [2.3522, 48.8566], date="1402", title_uz="Amir Temurning Fransiya qiroli Karl VI ga maktubi", category="diplomacy", period_id="P07", topic_refs="13", coordinate_quality="recipient court represented by Paris", source_refs=[UNESCO_TIMUR]),
        point_feature("EV_1403_CLAVIJO", [66.9597, 39.6542], date="1403", title_uz="Kastiliya elchisi Klavixoning Samarqandga yo‘l olishi", category="diplomacy", period_id="P07", topic_refs="13", coordinate_quality="destination city-fixed", source_refs=["https://www.iranicaonline.org/articles/clavijo-ruy-gonzlez-de-d/"]),
        point_feature("EV_1404_MING_ENVOYS", [66.9597, 39.6542], date="1404", title_uz="Samarqandda Xitoy va boshqa davlatlar elchilari", category="diplomacy", period_id="P07", topic_refs="13", coordinate_quality="city-fixed", source_refs=[{**TEXTBOOK_REF, "pages": [109, 116]}]),
    ]
    for record in records:
        upsert_feature(events, record)
    for feature in events["features"]:
        feature_id = feature.get("properties", {}).get("id")
        mapping = {
            "EV_1381_HERAT": "11", "EV_1391_KONDURCHA": "12", "EV_1395_TEREK": "12,14",
            "EV_1398_DELHI": "12,14", "EV_1400_ALEPPO": "12", "EV_1401_DAMASCUS": "12",
            "EV_1401_BAGHDAD": "12", "EV_1402_ANKARA": "12,14", "EV_1405_OTRAR": "12",
        }
        if feature_id in mapping:
            feature["properties"]["topic_refs"] = mapping[feature_id]
    write_json(path, events)


def build_routes() -> None:
    path = DATA / "routes_master_v2.geojson"
    routes = read_json(path)
    records = [
        line_feature("CAM_1372_1379_MOGHUL_KHWARAZM", [[66.96, 39.65], [69.24, 41.30], [69.76, 42.30], [68.27, 43.30], [60.55, 41.55]], start_date="1372", end_date="1379", title_uz="Mo‘g‘uliston va Xorazm yo‘nalishlaridagi yurishlar", period_id="P07", topic_refs="11", confidence=0.58, route_quality="textbook-based schematic waypoint route", source_refs=[{**TEXTBOOK_REF, "pages": [94, 95, 96]}]),
        line_feature("CAM_1380_1387_KHORASAN_IRAN", [[66.96, 39.65], [66.90, 36.75], [62.20, 34.35], [57.68, 36.21], [59.61, 36.30], [51.68, 32.65], [52.58, 29.59], [46.29, 38.08]], start_date="1380", end_date="1387", title_uz="Xuroson va Eron tomon kengayish", period_id="P07", topic_refs="11", confidence=0.58, route_quality="city-waypoint route; exact march track is uncertain", source_refs=[{**TEXTBOOK_REF, "pages": [97, 98]}, IRANICA_CENTRAL_ASIA]),
        line_feature("ROUTE_CLAVIJO_1403_1404", [[-4.03, 39.86], [-5.99, 37.39], [12.50, 41.90], [28.98, 41.01], [39.72, 41.01], [48.80, 36.44], [59.61, 36.30], [66.96, 39.65]], start_date="1403", end_date="1404", title_uz="Rui Gonsales de Klavixoning Kastiliyadan Samarqandga elchilik yo‘li", period_id="P07", topic_refs="13", confidence=0.62, route_quality="major-stop itinerary, not an exact road trace", source_refs=["https://www.iranicaonline.org/articles/clavijo-ruy-gonzlez-de-d/"]),
        line_feature("ROUTE_TIMUR_WESTERN_DIPLOMACY_1402", [[66.96, 39.65], [48.80, 36.44], [39.72, 41.01], [28.98, 41.01], [12.50, 41.90], [2.35, 48.86], [-0.13, 51.51]], start_date="1402", end_date="1404", title_uz="Samarqand–Fransiya–Angliya diplomatik aloqalari", period_id="P07", topic_refs="13", confidence=0.42, route_quality="relationship line; not a single courier itinerary", source_refs=[UNESCO_TIMUR]),
    ]
    for record in records:
        upsert_feature(routes, record)
    topic_map = {
        "CAM_1394_95_GOLDEN_HORDE": "12,14", "CAM_1398_INDIA": "12,14",
        "CAM_1400_01_SYRIA": "12,14", "CAM_1402_ANATOLIA": "12,14",
        "CAM_1404_05_CHINA_START": "12,14",
    }
    route_metadata = {
        "CAM_1372_1379_MOGHUL_KHWARAZM": {"route_kind": "military_campaign", "waypoints": ["Samarqand", "Toshkent", "Yettisuv", "Mo‘g‘uliston yo‘nalishi", "Gurganj"]},
        "CAM_1380_1387_KHORASAN_IRAN": {"route_kind": "military_campaign", "waypoints": ["Samarqand", "Balx", "Hirot", "Nishopur", "Mashhad", "Isfahon", "Sherozi", "Tabriz"]},
        "CAM_1394_95_GOLDEN_HORDE": {"route_kind": "military_campaign", "waypoints": ["Samarqand", "Sirdaryo dashtlari", "Ural oralig‘i", "Terek", "Kavkaz"]},
        "CAM_1398_INDIA": {"route_kind": "military_campaign", "waypoints": ["Samarqand", "Balx", "Kobul", "Panjob", "Dehli"]},
        "CAM_1400_01_SYRIA": {"route_kind": "military_campaign", "waypoints": ["Samarqand", "Hirot", "Tabriz", "Halab", "Damashq", "Bag‘dod"]},
        "CAM_1402_ANATOLIA": {"route_kind": "military_campaign", "waypoints": ["Bag‘dod", "Tabriz", "Sivas", "Anadolu", "Anqara"]},
        "CAM_1404_05_CHINA_START": {"route_kind": "military_campaign", "waypoints": ["Samarqand", "Toshkent", "O‘tror"]},
        "ROUTE_CLAVIJO_1403_1404": {"route_kind": "diplomatic_mission", "waypoints": ["Kastiliya", "Sevilya", "Rim", "Konstantinopol", "Trabzon", "Tabriz", "Mashhad", "Samarqand"]},
        "ROUTE_TIMUR_WESTERN_DIPLOMACY_1402": {"route_kind": "diplomatic_correspondence", "waypoints": ["Samarqand", "Tabriz", "Trabzon", "Konstantinopol", "Rim", "Parij", "London"]},
    }
    for feature in routes["features"]:
        feature_id = feature.get("properties", {}).get("id")
        if feature_id in topic_map:
            feature["properties"]["topic_refs"] = topic_map[feature_id]
        if feature_id in route_metadata:
            feature["properties"].update(route_metadata[feature_id])
    write_json(path, routes)


def build_thematic_points() -> None:
    path = DATA / "thematic_points_v2.geojson"
    points = read_json(path)
    records = [
        point_feature("TH_DIPLOMACY_SAMARKAND", [66.9597, 39.6542], name="Samarqand diplomatik qabul markazi", feature_class="site", role="elchilar qabuli va xalqaro yozishmalar", topic_refs="13", date="1402-1404", coordinate_quality="city-based", period_id="P07", source_refs=[UNESCO_TIMUR]),
        point_feature("TH_MING_DIPLOMACY_SAMARKAND", [67.02, 39.70], name="Ming elchilari sahnasi", feature_class="site", role="Xitoy bilan elchilik munosabatlari", topic_refs="13", date="1404", coordinate_quality="city-based symbolic", period_id="P07", source_refs=[{**TEXTBOOK_REF, "pages": [109, 116]}]),
        point_feature("TH_ARMY_MUSTER_SAMARKAND", [66.9597, 39.6542], name="Qo‘shin yig‘ilishi — Samarqand", feature_class="site", role="tavochi, ta’minot va qo‘mondonlik markazi", topic_refs="14", date="1370-1405", coordinate_quality="city-based symbolic", period_id="P07", source_refs=[{**TEXTBOOK_REF, "pages": [117, 120]}]),
        point_feature("TH_ARMY_EASTERN_STAGE_OTRAR", [68.3048, 42.8532], name="O‘tror harbiy yig‘in nuqtasi", feature_class="site", role="1404–1405 Xitoy yurishi qishlov va ta’minot tuguni", topic_refs="14", date="1404-1405", coordinate_quality="archaeological-site approximate", period_id="P07", source_refs=[{**TEXTBOOK_REF, "pages": [109, 117]}]),
        point_feature("TH_DIWAN_SAMARKAND", [66.9597, 39.6542], name="Markaziy devon — Samarqand", feature_class="site", role="markaziy hokimiyat va boshqaruv organlari", topic_refs="15", date="1370-1405", coordinate_quality="city-based symbolic", period_id="P07", source_refs=[{**TEXTBOOK_REF, "pages": [127, 128, 129]}]),
        point_feature("TH_JUSTICE_SAMARKAND", [67.01, 39.66], name="Adolat va sud tizimi", feature_class="site", role="qozilar va adolat devoni", topic_refs="15", date="1370-1405", coordinate_quality="city-based symbolic", period_id="P07", source_refs=[{**TEXTBOOK_REF, "pages": [130, 131]}]),
    ]
    for record in records:
        upsert_feature(points, record)
    write_json(path, points)


def build_media_manifest() -> None:
    path = DATA / "media_manifest.json"
    media = read_json(path)
    records = [
        {"id": "src_t11_met_baghdad", "topic": 11, "kind": "source", "file": "assets/images/source/topic_11/met_451304_conquest_baghdad.jpg", "title": "Amir Temurning Bag‘dod yurishi — Zafarnoma miniatyurasi", "source_url": "https://www.metmuseum.org/art/collection/search/451304", "license": "Public Domain · The Met Open Access"},
        {"id": "src_t12_met_battle", "topic": 12, "kind": "source", "file": "assets/images/source/topic_12/met_450512_battle_scene.jpg", "title": "Zafarnomadagi jang sahnasi", "source_url": "https://www.metmuseum.org/art/collection/search/450512", "license": "Public Domain · The Met Open Access"},
        {"id": "src_t13_met_chinese_emperor", "topic": 13, "kind": "source", "file": "assets/images/source/topic_13/met_448242_chinese_emperor.jpg", "title": "Xitoy hukmdori — Temuriylar davri tarixiy qo‘lyozmasi", "source_url": "https://www.metmuseum.org/art/collection/search/448242", "license": "Public Domain · The Met Open Access"},
        {"id": "src_t14_met_timur_before_battle", "topic": 14, "kind": "source", "file": "assets/images/source/topic_14/met_451303_timur_before_battle.jpg", "title": "Amir Temur jang oldidan — Zafarnoma miniatyurasi", "source_url": "https://www.metmuseum.org/art/collection/search/451303", "license": "Public Domain · The Met Open Access"},
        {"id": "src_t15_met_court_audience", "topic": 15, "kind": "source", "file": "assets/images/source/topic_15/met_451959_court_audience.jpg", "title": "Temuriy siyosiy an’anadagi saroy qabuli — Boburnoma miniatyurasi", "source_url": "https://www.metmuseum.org/art/collection/search/451959", "license": "Public Domain · The Met Open Access"},
    ]
    by_id = {item["id"]: item for item in media}
    by_id.update({item["id"]: item for item in records})
    write_json(path, list(by_id.values()))


def build_enriched_media_manifest() -> None:
    """Add sourced and reconstructed lesson media without disturbing topics 1-10."""
    path = DATA / "media_manifest.json"
    media = read_json(path)
    by_id = {item["id"]: item for item in media}

    # The Baghdad folio belongs to the later western campaigns in topic 12.
    by_id["src_t11_met_baghdad"] = {
        **by_id["src_t11_met_baghdad"],
        "topic": 12,
    }

    web_sources_path = DATA / "web_sources_topics_11_15.json"
    if web_sources_path.exists():
        for item in read_json(web_sources_path):
            by_id[item["id"]] = {
                "id": item["id"],
                "topic": item["topic"],
                "kind": "source",
                "file": item["file"],
                "title": item["title_uz"],
                "source_url": item["source_url"],
                "original_url": item["original_url"],
                "license": item["license"],
                "width": item["width"],
                "height": item["height"],
            }

    generated = [
        ("gen_t11_balkh_qurultay", 11, "assets/images/generated/topic_11/gen_t11_balkh_qurultay.png", "1370-yil Balx qurultoyi va markazlashuv", "Balxdagi siyosiy kengash va markazlashgan davlat tuzish jarayoni"),
        ("gen_t11_herat_1381", 11, "assets/images/generated/topic_11/gen_t11_herat_1381.png", "1381-yil Hirot yurishi", "Hirot darvozasida siyosiy nazorat almashinuvi"),
        ("gen_t12_terek_1395", 12, "assets/images/generated/topic_12/gen_t12_terek_1395.png", "1395-yil Terek jangi", "Temur va To‘xtamish qo‘shinlarining Terek bo‘yidagi harakati"),
        ("gen_t12_ankara_1402", 12, "assets/images/generated/topic_12/gen_t12_ankara_1402.png", "1402-yil Anqara jangi", "Temur va Boyazid qo‘shinlarining Anqara yaqinidagi taktik joylashuvi"),
        ("gen_t13_clavijo_samarkand", 13, "assets/images/generated/topic_13/gen_t13_clavijo_samarkand.png", "Klavixoning Samarqanddagi qabuli", "1404-yilda Kastiliya elchilarining Temuriylar saroyidagi qabuli"),
        ("gen_t13_western_couriers", 13, "assets/images/generated/topic_13/gen_t13_western_couriers.png", "G‘arbga yo‘l olgan diplomatik choparlar", "Samarqanddan Yevropa tomon maktub olib ketayotgan elchilar"),
        ("gen_t13_ming_envoys", 13, "assets/images/generated/topic_13/gen_t13_ming_envoys.png", "Ming elchilarining Samarqanddagi qabuli", "Temuriy va Ming elchilari o‘rtasidagi rasmiy uchrashuv"),
        ("gen_t14_seven_corps", 14, "assets/images/generated/topic_14/gen_t14_seven_corps.png", "Yetti qo‘l qo‘shin tartibi", "Qo‘shinning markaz, qanot, ilg‘or va zaxira qismlariga bo‘linishi"),
        ("gen_t14_logistics", 14, "assets/images/generated/topic_14/gen_t14_logistics.png", "Temuriy qo‘shin ta’minoti", "Uzoq yurish oldidan oziq-ovqat, ot-ulov va qurol ta’minoti"),
        ("gen_t15_central_divan", 15, "assets/images/generated/topic_15/gen_t15_central_divan.png", "Samarqanddagi markaziy devon", "Kotiblar, moliya amaldorlari va viloyat xabarchilari ish jarayoni"),
        ("gen_t15_justice_court", 15, "assets/images/generated/topic_15/gen_t15_justice_court.png", "Adolat va sud majlisi", "Savdogarlar nizosi tinglanayotgan ma’muriy-sud jarayoni"),
    ]
    for media_id, topic, file, title, prompt_summary in generated:
        by_id[media_id] = {
            "id": media_id,
            "topic": topic,
            "kind": "generated",
            "file": file,
            "title": title,
            "license": "TARIX360 AI educational reconstruction",
            "method": "OpenAI built-in image generation",
            "prompt_summary": prompt_summary,
            "reconstruction_note": "Bu tarixiy foto emas; darslik va davr kontekstiga tayangan ta’limiy vizual rekonstruksiya.",
        }

    reused = [
        ("src_t09_004", "src_t11_balkh_attack_reuse", 11, "1370-yil Balx voqealari — Zafarnoma tasviri"),
        ("src_t10_006", "src_t11_timurid_map_reuse", 11, "Amir Temur davlati xaritasi"),
        ("src_t10_005", "src_t14_tokhtamysh_battle_reuse", 14, "Temur va To‘xtamish qo‘shinlari — tarixiy miniatyura"),
        ("src_t10_001", "src_t15_genealogy_reuse", 15, "Temuriylar shajarasi va siyosiy tuzilma"),
    ]
    for source_id, media_id, topic, title in reused:
        source = dict(by_id[source_id])
        source.update({"id": media_id, "topic": topic, "title": title, "reused_from": source_id})
        by_id[media_id] = source

    write_json(path, list(by_id.values()))


def rebuild_master() -> None:
    layers = [
        ("states_master_v2.geojson", "state", "states"),
        ("cities_master_v2.geojson", "city", "cities"),
        ("events_master_v2.geojson", "event", "events"),
        ("routes_master_v2.geojson", "route", "routes"),
        ("thematic_points_v2.geojson", None, "thematic_points"),
    ]
    features = []
    for filename, feature_class, source_layer in layers:
        collection = read_json(DATA / filename)
        for feature in collection["features"]:
            feature = json.loads(json.dumps(feature, ensure_ascii=False))
            properties = feature.setdefault("properties", {})
            if feature_class:
                properties["feature_class"] = feature_class
            else:
                properties.setdefault("feature_class", "thematic")
            properties["source_layer"] = source_layer
            feature.pop("id", None)
            features.append(feature)
    write_json(DATA / "master_all_features.geojson", {"type": "FeatureCollection", "features": features})


def write_sources() -> None:
    payload = {
        "schemaVersion": 1,
        "scope": "TARIX360 topics 11–15",
        "authority": "The textbook fixes lesson scope and pages; academic and museum sources support geography, chronology and media metadata.",
        "sources": [
            {"id": "BOOK_2023", "title": TEXTBOOK_REF["title"], "driveFileId": BOOK_DRIVE_ID, "pages": [94, 131], "use": "topic structure, textbook narrative and reference map"},
            {"id": "IRANICA_CENTRAL_ASIA", "title": "Encyclopaedia Iranica — Central Asia in the Mongol and Timurid Periods", "url": IRANICA_CENTRAL_ASIA, "use": "territorial chronology, cities and political context"},
            {"id": "UNESCO_TIMUR", "title": "UNESCO History of Civilizations of Central Asia — Central Asia under Timur", "url": UNESCO_TIMUR, "use": "campaigns, administration and relations with western European rulers"},
            {"id": "MET_TIMURID", "title": "The Metropolitan Museum of Art — The Art of the Timurid Period", "url": MET_TIMURID, "use": "period overview and open-access visual context"},
            {"id": "IRANICA_CLAVIJO", "title": "Encyclopaedia Iranica — Ruy González de Clavijo", "url": "https://www.iranicaonline.org/articles/clavijo-ruy-gonzlez-de-d/", "use": "1403–1404 embassy itinerary and chronology"},
            {"id": "UNESCO_SILK_CITIES", "title": "UNESCO Silk Roads — Cities along the Silk Roads", "url": "https://en.unesco.org/silkroad/silk-road-themes/cities-silk-roads", "use": "city-network interpretation"},
        ],
        "geometryPolicy": "Boundaries are generalized teaching reconstructions, not cadastral borders. Campaign reach is encoded as dated routes and events rather than permanent territorial fill.",
    }
    write_json(DATA / "sources_topics_11_15.json", payload)


def apply_drive_sync() -> None:
    sync_path = DATA / "drive_sync_topics_11_15.json"
    if not sync_path.exists():
        return
    sync = read_json(sync_path)

    book_path = DATA / "book_pages_manifest.json"
    book = read_json(book_path)
    for page in book.get("pages", []):
        drive_id = sync.get("pages", {}).get(str(page["page"]))
        if drive_id:
            page["driveFileId"] = drive_id
    book.setdefault("drive", {}).setdefault("topicFolderIds", {}).update(
        {str(key): value for key, value in sync.get("folders", {}).get("book", {}).items()}
    )
    write_json(book_path, book)

    manifest_path = DATA / "web_content_manifest.json"
    manifest = read_json(manifest_path)
    manifest["release"] = "first15-hybrid-v4"
    manifest["drive"]["bookTopicFolderIds11To15"] = sync["folders"]["book"]
    manifest["drive"]["sourceTopicFolderIds11To15"] = sync["folders"]["source"]
    dataset_paths = {
        "data/topic_config_10.json",
        "data/book_pages_manifest.json",
        "data/master_all_features.geojson",
        "data/media_manifest.json",
        "data/states_master_v2.geojson",
        "data/events_master_v2.geojson",
        "data/cities_master_v2.geojson",
        "data/routes_master_v2.geojson",
        "data/thematic_points_v2.geojson",
    }
    for record in manifest.get("datasets", []):
        if record.get("path") in dataset_paths:
            local_path = ROOT / record["path"]
            if local_path.exists():
                record["size"] = local_path.stat().st_size
    datasets_by_path = {item["path"]: item for item in manifest.get("datasets", [])}
    for relative_path, sync_key in [
        ("data/sources_topics_11_15.json", "sources_topics_11_15"),
        ("data/drive_sync_topics_11_15.json", "drive_sync_topics_11_15"),
        ("data/web_sources_topics_11_15.json", "web_sources_topics_11_15"),
    ]:
        local_path = ROOT / relative_path
        datasets_by_path[relative_path] = {
            "path": relative_path,
            "driveFileId": sync["datasets"][sync_key],
            "mimeType": "application/json",
            "size": local_path.stat().st_size,
        }
    manifest["datasets"] = list(datasets_by_path.values())

    media_paths = {
        "src_t11_met_baghdad": ("assets/images/source/topic_11/met_451304_conquest_baghdad.jpg", 11),
        "src_t12_met_battle": ("assets/images/source/topic_12/met_450512_battle_scene.jpg", 12),
        "src_t13_met_chinese_emperor": ("assets/images/source/topic_13/met_448242_chinese_emperor.jpg", 13),
        "src_t14_met_timur_before_battle": ("assets/images/source/topic_14/met_451303_timur_before_battle.jpg", 14),
        "src_t15_met_court_audience": ("assets/images/source/topic_15/met_451959_court_audience.jpg", 15),
    }
    by_path = {item["path"]: item for item in manifest.get("media", [])}
    for media_id, (relative_path, topic) in media_paths.items():
        local_path = ROOT / relative_path
        by_path[relative_path] = {
            "path": relative_path,
            "topic": topic,
            "kind": "source",
            "driveFileId": sync["media"][media_id],
            "mimeType": "image/jpeg",
            "size": local_path.stat().st_size,
        }
    for item in read_json(DATA / "media_manifest.json"):
        drive_id = sync.get("media", {}).get(item.get("id"))
        relative_path = item.get("file")
        local_path = ROOT / relative_path if relative_path else None
        if not drive_id or not local_path or not local_path.exists():
            continue
        mime_type = "image/png" if local_path.suffix.lower() == ".png" else "image/jpeg"
        by_path[relative_path] = {
            "path": relative_path,
            "topic": item.get("topic"),
            "kind": item.get("kind"),
            "driveFileId": drive_id,
            "mimeType": mime_type,
            "size": local_path.stat().st_size,
        }
    manifest["media"] = list(by_path.values())
    manifest["book"]["status"] = "original-and-first15-web-pages-ready"
    write_json(manifest_path, manifest)


def main() -> int:
    build_topics()
    build_states()
    build_cities()
    build_events()
    build_routes()
    build_thematic_points()
    build_media_manifest()
    build_enriched_media_manifest()
    localize_media_manifest()
    rebuild_master()
    write_sources()
    apply_drive_sync()
    print("BUILT topics 11–15: config, states, cities, events, routes, thematic points, media, master")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
