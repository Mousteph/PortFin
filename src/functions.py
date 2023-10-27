import pandas as pd
from src.optimizer import optimize_portfolio, discrete_allocation
from typing import Dict
from tqdm import tqdm

def __delete_null_tickers(tickers: pd.DataFrame) -> pd.DataFrame:
    """Deletes tickers with null values from a DataFrame.

    Args:
        tickers (pd.DataFrame): A pandas DataFrame containing the ticker data.

    Returns:
        pd.DataFrame: A pandas DataFrame without null values.
    """

    sum_null = tickers.isnull().sum()
    null_tickers = sum_null[sum_null > 0].index
    tickers = tickers.drop(columns=null_tickers)
    
    return tickers

def generate_allocation(df_tickers: pd.DataFrame, x_years_lb: int, optimizer: str = 'max_sharpe', gamma: float = 0.1) -> Dict[int, Dict[str, float]]:
    """Generates an allocation for each year between the first year and x_years_lb years after the first year.

    Args:
        df_tickers (TickerManager): A TickerManager object containing the asset returns.
        x_years_lb (int): The number of years after the first year to generate allocations for.
        optimizer (str, optional): The optimization objective. Must be either "max_sharpe" or "min_volatility". Defaults to 'max_sharpe'.
        gamma (float, optional): The regularization parameter. Defaults to 0.1.

    Returns:
        Dict[int, Dict[str, float]]: A dictionary containing the allocation for each year.
    """

    first_year = df_tickers.index[0].year
    first_year_calculation = first_year + x_years_lb
    last_year = df_tickers.index[-1].year
    
    allocation_years = {}
    t_range = tqdm(range(first_year_calculation, last_year + 1),
                   desc='Generating allocations',
                   ncols=100)

    for year in t_range:
        t_range.set_description(f"Generating allocations for {year}")
        t_range.refresh()
        
        df_x_year = df_tickers.loc[str(year - 5):str(year - 1)]
        df_x_year = __delete_null_tickers(df_x_year)
        
        allocation = optimize_portfolio(df_x_year, optimizer, gamma=gamma)
        allocation_years[year] = allocation
        
    return allocation_years
    

def calculate_portfolio(df: pd.DataFrame, allocation: Dict) -> pd.Series:
    """Calculates the value of a portfolio given a DataFrame of asset returns and an allocation.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing the asset returns.
        allocation (Dict): A dictionary containing the asset allocation weights.

    Returns:
        pd.Series: A pandas Series containing the value of the portfolio.
    """

    df_assets = df[allocation.keys()]
    df_weights = allocation.values()
    portfolio_value = df_assets.mul(df_weights, axis=1).sum(axis=1)
    
    return portfolio_value
    

def generate_portfolio(df_tickers: pd.DataFrame, allocation: Dict, money: int) -> pd.DataFrame:
    """Generates a portfolio given a TickerManager object, an allocation, and an initial investment.

    Args:
        df_tickers (TickerManager): A TickerManager object containing the asset returns.
        allocation (Dict): A dictionary containing the asset allocation weights.
        money (int): The initial investment.

    Returns:
        pd.DataFrame: A pandas DataFrame containing the portfolio value over time.
    """

    portfolio = pd.DataFrame()
    
    for year, allocation in allocation.items():
        df_x_year = df_tickers.loc[str(year)]
        df_x_year = __delete_null_tickers(df_x_year)
        
        dis_allocation, left_over = discrete_allocation(df_x_year, allocation, money)
        dx_x_year_value = calculate_portfolio(df_x_year, dis_allocation) + left_over
        portfolio = pd.concat([portfolio, dx_x_year_value])
        money = dx_x_year_value.iloc[-1]
    
    portfolio.index = pd.to_datetime(portfolio.index)
    portfolio.columns = ["Portfolio"]
    portfolio.index.name = "Date"
    
    return portfolio