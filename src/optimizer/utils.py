from pypfopt.discrete_allocation import DiscreteAllocation

import pandas as pd
from typing import Dict, Tuple

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

    latest_prices = df.ffill().iloc[0]
    da = DiscreteAllocation(weights, latest_prices, total_portfolio_value=total_portfolio_value)
    allocation, leftover = da.greedy_portfolio()
    
    return allocation, leftover