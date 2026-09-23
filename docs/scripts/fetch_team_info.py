"""
Fetch Team Member Information from OpenAlex API
Retrieves ORCID IDs, publication metrics, and affiliations for project team members.
"""

import requests
import json
from pathlib import Path
import time

# OpenAlex API configuration
OPENALEX_BASE = "https://api.openalex.org"
EMAIL = "dennis.hoffmann@utwente.nl"  # For polite pool access

# Team members to search
TEAM_MEMBERS = [
    {
        "name": "Joerg Osterrieder",
        "search_terms": ["Joerg Osterrieder", "Jorg Osterrieder", "J. Osterrieder"],
        "openalex_id": "A5032430973",
        "role": "Primary Supervisor",
        "affiliation": "University of Twente",
        "department": "Financial Engineering & Business Information Systems (FEBIS)",
        "google_scholar_id": "ocRaXoIAAAAJ"
    },
    {
        "name": "Xiaohong Huang",
        "search_terms": ["Xiaohong Huang"],
        "openalex_id": "A5101539394",
        "orcid": "0000-0003-0532-2773",
        "role": "Co-Supervisor",
        "affiliation": "University of Twente",
        "department": "Financial Engineering & Business Information Systems (FEBIS)",
        "google_scholar_id": "Z7p5XyIAAAAJ",
        # Override: OpenAlex A5101539394 merged with a different Xiaohong Huang
        # (Northeastern Univ CN). Using Google Scholar as authoritative source.
        # Last verified: 2026-04-02
        # TODO: Remove override after OpenAlex disambiguation fix
        "metrics_override": {
            "works_count": 34,
            "cited_by_count": 470,
            "h_index": 8,
            "affiliations": [{"name": "University of Twente", "country": "NL"}],
        },
    },
    {
        "name": "Axel Gross-Klussmann",
        "search_terms": ["Axel Gross-Klussmann", "Axel Groß-Klußmann", "A. Gross-Klussmann"],
        "openalex_id": "A5049079953",
        "orcid": "0000-0003-0541-9428",
        "role": "Industry Supervisor",
        "affiliation": "Quoniam Asset Management",
        "department": "Quantitative Research",
        "google_scholar_id": "x_lUAskAAAAJ"
    },
    {
        "name": "Dennis Hoffmann",
        "search_terms": ["Dennis Hoffmann"],
        "openalex_id": None,
        "orcid": "0009-0007-4623-555X",
        "role": "PhD Researcher",
        "affiliation": "Quoniam Asset Management / University of Twente",
        "department": "Industry PhD"
    }
]


def fetch_author_by_id(openalex_id: str) -> dict | None:
    """Fetch an author directly by OpenAlex ID."""
    url = f"{OPENALEX_BASE}/authors/{openalex_id}"
    params = {"mailto": EMAIL}
    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"  Error fetching author {openalex_id}: {e}")
        return None


def search_author(search_terms: list) -> dict | None:
    """Search for an author in OpenAlex using multiple search terms."""

    for term in search_terms:
        url = f"{OPENALEX_BASE}/authors"
        params = {
            "search": term,
            "mailto": EMAIL
        }

        try:
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            data = response.json()

            if data.get("results") and len(data["results"]) > 0:
                # Return the first (most relevant) result
                author = data["results"][0]

                # Verify it's a reasonable match by checking works count
                if author.get("works_count", 0) >= 1:
                    return author

        except requests.RequestException as e:
            print(f"  Error searching for '{term}': {e}")

        time.sleep(0.5)  # Rate limiting

    return None


