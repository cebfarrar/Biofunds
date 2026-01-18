# Biofunds: Following Smart Money in Biotech Clinical Trials

## What This Does

Tracks what biotech-only hedge funds are betting on and attempts to profit from their positioning. The basic premise is wisdom of the crowd applied to hedge funds, whose conviction (percentage concentration of their fund in a single Phase 2/3 trial), signals confidence in approval, and using an aggregate of all of their bets, to benefit from their scientific understanding. 

## The Idea

Biotech markets systematically misprice binary clinical events. A Phase 3 trial either works or it doesn't, but the market often gets the probability wrong. Meanwhile, specialist funds with PhDs on staff and years of experience are taking concentrated bets.

## Three-Step Process

### 1. What's the market pricing in?

For any biotech approaching a readout, you can calculate what probability the current stock price implies.

**Success case:** Company gets approval, captures market share, generates cash flows. I run a DCF with realistic assumptions (TAM, market penetration, margins, multiples). I Get a price target.

**Failure case:** Trial fails, company burns through cash, eventually liquidates or gets acquired for intellectual property pipeline. Calculate liquidation value (cash + salvageable assets - liabilities).

**Current price sits between these.**:
```
P(success) = (Current Price - Failure Value) / (Success Value - Failure Value)
```

This gives you the market's implied probability of the full success path: Phase 3 works AND FDA approves AND commercial launch succeeds AND company doesn't go bankrupt.

To isolate just Phase 3 probability, divide out the downstream steps using industry benchmarks (~85% FDA approval post-Phase 3, ~90% commercial execution, ~96% no bankruptcy).

### 2. What do the smart funds think?

I have scrape quarterly 13F filings for 52 specialist biotech funds. Position size = conviction:

- 3-5% of fund: Did real work, believes in it
- 5-7%: High conviction, extensive diligence  
- 7%+: Very high conviction, probably proprietary edge

Track their historical performance at each concentration level. OrbiMed at 5%+ positions: 219 bets over 12 years, hit ~65% vs 50-60% base rates.

### 3. Update your probability

Start with disease-specific base rates from historical data:
- Oncology Phase 3: ~48%
- Nephrology: ~59%
- Rare disease: ~70%
- Ophthalmology: ~51%

When a fund with a strong track record takes a 6% position, update the likelihood based on their prior success rate in that conviction band (5-6%). If market implies 31% and your posterior comes out to 63%, that's a +32 percentage point edge!

## Real Numbers (April 2019 - January 2026)

Trained on fund positioning data from Q4 2005 through March 2018. Tested from April 2019 through January 2026 (6.7 years covering both the 2021-2023 biotech winter and 2024-2025 recovery).

