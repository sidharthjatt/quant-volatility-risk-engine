import numpy as np
import pandas as pd
import os

from risk_allocator.apply_allocator import apply_risk_allocator


# =====================================================
# PORTFOLIO BACKTEST (RISK-CONSTRAINED)
# =====================================================

def run_portfolio_backtest(returns_df, portfolio_stocks):
    """
    Runs inverse-volatility weighted portfolio backtest
    with RISK-CONSTRAINED ALLOCATION
    """

    # -----------------------------------
    # Create return matrix
    # -----------------------------------
    portfolio_df = (
        returns_df[
            returns_df["Ticker"].isin(portfolio_stocks)
        ]
        .pivot(
            index="Date",
            columns="Ticker",
            values="log_return"
        )
        .dropna()
    )

    # -----------------------------------
    # Rolling volatility (proxy for GARCH)
    # -----------------------------------
    rolling_window = 60
    vol_df = portfolio_df.rolling(rolling_window).std()

    # -----------------------------------
    # Inverse volatility weights
    # -----------------------------------
    vol_df = vol_df.replace(0, np.nan)

    inv_vol = 1 / vol_df
    weights = inv_vol.div(inv_vol.sum(axis=1), axis=0)
    weights = weights.dropna()

    # -----------------------------------
    # ALIGN INDEX (CRITICAL FIX)
    # -----------------------------------
    common_index = portfolio_df.index.intersection(weights.index)

    portfolio_df = portfolio_df.loc[common_index]
    weights = weights.loc[common_index]

    # -----------------------------------
    # Portfolio returns (RAW)
    # -----------------------------------
    portfolio_df = portfolio_df.copy()

    portfolio_df["Portfolio_Return"] = (weights * portfolio_df).sum(axis=1)

    # =========================
    # STOP-LOSS ADDED
    # =========================

    stop_loss_threshold = -0.02  # -2% loss limit

    portfolio_df["Portfolio_Return"] = np.where(
        portfolio_df["Portfolio_Return"] < stop_loss_threshold,
        stop_loss_threshold,
        portfolio_df["Portfolio_Return"]
    )
    # stop loss end here
    
    # -----------------------------------
    # RISK-CONSTRAINED ALLOCATION (NEW)
    # -----------------------------------
    portfolio_df, risk_summary = apply_risk_allocator(
        portfolio_df,
        portfolio_df["Portfolio_Return"]
    )

    # -----------------------------------
    # Final equity (risk-adjusted)
    # -----------------------------------
    portfolio_df["Equity"] = portfolio_df["Adj_Equity"]

    return (
        portfolio_df,
        portfolio_df["Adj_Return"],
        portfolio_df["Equity"],
        risk_summary
    )


# =====================================================
# PORTFOLIO PERFORMANCE METRICS
# =====================================================

def portfolio_performance_metrics(portfolio_df):
    trading_days = 252
    eps = 1e-8

    equity = portfolio_df["Equity"]
    returns = portfolio_df["Adj_Return"]

    ann_return = equity.iloc[-1] ** (trading_days / len(equity)) - 1
    ann_vol = returns.std() * np.sqrt(trading_days)
    sharpe = ann_return / (ann_vol + eps)

    max_dd = (equity / equity.cummax() - 1).min()

    return {
        "Annual Return": ann_return,
        "Annual Volatility": ann_vol,
        "Sharpe Ratio": sharpe,
        "Max Drawdown": max_dd
    }


# =====================================================
# PORTFOLIO RISK (VaR, ES, DIVERSIFICATION)
# =====================================================

def portfolio_risk_metrics(returns_df, portfolio_df):
    trading_days = 252

    portfolio_returns = portfolio_df["Adj_Return"].dropna()

    alpha_95 = 0.05
    alpha_99 = 0.01

    var_95 = abs(np.percentile(portfolio_returns, alpha_95 * 100))
    es_95 = abs(
        portfolio_returns[
            portfolio_returns <= -var_95
        ].mean()
    )

    var_99 = abs(np.percentile(portfolio_returns, alpha_99 * 100))
    es_99 = abs(
        portfolio_returns[
            portfolio_returns <= -var_99
        ].mean()
    )

    # Annualized
    var_annual = var_95 * np.sqrt(trading_days)
    es_annual = es_95 * np.sqrt(trading_days)

    # Diversification benefit
    individual_var = (
        returns_df
        .groupby("Ticker")["log_return"]
        .apply(lambda x: abs(np.percentile(x, 5)))
    )

    diversification_benefit = 1 - var_95 / individual_var.mean()

    return {
        "VaR_95": var_95,
        "ES_95": es_95,
        "VaR_99": var_99,
        "ES_99": es_99,
        "Annual_VaR": var_annual,
        "Annual_ES": es_annual,
        "Diversification_Benefit": diversification_benefit
    }


# =====================================================
# SAVE RESULTS
# =====================================================

def save_portfolio_outputs(metrics_dict, output_dir="phase4_outputs"):
    os.makedirs(output_dir, exist_ok=True)

    pd.DataFrame(
        list(metrics_dict.items()),
        columns=["Metric", "Value"]
    ).to_csv(
        f"{output_dir}/portfolio_risk_metrics.csv",
        index=False
    )

# =====================================================
# RUN AS SCRIPT (PIPELINE SUPPORT)
# =====================================================

if __name__ == "__main__":

    from scripts.preprocess import load_returns_data

    portfolio_stocks = [
        "INFY.NS", "TCS.NS", "RELIANCE.NS", "HDFCBANK.NS",
        "ICICIBANK.NS", "LT.NS", "ITC.NS", "SBIN.NS",
        "AXISBANK.NS", "HINDUNILVR.NS"
    ]

    returns_df = load_returns_data()

    portfolio_df, port_ret, port_eq, risk_summary = run_portfolio_backtest(
        returns_df,
        portfolio_stocks
    )

    metrics = portfolio_performance_metrics(portfolio_df)

    os.makedirs("outputs/final", exist_ok=True)

    pd.DataFrame(
        list(metrics.items()),
        columns=["Metric", "Value"]
    ).to_csv(
        "outputs/final/portfolio_performance.csv",
        index=False
    )

    print("----- Baseline portfolio saved → outputs/final/portfolio_performance.csv -----")



    # -----------------------------------
    # SAVE BASELINE PORTFOLIO EQUITY (FOR PLOTS)
    # -----------------------------------
    portfolio_df[[
        "Adj_Return",
        "Equity"
    ]].rename(
        columns={
            "Adj_Return": "Portfolio_Return",
            "Equity": "Portfolio_Equity"
        }
    ).to_csv(
        "outputs/final/portfolio_equity.csv",
        index=False
    )

    print("Baseline portfolio equity saved → outputs/final/portfolio_equity.csv")

