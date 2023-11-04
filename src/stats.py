import pandas as pd


def get_pct_change(df: pd.DataFrame, period: str = 'D') -> pd.DataFrame:
    """Calculates the percentage change between the current and a prior element in a DataFrame.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing the data to calculate the percentage change for.
        period (str, optional): The time period to resample the data to. Defaults to 'D'. Can be any valid pandas time period.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the percentage change between the current and a prior element.
    """

    return df.resample(period).ffill().pct_change()


def get_returns(df: pd.DataFrame, period: str = 'D') -> pd.DataFrame:
    """Calculates the cumulative returns of a DataFrame.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing the data to calculate the cumulative returns for.
        period (str, optional): The time period to resample the data to. Defaults to 'D'. Can be any valid pandas time period.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the cumulative returns of the input DataFrame.
    """
    
    return (1 + get_pct_change(df, period)).cumprod()


def get_max_drawdown(df: pd.DataFrame, period: str = 'D') -> float:
    """Calculates the maximum drawdown of a DataFrame.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing the data to calculate the maximum drawdown for.
        period (str, optional): The time period to resample the data to. Defaults to 'D'. Can be any valid pandas time period.

    Returns:
        float: A float representing the maximum drawdown of the input DataFrame.
    """

    returns = get_returns(df, period)
    return returns / returns.cummax() - 1