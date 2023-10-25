from pdf_report import PdfReport
from graphics import graph_portfolio_market
import pandas as pd


def generate_report(portfolio: pd.DataFrame, market: pd.DataFrame) -> None:
    """Generates a PDF report containing a summary page and a graph of the cumulative returns of a portfolio and a market index.

    Args:
        portfolio (pd.DataFrame): A pandas DataFrame containing the portfolio returns.
        market (pd.DataFrame): A pandas DataFrame containing the market returns.
    """

    document = PdfReport("report.pdf")
    document.first_page("Investment Report")
    image_result = graph_portfolio_market(portfolio, market, "Cumulative Returns Portfolio vs Market")
    document.add_summary_page(image_result)
    document.create_document()