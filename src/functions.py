import pandas as pd
from src.tickers import TickerManager
from src.optimizer import optimize_portfolio
from typing import Dict


def get_cumulative_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the cumulative returns of a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the returns data.

    Returns:
        pd.DataFrame: A DataFrame containing the cumulative returns.
    """

    return (1 + df.pct_change()).cumprod() - 1


def generate_allocation(df_tickers: TickerManager, x_years_lb: int) -> Dict[int, Dict[str, float]]:
    """Generates an allocation for each year between the first year and x_years_lb years after the first year.

    Args:
        df_tickers (TickerManager): A TickerManager object containing the asset returns.
        x_years_lb (int): The number of years after the first year to generate allocations for.

    Returns:
        Dict[int, Dict[str, float]]: A dictionary containing the allocation for each year.
    """

    first_year = df_tickers.tickers.index[0].year
    first_year_calculation = first_year + x_years_lb
    last_year = df_tickers.tickers.index[-1].year
    
    allocation_years = {}
    
    for year in range(first_year_calculation, last_year):
        df_x_year = df_tickers.tickers.loc[:str(year - 1)]
        allocation = optimize_portfolio(df_x_year, 'max_sharpe', gamma=0.1)
        allocation_years[year] = allocation
        
    return allocation_years