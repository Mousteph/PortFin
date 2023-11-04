import pandas as pd
from typing import Dict

class OptimizerBase:
    """Base class for portfolio optimization.
    
    Equally weights all assets in the portfolio.
    """

    def __call__(self, df: pd.DataFrame) -> Dict[str, float]:
        """Calculates the portfolio weights for a given DataFrame.

        Args:
            df: A pandas DataFrame containing the asset returns.

        Returns:
            A dictionary containing the portfolio weights for each asset.
        """

        cols = df.columns
        return {i: 1 / len(cols) for i in cols}