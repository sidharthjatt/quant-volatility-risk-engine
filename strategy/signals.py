import numpy as np
import pandas as pd


def momentum_signal(df):
    """
    Simple momentum signal:
    Buy if yesterday's return was positive.

    Parameters
    ----------
    df : pd.DataFrame
        Must contain column: 'log_return'

    Returns
    -------
    pd.Series
        Signal series (1 = invest, 0 = no position)
    """

    signal = np.where(
        df["log_return"].shift(1) > 0,
        1,
        0
    )

    return pd.Series(signal, index=df.index, name="Signal")


def trend_volatility_signal(
    df,
    ma_window=20,
    vol_window=60
):
    """
    Trend + Volatility filter signal (YOUR ORIGINAL LOGIC)

    Conditions:
    1. Price > Moving Average (trend filter)
    2. Forecasted volatility < rolling median volatility (risk filter)

    Parameters
    ----------
    df : pd.DataFrame
        Must contain columns:
        - 'Price'
        - 'Forecasted_Volatility'

    ma_window : int, default=20
        Moving average window for price

    vol_window : int, default=60
        Rolling window for volatility median

    Returns
    -------
    pd.Series
        Signal series (1 = invest, 0 = no position)
    """

    temp_df = df.copy()

    # Moving average on price
    temp_df["MA_Price"] = temp_df["Price"].rolling(ma_window).mean()

    signal = np.where(
        (
            (temp_df["Price"] > temp_df["MA_Price"]) &   # trend
            (
                temp_df["Forecasted_Volatility"]
                < temp_df["Forecasted_Volatility"]
                .rolling(vol_window)
                .median()
            ) &                                          # volatility
            (temp_df["RSI_14"] < 70)                     # momentum (NEW)
        ),
        1,
        0
    )

    return pd.Series(signal, index=df.index, name="Signal")

