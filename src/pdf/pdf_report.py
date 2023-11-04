import matplotlib.pyplot as plt
from io import BytesIO
from typing import List, Dict
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, inch
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.platypus import PageBreak, Table, TableStyle
import pandas as pd

class StructSummaryData:
    def __init__(self, returns_figure: plt.figure, drawdown_figure: plt.Figure,
                 price: pd.DataFrame, returns: pd.DataFrame, drawdown: pd.DataFrame,
                 reinvested: float):
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

    Attributes:
        pdf_name (str): The name of the PDF file to be generated.
        doc (SimpleDocTemplate): The SimpleDocTemplate object used to build the PDF document.
        styles (reportlab.lib.styles.StyleSheet): The StyleSheet object used to define the styles of the report.
        report (List): The list of Platypus flowables used to build the PDF document.
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

    def first_page(self, title: str, image: plt.Figure) -> None:
        """Adds a title and image to the first page of the report.

        Args:
            title (str): The title to be added to the first page of the report.
            image (plt.Figure): The matplotlib Figure object to add to the first page of the report.
        """
        
        image = self.__create_image_pdf(image, 450, 300)
        title = self.add_title(title)  
        
        self.report.append(title)
        self.report.append(Spacer(1, 12))
        self.report.append(image)

        self.add_page_break()

    def summary_page(self, title: str, portfolio: StructSummaryData, market: StructSummaryData) -> None:
        """Adds a title and two images to a summary page of the report.

        Args:
            title (str): The title to be added to the summary page of the report.
            returns (plt.Figure): The matplotlib Figure object containing the returns data to add to the summary page of the report.
            drawdown (plt.Figure): The matplotlib Figure object containing the drawdown data to add to the summary page of the report.
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
        """Adds a title and four images to a yearly page of the report.

        Args:
            title (str): The title to be added to the yearly page of the report.
            returns (plt.Figure): The matplotlib Figure object containing the returns data to add to the yearly page of the report.
            drawdown (plt.Figure): The matplotlib Figure object containing the drawdown data to add to the yearly page of the report.
            allocation (plt.Figure): The matplotlib Figure object containing the allocation data to add to the yearly page of the report.
            allocation_sector (plt.Figure): The matplotlib Figure object containing the allocation sector data to add to the yearly page of the report.
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
