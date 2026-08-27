"""Build the lightweight static image manifest used by GitHub Pages."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE_MANIFEST = ROOT / "data" / "media_manifest.json"
OUTPUT_MANIFEST = ROOT / "data" / "media_manifest_github.json"
OUTPUT_ROOT = ROOT / "assets" / "images" / "web"
MAX_DIMENSION = 1600
WEBP_QUALITY = 82


def web_path(source_path: Path) -> Path:
    relative = source_path.relative_to(ROOT / "assets" / "images")
    destination = OUTPUT_ROOT / relative
    if source_path.suffix.lower() != ".svg":
        destination = destination.with_suffix(".webp")
    return destination


def optimize_raster(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        image.thumbnail((MAX_DIMENSION, MAX_DIMENSION), Image.Resampling.LANCZOS)
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGBA" if "transparency" in image.info else "RGB")
        image.save(destination, "WEBP", quality=WEBP_QUALITY, method=6)


def build() -> None:
    records = json.loads(SOURCE_MANIFEST.read_text(encoding="utf-8"))
    output_records = []

    for record in records:
        source = ROOT / record["file"]
        destination = web_path(source)
        if source.suffix.lower() == ".svg":
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
        else:
            optimize_raster(source, destination)

        output_record = dict(record)
        output_record["file"] = destination.relative_to(ROOT).as_posix()
        output_records.append(output_record)

    OUTPUT_MANIFEST.write_text(
        json.dumps(output_records, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"GitHub Pages snapshot: {len(output_records)} media records")


if __name__ == "__main__":
    build()
