from pypfopt import EfficientFrontier
from pypfopt.risk_models import CovarianceShrinkage
from pypfopt import expected_returns
from pypfopt import objective_functions

import pandas as pd
from typing import Dict

from .optimizer_base import OptimizerBase


class OptimizerEfficient(OptimizerBase):
    """Class for optimizing a portfolio using the Efficient Frontier algorithm.

    Attributes:
        optimizer (str): The optimization objective to use. Must be either "max_sharpe" or "min_volatility".
        gamma (float): The regularization parameter for the L2 regularization objective.

    Methods:
        __call__: Optimizes a portfolio using the Efficient Frontier algorithm.
    """

    def __init__(self, optimizer: str = "max_sharpe", gamma: float = 0.1):
        """Initializes a new instance of the OptimizerEfficient class.

        Args:
            optimizer (str): The optimization objective to use. Must be either "max_sharpe" or "min_volatility".
            gamma (float): The regularization parameter for the L2 regularization objective.
        """

        self.optimizer = optimizer
        self.gamma = gamma
        
    def __call__(self, df: pd.DataFrame) -> Dict[str, float]:
        """Optimizes a portfolio using the Efficient Frontier algorithm.

        Args:
            df (pd.DataFrame): A pandas DataFrame containing the asset returns.
        
        Returns:
            Dict[str, float]: A dictionary containing the optimized weights for each asset.

        Raises:
            ValueError: If the optimizer parameter is not "max_sharpe" or "min_volatility".
        """

        mu = expected_returns.mean_historical_return(df)
        S = CovarianceShrinkage(df).ledoit_wolf()
        
        ef = EfficientFrontier(mu, S)
        ef.add_objective(objective_functions.L2_reg, gamma=self.gamma)
        
        if self.optimizer == 'max_sharpe':
            ef.max_sharpe()
        elif self.optimizer == 'min_volatility':
            ef.min_volatility()
        else:
            raise ValueError('Invalid optimizer. Must be either "max_sharpe" or "min_volatility".')
        
        cleaned_weights = ef.clean_weights()

        return {i: cleaned_weights[i] for i in cleaned_weights if cleaned_weights[i] > 0}