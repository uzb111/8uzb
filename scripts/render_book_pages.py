#!/usr/bin/env python3
"""Render TARIX360 FIRST10 textbook pages as lightweight WebP assets."""

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
    parser.add_argument("--drive-file-id", required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    document = fitz.open(args.input_pdf)
    if document.page_count < 93:
        raise RuntimeError(f"Expected at least 93 pages, found {document.page_count}")

    pages = []
    for page_number in range(8, 94):
        page = document[page_number - 1]
        scale = args.width / page.rect.width
        pixmap = page.get_pixmap(matrix=fitz.Matrix(scale, scale), colorspace=fitz.csRGB, alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        filename = f"page-{page_number:03d}.webp"
        output = args.output_dir / filename
        image.save(output, "WEBP", quality=args.quality, method=6)
        pages.append(
            {
                "page": page_number,
                "topic": topic_for_page(page_number),
                "file": f"assets/book/web_pages_first10/{filename}",
                "width": image.width,
                "height": image.height,
                "bytes": output.stat().st_size,
                "driveFileId": None,
            }
        )
        print(f"RENDERED {page_number}: {image.width}x{image.height} {output.stat().st_size} bytes")

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
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"MANIFEST {args.manifest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
