#!/usr/bin/env python3
"""Download reviewed public-domain Commons images for TARIX360 topics 11-15."""

from __future__ import annotations

import json
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
API = "https://commons.wikimedia.org/w/api.php"
USER_AGENT = "TARIX360-school-history/1.0"

SOURCES = [
    {
        "id": "src_t11_commons_balkh_audience",
        "topic": 11,
        "filename": "src_t11_commons_balkh_audience.jpg",
        "commons_title": "File:Depiction of Timur granting audience on the occasion of his accession, in the near contemporary Zafarnama (1424-1428), 1467 edition.jpg",
        "title_uz": "Amir Temurning 1370-yil Balxdagi qabul marosimi — Zafarnoma miniatyurasi",
    },
    {
        "id": "src_t12_commons_tokhtamysh_1391",
        "topic": 12,
        "filename": "src_t12_commons_tokhtamysh_1391.jpg",
        "commons_title": "File:Battle between Timur and Toqtamish Khan in 1391. Zafarnama of 1436 (Toqtamish detail).jpg",
        "title_uz": "Temur va To‘xtamish jangi — 1436-yilgi Zafarnoma tafsiloti",
    },
    {
        "id": "src_t13_commons_clavijo_manuscript",
        "topic": 13,
        "filename": "src_t13_commons_clavijo_manuscript.jpg",
        "commons_title": "File:Clavijo BNE ms. f. 1r.jpg",
        "title_uz": "Klavixoning Samarqand elchiligi bayon qilingan qo‘lyozma sahifasi",
    },
    {
        "id": "src_t14_commons_timur_tokhtamysh_battle",
        "topic": 14,
        "filename": "src_t14_commons_timur_tokhtamysh_battle.jpg",
        "commons_title": "File:Battle between Timur and Toqtamish Khan in 18 June 1391. Zafarnama of 1436, facing folios 208v-207r.jpg",
        "title_uz": "Temur va To‘xtamish qo‘shinlari — Zafarnomaning ikki sahifali jang tasviri",
    },
    {
        "id": "src_t15_commons_khalil_court",
        "topic": 15,
        "filename": "src_t15_commons_khalil_court.jpg",
        "commons_title": "File:Contemporary drawing of Khalil Sultan enthroned, 1405-1406 (Ms. Diez A. fol.74, p.24) b.jpg",
        "title_uz": "Xalil Sulton saroyi: qilich va qalam ahli tasvirlangan boshqaruv majlisi",
    },
]


def fetch_json(url: str) -> dict:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=60) as response:
        return json.load(response)


def download(url: str, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists() and destination.stat().st_size:
        return
    for attempt in range(4):
        request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
        try:
            with urllib.request.urlopen(request, timeout=120) as response:
                destination.write_bytes(response.read())
            return
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 3:
                raise
            time.sleep(4 * (attempt + 1))


def main() -> None:
    records = []
    for source in SOURCES:
        query = urllib.parse.urlencode(
            {
                "action": "query",
                "format": "json",
                "formatversion": "2",
                "prop": "imageinfo",
                "iiprop": "url|size|mime|extmetadata",
                "titles": source["commons_title"],
            }
        )
        page = fetch_json(f"{API}?{query}")["query"]["pages"][0]
        if page.get("missing") or not page.get("imageinfo"):
            raise RuntimeError(f"Commons file not found: {source['commons_title']}")

        info = page["imageinfo"][0]
        metadata = info.get("extmetadata", {})
        license_name = metadata.get("LicenseShortName", {}).get("value", "")
        if "public domain" not in license_name.lower() and not license_name.lower().startswith("cc"):
            raise RuntimeError(f"Unapproved license for {source['commons_title']}: {license_name}")

        destination = ROOT / "assets" / "images" / "source" / f"topic_{source['topic']}" / source["filename"]
        download(info["url"], destination)
        page_url = "https://commons.wikimedia.org/wiki/" + urllib.parse.quote(page["title"].replace(" ", "_"), safe=":()_,.-")
        records.append(
            {
                **source,
                "file": destination.relative_to(ROOT).as_posix(),
                "source_url": page_url,
                "original_url": info["url"],
                "license": license_name,
                "width": info.get("width"),
                "height": info.get("height"),
                "mime_type": info.get("mime"),
                "size": destination.stat().st_size,
            }
        )
        print(f"topic {source['topic']}: {destination.name} ({destination.stat().st_size} bytes)")

    output = ROOT / "data" / "web_sources_topics_11_15.json"
    output.write_text(json.dumps(records, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
