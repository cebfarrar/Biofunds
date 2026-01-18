# Biofunds: Following Smart Money in Biotech Clinical Trials

## Overview

This project tracks what biotech-focused hedge funds are betting on and attempts to profit from their positioning. The premise: specialist funds with PhDs and years of experience take concentrated bets on clinical trials. Their position sizes signal conviction, and by aggregating their bets, we can benefit from their scientific edge.

## The Hypothesis

Biotech markets systematically misprice binary clinical events. 
<img width="919" height="442" alt="Screenshot 2026-01-18 at 21 54 58" src="https://github.com/user-attachments/assets/6bf8c33c-b874-4b9b-be37-d2b81c09a9ff" />

A Phase 3 trial either succeeds or it doesn't - but the market often gets the probability wrong. With perfect information and totally efficient markets, such troughs would not happen. Meanwhile, specialist funds are taking 5-25%+ portfolio positions on single trials. A big bet is a confident bet, and these funds will have internal risk management procedures to know their failure rate at big bets, and so confident bets should be worth following.

## How It Works

### Step 1: What's the Market Pricing In?

For any biotech approaching a readout, calculate what probability the current stock price implies.

**Success case:** Company gets approval, captures market share, generates cash flows. Run a fundamental analysis DCF with realistic assumptions (TAM, market penetration, margins, exit multiple). Get a price target.

**Failure case:** Trial fails, company burns cash, eventually liquidates or gets acquired for salvage value. Calculate liquidation value (cash + salvageable assets - liabilities).

**The current price sits between these two scenarios:**

```
P(success) = (Current Price - Failure Value) / (Success Value - Failure Value)
```

This gives the market's implied probability of the *full success path*: Phase 3 works AND FDA approves AND commercial launch succeeds AND company doesn't go bankrupt.

To isolate just the Phase 3 probability, divide out the downstream steps using industry benchmarks (~85% FDA approval post-Phase 3, ~90% commercial execution, ~96% no bankruptcy).

**Example: Company X**

Phase 3 nephrology readout expected Q2 2026

**Market data:**
- Current price: $30
- Success scenario DCF: $121 (assuming approval, market penetration, 10x EBITDA multiple)
- Failure liquidation: $0.75 (cash on hand + salvage value - liabilities)

**Calculate implied probability:**

```
P(full path) = ($30 - $0.75) / ($121 - $0.75) = 24.4%

P(Phase 3 success) = 24.4% / (0.85 × 0.90 × 0.96) = 31.4%
```

The market is pricing in a roughly 31.4% chance the Phase 3 trial succeeds.

### Step 2: What Do the Smart Funds Think?

Download quarterly 13F filings for 52 specialist biotech funds. Position size reveals conviction:

- **3-5% of fund:** Believes in it
- **5-7%:** High conviction, extensive diligence  
- **7%+:** Very high conviction

Track their historical performance at each concentration level.

**Example:** OrbiMed took 219 bets at 5%+ positions over 12 years → hit ~65% success rate vs. 50-60% industry base rates.

**Company X positioning:**
- Baker Bros: 6.2% position, entered Q2 2025
- Historical success rate at 6%+ positions: 68% (38 trials)

### Step 3: Update Probability

Start with disease-specific base rates from historical clinical trial data:

| Disease Area | Phase 3 Success Rate |
|--------------|---------------------|
| Oncology | 48% |
| Nephrology | 59% |
| Rare disease | 70% |
| Ophthalmology | 51% |

When a fund with a strong track record takes a 6% position, update the probability based on their historical success rate at that conviction level.

**For Company X:**
- Base rate (nephrology): 59%
- Baker Bros signal (6.2% position, 68% historical): Strong positive
- **Updated posterior: 63%**

**Calculate expected value:**

```
EV = P(success) × (Success Price - Current) + P(failure) × (Failure Price - Current)
   = 0.63 × ($121 - $30) + 0.37 × ($0.75 - $30)
   = 0.63 × $91 + 0.37 × (-$29.25)
   = $57.33 - $10.82
   = +$46.51 per share (+155% expected return)
```

Market implies 31% → Analysis suggests 63% → **+32 percentage point edge**

## Backtest Results

**Training period:** Q4 2005 - March 2018  
**Test period:** April 2019 - January 2026 (6.7 years)

The test period covers both the 2021-2023 biotech bear market and the 2024-2025 recovery.

### Trade-Level Statistics

| Metric | Value |
|--------|-------|
| Trials screened | 2,674 |
| Trades taken | 1,193 (44.6% of opportunities) |
| Win rate | 48.4% |
| Average win | +34.0% |
| Average loss | -25.0% |
| Best trade | +198.5% |
| Worst trade | -93.2% |
| Avg trade (after costs) | +3.8% |

