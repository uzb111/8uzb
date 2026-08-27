#!/usr/bin/env python3
"""Improve FIRST10 historical boundaries and attach uncertainty metadata."""

from __future__ import annotations

import copy
import json
import pathlib


ROOT = pathlib.Path(__file__).resolve().parents[1]
STATES_PATH = ROOT / "data" / "states_master_v2.geojson"
MASTER_PATH = ROOT / "data" / "master_all_features.geojson"
BOOK_ID = "1MBVkyq1JJmz3WtFZDjpW4vQeKKoJ2ddY"


BOUNDARY_UPDATES = {
    "P00_KHWARAZM_1218": {
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [52.8, 44.5],
                [55.0, 45.2],
                [58.0, 46.0],
                [61.0, 45.8],
                [64.0, 44.9],
                [66.8, 44.2],
                [68.5, 43.5],
                [70.2, 42.8],
                [71.2, 41.2],
                [71.0, 39.0],
                [70.0, 37.2],
                [68.2, 35.4],
                [66.5, 33.2],
                [65.0, 30.6],
                [63.8, 28.0],
                [61.5, 25.6],
                [59.0, 25.2],
                [56.5, 25.5],
                [54.0, 26.5],
                [52.0, 28.0],
                [50.2, 30.0],
                [48.8, 32.0],
                [47.0, 34.0],
                [45.8, 36.0],
                [46.0, 38.0],
                [47.2, 39.5],
                [49.0, 39.2],
                [50.8, 37.7],
                [52.8, 36.9],
                [54.5, 37.2],
                [54.2, 39.0],
                [53.5, 41.0],
                [52.8, 44.5]
            ]],
        },
        "properties": {
            "confidence": 0.64,
            "boundary_kind": "territorial_extent",
            "boundary_quality": "textbook-georeferenced approximation",
            "uncertainty_note": "Chegara darslikdagi 1217–1218-yil siyosiy hudud xaritasidan umumlashtirilgan.",
            "source_refs": [{
                "title": "O‘zbekiston tarixi, 8-sinf (2023)",
                "drive_file_id": BOOK_ID,
                "pages": [9]
            }],
        },
    },
    "P01_CHAGATAI_EARLY": {
        "geometry": {
            "type": "Polygon",
            "coordinates": [[
                [58.7, 37.5],
                [59.0, 39.8],
                [60.2, 42.0],
                [62.5, 43.6],
                [65.2, 44.4],
                [68.5, 45.3],
                [72.0, 46.6],
                [75.5, 47.2],
                [79.0, 46.8],
                [82.5, 46.0],
                [86.0, 44.8],
                [89.2, 43.0],
                [90.0, 41.0],
                [89.0, 39.2],
                [87.0, 37.5],
                [84.0, 36.0],
                [80.5, 35.0],
                [77.0, 34.4],
                [73.5, 34.2],
                [70.5, 34.5],
                [68.0, 35.1],
                [65.0, 35.6],
                [62.0, 36.0],
                [59.8, 36.5],
                [58.7, 37.5]
            ]],
        },
        "properties": {
            "confidence": 0.62,
            "boundary_kind": "territorial_extent",
            "boundary_quality": "textbook-georeferenced approximation",
            "uncertainty_note": "Chig‘atoy ulusi hududi darslikning ikki masshtabdagi xaritasidan umumlashtirilgan.",
            "source_refs": [{
                "title": "O‘zbekiston tarixi, 8-sinf (2023)",
                "drive_file_id": BOOK_ID,
                "pages": [54, 55]
            }],
        },
    },
}


INFLUENCE_ZONES = {
    "P03_MOGHULISTAN_1372": (0.48, [63, 64, 65]),
    "P04_WEST_CHAGATAI": (0.48, [63, 64, 65]),
    "P05_BARLAS": (0.36, [76, 77, 78]),
    "P05_QARAUNAS": (0.34, [76, 77, 78]),
    "P05_SAMARKAND": (0.38, [76, 77, 83, 84]),
    "P05_FERGHANA": (0.32, [76, 77]),
    "P05_BUKHARA": (0.34, [76, 77]),
    "P06_TIMUR_1370": (0.46, [87, 88, 89, 90]),
}


def load(path: pathlib.Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write(path: pathlib.Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def update_collection(collection: dict, *, master: bool) -> None:
    for feature in collection["features"]:
        properties = feature.get("properties", {})
        feature_id = properties.get("id")
        if feature_id in BOUNDARY_UPDATES:
            update = BOUNDARY_UPDATES[feature_id]
            feature["geometry"] = copy.deepcopy(update["geometry"])
            properties.update(copy.deepcopy(update["properties"]))
        elif feature_id in INFLUENCE_ZONES:
            confidence, pages = INFLUENCE_ZONES[feature_id]
            properties.update({
                "confidence": confidence,
                "boundary_kind": "influence_zone",
                "boundary_quality": "schematic political influence zone",
                "uncertainty_note": "Bu kontur qat’iy davlat chegarasi emas; darslik matnidagi siyosiy ta’sir makonini ko‘rsatadi.",
                "source_refs": [{
                    "title": "O‘zbekiston tarixi, 8-sinf (2023)",
                    "drive_file_id": BOOK_ID,
                    "pages": pages,
                }],
            })
        elif feature_id in {"OHM_REL_2790245", "OHM_REL_2790247"}:
            properties.setdefault("boundary_kind", "territorial_extent")
            properties.setdefault("boundary_quality", "external historical map geometry")
            properties.setdefault("uncertainty_note", "Tarixiy chegara taxminiy; zamonaviy ma’muriy chegara sifatida talqin qilinmaydi.")
        if master and feature_id in (set(BOUNDARY_UPDATES) | set(INFLUENCE_ZONES)):
            properties["source_layer"] = "states"


def main() -> int:
    states = load(STATES_PATH)
    master = load(MASTER_PATH)
    update_collection(states, master=False)
    update_collection(master, master=True)
    write(STATES_PATH, states)
    write(MASTER_PATH, master)
    print("UPDATED FIRST10 boundary geometry and uncertainty metadata")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
