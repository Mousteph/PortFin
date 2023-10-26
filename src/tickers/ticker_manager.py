import pandas as pd
from typing import Dict


class TickerManager:
    """A class used to manage ticker data.

    Attributes:
        tickers (pd.DataFrame): A pandas DataFrame containing ticker data.

    Methods:
        get_ticket_between_dates(start: str = None, end: str = None) -> pd.DataFrame:
            Returns a pandas DataFrame containing ticker data between two dates.
        portfolio_value(allocation: Dict, start: str = None, end: str = None, last: bool = False) -> pd.DataFrame:
            Returns a pandas DataFrame containing the portfolio value between two dates.
    """

    def __init__(self, tickers: pd.DataFrame):
        """Initializes the TickerManager object.

        Args:
            tickers (pd.DataFrame): A pandas DataFrame containing ticker data.
        """

        self.tickers = tickers
        
    def get_ticket_between_dates(self, start: str = None, end: str = None) -> pd.DataFrame:
        """Returns a pandas DataFrame containing ticker data between two dates.

        Args:
            start (str, optional): The start date of the ticker data. Defaults to None.
            end (str, optional): The end date of the ticker data. Defaults to None.

        Returns:
            pd.DataFrame: A pandas DataFrame containing ticker data between two dates.
        """

        start = pd.to_datetime(start) if start is not None else self.tickers.index.min()
        end = pd.to_datetime(end) if end is not None else self.tickers.index.max()
        
        all_tickers = self.tickers.loc[start:end]
        return all_tickers 


    def portfolio_value(self, allocation: Dict, start: str = None, end: str = None, last: bool = False) -> pd.DataFrame:
        """Returns a pandas DataFrame containing the portfolio value between two dates.

        Args:
            allocation (Dict): A dictionary containing the asset allocation weights.
            start (str, optional): The start date of the portfolio value. Defaults to None.
            end (str, optional): The end date of the portfolio value. Defaults to None.
            last (bool, optional): If True, returns the portfolio value for the last available date. Defaults to False.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the portfolio value between two dates.
        """
        
        if allocation == {}:
            return pd.DataFrame()
        
        start = pd.to_datetime(start) if start is not None else self.tickers.index.min()
        end = pd.to_datetime(end) if end is not None else self.tickers.index.max()

        df_assets = self.tickers[allocation.keys()].loc[start:end]
        
        if last:
            last_i = df_assets.index.max()
            df_assets = df_assets.loc[last_i:last_i]
        
        df_weights = allocation.values()
        portfolio = df_assets.mul(df_weights, axis=1).sum(axis=1)
        
        return portfolio