"""
Unit Tests for Publication Verification
"""

import unittest
import sys
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent))

from verify_publications import (
    AUTHORIZED_AUTHORS,
    get_team_authors,
    verify_publication_authors,
    format_apa_citation,
    _format_author_apa,
    generate_apa_citations
)


class TestAuthorizedAuthors(unittest.TestCase):
    """Test authorized authors list."""

    def test_joerg_variants_included(self):
        """Test all Joerg name variants are in authorized list."""
        self.assertIn("Joerg Osterrieder", AUTHORIZED_AUTHORS)
        self.assertIn("Jorg Osterrieder", AUTHORIZED_AUTHORS)
        self.assertIn("J. Osterrieder", AUTHORIZED_AUTHORS)

    def test_axel_variants_included(self):
        """Test all Axel name variants are in authorized list."""
        self.assertIn("Axel Gross-Klussmann", AUTHORIZED_AUTHORS)
        self.assertIn("Axel Grossklussmann", AUTHORIZED_AUTHORS)
        self.assertIn("A. Gross-Klussmann", AUTHORIZED_AUTHORS)

    def test_unauthorized_not_included(self):
        """Test unauthorized authors are not in list."""
        self.assertNotIn("Xiaohong Huang", AUTHORIZED_AUTHORS)
        self.assertNotIn("Dennis Hoffmann", AUTHORIZED_AUTHORS)
        self.assertNotIn("Random Author", AUTHORIZED_AUTHORS)


class TestGetTeamAuthors(unittest.TestCase):
    """Test team authors extraction."""

    def test_with_team_authors(self):
        """Test extraction when team_authors field exists."""
        pub = {"team_authors": ["Joerg Osterrieder"]}
        self.assertEqual(get_team_authors(pub), ["Joerg Osterrieder"])

    def test_without_team_authors(self):
        """Test extraction when team_authors field missing."""
        pub = {"title": "Test"}
        self.assertEqual(get_team_authors(pub), [])

    def test_empty_team_authors(self):
        """Test extraction with empty team_authors."""
        pub = {"team_authors": []}
        self.assertEqual(get_team_authors(pub), [])


class TestVerifyPublicationAuthors(unittest.TestCase):
    """Test publication verification."""

    def test_valid_single_pub_joerg(self):
        """Test verification passes with Joerg as author."""
        pubs = [{"team_authors": ["Joerg Osterrieder"], "title": "Test"}]
        result = verify_publication_authors(pubs)
        self.assertTrue(result["valid"])
        self.assertEqual(result["total"], 1)
        self.assertEqual(result["invalid_count"], 0)

    def test_valid_single_pub_axel(self):
        """Test verification passes with Axel as author."""
        pubs = [{"team_authors": ["Axel Gross-Klussmann"], "title": "Test"}]
        result = verify_publication_authors(pubs)
        self.assertTrue(result["valid"])

    def test_invalid_unauthorized_author(self):
        """Test verification fails with unauthorized author."""
        pubs = [{"team_authors": ["Xiaohong Huang"], "title": "Test"}]
        result = verify_publication_authors(pubs)
        self.assertFalse(result["valid"])
        self.assertEqual(result["invalid_count"], 1)

    def test_invalid_no_team_authors(self):
        """Test verification fails with no team_authors."""
        pubs = [{"title": "Test"}]
        result = verify_publication_authors(pubs)
        self.assertFalse(result["valid"])

    def test_mixed_valid_invalid(self):
        """Test with mix of valid and invalid publications."""
        pubs = [
            {"team_authors": ["Joerg Osterrieder"], "title": "Valid"},
            {"team_authors": ["Unknown Author"], "title": "Invalid"}
        ]
        result = verify_publication_authors(pubs)
        self.assertFalse(result["valid"])
        self.assertEqual(result["total"], 2)
        self.assertEqual(result["invalid_count"], 1)

    def test_empty_publications_list(self):
        """Test with empty publications list."""
        result = verify_publication_authors([])
        self.assertTrue(result["valid"])
        self.assertEqual(result["total"], 0)


