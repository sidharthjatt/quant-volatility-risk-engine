import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# -------------------------------------------------
# CORE PREPROCESSING LOGIC
# -------------------------------------------------

def preprocess_data():

    # Load combined CSV
    df = pd.read_csv(
        "nifty50_history_with_adj/nifty50_combined_2015_2025.csv",
        parse_dates=["Date"]
    )

    # Sort by Ticker + Date
    df = df.sort_values(["Ticker", "Date"]).reset_index(drop=True)

    if "Adj Close" not in df.columns:
        raise ValueError("Adj Close column missing in combined CSV!")

    # Compute log returns
    df["log_return"] = df.groupby("Ticker")["Adj Close"].transform(
        lambda x: np.log(x / x.shift(1))
    )

    # Save raw returns
    raw_path = "nifty50_history_with_adj/nifty50_log_returns_adjclose.csv"
    df.to_csv(raw_path, index=False)

    print("Daily log-return file created (Adj Close only):")
    print(raw_path)

    # Clean data
    df = df.dropna(subset=["log_return"]).reset_index(drop=True)
    df.index = df.index + 1
    df["Date"] = pd.to_datetime(df["Date"]).dt.date

    returns_df = df[["Date", "Ticker", "Adj Close", "Volume", "log_return"]]

    # =========================
    # new improvement - Moving average added 
    # =========================

    returns_df["MA_5"] = returns_df.groupby("Ticker")["Adj Close"].transform(
        lambda x: x.rolling(5).mean()
    )

    returns_df["MA_10"] = returns_df.groupby("Ticker")["Adj Close"].transform(
        lambda x: x.rolling(10).mean()
    )
    # print(returns_df.head())
    # New improvement end of MA

    # =========================
    # new improvement - RSI added 
    # =========================

    def compute_rsi(series, window=14):
        delta = series.diff()

        gain = (delta.where(delta > 0, 0)).rolling(window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        return rsi

    returns_df["RSI_14"] = returns_df.groupby("Ticker")["Adj Close"].transform(
        lambda x: compute_rsi(x, 14)
    )
    # New improvement end of RSI
    # print(returns_df.head())



    clean_path = "nifty50_history_with_adj/nifty50_log_returns_clean.csv"
    returns_df.to_csv(clean_path, index=False)

    return returns_df


# -------------------------------------------------
# HELPER FOR OTHER MODULES
# -------------------------------------------------

def load_returns_data():
    """
    Loads preprocessed log-return data.
    Used by backtest & risk modules.
    """
    path = "nifty50_history_with_adj/nifty50_log_returns_adjclose.csv"
    return pd.read_csv(path, parse_dates=["Date"])


# -------------------------------------------------
# SCRIPT ENTRY POINT
# -------------------------------------------------

if __name__ == "__main__":
    preprocess_data()
