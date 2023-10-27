from src.pdf.pdf_report import PdfReport
from src.tickers import TickerDownloader
from src.graphics import graphic_plot, allocation_plot
from src.stats import get_returns, get_max_drawdown

import pandas as pd
from typing import Dict
from tqdm import tqdm

class StructPortfolio:
    def __init__(self, portfolio: pd.DataFrame, allocation: Dict):
        self.portfolio = portfolio
        self.allocation = allocation


def generate_report(portfolio: StructPortfolio, market: StructPortfolio,
                    downloader: TickerDownloader, pdf_name: str = 'report.pdf',
                    full_report: bool = True) -> None:
    """Generates a PDF report containing portfolio performance metrics and visualizations.

    Args:
        portfolio (pd.DataFrame): A pandas DataFrame containing the portfolio returns.
        market (pd.DataFrame): A pandas DataFrame containing the market returns.
        allocations (Dict): A dictionary containing the asset allocation weights for each year.
        downloader (TickerDownloader): A TickerDownloader object used to download and process financial data.
        pdf_name (str, optional): The name of the PDF report. Defaults to 'report.pdf'.
        full_report (bool, optional): Whether to generate a full report or not. Defaults to True.
    """

    print("Generating report...")
    returns_portfolio = get_returns(portfolio.portfolio)
    returns_market = get_returns(market.portfolio)
    drawdown_portfolio = get_max_drawdown(portfolio.portfolio)
    drawdown_market = get_max_drawdown(market.portfolio)

    returns_plot = graphic_plot(returns_portfolio, returns_market, "Returns")
    drawdown_plot = graphic_plot(drawdown_portfolio, drawdown_market, "Drawdown")

    document = PdfReport(pdf_name)
    document.first_page("Portfolio Report", returns_plot)
    document.summary_page("Summary", returns_plot, drawdown_plot)

    if not full_report:
        print("Concise report generated, creating PDF...")
        document.create_document()
        return

    t_range = tqdm(portfolio.allocation.keys(),
                   desc='Generating report page',
                   ncols=100)
    
    for year in t_range:
        t_range.set_description(f"Generating  report page for {year}")
        t_range.refresh()
        
        portfolio_year = portfolio.portfolio.loc[str(year)]
        market_year = market.portfolio.loc[str(year)]
        
        returns_portfolio_year = get_returns(portfolio_year)
        returns_market_year = get_returns(market_year)
        drawdown_portfolio_year = get_max_drawdown(portfolio_year)
        drawdown_market_year = get_max_drawdown(market_year)
        
        title_allocation = f"Portfolio allocation % in {year}"
        allocation_plot_year = allocation_plot(title_allocation, portfolio.allocation.get(year))

        title_allocatio_sector = f"Portfolio allocation % in {year} by sector"
        allocation_sector = downloader.generate_allocation_sectors(portfolio.allocation.get(year))
        all_sector_plot_year = allocation_plot(title_allocatio_sector, allocation_sector)
        
        returns_plot_year = graphic_plot(returns_portfolio_year, returns_market_year, "Returns")
        drawdown_plot_year = graphic_plot(drawdown_portfolio_year, drawdown_market_year, "Drawdown")
        
        document.year_page(f"Year {year}", returns_plot_year, drawdown_plot_year, allocation_plot_year, all_sector_plot_year)
        
    print("Full report generated, creating PDF...")
    document.create_document()