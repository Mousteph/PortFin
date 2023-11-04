import matplotlib.pyplot as plt
from io import BytesIO
from typing import List, Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus import PageBreak, Table, TableStyle
import pandas as pd
import argparse

class StructSummaryData:
    def __init__(self, returns_figure: plt.figure, drawdown_figure: plt.Figure,
                 price: pd.DataFrame, returns: pd.DataFrame, drawdown: pd.DataFrame,
                 reinvested: float):
        """Constructs all the necessary attributes for the StructSummaryData object.

        Args:
            returns_figure (plt.figure): The figure object for returns.
            drawdown_figure (plt.Figure): The figure object for drawdown.
            price (pd.DataFrame): The DataFrame object for price.
            returns (pd.DataFrame): The DataFrame object for returns.
            drawdown (pd.DataFrame): The DataFrame object for drawdown.
            reinvested (float): The reinvested amount.
        """
        
        self.returns_figure = returns_figure
        self.drawdown_figure = drawdown_figure
        self.price = price
        self.returns = returns
        self.drawdown = drawdown
        self.reinvested = reinvested

class StructYearSummaryData:
    def __init__(self, returns_figure: plt.figure, drawdown_figure: plt.Figure,
                 allocation_figure: plt.Figure, allocation_sector_figure: plt.Figure,
                 price: pd.DataFrame, returns: pd.DataFrame, drawdown: pd.DataFrame,
                 allocation: Dict):
        """Constructs all the necessary attributes for the StructYearSummaryData object.

        Args:
            returns_figure (plt.figure): The figure object for returns.
            drawdown_figure (plt.Figure): The figure object for drawdown.
            allocation_figure (plt.Figure): The figure object for allocation.
            allocation_sector_figure (plt.Figure): The figure object for allocation by sector.
            price (pd.DataFrame): The DataFrame object for price.
            returns (pd.DataFrame): The DataFrame object for returns.
            drawdown (pd.DataFrame): The DataFrame object for drawdown.
            allocation (Dict): The dictionary object for allocation.
        """
        
        self.returns_figure = returns_figure
        self.drawdown_figure = drawdown_figure
        self.allocation_figure = allocation_figure
        self.allocation_sector_figure = allocation_sector_figure
        self.price = price
        self.returns = returns
        self.drawdown = drawdown
        self.allocation = allocation

