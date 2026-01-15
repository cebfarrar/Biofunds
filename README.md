# Biofunds
**"In the short run, the market is a voting machine" - Benjamin Graham**

Hypothesis:
Markets do not have perfect information regarding upcoming clinical trial catalyst events (principal–agent problem), and so there is frequently a market correction, which we would not see if this information is priced in. In a world with perfect information and totally efficient markets, this would not happen, because scientifically inclined individuals would exploit this information gap, and predict clinical trial outcomes based on the strength of what they are studying. 
<img width="906" height="461" alt="Screenshot 2026-01-14 at 16 44 49" src="https://github.com/user-attachments/assets/6cc6f808-0498-4a0d-b6c5-5a5ba5f8ab97" />

Thesis:
At it's core, this project identifies mispriced clinical trial outcomes by combining fundamental analysis with institutional positioning data. The strategy detects situations where biotech-focused hedge funds' concentrated positions suggest higher probability of success than market-implied probabilities indicate.

By tracking how elite biotech hedge funds position their portfolios before trial results, we can identify situations where:
example:
1. Market-implied probability (derived from fundamental DCF analysis) suggests 24% chance of approval
2. Smart money conviction (measured by position concentration) historically correlates with 54% success rate
3. Historical trial data (phase-specific, indication-specific) provides base rate of 47.5%
When 2. & 3. > 1. and Bayesian updating supports the edge, we have an exploitable opportunity.

**Example: Calculating Market-Implied Probability**
Ardelyx is awaiting Phase 3 results for a once-daily hyperphosphatemia treatment for dialysis patients. Let's calculate what probability of success the market is currently pricing in.

****__Market Implied Probability__****
**Addressable Market**
Target Population:
- US dialysis patients: 500,000
- With hyperphosphatemia: ~400,000

**Pricing:**
- Annual treatment cost: $5,000/patient
- Total addressable market: $2.0B

**Market Share Assumption**
Competitive Position:
- Advantage: Once-daily dosing vs. 3x daily for competitors
- Market entry: 6th entrant in established market
- Conservative market share: 15%
Patients captured: 60,000

**Revenue Projection (Peak Year)**
> 60,000 patients × $5,000/year = $300M annual revenue
Assumes: 5-year ramp to peak sales

**Valuation if Approved**
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

**Failure Scenario**
Assume Total Assets = $27.1M -> (Cash & equivalents, Marketable securities, Accounts receivable, Equipment (at 40% of book), Real estate/facilities (lease buyout value), IP portfolio (early-stage programs)
Assume Total Liabilities = $12.6M

$27.1M - $12.6M = $14.5M
$14.5M ÷ 20M shares = $0.73/share

**Failure Value: ~$0.75/share (rounded for trading purposes)**

Market-Implied Probability
Current Market Data:
- Current price: $30/share
- Approval scenario: $120.50/share
- Failure scenario: $1/share (cash value only)

Formula:
P(success) = (Current Price - Failure Value) / (Approval Value - Failure Value)

P(success) = ($30.00 - $0.75) / ($120.50 - $0.75)
P(success) = $29.25 / $119.75
P(success) = 0.244 = 24.4%

The Market Is Pricing In: ~24% Probability of success, Phase 3 approval, full successful roll out, and capturing oligopoly rents successfully. 

Given the post Phase 3 risks of: default of company, failure to establish itself to hyperphosphatemia patients, failure to capture any market share, rollout failure. Given this ~24% probability includes these risks, the market is pricing in higher probability than 24% probability of a successful Phase 3, and there is persistent risk with 10-15% of drugs that successfully complete a Phase 3 trial and do not receive FDA approval [1].

The Edge Explained
Market pricing of 24.4% for full success implies:

Either the market thinks Phase 3 has only 41% chance
Or the market is skeptical of commercial execution even if approved
Or both

If elite funds are taking >5% positions:
e.g
"Baker Bros": {
    "total_high_conviction_bets": 135,
    "overall_success_rate_%": 85.2,
    "by_position_band": {
    ">15%": {
        "total_bets": 38,
        "success": 26,
        "failure": 6,
        "neutral": 6,
        "success_rate_%": 68.4,
        "avg_spike_%": 29.3
      }
    }
Baker Bros historical hit rate at this concentration: 68.4%
Their edge is in clinical/scientific analysis, not commercial forecasting

The Bayesian Update:
Prior: 58.6% (base rate for nephrology Phase 3)
Likelihood: 68.4% assume same scientific talent made the statistically significant success of 28/38 bets possible.
Market: 43% (implied Phase 3 probability -> 24% + 15% (being generous [1]) + 4% (default risk) = 43%

If Baker Bros takes a 6% position:
→ Posterior probability ≈ 58.6-68.4%
→ Edge vs market: 15.6-25.4 percentage points
→ Expected value: strongly positive, buy.


[1]:
BIO / Biomedtracker (2011–2020): Covering 12,728 clinical and regulatory transitions, found that 90.6% of New Drug Application (NDA) or Biologics License Application (BLA) filings resulted in approval. This leaves a failure rate of 9.4% for programs that successfully navigated Phase 3 and filed for approval.
Wong et al. / MIT (2018): Published in Biostatistics, this study utilized a large-scale data set of over 21,000 compounds from 2000 to 2015. It identified that the transition from Phase 3 success to final approval had a probability of success of approximately 85% to 90%, depending on the therapeutic area.
Hay et al. / Nature Biotechnology (2014): This seminal review analyzed 4,451 compounds from 2003 to 2011 and found an 83% success rate from the submission of an NDA/BLA to final approval. This indicated a higher failure rate of 17% at the final stage during that specific window.
Academic-Industrial Study (2018): Research published in Clinical and Translational Science analyzed 798 drug discovery projects and reported an 87.5% success rate for the final NDA/BLA phase, closely mirroring industry-wide benchmarks. 
