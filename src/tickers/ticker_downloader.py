import os
import json
import yfinance as yf
import pandas as pd
from typing import List, Dict

class TickerDownloader:
    SP500_COMPANIES = 'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'
    FOLDER = './data'
    FILE_DATA = "./data/sp500_tickers.csv"
    FILE_META = "./data/sp500_tickers_meta.json"
    

    def __reload_download_tickers(self, tickers: List, start: str, end: str, force_reload: bool = False) -> pd.DataFrame:
        """Reloads and downloads the tickers data.
           
        This function checks if the file with ticker data exists. If it does not exist or if force_reload is True,
        it downloads the ticker data for the specified date range and saves it to the file. If the file exists,
        it checks the metadata to see if the requested date range is covered. If not, it downloads the missing data
        and appends it to the existing data.

        Args:
            tickers (List): List of tickers to download.
            start (str): Start date.
            end (str): End date.
            force_reload (bool, optional): Whether to force a reload of the ticker data. Defaults to False.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the ticker data.
        """
        
        file = TickerDownloader.FILE_DATA
        meta = TickerDownloader.FILE_META
        folder = TickerDownloader.FOLDER
        
        if not os.path.isfile(file) or force_reload:
            print(f"File {file} not found, creating new one...")
            df = self.download_tickers_data(tickers, start=start, end=end)

            if not os.path.exists(folder):
                os.makedirs(folder)
            df.to_csv(file)

            with open(meta, 'w') as fp:
                meta_data = {"start": start, "end": end}
                json.dump(meta_data, fp)
                
            return df
            
        df = pd.read_csv(file, header=[0,1], index_col=0)
        df.index = pd.to_datetime(df.index)

        meta_data = None
        with open(meta, 'r') as fp:
            meta_data = json.load(fp)

        if pd.to_datetime(start) < pd.to_datetime(meta_data["start"]):
            print(f"Start date, {start}, is before meta start date, {meta_data['start']}, downloading missing data...")
            df = self.download_tickers_data(tickers, start=start, end=meta_data["start"]).append(df)
            df.to_csv(file)
            meta_data["start"] = start

        if pd.to_datetime(end) > pd.to_datetime(meta_data["end"]):
            print(f"End date, {end}, is after meta end date, {meta_data['end']}, downloading missing data...")
            df = df.append(self.download_tickers_data(tickers, start=meta_data["end"], end=end))
            df.to_csv(file)
            meta_data["end"] = end
            
        with open(meta, 'w') as fp:
            json.dump(meta_data, fp)

        return df.loc[start:end]

    @property
    def sp500(self) -> pd.DataFrame:
        return self.__sp500 
    
    def __init__(self):
        self.__sp500 = None

    def get_all_sp500_tickers_raw(self) -> pd.DataFrame:
        """Returns the raw S&P 500 tickers data.

        This function checks if the S&P 500 data has already been loaded. If not, it loads the data from the URL
        specified in the SP500_COMPANIES attribute and stores it in the __sp500 attribute.

        Returns:
            pd.DataFrame: A pandas DataFrame containing the S&P 500 tickers.
        """
        
        if self.__sp500 is None:
            self.__sp500 = pd.read_html(TickerDownloader.SP500_COMPANIES)[0]
        
        return self.__sp500

    def get_all_sp500_tickers_filtered(self) -> pd.DataFrame:
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
   
        return tickers
    
    def download_tickers_data(self, tickers: List[str], start: str = None, end: str = None) -> pd.DataFrame:
        """Downloads the tickers data.

        This function downloads the data for the specified tickers for the specified date range using the yfinance library.
        It prints a message before and after the download process.

        Args:
            tickers (List[str]): List of tickers to download.
            start (str, optional): Start date. Defaults to None.
            end (str, optional): End date. Defaults to None.

        Returns:
            pd.DataFrame: Pandas DataFrame containing the ticker data.
        """
        
        print_tickers = str(tickers)
        if len(tickers) > 5:
            print_tickers = str(tickers[:2]) + "..." + str(tickers[-2:])
            
        print(f"Downloading {len(tickers)} tickers: {print_tickers} from {start} to {end}...")
        tickers_data = yf.download(tickers, start=start, end=end, progress=False)
        print("Finished downloading.")
        
        return tickers_data
    
    def download_tickers_data_since(self, tickers: List[str], x_years: int) -> pd.DataFrame:
        """Downloads the tickers data since a certain number of years.

        This function calculates the start date by subtracting x_years from the current year and setting the month and day to January 1.
        It then calls the download_tickers_data function with the calculated start date and the current date as the end date.

        Args:
            tickers (List[str]): List of tickers to download.
            x_years (int): Number of years of data to download.

        Returns:
            pd.DataFrame: Pandas DataFrame containing the ticker data.
        """
        
        end = str(pd.to_datetime("today").date())
        years = pd.to_datetime("today").year - x_years
        start = f"{years}-01-01"

        return self.download_tickers_data(tickers, start=start, end=end)
    
    def download_tickers_sp500(self, x_years: int, force_reload: bool = False) -> pd.DataFrame:
        """Downloads the S&P 500 tickers data.

        This function calculates the start date by subtracting x_years from the current year and setting the month and day to January 1.
        It then gets the list of S&P 500 tickers, reloads and downloads the tickers data for the calculated date range.

        Args:
            x_years (int): Number of years of data to download.
            force_reload (bool, optional): Whether to force a reload of the ticker data. Defaults to False.

        Returns:
            pd.DataFrame: Pandas DataFrame containing the ticker data.
        """

        end = str(pd.to_datetime("today").date())
        years = pd.to_datetime("today").year - x_years
        start = f"{years}-01-01"
        
        sp500_tickers = self.get_all_sp500_tickers_filtered().index.tolist()
        reloaded = self.__reload_download_tickers(sp500_tickers, start, end, force_reload)
        
        return reloaded

    def generate_allocation_sectors(self, allocation: Dict) -> Dict:
        """Generates the allocation sectors.

        This function takes a dictionary with ticker symbols as keys and allocation percentages as values.
        It filters the S&P 500 tickers data to include only the tickers in the allocation dictionary.
        It then groups the filtered data by sector and calculates the sum of the allocation percentages for each sector.

        Args:
            allocation (Dict): A dictionary containing the allocation for each year.

        Returns:
            Dict: A dictionary containing the allocation for each sector.
        """
        
        keys = allocation.keys()
        sectors_keys = self.get_all_sp500_tickers_filtered()[self.get_all_sp500_tickers_filtered().index.isin(keys)]
        sectors_keys = sectors_keys["Sector"].to_frame()
        sectors_keys["Allocation"] = sectors_keys.index.map(allocation)
        
        sectors = sectors_keys.groupby("Sector").sum().to_dict()["Allocation"]

        return sectors