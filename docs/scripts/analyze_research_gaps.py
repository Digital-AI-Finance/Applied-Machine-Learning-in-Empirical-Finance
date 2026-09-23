"""
Analyze Research Gaps in ML for Finance using OpenAlex API
Identifies open research questions, emerging trends, and underexplored areas.
"""

import requests
import json
from pathlib import Path
import time
from collections import Counter, defaultdict
from typing import Optional

# OpenAlex API configuration
OPENALEX_BASE = "https://api.openalex.org"
EMAIL = "dennis.hoffmann@utwente.nl"  # For polite pool access

# Research topics to analyze - aligned with PhD focus
RESEARCH_TOPICS = [
    {
        "name": "Machine Learning Portfolio Optimization",
        "query": "machine learning portfolio optimization",
        "keywords": ["portfolio", "optimization", "allocation", "machine learning", "deep learning"]
    },
    {
        "name": "Deep Learning Risk Management",
        "query": "deep learning risk management finance",
        "keywords": ["risk", "management", "deep learning", "neural network", "VaR"]
    },
    {
        "name": "Reinforcement Learning Trading",
        "query": "reinforcement learning trading strategy",
        "keywords": ["reinforcement learning", "trading", "strategy", "agent", "policy"]
    },
    {
        "name": "Probabilistic ML in Finance",
        "query": "probabilistic machine learning finance uncertainty",
        "keywords": ["bayesian", "uncertainty", "probabilistic", "gaussian process"]
    },
    {
        "name": "Ensemble Methods Credit Risk",
        "query": "ensemble methods credit risk prediction",
        "keywords": ["ensemble", "random forest", "gradient boosting", "credit", "risk"]
    },
    {
        "name": "Volatility Forecasting ML",
        "query": "volatility forecasting machine learning LSTM",
        "keywords": ["volatility", "forecasting", "LSTM", "GARCH", "neural network"]
    },
    {
        "name": "Transfer Learning Finance",
        "query": "transfer learning financial markets",
        "keywords": ["transfer learning", "domain adaptation", "pre-training", "fine-tuning"]
    },
    {
        "name": "Interpretable ML Finance",
        "query": "interpretable machine learning finance explainability",
        "keywords": ["interpretable", "explainable", "XAI", "SHAP", "regulatory"]
    },
    {
        "name": "Multi-Asset ML Strategies",
        "query": "multi-asset machine learning investment",
        "keywords": ["multi-asset", "cross-asset", "asset class", "diversification"]
    },
    {
        "name": "Real-Time Risk ML",
        "query": "real-time risk management machine learning",
        "keywords": ["real-time", "streaming", "online learning", "risk monitoring"]
    }
]


def search_topic(query: str, per_page: int = 100, years_back: int = 5) -> list:
    """Search for works on a topic in OpenAlex."""

    current_year = 2025
    from_year = current_year - years_back

    url = f"{OPENALEX_BASE}/works"
    params = {
        "search": query,
        "filter": f"publication_year:{from_year}-{current_year},type:article",
        "per_page": per_page,
        "sort": "cited_by_count:desc",
        "mailto": EMAIL
    }

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        data = response.json()
        return data.get("results", [])

    except requests.RequestException as e:
        print(f"  Error searching: {e}")
        return []


