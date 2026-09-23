"""
Download Team Photos
Fetches team member photos from verified sources.
"""

import requests
from pathlib import Path
from PIL import Image, ImageOps
from io import BytesIO

# Team photos - verified URLs
TEAM_PHOTOS = {
    "joerg_osterrieder": {
        "url": "https://loop.frontiersin.org/images/profile/587887/203",
        "fallback": None
    },
    "xiaohong_huang": {
        "url": "https://utwente.becdn.net/.wh/ea/uc/ie6d37ac001033594f201f93b7403467451416b7cd5280c016340014001804100000000/xhuang.jpg",
        "fallback": None
    },
    "axel_gross_klussmann": {
        "url": "https://www.quoniam.com/wp-content/uploads/2024/09/D-W_interview_Gross-Klussmann-921x461-c-default.jpg",
        "fallback": None
    }
}

OUTPUT_DIR = Path(__file__).parent.parent / "assets" / "images" / "team"


def download_and_convert_photo(name: str, urls: dict) -> bool:
    """
    Download photo and convert to JPG format.

    Args:
        name: Team member identifier (e.g., 'joerg_osterrieder')
        urls: Dict with 'url' and optional 'fallback' URL

    Returns:
        True if successful, False otherwise
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{name}.jpg"

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    for url in [urls['url'], urls.get('fallback')]:
        if not url:
            continue

        try:
            print(f"Downloading {name} from {url[:60]}...")
            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                # Load image and convert to RGB JPG
                img = Image.open(BytesIO(response.content))

                # Convert to RGB if necessary (for AVIF/PNG with transparency)
                if img.mode in ('RGBA', 'P'):
                    img = img.convert('RGB')
                elif img.mode != 'RGB':
                    img = img.convert('RGB')

                # Resize to standard size (200x200) for consistency
                img = ImageOps.fit(img, (200, 200), Image.Resampling.LANCZOS)

                # Save as JPG
                img.save(output_path, 'JPEG', quality=90)
                print(f"  Saved: {output_path}")
                return True

        except Exception as e:
            print(f"  Error: {e}")
            continue

    print(f"  Failed to download {name}")
    return False


def create_placeholder(name: str, initials: str, color: str = "#3b82f6") -> bool:
    """
    Create a placeholder image with initials.

    Args:
        name: Team member identifier
        initials: 2-letter initials
        color: Background color (hex)

    Returns:
        True if successful
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT_DIR / f"{name}.jpg"

    try:
        from PIL import ImageDraw, ImageFont

        # Create image with solid color
        img = Image.new('RGB', (200, 200), color)
        draw = ImageDraw.Draw(img)

        # Try to use a nice font, fallback to default
        try:
            font = ImageFont.truetype("arial.ttf", 72)
        except:
            font = ImageFont.load_default()

        # Draw initials centered
        bbox = draw.textbbox((0, 0), initials, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (200 - text_width) // 2
        y = (200 - text_height) // 2 - 10

        draw.text((x, y), initials, fill="white", font=font)

        img.save(output_path, 'JPEG', quality=90)
        print(f"Created placeholder: {output_path}")
        return True

    except Exception as e:
        print(f"Error creating placeholder for {name}: {e}")
        return False


def main():
    """Download all team photos."""
    print("=" * 60)
    print("Team Photo Downloader")
    print("=" * 60)
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Download available photos
    for name, urls in TEAM_PHOTOS.items():
        download_and_convert_photo(name, urls)

    print()

    # Convert local photos (placed manually in the team directory)
    local_photos = {
        "dennis_hoffmann": "portrait_white_bg.png",
    }

    for name, source_file in local_photos.items():
        source_path = OUTPUT_DIR / source_file
        if source_path.exists():
            print(f"Converting local photo: {source_file} -> {name}.jpg")
            img = Image.open(source_path)
            if img.mode != 'RGB':
                img = img.convert('RGB')
            img = ImageOps.fit(img, (200, 200), Image.Resampling.LANCZOS)
            img.save(OUTPUT_DIR / f"{name}.jpg", 'JPEG', quality=90)
            print(f"  Saved: {OUTPUT_DIR / f'{name}.jpg'}")
        else:
            print(f"  Local photo not found: {source_path}")

    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)

    for f in OUTPUT_DIR.glob("*.jpg"):
        print(f"  {f.name}")

    return 0


if __name__ == "__main__":
    exit(main())
