import argparse

from src.tickers import TickerDownloader
from src.functions import generate_allocation, generate_portfolio
from src.pdf.generate_report import generate_report

def parse_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PortFin - Portfolio Allocation')
    
    parser.add_argument('-y', '--years', type=int, default=20, help='Number of years of data to download.')
    parser.add_argument('-w', '--window', type=int, default=5, help='Number of years needed to backtest the stock.')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_argument()
    
    ticker_downloader = TickerDownloader()

    df_tickers = ticker_downloader.download_tickers_sp500(20)["Close"]

    sp500_market = ticker_downloader.download_tickers_data(['^GSPC'], 20, keep_null=True)["Close"]

    allocations = generate_allocation(df_tickers, 5)
    portfolio = generate_portfolio(df_tickers, allocations, 1000)
    market = sp500_market.loc[portfolio.index[0]:]

    generate_report(portfolio, market, allocations, ticker_downloader)
    