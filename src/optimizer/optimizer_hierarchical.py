from pypfopt import risk_models
from pypfopt import hierarchical_portfolio

import pandas as pd
from typing import Dict

from .optimizer_base import OptimizerBase


class OptimizerHierarchical(OptimizerBase):
    """A Hierarchical Risk Parity optimizer.

    This class extends the OptimizerBase class and implements a Hierarchical Risk Parity optimizer.

    Attributes:
        min_weight (float): The minimum weight for an asset in the portfolio. Default is 0.05.
    """

    def __init__(self, min_weight: float = 0.05):
        """Constructs all the necessary attributes for the OptimizerHierarchical object.

        Args:
            min_weight (float): The minimum weight for an asset in the portfolio. Default is 0.05.
        """

        self.min_weight = min_weight
        
    def __call__(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculate the optimal portfolio weights using Hierarchical Risk Parity.

        Args:
            df (pd.DataFrame): A DataFrame where each column represents a different asset, and each row represents a different time period.

        Returns:
            Dict[str, float]: A dictionary where the keys are the asset names and the values are the corresponding weights.
        """

        S = risk_models.semicovariance(df)
        ef = hierarchical_portfolio.HRPOpt(df, S)

        ef.optimize()
        
        cleaned_weights = ef.clean_weights()

        return {i: cleaned_weights[i] for i in cleaned_weights if cleaned_weights[i] > self.min_weight}