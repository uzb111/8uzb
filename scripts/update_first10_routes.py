#!/usr/bin/env python3
"""Replace FIRST10 schematic lines with dated, sourced campaign phases."""

from __future__ import annotations

import copy
import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
ROUTES_PATH = ROOT / "data" / "routes_master_v2.geojson"
MASTER_PATH = ROOT / "data" / "master_all_features.geojson"
TOPICS_PATH = ROOT / "data" / "topic_config_10.json"

TEXTBOOK_SOURCE = {
    "title": "O‘zbekiston tarixi, 8-sinf (2023)",
    "drive_file_id": "1MBVkyq1JJmz3WtFZDjpW4vQeKKoJ2ddY",
}
IRANICA_URL = "https://www.iranicaonline.org/articles/jalal-al-din-kvarazmsahi-mengbirni/"


def route_feature(
    feature_id: str,
    title: str,
    start: int,
    end: int,
    coordinates: list[list[float]],
    waypoints: list[str],
    topic_refs: str,
    source_pages: list[int],
    confidence: float,
    phase: str,
    extra_source: str | None = None,
) -> dict:
    source_refs = [
        {
            **TEXTBOOK_SOURCE,
            "pages": source_pages,
        }
    ]
    if extra_source:
        source_refs.append({"title": "Encyclopaedia Iranica", "url": extra_source})
    return {
        "type": "Feature",
        "geometry": {"type": "LineString", "coordinates": coordinates},
        "properties": {
            "id": feature_id,
            "start_date": str(start),
            "end_date": str(end),
            "title_uz": title,
            "period_id": "P00" if start < 1300 else "P05",
            "confidence": confidence,
            "route_quality": "sourced educational waypoint route; not an exact march track",
            "topic_refs": topic_refs,
            "feature_class": "route",
            "phase": phase,
            "waypoints": waypoints,
            "source_refs": source_refs,
        },
    }


