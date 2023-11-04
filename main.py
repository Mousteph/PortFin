import argparse

from src.tickers import TickerDownloader
from src.functions import generate_allocation, generate_portfolio
from src.pdf.generate_report import generate_report, StructPortfolio 
from src.optimizer import OptimizerEfficient, OptimizerBase, OptimizerHierarchical

def parse_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PortFin - Portfolio Allocation')
    
    parser.add_argument('-y', '--years', type=int, default=30, help='Number of years of data to download.')
    parser.add_argument('-w', '--window', type=int, default=7, help='Number of years needed to backtest the stock.')
    parser.add_argument('-o', '--optimizer', type=str, default='hierarchical', help='The optimizer to use, hierarchical or efficient, default is hierarchical.')
    parser.add_argument('-t', '--type', type=str, default='max_sharpe', help='The objective to use, max_sharpe or min_volatility, default is max_sharpe.')
    parser.add_argument('-g', '--gamma', type=float, default=0.1, help='The regularization parameter, default is 0.1.')
    parser.add_argument('-m', '--money', type=int, default=1000, help='The initial investment, default is 1000.')
    parser.add_argument('-r', '--reinvest', type=int, default=0, help='The amount of money to reinvest each year, default is 0.')
    parser.add_argument('-n', '--name', type=str, default='report.pdf', help='The name of the PDF report, default is report.pdf.')
    parser.add_argument('-f', '--full', action='store_true', help='Whether to generate a full report or not. Default is False.')
    parser.add_argument('-F', '--force', action='store_true', help='Whether to force a reload of the ticker data. Default is False.')
    parser.add_argument('-W', '--weight', type=float, default=0.03, help='Minimum weight of each asset. Default is 0.05.')
    
    return parser.parse_args()

def print_arguments_selected(args: argparse.Namespace):
    print(f"Number of years needed to backtest the strategy: {args.years}")
    print(f"Minimum number of years needed to backtest the stock: {args.window}")
    print(f"Initial investment: {args.money} | Reinvest each year: {args.reinvest}")
    print(f"Optimizer selected: {args.optimizer} | Minimum weight: {args.weight}")
    if args.optimizer == 'efficient':
        print(f"Regularization parameter: {args.gamma} | Type of the objective: {args.type}")
    print(f"Name of the PDF report: {args.name} | Full report: {args.full}")
    print(f"Reload ticker data: {args.force}\n")

if __name__ == '__main__':
    args = parse_argument()
    print_arguments_selected(args)
    
    ticker_downloader = TickerDownloader()

    df_tickers = ticker_downloader.download_tickers_sp500(args.years, force_reload=args.force)["Close"]
    sp500_market = ticker_downloader.download_tickers_data_since(['^GSPC'], args.years)["Close"] / 10
    sp500_market = sp500_market.to_frame()

    if args.optimizer == 'efficient':
        optimizer_tickers = OptimizerEfficient(args.type, args.gamma, args.weight)
    elif args.optimizer == 'hierarchical':
        optimizer_tickers = OptimizerHierarchical(args.weight)
    else:
        raise ValueError("Optimizer not recognized.")
    
    allocations_tickers = generate_allocation(df_tickers, args.window, optimizer_tickers)
    portfolio_tickers, ticker_rein = generate_portfolio(df_tickers, allocations_tickers, args.money, args.reinvest)
    portfolio = StructPortfolio(portfolio_tickers, allocations_tickers, ticker_rein)
    
    optimizer_market = OptimizerBase()
    allocations_market = generate_allocation(sp500_market, args.window, optimizer_market)
    portfolio_market, market_rein = generate_portfolio(sp500_market, allocations_market, args.money, args.reinvest)
    market = StructPortfolio(portfolio_market, allocations_market, market_rein)

    generate_report(portfolio, market, ticker_downloader, args)
    