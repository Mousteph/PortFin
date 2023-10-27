import os
from typing import List, Dict
import pandas as pd
import yfinance as yf


class TickerDownloader:
    """A class used to download and filter ticker data.

    Attributes:
        SP500_COMPANIES (str): The URL of the S&P 500 companies list.
        FOLDER (str): The folder where the ticker data is saved.
        file_name (function): A lambda function that returns the filename of the ticker data file.

    Methods:
        __delete_all_null_tickers(tickers: pd.DataFrame) -> pd.DataFrame:
            Deletes all tickers with null values from a pandas DataFrame.
        __reload_download_tickers(start: str, end: str) -> pd.DataFrame:
            Reloads the ticker data from a file if it exists.
        get_all_sp500_tickers_raw() -> pd.DataFrame:
            Returns a pandas DataFrame containing the raw S&P 500 ticker data.
        get_all_sp500_tickers_filtered(x_years: int = None) -> pd.DataFrame:
            Returns a pandas DataFrame containing the filtered S&P 500 ticker data.
        download_tickers_data(tickers: List[str], start: str, end: str, keep_null: bool = False) -> pd.DataFrame:
            Downloads ticker data for a list of tickers and a specified date range.
        download_tickers_sp500(x_years: int, keep_null: bool = False, force_reload: bool = False) -> pd.DataFrame:
            Downloads ticker data for all S&P 500 tickers and a specified date range.
        generate_allocation_sectors(self, allocations: Dict) -> Dict:
            Generates a dictionary of sector allocations for each year.
    """

    SP500_COMPANIES = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    FOLDER = './data'
    file_name = lambda start, end: f"{TickerDownloader.FOLDER}/sp500_tickers_{start}_{end}.csv"
    
    def __delete_all_null_tickers(self, tickers: pd.DataFrame) -> pd.DataFrame:
        """Deletes all tickers with null values from a pandas DataFrame.

        Args:
            tickers (pd.DataFrame): A pandas DataFrame containing ticker data.

        Returns:
            pd.DataFrame: A pandas DataFrame with all tickers that have null values removed.
        """

        sum_null = tickers.isnull().sum()
        null_tickers = {i[1] for i in sum_null[sum_null > 0].index}
        
        return tickers.drop(columns=null_tickers, level=1)
    
    def __reload_download_tickers(self, start: str, end: str) -> pd.DataFrame:
        """Reloads the ticker data from a file if it exists.

        Args:
            start (str): The start date of the ticker data.
            end (str): The end date of the ticker data.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the ticker data if it exists, otherwise None.
        """

        file = TickerDownloader.file_name(start, end)

        if os.path.isfile(file):
            df = pd.read_csv(file, header=[0,1], index_col=0)
            df.index = pd.to_datetime(df.index)
            return df
        
        return None
       
    @property
    def sp500(self) -> pd.DataFrame:
        """pd.DataFrame: A pandas DataFrame containing the filtered S&P 500 ticker data."""

        return self.__sp500 
    
    def __init__(self):
        self.__sp500 = None

    def get_all_sp500_tickers_raw(self) -> pd.DataFrame:
        """Returns a pandas DataFrame containing the raw S&P 500 ticker data.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the raw S&P 500 ticker data.
        """

        if self.__sp500 is None:
            self.__sp500 = pd.read_html(TickerDownloader.SP500_COMPANIES)[0]
        
        return self.__sp500

    def get_all_sp500_tickers_filtered(self, x_years: int = None) -> pd.DataFrame:
        """Returns a pandas DataFrame containing the filtered S&P 500 ticker data.

        Args:
            x_years (int, optional): The number of years to filter the ticker data by. Defaults to None.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the filtered S&P 500 ticker data.
        """

        cols_name = {
            "Symbol": "Ticker", 
            "Security": "Name", 
            "GICS Sector": "Sector", 
            "GICS Sub-Industry": "Sub-Industry",
            "Date added": "Added"
        }
        
        tickers = self.get_all_sp500_tickers_raw()

        tickers = tickers.drop(columns=["CIK", "Founded", "Headquarters Location"])
        tickers = tickers.rename(columns=cols_name) 
        tickers["Added"] = pd.to_datetime(tickers["Added"], errors='coerce')
        tickers = tickers.set_index("Ticker")
   
        if x_years is not None: 
            years = pd.to_datetime("today").year - x_years  
            tickers = tickers[tickers["Added"] < pd.to_datetime(str(years))]

        return tickers
    
    def download_tickers_data(self, tickers: List[str], x_years: int = None, start: str = None, end: str = None, keep_null: bool = False) -> pd.DataFrame:
        """Downloads ticker data for a list of tickers and a specified date range.

        Args:
            tickers (List[str]): A list of tickers to download data for.
            x_years (int, optional): The number of years to filter the ticker data by. Defaults to None.
            start (str, optional): The start date of the ticker data. Defaults to None.
            end (str, optional): The end date of the ticker data. Defaults to None.
            keep_null (bool, optional): Whether to keep tickers with null values. Defaults to False.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the downloaded ticker data.
        """
        
        if x_years is not None:
            current_year = pd.to_datetime("today").year
            end = f"{current_year}-01-01"
            years = current_year - x_years
            start = f"{years}-01-01"

        print_tickers = str(tickers)
        if len(tickers) > 5:
            print_tickers = str(tickers[:2]) + "..." + str(tickers[-2:])
            
        print(f"Downloading {print_tickers} tickers from {start} to {end}...")
        tickers_data = yf.download(tickers, start=start, end=end, progress=False)
        print(f"Downloaded {print_tickers} tickers from {start} to {end}.")
        
        if not keep_null:
            tickers_data = self.__delete_all_null_tickers(tickers_data)
        
        return tickers_data
    
    def download_tickers_sp500(self, x_years: int, keep_null: bool = False, force_reload: bool = False) -> pd.DataFrame:
        """Downloads ticker data for all S&P 500 tickers and a specified date range.

        Args:
            x_years (int): The number of years to filter the ticker data by.
            keep_null (bool, optional): Whether to keep tickers with null values. Defaults to False.
            force_reload (bool, optional): Whether to force a reload of the ticker data. Defaults to False.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the downloaded ticker data.
        """

        current_year = pd.to_datetime("today").year
        end = f"{current_year}-01-01"
        years = current_year - x_years
        start = f"{years}-01-01"
        
        reloaded = self.__reload_download_tickers(start, end)
        if not force_reload and reloaded is not None:
            print(f"Already downloaded S&P500 tickers from {start} to {end} "\
                  f"founded in {TickerDownloader.file_name(start, end)}")
            return reloaded
        
        sp500_tickers = self.get_all_sp500_tickers_filtered(x_years).index.tolist()
        df = self.download_tickers_data(sp500_tickers, start=start, end=end, keep_null=keep_null)
        
        if not os.path.exists(TickerDownloader.FOLDER):
            os.makedirs(TickerDownloader.FOLDER)
        
        df.to_csv(TickerDownloader.file_name(start, end))
        
        return df

    def generate_allocation_sectors(self, allocation: Dict) -> Dict:
        """Generates a dictionary of sector allocations for each year.

        Args:
            allocation (Dict): A dictionary containing the asset allocation weights.

        Returns:
            Dict: A dictionary of sector allocations for each year.
        """
        
        keys = allocation.keys()
        sectors_keys = self.get_all_sp500_tickers_filtered()[self.get_all_sp500_tickers_filtered().index.isin(keys)]
        sectors_keys = sectors_keys["Sector"].to_frame()
        sectors_keys["Allocation"] = sectors_keys.index.map(allocation)
        
        sectors = sectors_keys.groupby("Sector").sum().to_dict()["Allocation"]

        return sectors