"""
Fetch Publications from OpenAlex API
Retrieves publications for team members and filters by relevance to ML + Finance.
"""

import requests
import json
from pathlib import Path
import time
from typing import Optional

# OpenAlex API configuration
OPENALEX_BASE = "https://api.openalex.org"
EMAIL = "dennis.hoffmann@utwente.nl"  # For polite pool access

# Relevant topics/concepts for filtering
ML_FINANCE_CONCEPTS = [
    "machine learning",
    "deep learning",
    "neural network",
    "reinforcement learning",
    "portfolio",
    "risk management",
    "asset allocation",
    "financial",
    "trading",
    "quantitative finance",
    "volatility",
    "forecasting",
    "prediction",
    "time series",
    "stock",
    "market"
]


def load_team_info(team_json_path: Path) -> list:
    """Load team info from JSON file."""

    if not team_json_path.exists():
        print(f"Warning: Team info file not found at {team_json_path}")
        return []

    with open(team_json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
        return data.get("team", [])


def fetch_author_works(author_id: str, per_page: int = 200) -> list:
    """Fetch all works for an author from OpenAlex."""

    works = []
    cursor = "*"

    while cursor:
        url = f"{OPENALEX_BASE}/works"
        params = {
            "filter": f"author.id:{author_id}",
            "per_page": per_page,
            "cursor": cursor,
            "mailto": EMAIL,
            "sort": "publication_year:desc"
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            results = data.get("results", [])
            works.extend(results)

            # Get next cursor
            meta = data.get("meta", {})
            cursor = meta.get("next_cursor")

            print(f"    Fetched {len(works)} works...")

        except requests.RequestException as e:
            print(f"    Error fetching works: {e}")
            break

        time.sleep(0.5)  # Rate limiting

    return works


def is_ml_finance_relevant(work: dict) -> bool:
    """Check if a work is relevant to ML + Finance based on title and abstract."""

    title = (work.get("title") or "").lower()
    abstract = ""

    # Get abstract from inverted index if available
    abstract_index = work.get("abstract_inverted_index")
    if abstract_index:
        # Reconstruct abstract from inverted index
        word_positions = []
        for word, positions in abstract_index.items():
            for pos in positions:
                word_positions.append((pos, word))
        word_positions.sort()
        abstract = " ".join(word for _, word in word_positions).lower()

    # Also check concepts
    concepts = [c.get("display_name", "").lower() for c in work.get("concepts", [])]
    concepts_text = " ".join(concepts)

    combined_text = f"{title} {abstract} {concepts_text}"

    # Count matching keywords
    matches = sum(1 for kw in ML_FINANCE_CONCEPTS if kw in combined_text)

    # Require at least 2 matching keywords for relevance
    return matches >= 2


def extract_work_info(work: dict) -> dict:
    """Extract relevant information from an OpenAlex work."""

    # Get DOI
    doi = work.get("doi", "")
    if doi and doi.startswith("https://doi.org/"):
        doi = doi.replace("https://doi.org/", "")

    # Get authors
    authors = []
    for authorship in work.get("authorships", [])[:10]:  # Limit to 10 authors
        author = authorship.get("author", {})
        authors.append({
            "name": author.get("display_name", ""),
            "orcid": (author.get("orcid") or "").replace("https://orcid.org/", "")
        })

    # Get venue/source
    primary_location = work.get("primary_location") or {}
    source = primary_location.get("source") or {}
    venue = source.get("display_name", "")

    # Check if open access
    open_access = work.get("open_access", {})
    is_oa = open_access.get("is_oa", False)
    oa_url = open_access.get("oa_url", "")

    # Get concepts (top 5)
    concepts = [c.get("display_name", "") for c in work.get("concepts", [])[:5]]

    return {
        "id": work.get("id", ""),
        "title": work.get("title", ""),
        "year": work.get("publication_year"),
        "doi": doi,
        "authors": authors,
        "venue": venue,
        "type": work.get("type", ""),
        "cited_by_count": work.get("cited_by_count", 0),
        "is_open_access": is_oa,
        "oa_url": oa_url,
        "concepts": concepts
    }


def fetch_all_publications(team_info: list) -> list:
    """Fetch publications for all team members."""

    all_publications = []
    seen_ids = set()

    # Only include publications from Joerg Osterrieder and Axel Gross-Klussmann
    INCLUDED_AUTHORS = ["Joerg Osterrieder", "Axel Gross-Klussmann"]

    for member in team_info:
        # Filter to only include specified authors
        if member.get("name") not in INCLUDED_AUTHORS:
            print(f"\nSkipping: {member['name']} (not in publication authors list)")
            continue

        if not member.get("openalex"):
            print(f"\nNo OpenAlex profile for: {member['name']}")
            continue

        author_id = member["openalex"].get("openalex_id")
        if not author_id:
            continue

        print(f"\nFetching publications for: {member['name']}")
        print(f"  OpenAlex ID: {author_id}")

        works = fetch_author_works(author_id)
        print(f"  Total works found: {len(works)}")

        # Filter for ML + Finance relevance and add to list
        relevant_count = 0
        for work in works:
            work_id = work.get("id")
            if work_id in seen_ids:
                continue

            if is_ml_finance_relevant(work):
                pub_info = extract_work_info(work)
                pub_info["team_authors"] = [member["name"]]
                all_publications.append(pub_info)
                seen_ids.add(work_id)
                relevant_count += 1
            else:
                # Still add non-filtered works but mark them
                pub_info = extract_work_info(work)
                pub_info["team_authors"] = [member["name"]]
                pub_info["ml_finance_relevant"] = False
                all_publications.append(pub_info)
                seen_ids.add(work_id)

        print(f"  ML+Finance relevant: {relevant_count}")

        time.sleep(1)  # Rate limiting between authors

    return all_publications


def generate_statistics(publications: list) -> dict:
    """Generate publication statistics."""

    # Filter to relevant publications
    relevant = [p for p in publications if p.get("ml_finance_relevant", True)]

    # Count by year
    by_year = {}
    for pub in relevant:
        year = pub.get("year")
        if year:
            by_year[year] = by_year.get(year, 0) + 1

    # Total citations
    total_citations = sum(p.get("cited_by_count", 0) for p in relevant)

    # Top cited
    top_cited = sorted(relevant, key=lambda x: x.get("cited_by_count", 0), reverse=True)[:10]

    # Recent publications (last 3 years)
    current_year = 2025
    recent = [p for p in relevant if p.get("year") and p["year"] >= current_year - 2]

    return {
        "total_publications": len(relevant),
        "total_all_publications": len(publications),
        "total_citations": total_citations,
        "by_year": dict(sorted(by_year.items())),
        "recent_count": len(recent),
        "top_cited": [
            {"title": p["title"], "year": p["year"], "citations": p["cited_by_count"]}
            for p in top_cited
        ]
    }


def save_publications(publications: list, stats: dict, output_path: Path):
    """Save publications to JSON file."""

    # Sort by year descending, then by citations
    publications.sort(key=lambda x: (-(x.get("year") or 0), -(x.get("cited_by_count") or 0)))

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "project": "Applied Machine Learning in Empirical Finance",
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "statistics": stats,
            "publications": publications
        }, f, indent=2, ensure_ascii=False)

    print(f"\nPublications saved to: {output_path}")


def main():
    """Main function to fetch and save publications."""

    print("=" * 60)
    print("Fetching Publications from OpenAlex")
    print("=" * 60)

    # Paths
    script_dir = Path(__file__).parent
    team_json_path = script_dir.parent / "data" / "team.json"
    output_path = script_dir.parent / "data" / "publications.json"

    # Load team info
    print(f"\nLoading team info from: {team_json_path}")
    team_info = load_team_info(team_json_path)

    if not team_info:
        print("No team info found. Please run fetch_team_info.py first.")
        return

    # Fetch publications
    publications = fetch_all_publications(team_info)

    # Generate statistics
    stats = generate_statistics(publications)

    # Save to JSON
    save_publications(publications, stats, output_path)

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Total publications: {stats['total_all_publications']}")
    print(f"ML+Finance relevant: {stats['total_publications']}")
    print(f"Total citations: {stats['total_citations']}")
    print(f"Recent (last 3 years): {stats['recent_count']}")

    print("\nTop cited publications:")
    for i, pub in enumerate(stats['top_cited'][:5], 1):
        print(f"  {i}. [{pub['year']}] {pub['title'][:60]}... ({pub['citations']} citations)")


if __name__ == "__main__":
    main()