**What happened:**
- Screened 2,674 completed clinical trials
- Generated 1,193 position signals (44.6% of opportunities)
- All long bias (0 shorts— I have assumed it's too expensive for Biotech funds to short individual drug pipelines, if it costs 20% for a 
- Individual trade win rate: 48.4%
- Average trade: +3.8% (after transaction costs)
- Best single trade: +198.5%
- Worst: -93.2%

**Portfolio level (assuming 2% position sizing, up to 50 concurrent):**
- CAGR: 11.9%
- Sharpe ratio: 0.64
- Max drawdown: -36.6%
- Correlation to S&P 500: 0.08

The 36.6% drawdown hit during the 2021-2022 biotech bear market when multiple trials failed in succession. XBI (biotech ETF) fell 60% in that window—strategy held up better but still brutal.

Win rate under 50% but profitable because winners (+34% avg) significantly outsize losers (-25% avg). Profit factor 1.3x.

## How It Actually Works

52 funds tracked, each with 1-7 position size "bands" based on historical performance:
```
OrbiMed: 5 bands, 219 training bets → reliable signal across 3-10% positions
Redmile: 5 bands, 150 bets → strong at 4-6% 
Baker Bros: 4 bands, 44 bets → excellent at 6%+
Sarissa: 3 bands, 197 bets → broad coverage
```

For each upcoming catalyst, check:
1. Which funds hold it at 1.5%+?
2. What's their historical success rate in that position band?
3. How many bets in training data? (penalize funds with <10 for credibility)

Conviction-weighted update:
```
Weight = (position_pct / 10) × credibility_score × 100
Posterior = (base_rate × 100 + Σ(fund_success_rate × weight)) / (100 + Σ(weight))
```

Signal triggers when posterior diverges significantly from market-implied probability:
- Long: posterior > market + threshold
- Short: posterior < market - threshold (rare in practice)

## Example Walkthrough

**Company X:** Phase 3 nephrology readout Q2 2026

**Market data:**
- Current price: $30
- Success scenario DCF: $121 (assuming approval, market penetration, 10x EBITDA multiple - usual multiple is 8-20x)
- Failure liquidation: $0.75 (cash + salvage - liabilities)

**Implied probability:**
```
P(full path) = ($30 - $0.75) / ($121 - $0.75) = 24.4%
P(Phase 3) = 24.4% / (0.85 × 0.90 × 0.96) = 31.4%
```

**Fund positioning:**
- Baker Bros: 6.2% position, entered Q2 2025
- Historical at 6%+: 68% success rate (38 bets)

**Base rate:** 58.6% (nephrology Phase 3 historical average)

**Bayesian posterior:** Blend base rate with fund signal weighted by position size and track record → 63%

**Expected value:**
```
EV = 0.63 × ($121 - $30) + 0.37 × ($0.75 - $30)
   = 0.63 × $91 + 0.37 × (-$29.25)
   = $57.33 - $10.82
   = +$46.51 per share = +155%
```

Quarter-Kelly sizing: ~4% of portfolio.

## What This Taught Me

**Fund track records matter.** OrbiMed with 219 training bets gives much stronger signal than EcoR1 with 3 bets. The system explicitly penalizes low-sample funds through credibility scoring.

**Position size is predictive.** Funds at 7%+ concentration hit ~73% vs ~58% at 3-5%. They're genuinely better at picking when they bet big.

**Base rates are harder than expected.** Disease classification matters enormously—calling something "oncology" (48% success) vs "hematology" (69%) changes the calculation. Spent a while tuning the disease category dictionary.

**Transaction costs hurt.** Modeled 0.3% spread on longs, 1.16% on shorts (2% annual borrow × 120 days + 0.5% spread). Real costs are probably higher for small accounts.

**Win rate doesn't matter as much as payoff ratio.** 48% win rate with 1.3x profit factor still makes money. The winners run far (avg +34%) while losers cap out around -25% due to stop losses.

## Limitations

This backtest covers 6.7 years including one long bear market 2021-2023. No idea if it works going forward, but it was a lot of fun! Some issues:

**Fund survivorship:** Only tracked funds that still exist today (filing 13Fs through 2025). Dead funds from 2005-2015 aren't included—they might have worse track records. Probably adds optimistic bias.

**13F lag:** Filings are 45 days delayed and quarterly. By the time you see a position, catalyst might be 2-3 months closer. Sometimes funds have already exited. But catalyst dates are public information.

**Hidden positions:** Funds can use derivatives, file for confidential treatment, or hold positions under $200k not disclosed in 13Fs. You're seeing incomplete data.

**Regime dependency:** 2019-2026 covered both bull and bear markets, but FDA approval standards could tighten, biotech funding could dry up permanently, or funds' edge could erode as more people track them.

**No short book:** Most biotech funds don't short extensively. Strategy is naturally long-biased which means difficulty in bear markets.

**Sample size:** 1,193 trades over 6.7 years = ~180/year. A few lucky/unlucky years could swing results significantly.

I have no idea if this actually works with real money. Backtest looks ok but there's probably overfitting I didn't catch.

## Data Pipeline

**Clinical trials:** ClinicalTrials.gov API (33k+ biotech trials)  
**Historical outcomes:** Manually labeled from trial completion dates + stock price moves  
**Success rates:** BIO Industry Analysis reports (2006-2024)  
**Fund holdings:** SEC EDGAR 13F filings (automated downloader)  
**Prices:** Yahoo Finance API (20 years daily history)  
**Company financials:** 10-K/10-Q for DCF inputs

Database is SQLite with ~34k trials, 17k with outcomes, 398 with missing dates (dropped from analysis).

## Files
```
Funds.py              # Main pipeline (13F scraper, database, backtest)
biotech_intelligence.db   # SQLite database
/Backtest/            # Results CSVs
/sec-edgar-filings/   # Raw 13F XML files by fund
master.csv            # Aggregated current holdings
```

Key functions:
- `populate_clinical_trials_database()` - Scrapes ClinicalTrials.gov
- `label_trial_outcomes_from_announcement_spike()` - Labels success/failure from price moves
- `generate_high_conviction_bet_analysis()` - Builds fund track records by position band
- `backtest_bayesian_strategy()` - Full train/test split backtest

## Running It
```bash
python3 Funds.py
```

Full pipeline from scratch takes 1 hour (13F downloads, trial scraping, price history).

## Current Pipeline

System maintains forward calendar of ~180 upcoming Phase 2/3 catalysts in next 24 months. Matches against current fund holdings from most recent 13F quarter.

Example output:
```
2026-03-15 (57d)  ARDX - PHASE3 | Hyperphosphatemia | P(success): 63% [Baker Bros 6.2%]
2026-04-22 (95d)  IONS - PHASE3 | ATTR Amyloidosis  | P(success): 71% [OrbiMed 4.8%]
```

Updates quarterly as new filings drop.

## Things I'd Change

**Better disease classification:** Current keyword matching misses nuances. "Oncology" is too broad—melanoma ≠ pancreatic cancer. Need finer categories.

**Incorporate trial design features:** Adaptive trials, surrogate endpoints, open-label vs blinded all matter. Haven't encoded this yet, but having spoken to doctors involved in clinical trials, they are highly standardised.

**Short side:** Could track fund exits as negative signal. If Baker Bros dumps a 6% position 2 quarters before catalyst, that's something to include.
