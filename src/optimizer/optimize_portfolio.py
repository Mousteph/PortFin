from pypfopt import EfficientFrontier
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from pypfopt import objective_functions

import pandas as pd
from typing import Dict, Tuple

def optimize_portfolio(df: pd.DataFrame, optizer: str = 'max_sharpe', gamma: float = 0) -> Dict[str, float]:
    """Optimizes a portfolio using the Efficient Frontier algorithm.

    Args:
        df (pd.DataFrame): A pandas DataFrame containing the asset returns.
        optizer (str, optional): The optimization objective. Must be either "max_sharpe" or "min_volatility". Defaults to 'max_sharpe'.
        gamma (float, optional): The regularization parameter. Defaults to 0.

    Returns:
        Dict[str, float]: A dictionary containing the optimized weights for each asset.
    """
    mu = expected_returns.mean_historical_return(df)
    S = CovarianceShrinkage(df).ledoit_wolf()
    
    ef = EfficientFrontier(mu, S)
    ef.add_objective(objective_functions.L2_reg, gamma=gamma)
    
    if optizer == 'max_sharpe':
        ef.max_sharpe()
    elif optizer == 'min_volatility':
        ef.min_volatility()
    else:
        raise ValueError('Invalid optizer. Must be either "max_sharpe" or "min_volatility".')
    
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