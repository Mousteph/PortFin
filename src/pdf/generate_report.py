from src.pdf.pdf_report import PdfReport, StructSummaryData, StructYearSummaryData
from src.tickers import TickerDownloader
from src.graphics import graphic_plot, allocation_plot
from src.stats import get_returns, get_max_drawdown
import argparse

import pandas as pd
from typing import Dict
from tqdm import tqdm

class StructPortfolio:
    def __init__(self, portfolio: pd.DataFrame, allocation: Dict, reinvested: float):
        """StructPortfolio constructor.

        Args:
            portfolio (pd.DataFrame): Pandas DataFrame containing the portfolio data.
            allocation (Dict): A dictionary containing the asset allocation weights for each year.
            reinvested (float): The amount of money reinvested in the portfolio.
        """
        
        self.portfolio = portfolio
        self.allocation = allocation
        self.reinvested = reinvested


def generate_report(portfolio: StructPortfolio, market: StructPortfolio,
                    downloader: TickerDownloader, args: argparse.Namespace) -> None:
    """Generates a PDF report containing portfolio performance metrics and visualizations.

    This function generates a PDF report that includes a summary page and yearly pages. The summary page includes 
    returns and drawdown plots for the entire period of the portfolio and market. Each yearly page includes returns 
    and drawdown plots, an allocation plot, and an allocation by sector plot for the portfolio and market for that year.

    Args:
        portfolio (StructPortfolio): A StructPortfolio object containing the portfolio data.
        market (StructPortfolio): A StructPortfolio object containing the market data.
        downloader (TickerDownloader): A TickerDownloader object used to download and process financial data.
        args (argparse.Namespace): The arguments passed to the script, which include details about the backtest.
    """
    
    print("Generating report...")
    returns_portfolio = get_returns(portfolio.portfolio)
    returns_market = get_returns(market.portfolio)
    drawdown_portfolio = get_max_drawdown(portfolio.portfolio)
    drawdown_market = get_max_drawdown(market.portfolio)

    returns_plot = graphic_plot(returns_portfolio, returns_market, "Returns")
    drawdown_plot = graphic_plot(drawdown_portfolio, drawdown_market, "Drawdown")

    portfolio_summary = StructSummaryData(returns_plot, drawdown_plot, portfolio.portfolio,
                                          returns_portfolio, drawdown_portfolio,
                                          portfolio.reinvested)
    market_summary = StructSummaryData(None, None, market.portfolio,
                                       returns_market, drawdown_market,
                                       market.reinvested)

    document = PdfReport(args.name)
    document.first_page("Portfolio Report", returns_plot, args)
    document.summary_page("Summary", portfolio_summary, market_summary)

    if not args.full:
        print("Concise report generated, creating PDF...")
        document.create_document()
        return

    t_range = tqdm(portfolio.allocation.keys(),
                   desc='Generating report page',
                   ncols=100)
    
    for year in t_range:
        t_range.set_description(f"Generating  report page for {year}")
        t_range.refresh()
       
        # Portfolio 
        portfolio_year = portfolio.portfolio.loc[str(year)]
        returns_portfolio_year = get_returns(portfolio_year)
        drawdown_portfolio_year = get_max_drawdown(portfolio_year)

        title_allocation = f"Portfolio allocation % in {year}"
        allocation_plot_year = allocation_plot(title_allocation, portfolio.allocation.get(year))
        
        # Market
        market_year = market.portfolio.loc[str(year)]
        drawdown_market_year = get_max_drawdown(market_year)
        returns_market_year = get_returns(market_year)

        title_allocatio_sector = f"Portfolio allocation % in {year} by sector"
        allocation_sector = downloader.generate_allocation_sectors(portfolio.allocation.get(year))
        all_sector_plot_year = allocation_plot(title_allocatio_sector, allocation_sector)
       
        # Figures
        returns_figure = graphic_plot(returns_portfolio_year, returns_market_year, "Returns")
        drawdown_figure = graphic_plot(drawdown_portfolio_year, drawdown_market_year, "Drawdown")

        data = StructYearSummaryData(returns_figure, drawdown_figure,
                                     allocation_plot_year, all_sector_plot_year,
                                     portfolio_year, returns_portfolio_year, drawdown_portfolio_year,
                                     portfolio.allocation.get(year))
        
        data_market = StructYearSummaryData(None, None, None, None, market_year,
                                            returns_market_year, drawdown_market_year,
                                            market.allocation.get(year))
        
        document.year_page(f"Year {year}", data, data_market)
        
    print("Full report generated, creating PDF...")
    document.create_document()