import pandas as pd

    
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