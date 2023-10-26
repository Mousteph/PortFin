import pandas as pd
from src.tickers import TickerManager
from src.optimizer import optimize_portfolio, discrete_allocation

from typing import Dict, Tuple, List



def sell_all_stocks(df_tickers: pd.DataFrame, allocation: Dict) -> float:
    """
    Calculates the total value of all stocks in the allocation dictionary
    based on the latest price in the df_tickers DataFrame.

    Args:
        df_tickers (pd.DataFrame): A DataFrame containing the latest stock prices for each ticker.
        allocation (dict): A dictionary containing the allocation of shares for each ticker.

    Returns:
        float: The total value of all stocks in the allocation dictionary.
    """

    if allocation == {}:
        return 0
    
    df_assets = df_tickers[allocation.keys()].iloc[-1]
    df_weights = list(allocation.values())
    portfolio = df_assets.mul(df_weights).sum()
    
    return portfolio


def portfolio_values(df_tickers: pd.DataFrame, allocation: Dict) -> pd.DataFrame:
    """
    Calculates the total value of the portfolio based on the latest price in
    the df_tickers DataFrame and the allocation of shares for each ticker.

    Args:
        df_tickers (pd.DataFrame): A DataFrame containing the latest stock prices for each ticker.
        allocation (dict): A dictionary containing the allocation of shares for each ticker.

    Returns:
        pd.DataFrame: A DataFrame containing the total value of
            the portfolio for each date in the df_tickers DataFrame.
    """
    df_assets = df_tickers[allocation.keys()]
    df_weights = allocation.values()
    portfolio = df_assets.mul(df_weights, axis=1).sum(axis=1)
    
    return portfolio


def calculate_each_year_allocation(df_tickers: TickerManager, nb_year_look_back: int) -> Tuple[List[float], pd.DataFrame]:
    """
    Calculates the allocation of a portfolio for each year based on the
    latest stock prices in the df_tickers DataFrame.

    Args:
        df_tickers (pd.DataFrame): A DataFrame containing the latest stock prices for each ticker.
        nb_year_look_back (int): The number of years to look back when calculating the allocation.

    Returns:
        Tuple[List[float], pd.DataFrame]: A tuple containing a list of the 
        total value of the portfolio for each year and a DataFrame containing the 
        total value of the portfolio for each date in the df_tickers DataFrame.
    """

    first_year = df_tickers.tickers.index[0].year
    first_year_calculation = first_year + nb_year_look_back
    last_year = df_tickers.tickers.index[-1].year
   
    print(f"First year: {first_year}")
     
    money = 10000
    dis_allocation = {}
    
    money_values = []
    df_money = pd.DataFrame()
    
    for i in range(first_year_calculation, last_year + 1):
        if dis_allocation != {}:
            close = df_tickers.get_ticket_between_dates(str(i), str(i + 1))
            df_porforlio_value = portfolio_values(close, dis_allocation)
            df_porforlio_value += money
    
            df_money = pd.concat([df_money, df_porforlio_value], axis=0)
        
        df_year = df_tickers.get_ticket_between_dates(str(i - nb_year_look_back), str(i + 1))
        money += sell_all_stocks(df_year, dis_allocation)
        money_values.append(money)
        
        allocation = optimize_portfolio(df_year, 'max_sharpe', gamma=0.1)
        dis_allocation, money = discrete_allocation(df_year, allocation, money)        
        
    money += sell_all_stocks(df_tickers.tickers, dis_allocation) 
    return money_values, df_money
