"""
Fetch Partner Logos

Downloads logos from partner organizations for use on the project website.
Includes content validation to prevent saving corrupted files (e.g. HTML 404 pages).
"""

import argparse
import os
import sys
import time
from pathlib import Path

import requests

# PNG magic bytes: \x89PNG\r\n\x1a\n
PNG_MAGIC = b"\x89PNG\r\n\x1a\n"
JPEG_MAGIC = b"\xff\xd8\xff"

LOGOS = [
    {
        "name": "quoniam",
        "url": "https://www.quoniam.com/wp-content/uploads/2025/07/qam.png",
        "filename": "quoniam_logo.png",
        "fallback_url": None,
        "convert_to_png": False,
    },
    {
        "name": "university_of_twente",
        "url": "https://www.utwente.nl/logo-stacked.png",
        "filename": "ut_logo.png",
        "fallback_url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/79/Universiteit_Twente_Logo.svg/320px-Universiteit_Twente_Logo.svg.png",
        "convert_to_png": False,
    },
    {
        "name": "cost_action",
        "url": "https://www.cost.eu/uploads/2022/03/COST_LOGO_rgb_highresolution-scaled.jpg",
        "filename": "cost_logo.png",
        "fallback_url": "https://www.cost.eu/uploads/2021/03/Logo-banner.png",
        "convert_to_png": True,
    },
    {
        "name": "eu_flag",
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/b/b7/Flag_of_Europe.svg/320px-Flag_of_Europe.svg.png",
        "filename": "eu_flag.png",
        "fallback_url": None,
        "convert_to_png": False,
    },
]

MIN_FILE_SIZE = 1024  # 1 KB minimum for a valid logo


def validate_image_bytes(data: bytes) -> bool:
    """Check that data starts with PNG or JPEG magic bytes."""
    return data[:8] == PNG_MAGIC or data[:3] == JPEG_MAGIC


def validate_content_type(content_type: str) -> bool:
    """Reject responses whose Content-Type is not an image."""
    return content_type.lower().startswith("image/")


def convert_jpeg_to_png(data: bytes) -> bytes:
    """Convert JPEG bytes to PNG bytes using Pillow."""
    from io import BytesIO

    from PIL import Image

    img = Image.open(BytesIO(data))
    buf = BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def file_is_valid(path: Path) -> bool:
    """Check if an existing file is a valid image (PNG/JPEG magic bytes, min size)."""
    if not path.exists():
        return False
    if path.stat().st_size < MIN_FILE_SIZE:
        return False
    data = path.read_bytes()[:8]
    return data[:8] == PNG_MAGIC or data[:3] == JPEG_MAGIC


def download_logo(url: str, output_path: Path, *, convert_to_png: bool = False) -> bool:
    """Download a logo with content validation and temp-file-then-move pattern."""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }

    try:
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        # Content-Type validation
        content_type = response.headers.get("Content-Type", "")
        if not validate_content_type(content_type):
            print(f"  Rejected: Content-Type is '{content_type}', not an image")
            return False

        data = response.content

        # Minimum size check
        if len(data) < MIN_FILE_SIZE:
            print(f"  Rejected: file too small ({len(data)} bytes)")
            return False

        # Magic bytes validation
        if not validate_image_bytes(data):
            print(f"  Rejected: invalid image magic bytes (likely HTML error page)")
            return False

        # JPEG -> PNG conversion if needed
        if convert_to_png and data[:3] == JPEG_MAGIC:
            print("  Converting JPEG to PNG...")
            data = convert_jpeg_to_png(data)

        # Write to temp file, then atomically move into place
        tmp_path = output_path.with_suffix(".tmp")
        tmp_path.write_bytes(data)
        os.replace(tmp_path, output_path)

        return True

    except requests.RequestException as e:
        print(f"  Error downloading: {e}")
        return False


def main() -> None:
    """Download all partner logos."""
    parser = argparse.ArgumentParser(description="Fetch partner logos")
    parser.add_argument(
        "--force",
        action="store_true",
        help="Re-download even if valid files already exist",
    )
    args = parser.parse_args()

    print("=" * 60)
    print("Fetching Partner Logos")
    print("=" * 60)

    script_dir = Path(__file__).parent
    output_dir = script_dir.parent / "assets" / "images" / "logos"
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nOutput directory: {output_dir}")

    success_count = 0

    for logo in LOGOS:
        print(f"\nDownloading: {logo['name']}")
        output_path = output_dir / logo["filename"]

        # Skip if valid file exists and --force not set
        if not args.force and file_is_valid(output_path):
            print(f"  Already exists and valid: {output_path}")
            success_count += 1
            continue

        # Try primary URL
        if download_logo(
            logo["url"], output_path, convert_to_png=logo.get("convert_to_png", False)
        ):
            print(f"  Saved to: {output_path}")
            success_count += 1
        elif logo.get("fallback_url"):
            print("  Trying fallback URL...")
            if download_logo(
                logo["fallback_url"],
                output_path,
                convert_to_png=False,
            ):
                print(f"  Saved fallback to: {output_path}")
                success_count += 1
            else:
                print(f"  Failed to download {logo['name']}")
        else:
            print(f"  Failed to download {logo['name']}")

        time.sleep(0.5)  # Rate limiting

    print("\n" + "=" * 60)
    print(f"Downloaded {success_count}/{len(LOGOS)} logos")
    print("=" * 60)

    if success_count < len(LOGOS):
        sys.exit(1)


if __name__ == "__main__":
    main()