NEW_ROUTES = [
    route_feature(
        "ROUTE_MONGOL_MAIN_1219_1220",
        "Chingizxonning O‘trordan Buxoro va Samarqandga asosiy yurishi",
        1219,
        1220,
        [
            [68.30, 42.85],
            [67.35, 42.45],
            [66.10, 41.85],
            [64.95, 40.95],
            [64.43, 39.77],
            [65.55, 39.60],
            [66.96, 39.65],
        ],
        ["O‘tror", "Qizilqum", "Buxoro", "Samarqand"],
        "3",
        [20, 21, 22, 23, 27],
        0.72,
        "main-army",
    ),
    route_feature(
        "ROUTE_MONGOL_SYRDARYA_1219_1221",
        "Jo‘chi qo‘shinining Sirdaryo bo‘ylab yurishi",
        1219,
        1221,
        [
            [68.30, 42.85],
            [67.40, 43.55],
            [66.75, 44.15],
            [65.50, 44.82],
            [63.60, 45.20],
            [61.85, 44.90],
            [60.63, 41.55],
        ],
        ["O‘tror", "Sig‘noq", "Jand", "Yangikent", "Urganch"],
        "3",
        [20, 21, 22, 32],
        0.58,
        "syr-darya-branch",
    ),
    route_feature(
        "ROUTE_MONGOL_KHUJAND_1219_1220",
        "Mo‘g‘ul qo‘shinining Banokat va Xo‘jand tomon yurishi",
        1219,
        1220,
        [
            [68.30, 42.85],
            [69.05, 42.10],
            [69.24, 41.30],
            [68.90, 40.82],
            [69.62, 40.28],
        ],
        ["O‘tror", "Toshkent vohasi", "Banokat", "Xo‘jand"],
        "3",
        [20, 21, 22, 24],
        0.63,
        "khujand-branch",
    ),
    route_feature(
        "ROUTE_JALOLIDDIN_PARVAN_INDUS_1221",
        "Jaloliddinning G‘azna–Parvon–Sind qarshilik yo‘li",
        1221,
        1221,
        [
            [68.42, 33.55],
            [69.17, 34.53],
            [69.17, 35.12],
            [69.23, 33.60],
            [70.60, 32.99],
            [71.55, 32.92],
        ],
        ["G‘azna", "Kobul", "Parvon", "Gardez", "Sind daryosi"],
        "4,5",
        [36, 37, 38, 39, 40],
        0.73,
        "parwan-indus",
        IRANICA_URL,
    ),
    route_feature(
        "ROUTE_JALOLIDDIN_INDIA_1221_1224",
        "Jaloliddinning Hindistondagi harakatlari",
        1221,
        1224,
        [
            [71.55, 32.92],
            [72.33, 31.55],
            [74.36, 31.52],
            [73.10, 30.20],
            [71.47, 30.20],
            [71.06, 29.24],
            [74.10, 29.00],
            [77.21, 28.61],
        ],
        ["Sind daryosi", "Panjob", "Lahor", "Multon", "Uch", "Dehli"],
        "4,5",
        [38, 39, 41, 42],
        0.55,
        "india",
        IRANICA_URL,
    ),
    route_feature(
        "ROUTE_JALOLIDDIN_RETURN_1224_1225",
        "Jaloliddinning Hindistondan Eron va Ozarbayjonga qaytishi",
        1224,
        1225,
        [
            [71.06, 29.24],
            [68.78, 27.85],
            [65.20, 26.10],
            [62.32, 25.13],
            [59.47, 28.95],
            [57.08, 30.28],
            [54.35, 29.61],
            [52.58, 29.59],
            [51.68, 32.65],
            [48.52, 34.80],
            [46.24, 37.39],
            [46.29, 38.08],
        ],
        ["Sind", "Makron", "Kirmon", "Fors", "Isfahon", "Hamadon", "Marog‘a", "Tabriz"],
        "5",
        [42, 43, 44, 45],
        0.61,
        "return-to-iran",
        IRANICA_URL,
    ),
    route_feature(
        "ROUTE_JALOLIDDIN_WEST_1226_1231",
        "Jaloliddinning Kavkaz va Sharqiy Anadoludagi yurishlari",
        1226,
        1231,
        [
            [46.29, 38.08],
            [47.58, 40.68],
            [44.80, 41.69],
            [44.52, 40.18],
            [43.05, 39.72],
            [42.48, 38.75],
            [40.52, 39.75],
            [39.49, 39.75],
            [40.23, 37.91],
        ],
        ["Tabriz", "Arron", "Tbilisi", "Ani", "Ahlat", "Yassi Chemen", "Amid"],
        "5",
        [43, 44, 45, 46, 47, 48, 49, 50],
        0.64,
        "caucasus-anatolia",
        IRANICA_URL,
    ),
]


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: pathlib.Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def replace_routes(collection: dict, *, master: bool) -> None:
    new_ids = {item["properties"]["id"] for item in NEW_ROUTES}
    collection["features"] = [
        item for item in collection["features"] if item.get("properties", {}).get("id") not in new_ids
    ]
    for route in NEW_ROUTES:
        item = copy.deepcopy(route)
        if master:
            item["properties"]["source_layer"] = "routes"
        collection["features"].append(item)


def update_topics(config: dict) -> None:
    replacements = {
        3: [
            "ROUTE_MONGOL_MAIN_1219_1220",
            "ROUTE_MONGOL_SYRDARYA_1219_1221",
            "ROUTE_MONGOL_KHUJAND_1219_1220",
        ],
        4: [
            "ROUTE_JALOLIDDIN_PARVAN_INDUS_1221",
            "ROUTE_JALOLIDDIN_INDIA_1221_1224",
        ],
        5: [
            "ROUTE_JALOLIDDIN_PARVAN_INDUS_1221",
            "ROUTE_JALOLIDDIN_INDIA_1221_1224",
            "ROUTE_JALOLIDDIN_RETURN_1224_1225",
            "ROUTE_JALOLIDDIN_WEST_1226_1231",
        ],
    }
    for topic in config["topics"]:
        if topic["id"] not in replacements:
            continue
        topic["showFeatureIds"] = [
            feature_id
            for feature_id in topic["showFeatureIds"]
            if feature_id != "ROUTE_JALOLIDDIN_1220_1223"
            and not feature_id.startswith("ROUTE_MONGOL_")
        ]
        topic["showFeatureIds"].extend(replacements[topic["id"]])


def main() -> int:
    routes = load(ROUTES_PATH)
    master = load(MASTER_PATH)
    topics = load(TOPICS_PATH)
    replace_routes(routes, master=False)
    replace_routes(master, master=True)
    update_topics(topics)
    write(ROUTES_PATH, routes)
    write(MASTER_PATH, master)
    write(TOPICS_PATH, topics)
    print(f"UPDATED {len(NEW_ROUTES)} dated route phases")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
