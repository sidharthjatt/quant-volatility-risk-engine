# Quant Volatility & Risk Engine  

**Tech Stack:** Python 3.11  
**Domain:** Quantitative Finance  

🔗 Project Repo: https://github.com/sidharthjatt/quant-volatility-risk-engine


## Quick Start

### Create and activate a virtual environment
```bash
python3.11 -m venv venv

# macOS / Linux
source venv/bin/activate   

# Windows
venv\Scripts\activate
```
### Install dependencies
```bash
pip install -r requirements.txt
```
### Run entire project
```bash
python -m run.run_full_pipeline
```
> The entire pipeline executes end-to-end with no manual intervention.


## Why I Built This Project

I started this project after going through several quantitative finance
projects that looked impressive on paper but quietly relied on hindsight.
Once you removed look-ahead or added basic realism, many of those results
fell apart.

Instead of chasing Sharpe ratios, I wanted to see how a strategy behaves
when conditions change — especially during volatility spikes. That meant
accepting weaker headline numbers in exchange for clarity, reproducibility,
and visible failure modes.

I don’t see this codebase as a “strategy to trade”. I see it as a research
sandbox — something I can stress, break, and inspect when market behavior
changes.


## Who This Project Is For

This project is useful for students and early-career researchers working
in quantitative finance, as well as candidates preparing for quant research
or trading roles. It may also help engineers who want to understand how
serious research pipelines are structured beyond static backtests.



## How to Review This Project 

If you are short on time:

1. Run the pipeline with one command
2. Look at `outputs/charts/`
3. Check `portfolio_comparison.csv`
4. Read the Diagnostics section

This gives a complete picture in a few minutes.


## Design Choices (and Trade-offs)

Several design decisions were made deliberately, even though they reduced
headline performance. Walk-forward evaluation is used instead of static
splits to better reflect real deployment. Volatility regimes are rule-based
and observable, which avoids black-box behavior but reacts more slowly to
sudden shifts.

Risk controls operate at the portfolio level rather than as a final filter,
and diagnostics are treated as core outputs rather than optional analysis.
Some of these choices make results look worse on paper, but they make the
system easier to reason about and debug.

I’m aware these decisions hurt some metrics. That’s a trade-off I was
comfortable making, and I’d still make the same calls if I rebuilt this.


## Technical Overview

### 1. What the System Does (Plain Language)

The pipeline is fully automated and reproducible.
The goal was not to maximize returns, but to study behavior.

In simple terms, the system focuses on:

- correct out-of-sample testing
- clear separation between training and evaluation
- portfolio behavior across different volatility regimes
- understanding why strategies fail, not just when they work
 


### 2. Core Ideas

#### Volatility modeling
GARCH-family models (GARCH, GJR-GARCH, EGARCH, FIGARCH) are used only to
estimate conditional volatility. They are not used to predict returns.

#### Evaluation discipline
Models are re-fit in a rolling walk-forward setup. Avoiding look-ahead bias
was treated as a hard constraint, even when it reduced performance.

#### Strategy logic
Signals combine expected returns with forecasted volatility. Position sizes
are controlled via volatility targeting, and market conditions are grouped
into LOW, MEDIUM, and HIGH volatility regimes.

#### Portfolio and risk
Assets are weighted by inverse volatility. A regime-aware allocator scales
exposure during high-risk periods. Risk is monitored using VaR, Expected
Shortfall, and historical stress episodes such as COVID-19 and rate-hike
phases.

#### Diagnostics
Instead of relying on a single Sharpe ratio, the system produces diagnostics
that show when the strategy struggles, when risk controls activate, and how
drawdowns evolve.


### 3. Project structure (clean & modular)

```
quant-volatility-risk-engine/
│
├── backtest/              # Single asset & portfolio backtests
├── walkforward/           # Rolling walk-forward framework
├── models/                # GARCH family models
├── model_switching/       # Dynamic model selection
├── regime/                # Volatility regime logic
├── risk/                  # VaR, ES, stress testing
├── risk_allocator/        # Risk-constrained scaling
├── strategy/              # Signals & position sizing
├── diagnostics/           # Research diagnostics
├── scripts/               # Data preprocessing & runners
├── run/                   # One-command pipeline runner
├── tests/                 # Sanity checks
├── outputs/
│   ├── final/             # CSV results
│   └── charts/            # All plots
└── README.md
```


### 4. Outputs

All results are saved under `outputs/`.

- `outputs/final/` contains CSV summaries and diagnostics
- `outputs/charts/` contains equity curves, regime plots, and crisis charts

Key plots include walk-forward equity, baseline vs regime-aware portfolios,
volatility regime distributions, and crisis-period performance.


### 5. Results and Limitations

The results are intentionally conservative. As constraints become stricter,
performance drops — which is expected and, in this context, acceptable.

Regime awareness mainly reduces downside risk rather than improving Sharpe
ratios. During calm markets, the regime-aware portfolio often underperforms
the baseline. During volatile periods, drawdowns are better controlled.

Limitations worth noting:

- regime detection is rule-based and reacts with some delay
- transaction costs are not modeled
- risk controls are defensive and do not aim to maximize upside

These trade-offs were accepted to keep the system interpretable and auditable.
The following plots are automatically generated by the pipeline and
summarize the behavior of the system visually:

#### Walk-Forward Equity Curve
![](outputs/charts/walkforward_equity.png)

#### Single Asset Strategy Equity
![](outputs/charts/INFY.NS_single_asset_equity.png)

#### Baseline vs Regime-Aware Portfolio
![](outputs/charts/portfolio_equity_comparison.png)

#### Volatility Regime Distribution
![](outputs/charts/regime_distribution.png)

#### Crisis Period Performance
**COVID-19**
![](outputs/charts/crisis_covid-19.png)

**Rate Hike Regime**
![](outputs/charts/crisis_rate_hikes.png)


### 6. Context

This project was built as a research prototype.
It is intended to demonstrate research discipline, reproducibility,
and risk-aware thinking rather than production-ready trading performance.



### 7. Disclaimer

This project documents how I think about quantitative systems under uncertainty:
explicit assumptions, controlled experimentation, and honest evaluation when
results are uncomfortable.


### Sidharth Choudhary
**Email**: jattsidh786@gmail.com

**LinkedIn**: [Sidharth Choudhary](https://www.linkedin.com/in/sidharthjatt)

**GitHub**: [Sidharth Choudhary](https://github.com/sidharthjatt)

**Website**: [Sidharth Choudhary](https://www.sidharthjatt.com)

Designed and implemented end-to-end as a personal quantitative research system.
