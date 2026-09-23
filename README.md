# Applied Machine Learning in Empirical Finance

Project website of the industry–university PhD project *Applied Machine Learning in Empirical Finance* (University of Twente).

## Structure

| Path | Content |
|---|---|
| `docs/` | Website: HTML pages, `css/`, `js/`, `data/` (JSON), `assets/images/` |
| `docs/scripts/` | Python helpers that refresh `docs/data/` from OpenAlex and check links/publications |

## Local preview

    python3 -m http.server 8000 --directory docs

Then open <http://localhost:8000/>.

## Refresh data (network access to OpenAlex)

Requires `requests`. Run from the repository root, in this order:

    python docs/scripts/fetch_team_info.py
    python docs/scripts/fetch_openalex.py
    python docs/scripts/analyze_research_gaps.py
    python docs/scripts/verify_publications.py

The wiki section will be added in a later step.
