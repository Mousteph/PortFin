import argparse
import pandas as pd

from src.helpers_tickers import (
    get_all_tickers_sp500,
    format_sp500_tickers,
    filter_out_tickers,
    download_tickers_data,
    delete_all_null_tickers,
)

from src.helpers_allocation import (
    calculate_each_year_allocation,
)

from src.generate_report import generate_report

def parse_argument() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='PortFin - Portfolio Allocation')
    
    parser.add_argument('-y', '--years', type=int, default=20, help='Number of years of data to download.')
    parser.add_argument('-w', '--window', type=int, default=5, help='Number of years needed to backtest the stock.')
    
    return parser.parse_args()

def load_all_tickers_sp500(nb_years: int) -> pd.DataFrame:
    all_tickers_raw = get_all_tickers_sp500()
    all_tickers = format_sp500_tickers(all_tickers_raw)
    all_tickers_filtered = filter_out_tickers(all_tickers, nb_years)
    list_tickers = all_tickers_filtered.index.tolist()
    
    all_tickers_data = download_tickers_data(list_tickers, nb_years)
    all_tickers_data = delete_all_null_tickers(all_tickers_data)
    
    return all_tickers_data

if __name__ == '__main__':
    args = parse_argument()
    
    df_tickers = load_all_tickers_sp500(args.years)
    sp500_market = download_tickers_data(['^GSPC'], 20)
    money_value, df_money = calculate_each_year_allocation(df_tickers, args.window)
    
    generate_report(df_money, sp500_market)
    