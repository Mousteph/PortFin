import pandas as pd
from src.optimizer import discrete_allocation, OptimizerBase
from typing import Dict, Tuple
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

def one_year_allocation(df_tickers: pd.DataFrame, x_years_lb: int, year: int, optimizer: OptimizerBase) -> Dict[int, float]:
    """Calculates the allocation for one year based on the given data and optimizer.

    This function takes a DataFrame of tickers, a lookback period, a year, and an optimizer. It filters the DataFrame 
    for the lookback period ending in the given year, removes any tickers with null values, and then calculates the 
    allocation using the given optimizer.

    Args:
        df_tickers (pd.DataFrame): The DataFrame of tickers.
        x_years_lb (int): The lookback period in years.
        year (int): The year for which to calculate the allocation.
        optimizer (OptimizerBase): The optimizer to use for calculating the allocation.

    Returns:
        Dict[int, float]: A dictionary with the year as the key and the allocation as the value.
    """

    df_x_year = df_tickers.loc[str(year - x_years_lb):str(year - 1)]
    df_x_year = __delete_null_tickers(df_x_year)
    
    allocation = optimizer(df_x_year)

    return {year: allocation}
    

def generate_allocation(df_tickers: pd.DataFrame, x_years_lb: int, optimizer: OptimizerBase) -> Dict[int, Dict[str, float]]:
    """Generates an allocation for each year between the first year and x_years_lb years after the first year.

    Args:
        df_tickers (pd.DataFrame): A DataFrame object containing the asset returns.
        x_years_lb (int): The number of years after the first year to generate allocations for.
        optimizer (OptimizerBase): An optimizer object to use for generating the allocations.

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

        allocation_years.update(one_year_allocation(df_tickers, x_years_lb, year, optimizer))
        
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
    

def generate_portfolio(df_tickers: pd.DataFrame, allocation: Dict, money: int,
                       reinvest: int = 0) -> Tuple[pd.DataFrame, float]:
    """Generates a portfolio given a TickerManager object, an allocation, and an initial investment.

    Args:
        df_tickers (TickerManager): A TickerManager object containing the asset returns.
        allocation (Dict): A dictionary containing the asset allocation weights.
        money (int): The initial investment.
        reinvest (int, optional): The amount of money to reinvest each year. Defaults to 0.

    Returns:
        Tuple[pd.DataFrame, float]: A pandas DataFrame containing the portfolio value over time and amount of money reinvested.
    """

    portfolio = pd.DataFrame()
    total_reinvested = 0
    
    for year, allocation in allocation.items():
        df_x_year = df_tickers.loc[str(year)]
        df_x_year = __delete_null_tickers(df_x_year)
        
        dis_allocation, left_over = discrete_allocation(df_x_year, allocation, money)
        dx_x_year_value = calculate_portfolio(df_x_year, dis_allocation) + left_over
        portfolio = pd.concat([portfolio, dx_x_year_value])
        money = dx_x_year_value.iloc[-1] + reinvest
        total_reinvested += reinvest
    
    portfolio.index = pd.to_datetime(portfolio.index)
    portfolio.columns = ["Portfolio"]
    portfolio.index.name = "Date"
    
    return portfolio, total_reinvested