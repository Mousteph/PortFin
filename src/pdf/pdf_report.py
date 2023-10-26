from reportlab.lib.pagesizes import A4

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, PageBreak
from reportlab.lib.styles import getSampleStyleSheet #, ParagraphStyle

from typing import List


class PdfReport:
    """A class used to generate a PDF report.

    Attributes:
        pdf_name (str): The name of the PDF file to be generated.
        doc (SimpleDocTemplate): The SimpleDocTemplate object used to build the PDF document.
        styles (reportlab.lib.styles.StyleSheet): The StyleSheet object used to define the styles of the report.
        report (List): The list of Platypus flowables used to build the PDF document.
    """

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

    def first_page(self, title: str) -> None:
        """Adds a title to the first page of the report.

        Args:
            title (str): The title to be added to the first page of the report.
        """
        
        title_style = self.styles["Title"]
        title_style.alignment = 1
        title = Paragraph(title, title_style)
        self.report.append(title)

        self.add_page_break()

    def add_title(self, title: str) -> None:
        """Adds a title to the report.

        Args:
            title (str): The title to be added to the report.
        """
        
        title_style = self.styles["Title"]
        title = Paragraph(title, title_style)
        self.report.append(title)

    def add_summary_page(self, image: str) -> None:
        """Adds a summary page to the report with an image.

        Args:
            image (str): The filename of the image to be added to the summary page.
        """
        
        self.add_title("Portfolio Generated vs Market")
        self.report.append(Spacer(1, 12))

        img = Image(image, width=600, height=400)
        self.report.append(img)