class PdfReport:
    """A class used to generate a PDF report.
    """
    
    def __create_image_pdf(self, image: plt.Figure, width: int = 600, height: int = 400, align: str = "CENTER") -> Image:
        """Creates a Platypus Image object from a matplotlib Figure object.

        Args:
            image (plt.Figure): The matplotlib Figure object to convert to a Platypus Image object.
            width (int, optional): The width of the resulting Image object. Defaults to 600.
            height (int, optional): The height of the resulting Image object. Defaults to 400.
            align (str, optional): The alignment of the resulting Image object. Defaults to "CENTER".

        Returns:
            Image: A Platypus Image object created from the matplotlib Figure object.
        """

        img_stream = BytesIO()
        image.savefig(img_stream, format='png', dpi=300, bbox_inches='tight')
        img_stream.seek(0)

        image = Image(img_stream, width=width, height=height, hAlign=align)
        return image
    
    def __init__(self, pdf_name: str) -> None:
        """Initializes the PdfReport object.

        Args:
            pdf_name (str): The name of the PDF file to be generated.
        """

        self.pdf_name = pdf_name
        self.doc = SimpleDocTemplate(self.pdf_name, pagesize=A4)
        self.styles = getSampleStyleSheet()
        self.report: List = []

    def create_document(self) -> None:
        """Builds the PDF document using the report list."""
        
        self.doc.build(self.report)

    def add_page_break(self) -> None:
        """Adds a page break to the report list."""
        
        self.report.append(PageBreak())
    
    def add_title(self, title: str) -> None:
        """Adds a title to the report.

        Args:
            title (str): The title to be added to the report.
        """
        
        title_style = self.styles["Title"]
        title = Paragraph(title, title_style)
        self.report.append(title)

    def first_page(self, title: str, image: plt.Figure, args: argparse.Namespace) -> None:
        """Adds a title, image, and backtest details to the first page of the report.

        This method creates the first page in the report, which includes a title, an image, and details about the backtest. 
        The image is created from the matplotlib Figure object. The backtest details include the backtest period, rolling window, 
        initial investment, reinvestment amount, selected optimizer, minimum asset weight, and other details specific to the 
        efficient optimizer. The backtest details are formatted and added as a Paragraph object to the report.

        Args:
            title (str): The title to be added to the first page of the report.
            image (plt.Figure): The matplotlib Figure object to add to the first page of the report.
            args (argparse.Namespace): The arguments passed to the script, which include details about the backtest.
        """
        
        image = self.__create_image_pdf(image, 450, 300)
        title = self.add_title(title)
        
        current_date = pd.to_datetime("today")
        start_date = current_date.year - args.years + args.window
        start_date = f"{start_date}-01-01"
        end_date = str(current_date.date())
        
        details_info = ""
        if args.optimizer == 'efficient':
            details_info = f"Regularization parameter: {args.gamma} | Type of the objective: {args.type}"
            
        backtest = f"""Backtest from {start_date} to {end_date}<br />\n
        <br />\n
        Rolling window: {args.window} years<br />\n
        Initial investment: {args.money}$ | Reinvest each year: {args.reinvest}$<br />\n
        Optimizer selected: {args.optimizer} | Minimum asset weight: {args.weight * 100}%<br />\n
        {details_info}<br />\n
        <br />\n
        Backtest performed on {current_date.date()} at by PortFin.
        """
        
        backtest_style = self.styles["BodyText"]
        backtest_style.alignment = 1
        backtest_style.fontSize = 14
        backtest_style.leading = 20
        backtest = Paragraph(backtest, backtest_style)
        
        self.report.append(title)
        self.report.append(Spacer(1, 12))
        self.report.append(image)
        self.report.append(Spacer(1, 30))
        self.report.append(backtest)

        self.add_page_break()

    def summary_page(self, title: str, portfolio: StructSummaryData, market: StructSummaryData) -> None:
        """Adds a title, two images, and a summary table to a summary page of the report.

        This method creates a summary page in the report, which includes a title, two images (returns and drawdown), 
        and a summary table. The images are created from the matplotlib Figure objects in the StructSummaryData objects 
        for the portfolio and market. The summary table includes data such as initial investment, money reinvested, 
        final value, returns, and max drawdown for both the portfolio and market.

        Args:
            title (str): The title to be added to the summary page of the report.
            portfolio (StructSummaryData): The StructSummaryData object containing the portfolio data.
            market (StructSummaryData): The StructSummaryData object containing the market data.
        """
        
        returns = self.__create_image_pdf(portfolio.returns_figure, 270, 180)
        drawdown = self.__create_image_pdf(portfolio.drawdown_figure, 270, 180)
        
        title = self.add_title(title)
        tables = Table([[returns, drawdown]])
        
        data_summary = [['', 'Portfolio', 'Market'],
                        ['Initial Investment', f"{round(portfolio.price.iloc[0][0], 2)}$", f"{round(market.price.iloc[0][0], 2)}$"],
                        ['Money Reinvested', f"{portfolio.reinvested}$", f"{market.reinvested}$"],
                        ['Final Value', f"{round(portfolio.price.iloc[-1][0], 2)}$", f"{round(market.price.iloc[-1][0], 2)}$"],
                        ['Returns', f"{round((portfolio.returns.iloc[-1][0] - 1) * 100, 2)}%", f"{round((market.returns.iloc[-1][0] - 1) * 100, 2)}%"],
                        ['Max Drawdown', f"{round(portfolio.drawdown.min()[0] * 100, 2)}%", f"{round(market.drawdown.min()[0] * 100, 2)}%"]]

        table_summary = Table(data_summary, len(data_summary[0]) * [2 * inch], len(data_summary) * [0.3 * inch])
        table_summary.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ('ALIGN', (0,0), (0, 2), 'LEFT'),
            ('ALIGN', (0,0),(0, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (0, -1), colors.beige),
            ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
                       ]))
        
        self.report.append(title)
        self.report.append(Spacer(1, 12))
        self.report.append(tables)
        self.report.append(Spacer(1, 30))
        self.report.append(table_summary)
        
        self.add_page_break()

    def year_page(self, title: str, data: StructYearSummaryData, data_market: StructYearSummaryData) -> None:
        """Adds a title, four images, and a summary table to a yearly page of the report.

        This method creates a yearly page in the report, which includes a title, four images (returns, drawdown, allocation, 
        and allocation by sector), and a summary table. The images are created from the matplotlib Figure objects in the 
        StructYearSummaryData objects for the data and data_market. The summary table includes data such as number of assets, 
        initial value, final value, returns, and max drawdown for both the data and data_market.

        Args:
            title (str): The title to be added to the yearly page of the report.
            data (StructYearSummaryData): The StructYearSummaryData object containing the data.
            data_market (StructYearSummaryData): The StructYearSummaryData object containing the market data.
        """
        
        returns = self.__create_image_pdf(data.returns_figure, 270, 180)
        drawdown = self.__create_image_pdf(data.drawdown_figure, 270, 180)
        allocation = self.__create_image_pdf(data.allocation_figure, 270, 270)
        allocation_sector = self.__create_image_pdf(data.allocation_sector_figure, 270, 270)
        
        title = self.add_title(title)
        alloc = Table([[allocation, allocation_sector]])
        retur = Table([[returns, drawdown]])
        
        data_summary = [['', 'Portfolio', 'Market'],
                        ['Number of assets', len(data.allocation), len(data_market.allocation)],
                        ['Initial Value', f"{round(data.price.iloc[0][0], 2)}$", f"{round(data_market.price.iloc[0][0], 2)}$"],
                        ['Final Value', f"{round(data.price.iloc[-1][0], 2)}$", f"{round(data_market.price.iloc[-1][0], 2)}$"],
                        ['Returns', f"{round((data.returns.iloc[-1][0] - 1) * 100, 2)}%", f"{round((data_market.returns.iloc[-1][0] - 1) * 100, 2)}%"],
                        ['Max Drawdown', f"{round(data.drawdown.min()[0] * 100, 2)}%", f"{round(data_market.drawdown.min()[0] * 100, 2)}%"]]

        table_summary = Table(data_summary, len(data_summary[0]) * [2 * inch], len(data_summary) * [0.3 * inch])
        table_summary.setStyle(TableStyle([
            ('INNERGRID', (0,0), (-1,-1), 0.25, colors.black),
            ('BOX', (0,0), (-1,-1), 0.25, colors.black),
            ('ALIGN', (0,0), (0, 2), 'LEFT'),
            ('ALIGN', (0,0),(0, -1), 'LEFT'),
            ('BACKGROUND', (0, 0), (0, -1), colors.beige),
            ('BACKGROUND', (0, 0), (-1, 0), colors.beige),
                       ]))
        
        
        self.report.append(title)
        self.report.append(Spacer(1, 12))
        self.report.append(alloc)
        self.report.append(Spacer(1, 12))
        self.report.append(retur)
        self.report.append(Spacer(1, 30))
        self.report.append(table_summary)

        self.add_page_break()
