import pandas as pd
import yfinance as yf

from typing import List

def get_all_tickers_sp500() -> pd.DataFrame:
    """Get all tickers from S&P 500 (Wikipedia).
    'https://en.wikipedia.org/wiki/List_of_S%26P_500_companies'

    Returns:
        pd.DataFrame: DataFrame of all the tickers.
    """
    
    sp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return sp500


def format_sp500_tickers(tickers: pd.DataFrame) -> pd.DataFrame:
    """
    Formats a pandas DataFrame containing S&P 500 ticker data.

    Args:
        tickers (pd.DataFrame): A pandas DataFrame containing S&P 500 ticker data.

    Returns:
        pd.DataFrame: A pandas DataFrame with the following columns:
            - Ticker: The ticker symbol for the stock.
            - Name: The name of the company.
            - Sector: The sector the company operates in.
            - Sub-Industry: The sub-industry the company operates in.
            - Added: The date the company was added to the S&P 500 index.
    """

    tickers = tickers.drop(columns=["CIK", "Founded", "Headquarters Location"])
    tickers = tickers.rename(columns={"Symbol": "Ticker", 
                                      "Security": "Name", 
                                      "GICS Sector": "Sector", 
                                      "GICS Sub-Industry": "Sub-Industry",
                                      "Date added": "Added"})
    tickers["Added"] = pd.to_datetime(tickers["Added"], errors='coerce')
    tickers = tickers.set_index("Ticker")

    return tickers


def filter_out_tickers(tickers: pd.DataFrame, years: int) -> pd.DataFrame:
    """Filter out tickers that have less than years of data.

    Args:
        tickers (pd.DataFrame): DataFrame of all the tickers.
        years (int): Number of years of data to filter out.

    Returns:
        pd.DataFrame: DataFrame of all the tickers that have more than years of data.
    """
    
    years = pd.to_datetime("today").year - years  
    tickers_filtered = tickers[tickers["Added"] < pd.to_datetime(str(years))]

    return tickers_filtered


def download_tickers_data(tickers: List[str], years: int) -> pd.DataFrame:
    """Download the data of the tickers for the last years.

    Args:
        tickers (List[str]): List of tickers to download the data from.
        years (int): Number of years needed.

    Returns:
        pd.DataFrame: DataFrame of all the tickers data.
    """
    
    current_year = pd.to_datetime("today").year
    end = f"{current_year}-01-01"
    years = current_year - years
    start = f"{years}-01-01"
    
    tickers_data = yf.download(tickers, start=start, end=end)
    return tickers_data


def delete_all_null_tickers(tickers: pd.DataFrame) -> pd.DataFrame:
    """
    Deletes all tickers with null values from a pandas DataFrame.

    Args:
        tickers (pd.DataFrame): A pandas DataFrame containing ticker data.

    Returns:
        pd.DataFrame: A pandas DataFrame with all tickers that have null values removed.
    """

    sum_null = tickers.isnull().sum()
    null_tickers = {i[1] for i in sum_null[sum_null > 0].index}
    
    return tickers.drop(columns=null_tickers, level=1)

    
def get_ticket_between_dates(tickers: pd.DataFrame, start: str, end: str) -> pd.DataFrame:
    """Get the tickers data between two dates.

    Args:
        tickers (pd.DataFrame): DataFrame of all the tickers data.
        start (str): Start date.
        end (str): End date.

    Returns:
        pd.DataFrame: DataFrame of all the tickers data between two dates.
    """
    
    start = pd.to_datetime(start)
    end = pd.to_datetime(end)
    
    all_tickers = tickers.loc[start:end]
    return all_tickers 