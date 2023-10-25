import pandas as pd
import matplotlib.pyplot as plt
from src.helpers_tickers import get_ticket_between_dates

from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import objective_functions

from typing import Dict, Tuple, List


def get_cumulative_returns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Calculates the cumulative returns of a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the returns data.

    Returns:
        pd.DataFrame: A DataFrame containing the cumulative returns.
    """

    return (1 + df.pct_change()).cumprod() - 1


def plot_stock(df: pd.DataFrame, title: str):
    """
    Plots the stock prices from a given DataFrame.

    Args:
        df (pd.DataFrame): The DataFrame containing the stock prices.
        title (str): The title of the plot.

    Returns:
        None
    """
    plt.figure(figsize=(14, 7))
    plt.plot(df, linewidth=2)
    plt.title(title)
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.show()


def optimize_portfolio(df: pd.DataFrame, gamma: float = 0) -> Dict[str, float]:
    """
    Optimizes a portfolio of assets based on historical returns and covariance.

    Args:
        df (pd.DataFrame): The DataFrame containing the asset prices.
        gamma (int): The regularization parameter for L2 regularization.

    Returns:
        Dict[str, float]: A dictionary containing the optimized weights for each asset.
    """

    mu = expected_returns.mean_historical_return(df)
    S = CovarianceShrinkage(df).ledoit_wolf()
    
    ef = EfficientFrontier(mu, S)
    ef.add_objective(objective_functions.L2_reg, gamma=gamma)
    
    ef.max_sharpe()
    # ef.min_volatility()
    cleaned_weights = ef.clean_weights(0.01, 3)

    return {i: cleaned_weights[i] for i in cleaned_weights if cleaned_weights[i] > 0}


def discrete_allocation(df: pd.DataFrame, weights: dict,
                        total_portfolio_value: int = 10000) -> Tuple[Dict[str, int], float]:
    """
    Calculates the discrete allocation of assets based on a given set of weights.

    Args:
        df (pd.DataFrame): The DataFrame containing the asset prices.
        weights (dict): A dictionary containing the weights for each asset.
        total_portfolio_value (int): The total value of the portfolio.

    Returns:
        Tuple[Dict[str, int], float]: A tuple containing the allocation of assets and the leftover cash.
    """
    latest_prices = get_latest_prices(df)

    da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=total_portfolio_value)
    allocation, leftover = da.greedy_portfolio()
    
    return allocation, leftover

def get_cumulative_returns_portfolio(df_tickers: pd.DataFrame, allocation: Dict) -> pd.DataFrame:
    """
    Calculates the cumulative returns of a portfolio based on a given set of allocations.

    Args:
        df_tickers (pd.DataFrame): The DataFrame containing the asset prices.
        allocation (Dict): A dictionary containing the allocation of assets.

    Returns:
        pd.DataFrame: A DataFrame containing the cumulative returns of the portfolio.
    """

    df_assets = df_tickers[allocation.keys()]
    df_weights = allocation.values()
    
    portfolio = df_assets.pct_change().mul(df_weights, axis=1).sum(axis=1)
    return (1 + portfolio).cumprod() - 1

    
def sell_all_stocks(df_tickers: pd.DataFrame, allocation: dict) -> float:
    """
    Calculates the total value of all stocks in the allocation dictionary
    based on the latest price in the df_tickers DataFrame.

    Args:
        df_tickers (pd.DataFrame): A DataFrame containing the latest stock prices for each ticker.
        allocation (dict): A dictionary containing the allocation of shares for each ticker.

    Returns:
        float: The total value of all stocks in the allocation dictionary.
    """

    total = 0
    
    for ticker, shares in allocation.items():
        total += df_tickers[ticker].iloc[-1] * shares
    
    return total


def portfolio_values(df_tickers: pd.DataFrame, allocation: dict) -> pd.DataFrame:
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


def calculate_each_year_allocation(df_tickers: pd.DataFrame, nb_year_look_back: int) -> Tuple[List[float], pd.DataFrame]:
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

    df_tickers_close = df_tickers["Close"]
    
    first_year = df_tickers_close.index[0].year
    first_year_calculation = first_year + nb_year_look_back
    last_year = df_tickers_close.index[-1].year
    
    money = 10000
    dis_allocation = {}
    
    money_values = []
    df_money = pd.DataFrame()
    
    for i in range(first_year_calculation, last_year + 1):
        if dis_allocation != {}:
            df_porforlio_value = portfolio_values(get_ticket_between_dates(df_tickers_close, 
                                                                           str(i), str(i + 1)), 
                                                  dis_allocation)
            df_porforlio_value += money
    
            df_money = pd.concat([df_money, df_porforlio_value], axis=0)
        
        df_year = get_ticket_between_dates(df_tickers_close, str(i - nb_year_look_back), str(i + 1))
        money += sell_all_stocks(df_year, dis_allocation)
        money_values.append(money)
        
        allocation = optimize_portfolio(df_year, 0.1)
        dis_allocation, money = discrete_allocation(df_year, allocation, money)        
        
    money += sell_all_stocks(df_tickers_close, dis_allocation) 
    return money_values, df_money


def compare_porfolio_to_market(portfolio: pd.DataFrame, market: pd.DataFrame) -> pd.DataFrame:
    """
    Compares the cumulative returns of a portfolio to a market index.

    Args:
        portfolio (pd.DataFrame): A DataFrame containing the total
            value of the portfolio for each date.
        market (pd.DataFrame): A DataFrame containing the total
            value of the market index for each date.

    Returns:
        pd.DataFrame: A DataFrame containing the cumulative returns of
            the portfolio and the market index.
    """

    first_date = portfolio.index[0]
    last_date = portfolio.index[-1]
    
    df = pd.concat([portfolio, market.loc[first_date:last_date]], axis=1)
    cum_returns = get_cumulative_returns(df)

    plot_stock(cum_returns, 'Cumulative Returns Portfolio vs Market')