#!/usr/bin/env python3
"""Restore missing TARIX360 static content from its authoritative Drive manifest.

This is a developer sync utility, not browser runtime code. It never downloads
the project ZIP and refuses to overwrite an existing local file.
"""

from __future__ import annotations

import argparse
import json
import os
import pathlib
import sys
import urllib.error
import urllib.parse
import urllib.request


PROJECT_ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST = PROJECT_ROOT / "data" / "web_content_manifest.json"
BOOK_PAGES_MANIFEST = PROJECT_ROOT / "data" / "book_pages_manifest.json"


def safe_target(relative_path: str) -> pathlib.Path:
    target = (PROJECT_ROOT / relative_path).resolve()
    try:
        target.relative_to(PROJECT_ROOT)
    except ValueError as exc:
        raise ValueError(f"Manifest path escapes project root: {relative_path}") from exc
    return target


def refresh_access_token() -> str:
    direct_token = os.environ.get("GOOGLE_DRIVE_ACCESS_TOKEN")
    if direct_token:
        return direct_token

    values = {
        "client_id": os.environ.get("GOOGLE_DRIVE_CLIENT_ID"),
        "client_secret": os.environ.get("GOOGLE_DRIVE_CLIENT_SECRET"),
        "refresh_token": os.environ.get("GOOGLE_DRIVE_REFRESH_TOKEN"),
        "grant_type": "refresh_token",
    }
    if not all(values.values()):
        raise RuntimeError(
            "Drive credentials missing. Set GOOGLE_DRIVE_ACCESS_TOKEN or "
            "GOOGLE_DRIVE_CLIENT_ID, GOOGLE_DRIVE_CLIENT_SECRET and "
            "GOOGLE_DRIVE_REFRESH_TOKEN."
        )

    request = urllib.request.Request(
        "https://oauth2.googleapis.com/token",
        data=urllib.parse.urlencode(values).encode("utf-8"),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=60) as response:
        payload = json.load(response)
    return payload["access_token"]


def manifest_records(manifest: dict) -> list[dict]:
    records = [*manifest.get("datasets", []), *manifest.get("media", [])]
    if BOOK_PAGES_MANIFEST.exists():
        with BOOK_PAGES_MANIFEST.open("r", encoding="utf-8") as stream:
            records.extend(json.load(stream).get("pages", []))
    book = manifest.get("book") or {}
    if book.get("driveFileId"):
        records.append(
            {
                "path": book["localPath"],
                "driveFileId": book["driveFileId"],
                "mimeType": "application/pdf",
                "size": book.get("size"),
            }
        )
    return records


def restore(record: dict, token: str, dry_run: bool) -> str:
    relative_path = record.get("path")
    file_id = record.get("driveFileId")
    if not relative_path or not file_id:
        return "ERROR incomplete manifest record"

    target = safe_target(relative_path)
    if target.exists():
        return f"SKIP exists: {relative_path}"
    if dry_run:
        return f"PLAN restore: {relative_path}"

    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".part")
    url = (
        "https://www.googleapis.com/drive/v3/files/"
        f"{urllib.parse.quote(file_id, safe='')}?alt=media&supportsAllDrives=true"
    )
    request = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    try:
        with urllib.request.urlopen(request, timeout=180) as response, temporary.open("wb") as output:
            while chunk := response.read(1024 * 1024):
                output.write(chunk)

        expected_size = record.get("size")
        if expected_size and temporary.stat().st_size != int(expected_size):
            temporary.unlink(missing_ok=True)
            return f"ERROR size mismatch: {relative_path}"

        temporary.replace(target)
        return f"RESTORED {relative_path}"
    except (OSError, urllib.error.URLError) as exc:
        temporary.unlink(missing_ok=True)
        return f"ERROR {relative_path}: {exc}"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", type=pathlib.Path, default=DEFAULT_MANIFEST)
    parser.add_argument("--path", action="append", help="Restore only this manifest path; repeatable.")
    parser.add_argument("--dry-run", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    with args.manifest.open("r", encoding="utf-8") as stream:
        manifest = json.load(stream)

    selected_paths = set(args.path or [])
    records = [
        record
        for record in manifest_records(manifest)
        if not selected_paths or record.get("path") in selected_paths
    ]
    if selected_paths:
        found = {record.get("path") for record in records}
        missing = sorted(selected_paths - found)
        if missing:
            print(f"ERROR paths not found in manifest: {', '.join(missing)}", file=sys.stderr)
            return 1

    token = "dry-run" if args.dry_run else refresh_access_token()
    errors = 0
    for record in records:
        result = restore(record, token, args.dry_run)
        print(result)
        errors += result.startswith("ERROR")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
