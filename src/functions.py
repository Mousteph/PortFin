import pandas as pd

def get_cumulative_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the cumulative returns of a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the returns data.

    Returns:
        pd.DataFrame: A DataFrame containing the cumulative returns.
    """

    return (1 + df.pct_change()).cumprod() - 1