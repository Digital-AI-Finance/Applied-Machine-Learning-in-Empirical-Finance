# Research resources

Tools and dataset sources to facilitate research.

Each tool is maintained in its own repository. This separation is intended to make the tools easier to discover and reuse, and to provide a focused place for community contributions.

## Tools

| Tool | Purpose |
| --- | --- |
| [SEC 10-K Item 1A Risk Factor Extractor](https://github.com/HoffmannDennis/edgar-10k-item1a) | Extracts Item 1A risk-factor sections from SEC Form 10-K filings, using local files or optional SEC downloads. Results include source information, extraction boundaries and hashes. |
| [LaTeX Claim & Bibliography Checker](https://github.com/HoffmannDennis/latex-claim-and-bib-checker) | Checks LaTeX citation consistency and bibliography metadata, and uses a language model to assess whether cited abstracts support citing sentences. |

The checker's claim assessments are based on abstracts, not full texts. They are a verification aid and require human review.

## Data collection

Datasets and data providers listed in the [website's dataset catalog](../docs/data/resources.json). Check each provider's current access and reuse conditions; inclusion here does not imply unrestricted use or redistribution.

### Asset Pricing & Factors

- [Kenneth French Data Library](https://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html)
- [AQR Data Library](https://www.aqr.com/Insights/Datasets)
- [Global Factor Library (JKP)](https://jkpfactors.com/) ([code](https://github.com/bkelly-lab/jkp-data))
- [Open Source Asset Pricing (Chen & Zimmermann)](https://www.openassetpricing.com/data/) ([code](https://github.com/OpenSourceAP/CrossSection))
- [Currency Factors](https://www.currencyfactors.com/currency-data)

### Market Data

- [Yahoo Finance](https://finance.yahoo.com/)
- [Binance Historical Data](https://data.binance.vision/)
- [Dukascopy Historical Data](https://www.dukascopy.com/swiss/english/marketwatch/historical/)
- [Kaggle Financial Datasets](https://www.kaggle.com/datasets?tags=13304-Finance)

### Macroeconomic & Predictors

- [FRED (Federal Reserve Economic Data)](https://fred.stlouisfed.org/)
- [Welch & Goyal Macro Predictors](https://sites.google.com/view/agoyal145)
- [Global Macro Database](https://www.globalmacrodata.com/) ([code](https://github.com/KMueller-Lab/Global-Macro-Database))
- [BIS Data Portal](https://www.bis.org/statistics/index.htm)
- [World Bank Open Data](https://data.worldbank.org/)
- [IMF Data (IFS, WEO)](https://www.imf.org/en/Data)

### European Financial Data

- [ECB Data Portal](https://data.ecb.europa.eu/)
- [Eurostat](https://ec.europa.eu/eurostat)
- [Deutsche Bundesbank Data](https://www.bundesbank.de/en/statistics)
- [EU ETS Emissions Data](https://www.eea.europa.eu/en/datahub)

### Volatility, Derivatives & Fixed Income

- [CBOE VIX Historical Data](https://www.cboe.com/tradable-products/vix/vix-historical-data/)
- [Fed Board Yield Curve Models](https://www.federalreserve.gov/data/yield-curve-models.htm)
- [LOBSTER](https://lobsterdata.com/)

### Corporate Fundamentals & Events

- [SEC EDGAR](https://www.sec.gov/edgar)
- [SimFin](https://www.simfin.com/)
- [SEC Insider & Institutional Holdings](https://www.sec.gov/data-research/sec-markets-data)
- [N-PORT (SEC Filings)](https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets) ([code](https://github.com/global-capital-allocation-project/public-us-funds-data))
- [GLEIF Global LEI Index](https://www.gleif.org/en/lei-data)

### Alternative Data, NLP & Benchmarks

- [GDELT Project](https://www.gdeltproject.org/)
- [Google Trends](https://trends.google.com/)
- [Wikipedia Clickstream](https://meta.wikimedia.org/wiki/Research:Wikipedia_clickstream)
- [Hugging Face Finance Datasets](https://huggingface.co/datasets?sort=trending&search=finance)
- [Financial PhraseBank](https://huggingface.co/datasets/takala/financial_phrasebank)
- [Loughran-McDonald Master Dictionary](https://sraf.nd.edu/loughranmcdonald-master-dictionary/)
- [CFPB Consumer Complaint Database](https://www.consumerfinance.gov/data-research/consumer-complaints/)
- [Numerai Tournament Data](https://numer.ai/data)

## Using and contributing

- For installation, examples, requirements and limitations, follow the README in the relevant tool repository.
- Report bugs, suggest features and submit contributions in the corresponding tool repository.
- The tool repositories are the primary sources for tool code and documentation; this directory provides an overview.

[Back to the project overview](../README.md)