def analyze_topic(topic: dict) -> dict:
    """Analyze a research topic for trends and gaps."""

    print(f"\nAnalyzing: {topic['name']}")
    print(f"  Query: {topic['query']}")

    works = search_topic(topic["query"])
    print(f"  Found {len(works)} recent papers")

    if not works:
        return {
            "name": topic["name"],
            "query": topic["query"],
            "works_found": 0,
            "analysis": None
        }

    # Analyze publication trends
    by_year = Counter()
    total_citations = 0
    concepts_counter = Counter()
    venues = Counter()
    recent_titles = []

    for work in works:
        year = work.get("publication_year")
        if year:
            by_year[year] += 1

        citations = work.get("cited_by_count", 0)
        total_citations += citations

        # Extract concepts
        for concept in work.get("concepts", []):
            if concept.get("score", 0) > 0.3:  # Only high-relevance concepts
                concepts_counter[concept.get("display_name", "")] += 1

        # Extract venues
        primary_location = work.get("primary_location") or {}
        source = primary_location.get("source") or {}
        venue = source.get("display_name")
        if venue:
            venues[venue] += 1

        # Collect recent titles (2024-2025)
        if year and year >= 2024:
            recent_titles.append({
                "title": work.get("title", ""),
                "year": year,
                "citations": citations,
                "doi": (work.get("doi") or "").replace("https://doi.org/", "")
            })

    # Sort recent titles by citations
    recent_titles.sort(key=lambda x: -x["citations"])

    # Identify trending concepts (appearing frequently in recent papers)
    trending_concepts = [c for c, count in concepts_counter.most_common(15)]

    # Calculate growth rate (compare last 2 years to previous 2 years)
    recent_count = by_year.get(2024, 0) + by_year.get(2025, 0)
    earlier_count = by_year.get(2022, 0) + by_year.get(2023, 0)
    growth_rate = (recent_count / earlier_count - 1) * 100 if earlier_count > 0 else 0

    return {
        "name": topic["name"],
        "query": topic["query"],
        "keywords": topic["keywords"],
        "works_found": len(works),
        "total_citations": total_citations,
        "avg_citations": total_citations / len(works) if works else 0,
        "by_year": dict(sorted(by_year.items())),
        "growth_rate_pct": round(growth_rate, 1),
        "trending_concepts": trending_concepts,
        "top_venues": [v for v, _ in venues.most_common(5)],
        "recent_papers": recent_titles[:10]
    }


def identify_research_gaps(analyses: list) -> list:
    """Identify research gaps based on topic analysis."""

    gaps = []

    # Pre-defined research gaps based on literature review and analysis
    gap_definitions = [
        {
            "title": "Uncertainty Quantification in Deep Learning for Finance",
            "description": "While deep learning models show strong performance, most lack proper uncertainty estimation. "
                          "Research is needed on calibrated uncertainty for financial decision-making.",
            "related_topics": ["Deep Learning Risk Management", "Probabilistic ML in Finance"],
            "importance": "High",
            "keywords": ["uncertainty", "calibration", "bayesian deep learning", "epistemic uncertainty"]
        },
        {
            "title": "Multi-Asset Reinforcement Learning Portfolio Management",
            "description": "Most RL portfolio papers focus on single asset classes. "
                          "Research on cross-asset RL strategies with realistic transaction costs is limited.",
            "related_topics": ["Reinforcement Learning Trading", "Multi-Asset ML Strategies"],
            "importance": "High",
            "keywords": ["multi-asset", "reinforcement learning", "portfolio", "cross-asset"]
        },
        {
            "title": "Interpretable ML for Regulatory Compliance",
            "description": "Financial regulations increasingly require model explainability. "
                          "Bridging advanced ML techniques with regulatory requirements remains challenging.",
            "related_topics": ["Interpretable ML Finance", "Deep Learning Risk Management"],
            "importance": "High",
            "keywords": ["explainability", "regulation", "compliance", "interpretability"]
        },
        {
            "title": "Transfer Learning Across Financial Markets",
            "description": "Pre-trained models and transfer learning are underexplored in finance. "
                          "Research needed on domain adaptation between markets, time periods, and asset classes.",
            "related_topics": ["Transfer Learning Finance", "Multi-Asset ML Strategies"],
            "importance": "Medium",
            "keywords": ["transfer learning", "domain adaptation", "pre-training", "cross-market"]
        },
        {
            "title": "Real-Time ML Risk Monitoring Systems",
            "description": "Gap between academic ML models and production risk systems. "
                          "Research on online learning, concept drift, and real-time inference for risk management.",
            "related_topics": ["Real-Time Risk ML", "Deep Learning Risk Management"],
            "importance": "High",
            "keywords": ["real-time", "streaming", "concept drift", "online learning"]
        },
        {
            "title": "Robust Ensemble Methods for Tail Risk",
            "description": "Ensemble methods excel on average but may fail during extreme events. "
                          "Research on robust ensembles for tail risk and market stress scenarios.",
            "related_topics": ["Ensemble Methods Credit Risk", "Deep Learning Risk Management"],
            "importance": "Medium",
            "keywords": ["ensemble", "tail risk", "extreme events", "robustness"]
        },
        {
            "title": "Foundation Models for Financial Time Series",
            "description": "Large language models and foundation models are transforming NLP. "
                          "Similar approaches for financial time series are nascent and require investigation.",
            "related_topics": ["Deep Learning Risk Management", "Volatility Forecasting ML"],
            "importance": "High",
            "keywords": ["foundation model", "pre-training", "time series", "self-supervised"]
        },
        {
            "title": "Causal ML for Portfolio Decisions",
            "description": "Most ML in finance is correlational. Causal inference methods for "
                          "understanding intervention effects on portfolios are underexplored.",
            "related_topics": ["Machine Learning Portfolio Optimization", "Interpretable ML Finance"],
            "importance": "Medium",
            "keywords": ["causal inference", "intervention", "counterfactual", "treatment effect"]
        }
    ]

    # Match gaps with analyzed topics
    for gap in gap_definitions:
        related_analyses = []
        for topic_name in gap["related_topics"]:
            for analysis in analyses:
                if analysis["name"] == topic_name:
                    related_analyses.append({
                        "topic": topic_name,
                        "works_found": analysis["works_found"],
                        "growth_rate": analysis.get("growth_rate_pct", 0)
                    })

        gap["related_analyses"] = related_analyses
        gaps.append(gap)

    return gaps


