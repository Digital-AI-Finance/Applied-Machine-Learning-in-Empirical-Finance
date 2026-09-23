"""
Link Checker Utility
Validates all internal and external links in the project website.
"""

import re
import requests
from pathlib import Path
from typing import Dict, List, Set, Tuple
from urllib.parse import urljoin, urlparse
import time
import concurrent.futures


# Configuration
DOCS_DIR = Path(__file__).parent.parent
TIMEOUT = 10
MAX_WORKERS = 5
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"


def extract_links_from_html(filepath: Path) -> Dict[str, List[str]]:
    """
    Extract all links from an HTML file.

    Returns dict with:
        - href: list of href links
        - src: list of src links (images, scripts)
    """
    content = filepath.read_text(encoding='utf-8')

    # Extract href links (exclude preconnect hints)
    # Preconnect hints are <link rel="preconnect" href="..."> and should be ignored
    href_pattern = r'href=["\']([^"\']+)["\']'
    all_hrefs = re.findall(href_pattern, content)

    # Filter out preconnect hints (fonts.googleapis.com, fonts.gstatic.com base URLs)
    preconnect_urls = {'https://fonts.googleapis.com', 'https://fonts.gstatic.com'}
    hrefs = [h for h in all_hrefs if h not in preconnect_urls]

    # Extract src links
    src_pattern = r'src=["\']([^"\']+)["\']'
    srcs = re.findall(src_pattern, content)

    return {
        'href': hrefs,
        'src': srcs
    }


def categorize_link(link: str) -> str:
    """
    Categorize a link as internal, external, or special.

    Returns: 'internal', 'external', 'anchor', 'mailto', 'javascript', 'data'
    """
    if link.startswith('#'):
        return 'anchor'
    elif link.startswith('mailto:'):
        return 'mailto'
    elif link.startswith('javascript:'):
        return 'javascript'
    elif link.startswith('data:'):
        return 'data'
    elif link.startswith('http://') or link.startswith('https://'):
        return 'external'
    else:
        return 'internal'


def check_internal_link(link: str, base_dir: Path) -> Tuple[bool, str]:
    """
    Check if an internal link/file exists.

    Returns: (exists: bool, message: str)
    """
    # Remove query strings and anchors
    clean_link = link.split('?')[0].split('#')[0]

    if not clean_link:
        return True, "Empty link (anchor only)"

    filepath = base_dir / clean_link

    if filepath.exists():
        return True, f"OK: {clean_link}"
    else:
        return False, f"NOT FOUND: {clean_link}"


def check_external_link(url: str) -> Tuple[bool, str]:
    """
    Check if an external URL is accessible.

    Returns: (accessible: bool, message: str)
    """
    try:
        headers = {'User-Agent': USER_AGENT}
        response = requests.head(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)

        if response.status_code < 400:
            return True, f"OK ({response.status_code}): {url}"
        else:
            # Try GET as some servers don't support HEAD
            response = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True)
            if response.status_code < 400:
                return True, f"OK ({response.status_code}): {url}"
            return False, f"ERROR ({response.status_code}): {url}"

    except requests.exceptions.Timeout:
        return False, f"TIMEOUT: {url}"
    except requests.exceptions.SSLError:
        return False, f"SSL ERROR: {url}"
    except requests.exceptions.ConnectionError:
        return False, f"CONNECTION ERROR: {url}"
    except Exception as e:
        return False, f"ERROR ({type(e).__name__}): {url}"


