import argparse

from src.tickers import TickerDownloader, TickerManager

from src.helpers_allocation import (
    calculate_each_year_allocation,
)

from src.pdf.generate_report import generate_report

def parse_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PortFin - Portfolio Allocation')
    
    parser.add_argument('-y', '--years', type=int, default=20, help='Number of years of data to download.')
    parser.add_argument('-w', '--window', type=int, default=5, help='Number of years needed to backtest the stock.')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_argument()
    
    ticker_downloader = TickerDownloader()
   
    df_tickers = ticker_downloader.download_tickers_sp500(args.years)["Close"]
    df_tickers = TickerManager(df_tickers)
    
    sp500_market = ticker_downloader.download_tickers_data(['^GSPC'], 20, keep_null=True)["Close"]
    
    money_value, df_money = calculate_each_year_allocation(df_tickers, args.window)
    
    generate_report(df_money, sp500_market)
    