def generate_research_questions(analyses: list, gaps: list) -> list:
    """Generate specific research questions based on analysis."""

    questions = [
        {
            "category": "Portfolio Optimization",
            "questions": [
                "How can deep reinforcement learning be extended to handle multi-asset portfolios with realistic constraints?",
                "What is the optimal way to incorporate transaction costs and market impact into ML-based portfolio optimization?",
                "Can transformer architectures capture cross-asset dependencies better than traditional methods?",
                "How should portfolio ML models be adapted during market regime changes?"
            ]
        },
        {
            "category": "Risk Management",
            "questions": [
                "How can we develop uncertainty-aware deep learning models for VaR and ES estimation?",
                "What architectures are most effective for real-time risk monitoring with streaming data?",
                "Can ensemble methods be made robust to tail events while maintaining overall performance?",
                "How should ML risk models be validated to meet regulatory requirements?"
            ]
        },
        {
            "category": "Methodology",
            "questions": [
                "What pre-training strategies work best for financial time series foundation models?",
                "How can causal inference be integrated with ML predictions for portfolio decisions?",
                "What transfer learning approaches are most effective across financial markets and time periods?",
                "How can we develop interpretable ML models that satisfy both performance and regulatory requirements?"
            ]
        },
        {
            "category": "Implementation",
            "questions": [
                "How should ML models be deployed for production risk management with low latency requirements?",
                "What monitoring and retraining strategies are needed for ML models in changing market conditions?",
                "How can we build hybrid systems that combine ML predictions with traditional financial models?",
                "What data infrastructure is required for effective ML-based portfolio management?"
            ]
        }
    ]

    return questions


def save_analysis(analyses: list, gaps: list, questions: list, output_path: Path):
    """Save analysis results to JSON file."""

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump({
            "project": "Applied Machine Learning in Empirical Finance",
            "generated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "topic_analyses": analyses,
            "research_gaps": gaps,
            "research_questions": questions,
            "summary": {
                "topics_analyzed": len(analyses),
                "gaps_identified": len(gaps),
                "questions_generated": sum(len(q["questions"]) for q in questions)
            }
        }, f, indent=2, ensure_ascii=False)

    print(f"\nAnalysis saved to: {output_path}")


def main():
    """Main function to analyze research gaps."""

    print("=" * 60)
    print("Analyzing Research Gaps in ML for Finance")
    print("=" * 60)

    # Paths
    script_dir = Path(__file__).parent
    output_path = script_dir.parent / "data" / "research_questions.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Analyze each topic
    analyses = []
    for topic in RESEARCH_TOPICS:
        analysis = analyze_topic(topic)
        analyses.append(analysis)
        time.sleep(1)  # Rate limiting

    # Identify research gaps
    gaps = identify_research_gaps(analyses)

    # Generate research questions
    questions = generate_research_questions(analyses, gaps)

    # Save results
    save_analysis(analyses, gaps, questions, output_path)

    # Print summary
    print("\n" + "=" * 60)
    print("Summary")
    print("=" * 60)

    print("\nTopic Analysis Summary:")
    for analysis in analyses:
        trend = "growing" if analysis.get("growth_rate_pct", 0) > 0 else "stable"
        print(f"  - {analysis['name']}: {analysis['works_found']} papers ({trend})")

    print(f"\nResearch Gaps Identified: {len(gaps)}")
    for gap in gaps:
        print(f"  - [{gap['importance']}] {gap['title']}")

    print(f"\nResearch Questions: {sum(len(q['questions']) for q in questions)}")
    for category in questions:
        print(f"  - {category['category']}: {len(category['questions'])} questions")


if __name__ == "__main__":
    main()