### Portfolio-Level Performance

Assumptions: 2% position sizing, max 50 concurrent positions, rebalanced quarterly

| Metric | Value |
|--------|-------|
| CAGR | 11.9% |
| Sharpe ratio | 0.64 |
| Max drawdown | -36.6% |
| Correlation to S&P 500 | 0.08 |

**Notes:**
- Win rate is below 50%, but profitable because winners (+34% avg) significantly outsize losers (-25% avg)
- Profit factor: 1.3x
- The 36.6% drawdown occurred during the 2021-2022 biotech bear market when multiple trials failed in succession
- XBI (biotech ETF) fell 60% in the same period—strategy held up better but still brutal

## Methodology Details

### Fund Tracking

52 funds tracked, each with 1-7 position size "bands" based on historical performance:

| Fund | Position Bands | Training Bets | Notes |
|------|---------------|---------------|-------|
| OrbiMed | 5 bands | 219 | Reliable signal across 3-10% positions |
| Redmile | 5 bands | 150 | Strong at 4-6% |
| Baker Bros | 4 bands | 44 | Excellent at 6%+ |
| Sarissa | 3 bands | 197 | Broad coverage |

### Signal Generation

For each upcoming catalyst, the system:

1. Identifies which funds hold the stock at 1.5%+ position size
2. Retrieves their historical success rate in that specific position band
3. Applies credibility penalty for funds with <10 training bets in that band
4. Calculates conviction-weighted posterior:

```
Weight = (position_pct / 10) × credibility_score × 100
Posterior = (base_rate × 100 + Σ(fund_success_rate × weight)) / (100 + Σ(weight))
```

**Signal triggers when:**
- **Long:** Posterior probability > Market-implied probability + threshold
- **Short:** Not used (biotech shorts are expensive to maintain, borrow costs often 10-20%+ annually)

### Transaction Cost Assumptions

- **Entry/Exit:** 1.5% round-trip (0.75% each way)
- **Includes:** Bid-ask spread, market impact, SEC fees
- **Rationale:** Biotech stocks often have wide spreads and low liquidity

## Key Learnings

### What Worked

**Fund track records matter.** OrbiMed with 219 training bets gives much stronger signal than a fund with 3 bets. The system penalizes low-sample-size funds through credibility scoring.

**Position size is predictive.** Funds at 7%+ concentration hit ~73% vs. ~58% at 3-5%. When they bet big, they're more certain—and more often correct.

**Disease classification is critical.** "Oncology" (48% base rate) vs. "hematology" (69% base rate) completely changes the calculation. Getting the base rate wrong breaks the entire framework.

### What Didn't Work

**Shorts are uneconomical.** Attempted to use fund exits as negative signals, but in reality a downgrade is more of a WEAK BUY signal, than a short signal. Strategy is naturally long-biased, because shorting/puts are very expensive.

**Win rate ≠ profitability.** 48% win rate still makes money (according to backtest!) due to asymmetric payoffs (1.3x profit factor). Winners run to +34% on average while losers cap at -25% due to stop losses.

## Limitations & Risks

### Data Quality Issues

**Survivorship bias:** Only tracked funds still filing 13Fs through 2025. Dead funds from 2005-2015 aren't included—they likely have worse track records. This survivor bias leads to overly optimistic outcomes.

**13F reporting lag:** Filings are 45 days delayed and quarterly. Sometimes funds exited right before announcement.

**Hidden positions:** Funds can use derivatives, file for confidential treatment, or hold positions under $200k that don't appear in 13Fs. Incomplete data.

### Structural Risks

**Regime dependency:** Backtest covers 2019-2026 (both bull and bear markets), but FDA approval standards could tighten, biotech funding could dry up, or funds' edge could erode.

**Small sample size:** 1,193 trades over 6.7 years = ~180 per year. A few lucky/unlucky years could swing results significantly.

**No short book:** I assumed most biotech funds don't short extensively. Strategy struggles in sustained bear markets when "long everything" is the wrong call.

**Overfitting risk:** Despite train/test split, disease classification and position band thresholds were tuned on partial test data. Real forward performance could be worse.

### Why This Might Not Work Going Forward

- Signals worked historically but not anymore.
- Biotech hedge fund edge expires, or weakens and the 45 day lag ruins this project.
- Funds could lose their edge as trials become more transparent
- 13F tracking is now common—alpha could be arbitraged away
- Biotech sector could enter multi-year bear market worse than 2021-2023
- FDA could change approval standards (already happening with accelerated approvals)

**I have no idea if this actually works with real money.** Backtest looks ok, but there's probably overfitting I didn't catch.

