#!/usr/bin/env python3
"""Render TARIX360 textbook pages as lightweight WebP assets.

The output manifest is merged with existing records so later topic batches do
not discard Drive IDs already assigned to earlier pages.
"""

from __future__ import annotations

import argparse
import json
import pathlib

import fitz
from PIL import Image


TOPICS = [
    {"topic": 1, "start": 8, "end": 11},
    {"topic": 2, "start": 12, "end": 19},
    {"topic": 3, "start": 20, "end": 35},
    {"topic": 4, "start": 36, "end": 40},
    {"topic": 5, "start": 41, "end": 51},
    {"topic": 6, "start": 52, "end": 62},
    {"topic": 7, "start": 63, "end": 69},
    {"topic": 8, "start": 70, "end": 75},
    {"topic": 9, "start": 76, "end": 86},
    {"topic": 10, "start": 87, "end": 93},
    {"topic": 11, "start": 94, "end": 99},
    {"topic": 12, "start": 100, "end": 111},
    {"topic": 13, "start": 112, "end": 116},
    {"topic": 14, "start": 117, "end": 126},
    {"topic": 15, "start": 127, "end": 131},
]


def topic_for_page(page_number: int) -> int:
    return next(item["topic"] for item in TOPICS if item["start"] <= page_number <= item["end"])


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input_pdf", type=pathlib.Path)
    parser.add_argument("output_dir", type=pathlib.Path)
    parser.add_argument("manifest", type=pathlib.Path)
    parser.add_argument("--width", type=int, default=1440)
    parser.add_argument("--quality", type=int, default=82)
    parser.add_argument("--start-page", type=int, default=TOPICS[0]["start"])
    parser.add_argument("--end-page", type=int, default=TOPICS[-1]["end"])
    parser.add_argument("--drive-file-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    document = fitz.open(args.input_pdf)
    if document.page_count < args.end_page:
        raise RuntimeError(f"Expected at least {args.end_page} pages, found {document.page_count}")

    existing_payload = {}
    existing_by_page = {}
    if args.manifest.exists():
        existing_payload = json.loads(args.manifest.read_text(encoding="utf-8"))
        existing_by_page = {int(item["page"]): item for item in existing_payload.get("pages", [])}

    rendered_by_page = {}
    for page_number in range(args.start_page, args.end_page + 1):
        page = document[page_number - 1]
        scale = args.width / page.rect.width
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB, alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        filename = f"page-{page_number:03d}.webp"
        output = args.output_dir / filename
        image.save(output, "WEBP", quality=args.quality, method=6)
        previous = existing_by_page.get(page_number, {})
        rendered_by_page[page_number] = {
            "page": page_number,
            "topic": topic_for_page(page_number),
            "file": f"assets/book/web_pages_first10/{filename}",
            "width": image.width,
            "height": image.height,
            "bytes": output.stat().st_size,
            "driveFileId": previous.get("driveFileId"),
        }
        print(f"RENDERED {page_number}: {image.width}x{image.height} {output.stat().st_size} bytes")

    pages = []
    for page_number in range(TOPICS[0]["start"], TOPICS[-1]["end"] + 1):
        record = rendered_by_page.get(page_number) or existing_by_page.get(page_number)
        if record is None:
            raise RuntimeError(f"Page {page_number} is absent; render it before publishing the manifest")
        record = dict(record)
        record["topic"] = topic_for_page(page_number)
        pages.append(record)

    payload = {
        "schemaVersion": 1,
        "source": {
            "title": "8-sinf O‘zbekiston tarixi (2023)",
            "driveFileId": args.drive_file_id,
            "originalBytes": args.input_pdf.stat().st_size,
            "totalPages": document.page_count,
        },
        "render": {
            "format": "webp",
            "targetWidth": args.width,
            "quality": args.quality,
            "policy": "Load the current page only; prefetch at most the adjacent pages.",
        },
        "topics": TOPICS,
        "pages": pages,
        "drive": existing_payload.get("drive", {}),
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MANIFEST {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
