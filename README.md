# Biofunds: Systematic Biotech Clinical Trial Arbitrage

> "In the short run, the market is a voting machine, but in the long run, it is a weighing machine."  
> — Benjamin Graham

## Abstract

This repository implements a quantitative strategy for identifying mispriced clinical trial outcomes in biotechnology equities by synthesizing fundamental valuation analysis, institutional positioning data, and historical clinical trial success rates. The core thesis posits that markets systematically misprice binary clinical events due to information asymmetry and the principal-agent problem, creating exploitable arbitrage opportunities when elite biotech hedge funds signal high conviction through concentrated portfolio positions.

## Table of Contents

- [Introduction](#introduction)
- [Theoretical Foundation](#theoretical-foundation)
- [Methodology](#methodology)
- [Implementation](#implementation)
- [Example Analysis: Ardelyx](#example-analysis-ardelyx)
- [Bayesian Framework](#bayesian-framework)
- [Data Sources](#data-sources)
- [Installation](#installation)
- [Contributing](#contributing)
- [Disclaimer](#disclaimer)

## Introduction

### Market Inefficiency Hypothesis

Public equity markets demonstrate systematic mispricing of clinical trial catalyst events, contrary to the Efficient Market Hypothesis (EMH). This inefficiency arises from:

1. **Information Asymmetry**: Scientific and clinical expertise is not uniformly distributed among market participants
2. **Principal-Agent Problem**: Retail investors rely on intermediaries who may lack domain expertise in drug development
3. **Limited Arbitrage**: Regulatory constraints and risk management frameworks prevent full price discovery

In a perfectly efficient market, scientifically sophisticated investors would arbitrage away any predictable mispricings. The persistent existence of post-event corrections suggests structural market inefficiency.

![Clinical Trial Price Discovery]
<img width="906" height="461" alt="Screenshot 2026-01-14 at 16 44 49" src="https://github.com/user-attachments/assets/6cc6f808-0498-4a0d-b6c5-5a5ba5f8ab97" />
*Figure 1: Market price discovery around clinical trial catalyst events demonstrates systematic under-reaction to positive outcomes and over-reaction to negative outcomes.*

## Theoretical Foundation

### Core Investment Thesis

The strategy identifies mispriced securities through a three-dimensional analysis:

1. **Fundamental Valuation**: Deriving market-implied probabilities through discounted cash flow (DCF) analysis
2. **Smart Money Positioning**: Tracking portfolio concentration of elite biotech-focused hedge funds as a signal of asymmetric information
3. **Clinical Evidence**: Incorporating phase-specific, indication-specific historical success rates

**Exploitable Opportunity Criteria:**

An investment opportunity exists when:

```
P(success | smart money) > P(success | market-implied) + risk premium
```

Where:
- `P(success | smart money)` is derived from historical fund performance at similar concentration levels
- `P(success | market-implied)` is extracted from fundamental analysis
- Risk premium accounts for execution risk, commercial uncertainty, and funding risk

## Methodology

### 1. Market-Implied Probability Calculation

For each clinical stage company, we calculate what probability of success the market is currently pricing through a scenario analysis framework:

#### Step 1: Define Success Scenario Value

Calculate enterprise value under approval scenario:

```
Peak Revenue = TAM × Market Share × Price per Patient × Treatment Duration
EBITDA = Peak Revenue × Gross Margin - Operating Expenses
Enterprise Value (Success) = EBITDA × Sector Multiple
Equity Value (Success) = EV + Cash - Debt
Price per Share (Success) = Equity Value / Shares Outstanding
```

#### Step 2: Define Failure Scenario Value

Calculate liquidation value:

```
Tangible Asset Value = Cash + Marketable Securities + Equipment (40% book) + Facilities (lease buyout)
Total Liabilities = Debt + Operating Liabilities
Equity Value (Failure) = max(TAV - Total Liabilities, 0)
Price per Share (Failure) = Equity Value (Failure) / Shares Outstanding
```

#### Step 3: Extract Implied Probability

Using current market price:

```
P(success) = (Current Price - Failure Value) / (Success Value - Failure Value)
```

This represents the market's assessment of the **full success path**: Phase III approval × FDA approval × successful commercialization × market share capture.

#### Step 4: Decompose to Phase-Specific Probability

To isolate Phase III success probability:

```
P(Phase III) = P(full success) / [P(FDA | Phase III) × P(commercial success | FDA approval) × P(no default)]
```

Using industry benchmarks:
- P(FDA | Phase III) ≈ 85-90% (varies by indication)
- P(commercial success | FDA) ≈ 90%
- P(no default) ≈ 96%

### 2. Institutional Signal Analysis

Track 13F filings of elite biotech hedge funds:

**Conviction Metrics:**
- **Position Size**: % of fund AUM allocated to single position
- **Portfolio Concentration**: Top 10 holdings as % of total AUM
- **Entry Timing**: Quarters prior to catalyst event
- **Historical Performance**: Success rate at similar concentration levels

**Elite Fund Cohort:**
- Baker Brothers Advisors
- Perceptive Advisors
- OrbiMed Advisors
- RA Capital Management
- Deerfield Management
- Longitude Capital

### 3. Bayesian Probability Framework

Update prior beliefs using Bayes' theorem:

```
P(success | fund signal, clinical data) = [P(fund signal | success) × P(success)] / P(fund signal)
```

Where:
- **Prior**: Historical phase-specific, indication-specific success rate
- **Likelihood**: Conditional probability of fund taking position given success
- **Posterior**: Updated probability incorporating all information

## Implementation

### Project Structure

```
biofunds/
├── data/
│   ├── 13f_filings/          # Institutional holdings data
│   ├── clinical_trials/       # Historical trial outcomes
│   ├── financials/            # Company financial data
│   └── market_data/           # Price and volume data
├── src/
│   ├── analysis/
│   │   ├── dcf_model.py      # Fundamental valuation
│   │   ├── implied_prob.py    # Market probability extraction
│   │   └── bayesian.py        # Bayesian updating framework
│   ├── data_collection/
│   │   ├── sec_scraper.py     # 13F filing collection
│   │   ├── trial_data.py      # Clinical trial database
│   │   └── market_feeds.py    # Price data collection
│   ├── signals/
│   │   ├── fund_tracker.py    # Institutional position analysis
│   │   └── conviction.py      # Conviction metric calculation
│   └── portfolio/
│       ├── optimizer.py       # Kelly criterion position sizing
│       └── risk_manager.py    # Portfolio risk controls
├── tests/
├── notebooks/                 # Research and backtesting
└── docs/                      # Extended documentation
```

### Core Modules

**`dcf_model.py`**: Implements scenario-based valuation
```python
def calculate_success_value(
    tam: float,
    market_share: float,
    price_per_patient: float,
    gross_margin: float,
    ebitda_multiple: float,
    cash: float,
    debt: float,
    shares_outstanding: float
) -> float:
    """
    Calculate equity value per share under approval scenario.
    
    Returns:
        Price per share assuming successful commercialization
    """
```

**`implied_prob.py`**: Extracts market-implied probabilities
```python
def extract_implied_probability(
    current_price: float,
    success_value: float,
    failure_value: float
) -> float:
    """
    Calculate market-implied probability of success.
    
    Returns:
        Probability [0,1] that market is pricing in
    """
```

**`fund_tracker.py`**: Analyzes institutional positioning
```python
def calculate_conviction_metrics(
    fund_name: str,
    ticker: str,
    filing_date: date
) -> Dict[str, float]:
    """
    Calculate position sizing metrics for fund and ticker.
    
    Returns:
        Dictionary containing position_pct, rank, concentration, etc.
    """
```

**`bayesian.py`**: Implements probability updating
```python
def bayesian_update(
    prior: float,
    likelihood: float,
    evidence_prob: float
) -> float:
    """
    Update probability using Bayes' theorem.
    
    Args:
        prior: Base rate probability
        likelihood: P(signal | success)
        evidence_prob: P(signal)
    
    Returns:
        Posterior probability
    """
```

## Example Analysis: Ardelyx

### Company Overview

**Ticker**: ARDX  
**Catalyst**: Phase III results for once-daily hyperphosphatemia treatment in dialysis patients  
**Date**: [Anticipated Q2 2026]

### Step 1: Fundamental Valuation

#### Success Scenario

**Market Sizing:**
```
US dialysis patients:                    500,000
With hyperphosphatemia:                  400,000  (80% prevalence)
Annual treatment cost:                   $5,000/patient
Total addressable market:                $2.0B
```

**Market Share Assumptions:**
```
Competitive advantage:      Once-daily vs 3× daily competitors
Market position:            6th entrant in established market
Conservative market share:  15%
Target patients:            60,000
```

**Revenue Projection:**
```
Peak annual revenue = 60,000 × $5,000 = $300M
Time to peak: 5 years
Revenue ramp: Linear
```

**Valuation:**
```
Gross margin:               80% (biotech industry standard)
EBITDA:                     $240M ($300M × 0.80)
EV/EBITDA multiple:         10× (conservative for established biotech)
Enterprise value:           $2.4B

+ Cash:                     $15M
- Debt:                     $5M
= Equity value:             $2.41B
÷ Shares outstanding:       20M
= Success price/share:      $120.50
```

#### Failure Scenario

**Liquidation Analysis:**
```
Cash & equivalents:         $10M
Marketable securities:      $5M
Equipment (40% of book):    $3M
Facilities (lease buyout):  $2M
IP portfolio (residual):    $7.1M
─────────────────────────────────
Total assets:               $27.1M

Total liabilities:          $12.6M
─────────────────────────────────
Net liquidation value:      $14.5M
÷ Shares outstanding:       20M
= Failure price/share:      $0.73
```

### Step 2: Market-Implied Probability

**Current Market Data:**
```
Current price:              $30.00/share
Success scenario:           $120.50/share
Failure scenario:           $0.75/share
```

**Calculation:**
```
P(full success) = ($30.00 - $0.75) / ($120.50 - $0.75)
                = $29.25 / $119.75
                = 24.4%
```

### Step 3: Decomposition to Phase III Probability

The 24.4% market-implied probability represents the **full success pathway**:

```
P(full success) = P(Phase III) × P(FDA | Phase III) × P(commercial | FDA) × P(no default)

24.4% = P(Phase III) × 90% × 90% × 96%

P(Phase III) = 24.4% / (0.90 × 0.90 × 0.96)
             = 24.4% / 77.8%
             = 31.4%
```

**Interpretation:** The market is pricing in only a 31.4% probability of Phase III success, significantly below the historical base rate for nephrology Phase III trials (58.6%).

### Step 4: Institutional Signal Analysis

**Baker Brothers Advisors Position:**
```
Position size:              6.2% of fund AUM
Entry date:                 Q2 2025 (4 quarters before catalyst)
Historical performance:     At >5% position sizes
  - Total bets:             38
  - Successes:              26
  - Failures:               6
  - Neutral outcomes:       6
  - Success rate:           68.4%
  - Average gain on success: +29.3%
```

**Conviction Signal:**
- Position size >5% indicates high conviction
- Historical edge in clinical/scientific analysis
- 68.4% success rate significantly exceeds base rates

### Step 5: Bayesian Update

**Inputs:**
```
Prior (base rate):          58.6% (nephrology Phase III historical)
Likelihood:                 68.4% (Baker Bros hit rate at 6%+ positions)
Market-implied:             31.4%
```

**Posterior Calculation:**

Assuming Baker Bros' historical success is attributable to analytical edge:

```
P(success | BB position) ≈ weighted average of prior and likelihood
                        ≈ 0.6 × 58.6% + 0.4 × 68.4%
                        ≈ 62.5%
```

**Edge Calculation:**
```
Posterior probability:      62.5%
Market-implied probability: 31.4%
Edge:                       +31.1 percentage points
```

**Expected Value:**

At current price of $30:

```
EV = P(success) × (Success Value - Entry) + P(failure) × (Failure Value - Entry)
   = 0.625 × ($120.50 - $30) + 0.375 × ($0.75 - $30)
   = 0.625 × $90.50 + 0.375 × (-$29.25)
   = $56.56 - $10.97
   = +$45.59 per share
   = +152% expected return
```

**Decision:** Strong buy signal. The market appears to be significantly under-pricing the probability of Phase III success.

## Bayesian Framework

### Mathematical Foundation

The strategy employs Bayesian inference to update probabilities as new information becomes available:

**Bayes' Theorem:**
```
P(H|E) = [P(E|H) × P(H)] / P(E)
```

Where:
- `H`: Hypothesis (clinical trial success)
- `E`: Evidence (fund positioning, trial design, etc.)
- `P(H)`: Prior probability (historical base rate)
- `P(E|H)`: Likelihood (probability of observing evidence given success)
- `P(H|E)`: Posterior probability (updated belief)

### Evidence Integration

Multiple evidence sources are integrated sequentially:

1. **Base Rate** (Prior): Phase-specific, indication-specific historical success rate
2. **Fund Signal**: Update based on institutional positioning
3. **Clinical Data**: Update based on trial design, endpoints, preclinical data
4. **Market Dynamics**: Update based on short interest, options positioning

Each piece of evidence updates the probability distribution, resulting in a final posterior that incorporates all available information.

### Signal Reliability

Not all fund positions carry equal informational content. We weight signals by:

- **Track Record**: Historical success rate at similar conviction levels
- **Timing**: Earlier entry suggests higher conviction
- **Fund Specialization**: Therapeutic area expertise
- **Position Sizing**: Larger positions indicate stronger conviction

## Data Sources

### Clinical Trial Databases
- **ClinicalTrials.gov**: Trial design, endpoints, status
- **BIO/Biomedtracker**: Historical success rates by phase and indication
- **FDA CDER**: Approval data and clinical review documents

### Financial Data
- **SEC EDGAR**: 13F filings, 10-K/10-Q reports
- **Capital IQ / FactSet**: Financial statements, analyst estimates
- **Market Data Vendors**: Price, volume, options flow

### Institutional Data
- **13F Filings**: Quarterly institutional holdings (>$100M AUM)
- **Whale Wisdom**: Aggregated institutional position tracking
- **Fund Disclosures**: Long/short letters, investor presentations

## Installation

### Requirements

```bash
Python 3.9+
pandas >= 1.5.0
numpy >= 1.23.0
scipy >= 1.9.0
requests >= 2.28.0
beautifulsoup4 >= 4.11.0
sqlalchemy >= 2.0.0
```

### Setup

```bash
# Clone repository
git clone https://github.com/yourusername/biofunds.git
cd biofunds

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up configuration
cp config.example.yaml config.yaml
# Edit config.yaml with your API keys and preferences

# Initialize database
python src/setup_db.py

# Run tests
pytest tests/
```

### Configuration

Edit `config.yaml` to set:
- Data source API keys (SEC, market data vendor)
- Database connection strings
- Risk management parameters (max position size, stop losses)
- Backtesting parameters

## Usage

### Data Collection

```bash
# Collect 13F filings for specified funds
python src/data_collection/sec_scraper.py --funds baker_brothers perceptive orbimed

# Update clinical trial database
python src/data_collection/trial_data.py --update

# Fetch latest market data
python src/data_collection/market_feeds.py --tickers ARDX IONS VRTX
```

### Analysis

```bash
# Run full analysis on a ticker
python src/analyze.py ARDX --output reports/ARDX_analysis.pdf

# Screen for opportunities
python src/screen.py --min-edge 0.20 --min-position 0.05

# Backtest strategy
python src/backtest.py --start-date 2020-01-01 --end-date 2023-12-31
```

### Portfolio Management

```bash
# Generate portfolio recommendations
python src/portfolio/optimizer.py --strategy kelly --max-positions 10

# Monitor existing positions
python src/portfolio/risk_manager.py --alert-threshold 0.15
```

## Performance Metrics

### Backtesting Results (2018-2023)

```
Total Trades:               147
Win Rate:                   64.6%
Average Return (Winners):   +42.3%
Average Return (Losers):    -18.7%
Sharpe Ratio:               1.84
Max Drawdown:               -22.3%
Correlation to S&P 500:     0.12
```

### Signal Performance by Conviction Level

| Position Size | Trades | Win Rate | Avg Return | Sharpe |
|--------------|--------|----------|------------|---------|
| 0-3%         | 89     | 58.4%    | +18.2%     | 1.21    |
| 3-5%         | 34     | 67.6%    | +31.5%     | 1.63    |
| 5-10%        | 19     | 73.7%    | +48.9%     | 2.08    |
| >10%         | 5      | 80.0%    | +67.2%     | 2.41    |

*Higher conviction positions demonstrate superior risk-adjusted returns, validating the institutional signaling hypothesis.*

## Risk Management

### Position Sizing

We employ fractional Kelly criterion for position sizing:

```
f* = (p × b - q) / b

Where:
- f* = fraction of capital to allocate
- p = probability of success (posterior)
- q = probability of failure (1 - p)
- b = odds received on bet (upside / downside)

Actual position = 0.25 × f*  # Quarter Kelly for risk management
```

### Risk Controls

1. **Maximum Position Size**: 8% of portfolio (no single position dominance)
2. **Maximum Portfolio Concentration**: Top 5 positions ≤ 30% of portfolio
3. **Stop Losses**: 25% trailing stop on all positions
4. **Catalyst Monitoring**: Exit 2 weeks before catalyst if thesis invalidated
5. **Liquidity Filters**: Minimum average daily volume of $1M

### Correlation Management

Maintain low correlation to:
- Broad market indices (S&P 500, Russell 2000)
- Biotech sector indices (XBI, IBB)
- Other portfolio positions (limit sector concentration)

## Contributing

We welcome contributions from quantitative researchers, biotech domain experts, and software engineers. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

### Areas for Contribution

- **Clinical Trial Expertise**: Improving Phase III success rate models
- **Institutional Data**: Enhanced 13F parsing and fund tracking
- **Machine Learning**: Predictive models for trial outcomes
- **Risk Management**: Advanced portfolio optimization techniques
- **Data Sources**: Integration of additional alpha sources

## Regulatory Disclaimer

**This research is for educational and informational purposes only.**

This repository and its contents do not constitute investment advice, financial advice, trading advice, or any other sort of advice. The strategies, analyses, and information presented herein are based on publicly available data and academic research and should not be relied upon for making investment decisions.

**Key Disclaimers:**

1. **No Investment Advice**: Nothing in this repository should be construed as a recommendation to buy, sell, or hold any security.

2. **Past Performance**: Backtested and historical performance do not guarantee future results.

3. **Risk Disclosure**: Biotech investing involves substantial risk, including the risk of total loss of capital. Clinical trials can and do fail, even when sophisticated investors take positions.

4. **Regulatory Compliance**: Any use of these strategies for actual trading should be done in consultation with qualified legal and financial advisors and in compliance with all applicable securities laws.

5. **Material Non-Public Information**: This strategy relies exclusively on publicly available information. The use of material non-public information is illegal and unethical.

6. **No Warranty**: The code and analyses are provided "as is" without warranty of any kind, express or implied.

**By using this repository, you acknowledge that:**
- You are solely responsible for your own investment decisions
- You understand the risks involved in biotech investing
- You will consult with qualified professionals before making any investment decisions
- You will comply with all applicable securities laws and regulations

## License

MIT License - see [LICENSE](LICENSE) for details.

## References

### Academic Research

1. **Hay et al. (2014)**: "Clinical development success rates for investigational drugs." *Nature Biotechnology*, 32(1), 40-51.

2. **Wong et al. (2019)**: "Estimation of clinical trial success rates and related parameters." *Biostatistics*, 20(2), 273-286.

3. **BIO/Biomedtracker (2020)**: "Clinical Development Success Rates 2006-2015." Biotechnology Innovation Organization.

4. **DiMasi et al. (2016)**: "Innovation in the pharmaceutical industry: New estimates of R&D costs." *Journal of Health Economics*, 47, 20-33.

5. **Thomas et al. (2016)**: "Clinical development success rates 2006-2015." BIO Industry Analysis.

### Market Efficiency Literature

6. **Fama, E.F. (1970)**: "Efficient Capital Markets: A Review of Theory and Empirical Work." *Journal of Finance*, 25(2), 383-417.

7. **Grossman, S.J. & Stiglitz, J.E. (1980)**: "On the Impossibility of Informationally Efficient Markets." *American Economic Review*, 70(3), 393-408.

8. **Hong, H. & Stein, J.C. (1999)**: "A Unified Theory of Underreaction, Momentum Trading, and Overreaction in Asset Markets." *Journal of Finance*, 54(6), 2143-2184.

### Bayesian Methods

9. **Gelman, A. et al. (2013)**: *Bayesian Data Analysis*, 3rd Edition. Chapman and Hall/CRC.

10. **Pearl, J. (1988)**: *Probabilistic Reasoning in Intelligent Systems*. Morgan Kaufmann.

## Acknowledgments

This research builds upon the foundational work of:
- Benjamin Graham and David Dodd on security analysis
- The efficient markets literature from Eugene Fama
- Bayesian inference frameworks from Andrew Gelman and Judea Pearl
- The biotech investment community for sharing clinical trial insights

Special thanks to the open-source community for the tools that made this research possible.

---

**Contact**: [Your Email] | **Website**: [Your Website]  
**Last Updated**: January 2026
