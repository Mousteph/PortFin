from src.pdf.pdf_report import PdfReport
from src.graphics import graphic_plot, allocation_plot
from src.stats import get_returns, get_max_drawdown
import pandas as pd
from typing import Dict


def generate_report(portfolio: pd.DataFrame, market: pd.DataFrame, allocations: Dict) -> None:
    """Generates a PDF report containing portfolio performance metrics and visualizations.

    Args:
        portfolio (pd.DataFrame): A pandas DataFrame containing the portfolio returns.
        market (pd.DataFrame): A pandas DataFrame containing the market returns.
        allocations (Dict): A dictionary containing the asset allocation weights for each year.
    """

    returns_portfolio = get_returns(portfolio)
    returns_market = get_returns(market)
    drawdown_portfolio = get_max_drawdown(portfolio)
    drawdown_market = get_max_drawdown(market)

    returns_plot = graphic_plot(returns_portfolio, returns_market, "Returns")
    drawdown_plot = graphic_plot(drawdown_portfolio, drawdown_market, "Drawdown")

    document = PdfReport("report.pdf")
    document.first_page("Portfolio Report", returns_plot)
    document.summary_page("Summary", returns_plot, drawdown_plot)

    for year in allocations.keys():
        portfolio_year = portfolio.loc[str(year)]
        market_year = market.loc[str(year)]
        
        returns_portfolio_year = get_returns(portfolio_year)
        returns_market_year = get_returns(market_year)
        drawdown_portfolio_year = get_max_drawdown(portfolio_year)
        drawdown_market_year = get_max_drawdown(market_year)
        
        allocation_plot_year = allocation_plot(year, allocations)
        returns_plot_year = graphic_plot(returns_portfolio_year, returns_market_year, "Returns")
        drawdown_plot_year = graphic_plot(drawdown_portfolio_year, drawdown_market_year, "Drawdown")
        
        document.year_page(f"Year {year}", returns_plot_year, drawdown_plot_year, allocation_plot_year)
        
    document.create_document()