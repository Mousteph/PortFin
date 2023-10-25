import pandas as pd


class TickerManager:
    """A class used to manage ticker data.

    Attributes:
        tickers (pd.DataFrame): A pandas DataFrame containing ticker data.

    Methods:
        get_ticket_between_dates(start: str = None, end: str = None) -> pd.DataFrame:
            Returns a pandas DataFrame containing ticker data between two dates.

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