## Data Sources

| Source | Purpose | Coverage |
|--------|---------|----------|
| ClinicalTrials.gov API | Clinical trial data | 33,000+ biotech trials |
| SEC EDGAR 13F filings | Fund holdings | 52 funds, Q4 2005 - present |
| Yahoo Finance API | Historical prices | 20 years daily data |
| BIO Industry Analysis | Success rate benchmarks | 2006-2024 reports |
| Company 10-K/10-Q filings | Financial data for DCF | SEC EDGAR |

**Database:** SQLite with ~34,000 trials, 17,000 with labeled outcomes, 398 dropped due to missing data.

## Repository Structure

```
├── Funds.py                    # Main pipeline script
├── biotech_intelligence.db     # SQLite database
├── /Backtest/                  # Results CSVs
├── /sec-edgar-filings/         # Raw 13F XML files by fund
└── master.csv                  # Aggregated current holdings
```

### Key Functions in `Funds.py`

- `populate_clinical_trials_database()` - Scrapes ClinicalTrials.gov
- `label_trial_outcomes_from_announcement_spike()` - Labels success/failure from price moves
- `generate_high_conviction_bet_analysis()` - Builds fund track records by position band
- `backtest_bayesian_strategy()` - Full train/test split backtest with transaction costs

## Setup & Usage

### 1. Install Dependencies

```bash
pip install pandas numpy requests beautifulsoup4 sec-edgar-downloader yfinance
```
Then download code/ copy paste it into an IDE.

### 2. Run Initial Setup

Execute these functions in order:

```python
# Functions 1-8: Initial data collection
if __name__ == '__main__':
    load_dotenv()
    file_downloader()
    process_filings()
    master_table = master_set(base_path)
    populate_fund_holdings_database()
    setup_database()
    build_company_mapping()
    populate_clinical_trials_database()
    export_companies_for_ticker_entry()

### 3. Manual Ticker Classification

After running the above, you'll have `tickers.csv` in `/sec-edgar-filings/`.

**Required (slightly painful):** Manually add these columns for each ticker:
- `ticker` - Stock symbol (e.g., ARDX)
- `exchange` - Trading venue (e.g., NASDAQ, NYSE)
- `is_biotech` - Type "Yes" (without quotes) if it's a biotech company

**Tip:** Use an LLM (Gemini is good for this, and will create a link to a Google sheet) to classify tickers. Paste the list into the model and save.

Copy the results back into `tickers.csv`.

### 4. Complete Setup

```python
# Functions 9-17: Data processing, replace Functions 1-8 with this:
if __name__="__main__":
   download_10y_price_history_for_all_tickers()
   fetch_historical_stock_prices_for_trials()
   label_trial_outcomes_from_announcement_spike()
   generate_fund_bet_trackers()
   generate_high_conviction_bet_analysis()
   harvest_pdufa_dates()
   harvest_upcoming_clinical_trials()
   generate_catalyst_calendar()
   generate_bayesian_catalyst_analysis()
```

### 5. Run Backtest

```python
# Functions 18-19: Analysis - Add this to if __name__="__main__"
backtest_df = backtest_bayesian_strategy(
    train_end_date='2021-03-30',
    test_start_date='2021-04-01',
    test_end_date='2026-01-16',
    long_threshold=0.0001,      # 2pp above base
    short_threshold=0.50,     # 15pp below base
    min_funds=2,              # Single fund can trigger signal
    min_sample_size=2         # Accept even 1 historical bet
    )

    stats_realistic = calculate_portfolio_level_statistics(
    position_size=0.02,  # 2% per position
    max_concurrent=50     # Up to 50 positions at once
    )
```

**Full pipeline runtime:** ~60 minutes (13F downloads + trial scraping + price history)

### Current Opportunities

System maintains a forward calendar of ~180 upcoming Phase 2/3 catalysts in the next 24 months, matched against current fund holdings.

**Example output:**

```
2026-03-15 (57d)  ARDX - PHASE3 | Hyperphosphatemia | P(success): 63% | Baker Bros 6.2%
2026-04-22 (95d)  IONS - PHASE3 | ATTR Amyloidosis  | P(success): 71% | OrbiMed 4.8%
```

Updates quarterly as new 13F filings are released.

## Future Improvements

**Finer disease classification:** Current keyword matching is too coarse. "Oncology" is too broad—melanoma ≠ pancreatic cancer. Need subcategory granularity for accurate base rates.

**Trial design features:** Adaptive trials, surrogate endpoints, open-label vs. blinded designs all affect success rates. Currently not encoded.

**Fund exit signals:** Track when funds dump positions 1-2 quarters before catalyst. Could be incorporated as negative signal.
