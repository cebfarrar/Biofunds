# Biofunds
What are bio-tech only hedge funds investing in?


**"In the short run, the market is a voting machine" - Benjamin Graham**

Hypothesis:
This project identifies mispriced clinical trial outcomes by combining fundamental analysis with institutional positioning data. The strategy detects situations where sophisticated biotech-focused hedge funds' concentrated positions suggest higher probability of success than market-implied probabilities indicate.

Thesis:
Markets don't have perfect information prior to clinical trial results announcements and so misprice binary clinical trial events. 
<img width="906" height="461" alt="Screenshot 2026-01-14 at 16 44 49" src="https://github.com/user-attachments/assets/6cc6f808-0498-4a0d-b6c5-5a5ba5f8ab97" />
By tracking how elite biotech hedge funds position their portfolios before trial results, we can identify situations where:
1. Market-implied probability (derived from fundamental DCF analysis) suggests X% chance of approval
2. Smart money conviction (measured by position concentration) historically correlates with Y% success rate
3. Historical trial data (phase-specific, indication-specific) provides base rate of Z%
When Y > X, and Bayesian updating confirms the edge, we have an exploitable opportunity.

**Example: Calculating Market-Implied Probability**
Ardelyx is awaiting Phase 3 results for a once-daily hyperphosphatemia treatment for dialysis patients. Let's calculate what probability of success the market is currently pricing in.

Step 1: Addressable Market
Target Population:
- US dialysis patients: 500,000
- With hyperphosphatemia: ~400,000

Pricing:
- Annual treatment cost: $5,000/patient
- Total addressable market: $2.0B

Step 2: Market Share Assumption
Competitive Position:
- Advantage: Once-daily dosing vs. 3x daily for competitors
- Market entry: 6th entrant in established market
- Conservative market share: 15%
Patients captured: 60,000

Step 3: Revenue Projection (Peak Year)
> 60,000 patients × $5,000/year = $300M annual revenue
Assumes: 5-year ramp to peak sales


Step 4: Valuation if Approved
Operating Metrics:
- Revenue: $300M
- Gross margin: 80% (biotech standard post-approval)
- EBITDA: $240M

Valuation Multiple:
- Apply conservative 10x EV/EBITDA (biotech sector lower end)
- Enterprise Value: $2.4B

Equity Value:
EV:     $2.4B
+ Cash:   $15M
- Debt:    $5M
─────────────────
Equity: $2.41B

$2.41B ÷ 20M shares = $120.50/share

Failure Scenario:
Combining Cash & equivalents, Marketable securities, Accounts receivable, Equipment (at 40% of book), Real estate/facilities (lease buyout value), IP portfolio (early-stage programs) - assume $27.1M total assets.
Assume Total Liabilities = $12.6M

Net Liquidation Value:
$27.1M - $12.6M = $14.5M
$14.5M ÷ 20M shares = $0.73/share

Failure Value: ~$0.75/share (rounded for trading purposes)

Step 5: Calculate Market-Implied Probability
Current Market Data:
- Current price: $30/share
- Approval scenario: $120.50/share
- Failure scenario: $1/share (cash value only)

Formula:
P(success) = (Current Price - Failure Value) / (Approval Value - Failure Value)

P(success) = ($30.00 - $0.75) / ($120.50 - $0.75)
P(success) = $29.25 / $119.75
P(success) = 0.244 = 24.4%

The Market Is Pricing In: ~24% Probability of Phase 3 success, full successful roll out, and capturing monopoly rents successfully. 

Context Check
Historical Phase 3 Success Rates:

Rare diseases: ~73%
Cardiovascular: ~58%
Oncology: ~48%
Nephrology/Metabolic: ~55-60%

Context Check
Historical Phase 3 Success Rates:

Rare diseases: ~73%
Cardiovascular: ~58%
Oncology: ~48%
Nephrology/Metabolic: ~55-60%

The Real Opportunity:
What Market PricesWhat History SuggestsSmart Money Hit Rate (@>5%)Potential Edge41% chance Phase 3 success55-60% base rate70-75% (if positioned)15-30 points

The Edge Explained
Market pricing of 24.4% for full success implies:

Either the market thinks Phase 3 has only 41% chance (vs. 55-60% base rate)
Or the market is skeptical of commercial execution even if approved
Or both

If elite funds are taking >5% positions:

Their historical hit rate at this concentration: 70-75%
They're not betting on commercial success—they're betting on Phase 3 + FDA approval
Their edge is in clinical/scientific analysis, not commercial forecasting

The Bayesian Update:
Prior: 55% (base rate for nephrology Phase 3)
Likelihood: 70-75% (smart money hit rate at >5% conviction)
Market: 41% (implied Phase 3 probability)

If Baker Bros takes a 6% position:
→ Posterior probability ≈ 65-70%
→ Edge vs market: 24-29 percentage points
→ Expected value: strongly positive

Summary Table
MetricValueAddressable Market$2.0BMarket Share15%Peak Revenue$300MEBITDA Margin80%Valuation Multiple10x EV/EBITDAApproval Price Target$120.50Current Price$30.00Failure Value$0.75Market-Implied P(Full Success)24.4%Implied P(Phase 3 Success)~41%Historical Base Rate (Phase 3)55-60%Smart Money Hit Rate (@>5%)70-75%Potential Edge25-30 points



