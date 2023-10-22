import pandas as pd
import matplotlib.pyplot as plt

from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import objective_functions

from typing import Dict, Tuple


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
    S = risk_models.sample_cov(df)
    
    ef = EfficientFrontier(mu, S)
    ef.add_objective(objective_functions.L2_reg, gamma=gamma)
    
    ef.max_sharpe()
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