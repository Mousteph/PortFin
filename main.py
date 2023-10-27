import argparse

from src.tickers import TickerDownloader
from src.functions import generate_allocation, generate_portfolio
from src.pdf.generate_report import generate_report

def parse_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PortFin - Portfolio Allocation')
    
    parser.add_argument('-y', '--years', type=int, default=20, help='Number of years of data to download.')
    parser.add_argument('-w', '--window', type=int, default=5, help='Number of years needed to backtest the stock.')
    parser.add_argument('-o', '--optimizer', type=str, default='max_sharpe', help='The optimizer to use, max_sharpe or min_volatility, default is max_sharpe.')
    parser.add_argument('-g', '--gamma', type=float, default=0.1, help='The regularization parameter, default is 0.1.')
    parser.add_argument('-m', '--money', type=int, default=1000, help='The initial investment, default is 1000.')
    parser.add_argument('-n', '--name', type=str, default='report.pdf', help='The name of the PDF report, default is report.pdf.')
    parser.add_argument('-f', '--full', action='store_true', help='Whether to generate a full report or not. Default is False.')
    
    return parser.parse_args()

if __name__ == '__main__':
    args = parse_argument()
    
    ticker_downloader = TickerDownloader()

    df_tickers = ticker_downloader.download_tickers_sp500(20)["Close"]

    sp500_market = ticker_downloader.download_tickers_data(['^GSPC'], 20, keep_null=True)["Close"]

    allocations = generate_allocation(df_tickers, 5, args.optimizer, args.gamma)
    portfolio = generate_portfolio(df_tickers, allocations, args.money)
    market = sp500_market.loc[portfolio.index[0]:]

    generate_report(portfolio, market, allocations, ticker_downloader, args.name, args.full)
    