class TestFormatAuthorAPA(unittest.TestCase):
    """Test APA author formatting."""

    def test_single_name(self):
        """Test formatting single name."""
        author = {"name": "Cher"}
        self.assertEqual(_format_author_apa(author), "Cher")

    def test_two_part_name(self):
        """Test formatting first last name."""
        author = {"name": "John Smith"}
        self.assertEqual(_format_author_apa(author), "Smith, J.")

    def test_three_part_name(self):
        """Test formatting first middle last name."""
        author = {"name": "John Michael Smith"}
        self.assertEqual(_format_author_apa(author), "Smith, J. M.")

    def test_empty_name(self):
        """Test formatting empty name."""
        author = {"name": ""}
        result = _format_author_apa(author)
        self.assertEqual(result, "Unknown")

    def test_missing_name(self):
        """Test formatting missing name field."""
        author = {}
        self.assertEqual(_format_author_apa(author), "Unknown")


class TestFormatAPACitation(unittest.TestCase):
    """Test full APA citation formatting."""

    def test_complete_citation(self):
        """Test citation with all fields."""
        pub = {
            "authors": [{"name": "John Smith"}],
            "year": 2024,
            "title": "A Test Paper",
            "venue": "Test Journal",
            "doi": "10.1234/test"
        }
        citation = format_apa_citation(pub)
        self.assertIn("Smith, J.", citation)
        self.assertIn("(2024)", citation)
        self.assertIn("A test paper", citation)
        self.assertIn("*Test Journal*", citation)
        self.assertIn("https://doi.org/10.1234/test", citation)

    def test_citation_no_doi(self):
        """Test citation without DOI."""
        pub = {
            "authors": [{"name": "John Smith"}],
            "year": 2024,
            "title": "Test Paper"
        }
        citation = format_apa_citation(pub)
        self.assertNotIn("doi.org", citation)

    def test_citation_no_year(self):
        """Test citation without year."""
        pub = {
            "authors": [{"name": "John Smith"}],
            "title": "Test Paper"
        }
        citation = format_apa_citation(pub)
        self.assertIn("(n.d.)", citation)

    def test_citation_two_authors(self):
        """Test citation with two authors."""
        pub = {
            "authors": [
                {"name": "John Smith"},
                {"name": "Jane Doe"}
            ],
            "year": 2024,
            "title": "Test"
        }
        citation = format_apa_citation(pub)
        self.assertIn("Smith, J. & Doe, J.", citation)

    def test_citation_three_authors(self):
        """Test citation with three authors."""
        pub = {
            "authors": [
                {"name": "John Smith"},
                {"name": "Jane Doe"},
                {"name": "Bob Jones"}
            ],
            "year": 2024,
            "title": "Test"
        }
        citation = format_apa_citation(pub)
        self.assertIn("Smith, J., Doe, J., & Jones, B.", citation)


class TestGenerateAPACitations(unittest.TestCase):
    """Test batch APA citation generation."""

    def test_generate_multiple(self):
        """Test generating multiple citations."""
        pubs = [
            {"authors": [{"name": "A B"}], "year": 2024, "title": "First"},
            {"authors": [{"name": "C D"}], "year": 2023, "title": "Second"}
        ]
        citations = generate_apa_citations(pubs)
        self.assertEqual(len(citations), 2)

    def test_generate_empty_list(self):
        """Test generating from empty list."""
        citations = generate_apa_citations([])
        self.assertEqual(citations, [])


class TestIntegration(unittest.TestCase):
    """Integration tests with actual data."""

    def test_load_and_verify_publications(self):
        """Test loading actual publications.json and verifying."""
        from verify_publications import load_publications, verify_publication_authors

        pub_path = Path(__file__).parent.parent / "data" / "publications.json"

        if pub_path.exists():
            data = load_publications(pub_path)
            publications = data.get("publications", [])
            result = verify_publication_authors(publications)

            # All publications should now be from authorized authors
            self.assertTrue(
                result["valid"],
                f"Found {result['invalid_count']} unauthorized publications"
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
