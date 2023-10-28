import argparse

from src.tickers import TickerDownloader
from src.functions import generate_allocation, generate_portfolio
from src.pdf.generate_report import generate_report, StructPortfolio
from src.optimizer import OptimizerEfficient, OptimizerBase

def parse_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PortFin - Portfolio Allocation')
    
    parser.add_argument('-y', '--years', type=int, default=30, help='Number of years of data to download.')
    parser.add_argument('-w', '--window', type=int, default=7, help='Number of years needed to backtest the stock.')
    parser.add_argument('-o', '--optimizer', type=str, default='max_sharpe', help='The optimizer to use, max_sharpe or min_volatility, default is max_sharpe.')
    parser.add_argument('-g', '--gamma', type=float, default=0.1, help='The regularization parameter, default is 0.1.')
    parser.add_argument('-m', '--money', type=int, default=1000, help='The initial investment, default is 1000.')
    parser.add_argument('-r', '--reinvest', type=int, default=0, help='The amount of money to reinvest each year, default is 0.')
    parser.add_argument('-n', '--name', type=str, default='report.pdf', help='The name of the PDF report, default is report.pdf.')
    parser.add_argument('-f', '--full', action='store_true', help='Whether to generate a full report or not. Default is False.')
    parser.add_argument('-F', '--force', action='store_true', help='Whether to force a reload of the ticker data. Default is False.')
    
    return parser.parse_args()

def print_arguments_selected(args: argparse.Namespace):
    print(f"Number of years needed to backtest the strategy: {args.years}")
    print(f"Minimum number of years needed to backtest the stock: {args.window}")
    print(f"Initial investment: {args.money} | Reinvest each year: {args.reinvest}")
    print(f"Optimizer selected: {args.optimizer} | Regularization parameter: {args.gamma}")
    print(f"Name of the PDF report: {args.name} | Full report: {args.full}")
    print(f"Reload ticker data: {args.force}\n")

if __name__ == '__main__':
    args = parse_argument()
    print_arguments_selected(args)
    
    ticker_downloader = TickerDownloader()

    df_tickers = ticker_downloader.download_tickers_sp500(args.years, force_reload=args.force)["Close"]
    sp500_market = ticker_downloader.download_tickers_data(['^GSPC'], args.years)["Close"] / 10
    market = sp500_market.to_frame()

    optimizer_tickers = OptimizerEfficient(args.optimizer, args.gamma)
    allocations_tickers = generate_allocation(df_tickers, args.window, optimizer_tickers)
    portfolio_tickers = generate_portfolio(df_tickers, allocations_tickers, args.money, args.reinvest)
    portfolio = StructPortfolio(portfolio_tickers, allocations_tickers)
    
    optimizer_market = OptimizerBase()
    allocations_market = generate_allocation(market, args.window, optimizer_market)
    portfolio_market = generate_portfolio(market, allocations_market, args.money, args.reinvest)
    market = StructPortfolio(portfolio_market, allocations_market)
    
    generate_report(portfolio, market, ticker_downloader, args.name, args.full)
    