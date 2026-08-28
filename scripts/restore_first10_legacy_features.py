#!/usr/bin/env python3
"""Restore first-ten features accidentally omitted by the topics 11-15 rebuild.

The recovery source is the last known-good Git revision. Recovered records are
written back to their authoritative layer files so future master rebuilds keep
them naturally.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data"
RECOVERY_REVISION = "8957eea"

LAYER_IDS = {
    "states_master_v2.geojson": {
        "OHM_REL_2790245",
        "OHM_REL_2790247",
    },
    "thematic_points_v2.geojson": {
        "TH_RUMI_KONYA",
        "TH_SAADI_SHIRAZ",
        "TH_AMIR_KHUSRAU_DELHI",
        "TH_RASHIDIDDIN_TABRIZ_8",
    },
}


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def load_recovery_master() -> dict:
    result = subprocess.run(
        ["git", "show", f"{RECOVERY_REVISION}:data/master_all_features.geojson"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return json.loads(result.stdout.decode("utf-8"))


def feature_id(feature: dict) -> str | None:
    return feature.get("properties", {}).get("id") or feature.get("id")


def upsert(collection: dict, recovered: dict) -> None:
    recovered_id = feature_id(recovered)
    recovered = json.loads(json.dumps(recovered, ensure_ascii=False))
    recovered["id"] = recovered_id
    for index, current in enumerate(collection["features"]):
        if feature_id(current) == recovered_id:
            collection["features"][index] = recovered
            return
    collection["features"].append(recovered)


def main() -> None:
    recovery_master = load_recovery_master()
    recovery_by_id = {
        feature_id(feature): feature for feature in recovery_master["features"]
    }

    for filename, required_ids in LAYER_IDS.items():
        missing_in_recovery = sorted(required_ids - recovery_by_id.keys())
        if missing_in_recovery:
            raise RuntimeError(
                f"Recovery revision is missing: {', '.join(missing_in_recovery)}"
            )

        path = DATA / filename
        collection = read_json(path)
        for required_id in sorted(required_ids):
            upsert(collection, recovery_by_id[required_id])
        write_json(path, collection)
        print(f"{filename}: {len(required_ids)} legacy feature restored")


if __name__ == "__main__":
    main()