def extract_author_info(author_data: dict) -> dict:
    """Extract relevant information from OpenAlex author response."""

    # Get ORCID if available
    orcid = None
    if author_data.get("orcid"):
        orcid = author_data["orcid"].replace("https://orcid.org/", "")

    # Get affiliations
    affiliations = []
    if author_data.get("affiliations"):
        for aff in author_data["affiliations"][:3]:  # Top 3 affiliations
            if aff.get("institution"):
                affiliations.append({
                    "name": aff["institution"].get("display_name", ""),
                    "country": aff["institution"].get("country_code", "")
                })

    # Get citation metrics
    cited_by_count = author_data.get("cited_by_count", 0)
    works_count = author_data.get("works_count", 0)

    # Calculate h-index from summary stats if available
    h_index = None
    if author_data.get("summary_stats"):
        h_index = author_data["summary_stats"].get("h_index")

    # Get recent works count
    counts_by_year = author_data.get("counts_by_year", [])
    recent_works = sum(c.get("works_count", 0) for c in counts_by_year[:3])  # Last 3 years

    return {
        "openalex_id": author_data.get("id", ""),
        "display_name": author_data.get("display_name", ""),
        "orcid": orcid,
        "works_count": works_count,
        "cited_by_count": cited_by_count,
        "h_index": h_index,
        "recent_works_3yr": recent_works,
        "affiliations": affiliations,
        "works_api_url": author_data.get("works_api_url", "")
    }


def fetch_team_info() -> list:
    """Fetch information for all team members."""

    team_info = []

    for member in TEAM_MEMBERS:
        print(f"\nSearching for: {member['name']}")

        author_data = None

        # Use known OpenAlex ID if available, skip search if explicitly None
        if "openalex_id" in member:
            if member["openalex_id"]:
                print(f"  Using known OpenAlex ID: {member['openalex_id']}")
                author_data = fetch_author_by_id(member["openalex_id"])
            else:
                print(f"  No OpenAlex profile configured (skipping search)")
        else:
            author_data = search_author(member["search_terms"])

        if author_data:
            info = extract_author_info(author_data)

            # Override ORCID from config if provided
            if member.get("orcid"):
                info["orcid"] = member["orcid"]

            # Apply metrics overrides (e.g., when OpenAlex has profile contamination)
            if member.get("metrics_override"):
                for key, value in member["metrics_override"].items():
                    info[key] = value

            # Merge with predefined member info
            member_info = {
                **member,
                "openalex": info
            }

            print(f"  Found: {info['display_name']}")
            print(f"  ORCID: {info['orcid'] or 'Not found'}")
            print(f"  Works: {info['works_count']}, Citations: {info['cited_by_count']}")
            if info['h_index']:
                print(f"  H-index: {info['h_index']}")
        else:
            print(f"  Not found in OpenAlex")
            member_info = {
                **member,
                "openalex": None
            }

            # Still set ORCID from config if available even without OpenAlex data
            if member.get("orcid"):
                member_info["openalex"] = {
                    "openalex_id": None,
                    "display_name": member["name"],
                    "orcid": member["orcid"],
                    "works_count": 0,
                    "cited_by_count": 0,
                    "h_index": None,
                    "recent_works_3yr": 0,
                    "affiliations": [],
                    "works_api_url": None
                }
                print(f"  ORCID (from config): {member['orcid']}")

        team_info.append(member_info)
        time.sleep(1)  # Rate limiting between members

    return team_info


def save_team_info(team_info: list, output_path: Path):
    """Save team information to JSON file."""

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "project": "Applied Machine Learning in Empirical Finance",
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "team": team_info
        }, f, indent=2, ensure_ascii=False)

    print(f"\nTeam info saved to: {output_path}")


def main():
    """Main function to fetch and save team information."""

    print("=" * 60)
    print("Fetching Team Member Information from OpenAlex")
    print("=" * 60)

    # Determine output path
    script_dir = Path(__file__).parent
    output_path = script_dir.parent / "data" / "team.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Fetch team info
    team_info = fetch_team_info()

    # Save to JSON
    save_team_info(team_info, output_path)

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    found_count = sum(1 for m in team_info if m.get("openalex"))
    print(f"Team members found in OpenAlex: {found_count}/{len(team_info)}")

    for member in team_info:
        status = "Found" if member.get("openalex") else "Not found"
        orcid = member.get("openalex", {}).get("orcid", "N/A") if member.get("openalex") else "N/A"
        print(f"  - {member['name']}: {status} (ORCID: {orcid})")


if __name__ == "__main__":
    main()
