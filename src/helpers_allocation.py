import pandas as pd
from src.tickers import TickerManager
from src.optimizer import optimize_portfolio, discrete_allocation

from typing import Tuple, List


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
            df_porforlio_value = df_tickers.portfolio_value(dis_allocation, str(i), str(i + 1))
            df_porforlio_value += money
    
            df_money = pd.concat([df_money, df_porforlio_value], axis=0)
        
        df_year = df_tickers.get_ticket_between_dates(str(i - nb_year_look_back), str(i + 1))
        money += df_tickers.portfolio_value(dis_allocation, str(i - nb_year_look_back), str(i + 1), True).get(0, 0)
        money_values.append(money)
        
        allocation = optimize_portfolio(df_year, 'max_sharpe', gamma=0.1)
        dis_allocation, money = discrete_allocation(df_year, allocation, money)        
        
    money += df_tickers.portfolio_value(dis_allocation, last=True).get(0, 0)
    return money_values, df_money