def check_all_links(check_external: bool = True) -> Dict:
    """
    Check all links in all HTML files.

    Returns comprehensive report.
    """
    html_files = list(DOCS_DIR.glob("*.html"))

    results = {
        'files_checked': [],
        'internal_links': {'valid': [], 'invalid': []},
        'external_links': {'valid': [], 'invalid': [], 'skipped': []},
        'assets': {'valid': [], 'invalid': []},
        'summary': {}
    }

    all_external_urls: Set[str] = set()
    all_internal_links: Set[str] = set()
    all_assets: Set[str] = set()

    print("=" * 60)
    print("Link Checker - Scanning HTML Files")
    print("=" * 60)

    # First pass: collect all links
    for html_file in html_files:
        print(f"\nScanning: {html_file.name}")
        results['files_checked'].append(html_file.name)

        links = extract_links_from_html(html_file)

        # Process href links
        for link in links['href']:
            category = categorize_link(link)
            if category == 'external':
                all_external_urls.add(link)
            elif category == 'internal':
                all_internal_links.add(link)

        # Process src links (assets)
        for src in links['src']:
            category = categorize_link(src)
            if category == 'external':
                all_external_urls.add(src)
            elif category == 'internal':
                all_assets.add(src)

    print(f"\nFound {len(all_internal_links)} internal links")
    print(f"Found {len(all_assets)} asset references")
    print(f"Found {len(all_external_urls)} external URLs")

    # Check internal links
    print("\n" + "=" * 60)
    print("Checking Internal Links")
    print("=" * 60)

    for link in sorted(all_internal_links):
        valid, msg = check_internal_link(link, DOCS_DIR)
        if valid:
            results['internal_links']['valid'].append(msg)
            print(f"  [OK] {link}")
        else:
            results['internal_links']['invalid'].append(msg)
            print(f"  [FAIL] {link}")

    # Check assets
    print("\n" + "=" * 60)
    print("Checking Assets (images, scripts, styles)")
    print("=" * 60)

    for asset in sorted(all_assets):
        valid, msg = check_internal_link(asset, DOCS_DIR)
        if valid:
            results['assets']['valid'].append(msg)
            print(f"  [OK] {asset}")
        else:
            results['assets']['invalid'].append(msg)
            print(f"  [FAIL] {asset}")

    # Check external links
    print("\n" + "=" * 60)
    print("Checking External URLs")
    print("=" * 60)

    if check_external:
        # Use thread pool for faster checking
        with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
            future_to_url = {
                executor.submit(check_external_link, url): url
                for url in all_external_urls
            }

            for future in concurrent.futures.as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    valid, msg = future.result()
                    if valid:
                        results['external_links']['valid'].append(msg)
                        print(f"  [OK] {url[:60]}...")
                    else:
                        results['external_links']['invalid'].append(msg)
                        print(f"  [FAIL] {url[:60]}...")
                except Exception as e:
                    results['external_links']['invalid'].append(f"ERROR: {url} - {e}")
                    print(f"  [ERROR] {url[:60]}...")
    else:
        for url in all_external_urls:
            results['external_links']['skipped'].append(url)
        print(f"  Skipped {len(all_external_urls)} external URLs (use --check-external to verify)")

    # Generate summary
    results['summary'] = {
        'files_checked': len(results['files_checked']),
        'internal_valid': len(results['internal_links']['valid']),
        'internal_invalid': len(results['internal_links']['invalid']),
        'assets_valid': len(results['assets']['valid']),
        'assets_invalid': len(results['assets']['invalid']),
        'external_valid': len(results['external_links']['valid']),
        'external_invalid': len(results['external_links']['invalid']),
        'external_skipped': len(results['external_links']['skipped'])
    }

    return results


def print_summary(results: Dict):
    """Print a summary of the link check results."""
    s = results['summary']

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)
    print(f"Files checked:     {s['files_checked']}")
    print(f"Internal links:    {s['internal_valid']} valid, {s['internal_invalid']} invalid")
    print(f"Assets:            {s['assets_valid']} valid, {s['assets_invalid']} invalid")
    print(f"External URLs:     {s['external_valid']} valid, {s['external_invalid']} invalid, {s['external_skipped']} skipped")

    total_invalid = s['internal_invalid'] + s['assets_invalid'] + s['external_invalid']

    if total_invalid == 0:
        print("\n[PASS] All links are valid!")
        return True
    else:
        print(f"\n[FAIL] Found {total_invalid} broken links")

        if results['internal_links']['invalid']:
            print("\nBroken internal links:")
            for link in results['internal_links']['invalid']:
                print(f"  - {link}")

        if results['assets']['invalid']:
            print("\nMissing assets:")
            for asset in results['assets']['invalid']:
                print(f"  - {asset}")

        if results['external_links']['invalid']:
            print("\nBroken external URLs:")
            for url in results['external_links']['invalid']:
                print(f"  - {url}")

        return False


def main():
    """Main function."""
    import sys

    check_external = '--check-external' in sys.argv or '-e' in sys.argv

    print("Link Checker for Applied ML in Empirical Finance Website")
    print(f"Docs directory: {DOCS_DIR}")
    print(f"Check external links: {check_external}")

    results = check_all_links(check_external=check_external)
    success = print_summary(results)

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
