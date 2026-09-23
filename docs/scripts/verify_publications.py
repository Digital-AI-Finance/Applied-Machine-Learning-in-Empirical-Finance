"""
Verify Publications Data
Ensures publications.json only contains publications from authorized authors.
"""

import json
from pathlib import Path
from typing import List, Dict, Set


# Authorized authors for publications
AUTHORIZED_AUTHORS = {
    "Joerg Osterrieder",
    "Jorg Osterrieder",
    "J. Osterrieder",
    "Axel Gross-Klussmann",
    "Axel Groß-Klußmann",
    "Axel Grossklussmann",
    "A. Gross-Klussmann"
}


def load_publications(filepath: Path) -> Dict:
    """Load publications from JSON file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_team_authors(publication: Dict) -> List[str]:
    """Extract team_authors field from a publication."""
    return publication.get("team_authors", [])


def verify_publication_authors(publications: List[Dict]) -> Dict:
    """
    Verify all publications have at least one authorized author.

    Returns dict with:
        - valid: bool - True if all publications pass
        - total: int - Total publications checked
        - invalid: List[Dict] - List of invalid publications with details
    """
    invalid_pubs = []

    for pub in publications:
        team_authors = get_team_authors(pub)

        # Check if any team author is in authorized list
        is_valid = any(
            author in AUTHORIZED_AUTHORS
            for author in team_authors
        )

        if not is_valid:
            invalid_pubs.append({
                "id": pub.get("id"),
                "title": pub.get("title"),
                "team_authors": team_authors,
                "all_authors": [a.get("name") for a in pub.get("authors", [])]
            })

    return {
        "valid": len(invalid_pubs) == 0,
        "total": len(publications),
        "invalid_count": len(invalid_pubs),
        "invalid": invalid_pubs
    }


def format_apa_citation(pub: Dict) -> str:
    """
    Format a publication in APA 7th edition style.

    Format: Authors (Year). Title. Journal/Venue. DOI
    """
    # Authors
    authors = pub.get("authors", [])
    if not authors:
        author_str = "Unknown"
    elif len(authors) == 1:
        author_str = _format_author_apa(authors[0])
    elif len(authors) == 2:
        author_str = f"{_format_author_apa(authors[0])} & {_format_author_apa(authors[1])}"
    elif len(authors) <= 20:
        author_parts = [_format_author_apa(a) for a in authors[:-1]]
        author_str = ", ".join(author_parts) + f", & {_format_author_apa(authors[-1])}"
    else:
        # More than 20 authors: first 19, ..., last
        author_parts = [_format_author_apa(a) for a in authors[:19]]
        author_str = ", ".join(author_parts) + f", ... {_format_author_apa(authors[-1])}"

    # Year
    year = pub.get("year")
    year_str = f"({year})" if year else "(n.d.)"

    # Title
    title = pub.get("title", "Untitled")
    if title:
        # Sentence case for article titles
        title = title[0].upper() + title[1:].lower() if len(title) > 1 else title

    # Venue/Journal
    venue = pub.get("venue", "")
    venue_str = f" *{venue}*." if venue else ""

    # DOI
    doi = pub.get("doi")
    doi_str = f" https://doi.org/{doi}" if doi else ""

    return f"{author_str} {year_str}. {title}.{venue_str}{doi_str}"


def _format_author_apa(author: Dict) -> str:
    """Format a single author in APA style: Last, F. M."""
    name = author.get("name", "Unknown")
    parts = name.split()

    if len(parts) == 0:
        return "Unknown"
    elif len(parts) == 1:
        return parts[0]
    else:
        last_name = parts[-1]
        initials = " ".join(f"{p[0]}." for p in parts[:-1])
        return f"{last_name}, {initials}"


def generate_apa_citations(publications: List[Dict]) -> List[str]:
    """Generate APA citations for all publications."""
    return [format_apa_citation(pub) for pub in publications]


def main():
    """Main verification function."""
    print("=" * 60)
    print("Verifying Publications Data")
    print("=" * 60)

    # Paths
    script_dir = Path(__file__).parent
    pub_path = script_dir.parent / "data" / "publications.json"

    # Load data
    print(f"\nLoading: {pub_path}")
    data = load_publications(pub_path)
    publications = data.get("publications", [])

    print(f"Total publications: {len(publications)}")
    print(f"Authorized authors: {', '.join(AUTHORIZED_AUTHORS)}")

    # Verify
    result = verify_publication_authors(publications)

    print(f"\n{'=' * 60}")
    print("Verification Results")
    print("=" * 60)
    print(f"Publications checked: {result['total']}")
    print(f"Invalid publications: {result['invalid_count']}")
    print(f"Status: {'PASS' if result['valid'] else 'FAIL'}")

    if not result['valid']:
        print(f"\nInvalid publications:")
        for pub in result['invalid'][:10]:  # Show first 10
            print(f"  - {pub['title'][:60]}...")
            print(f"    Team authors: {pub['team_authors']}")

    # Sample APA citations
    print(f"\n{'=' * 60}")
    print("Sample APA Citations")
    print("=" * 60)
    for pub in publications[:3]:
        print(f"\n{format_apa_citation(pub)}")

    return result['valid']


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
