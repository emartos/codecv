import os

from fpdf import FPDF
from src.exporter.format.format_interface import FormatInterface


class Pdf(FormatInterface):
    """
    Concrete implementation of the FormatInterface for exporting CV data into a PDF file.
    This class uses the `fpdf` library to generate a formatted PDF document from structured CV data.
    """

    EXTENSION = "pdf"

    def export(
        self, author_name: str, extract: str, data, filename: str = "resume"
    ) -> str:
        """
        Exports the given CV data (`data`) to a PDF file in the output directory.

        Args:
            author_name (str): The author's name.
            extract (str): The CV extract.
            data (list[dict]): A list of dictionaries where each dictionary represents a CV section.
            filename (str): The name of the PDF file where the content will be saved.
                            Defaults to "resume".

        Returns:
            str: The full path of the generated PDF file.
        """
        pdf = self._generate_pdf(author_name, extract, data)
        filename = f"{filename}.{self.EXTENSION}"
        path = os.path.join(self.output_dir, filename)
        pdf.output(path)
        return path

    def _generate_pdf(self, author_name: str, extract: str, data):
        """
        Generates an FPDF object containing the CV data formatted as a PDF.

        Args:
            author_name (str): The author's name.
            extract (str): The CV extract.
            data (list[dict]): A list of dictionaries.

        Returns:
            FPDF: An FPDF object representing the formatted CV data.
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()

        pdf.set_font("Arial", style="B", size=18)
        pdf.multi_cell(200, 10, txt=author_name, ln=True)

        for item in data:
            name = item.get("name", self._untitled)
            position = item.get("position", self._not_apply)
            highlights = item.get("highlights", [])
            title = item.get("title", self._untitled)
            domain = item.get("domain", self._not_apply)
            date_start = item.get("date_start", "")
            if date_start:
                date_start = self._format_date(date_start)
            date_end = item.get("date_end", "")
            if date_end:
                date_end = self._format_date(date_end)
            description = item.get("description", "")
            highlights = item.get("highlights", [])
            technologies = item.get("technologies", [])
            technologies = ", ".join(technologies)

            pdf.set_font("Arial", style="B", size=14)
            pdf.multi_cell(200, 10, txt=f"{title} ({date_start} - {date_end})", ln=True)

            pdf.ln(5)  # Add empty spacing
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(50, 10, txt=f"{self._name}:", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(250, 10, txt=name, ln=True)

            pdf.ln(5)  # Add empty spacing
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(50, 10, txt=f"{self._position}:", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(150, 10, txt=position, ln=True)

            pdf.ln(5)  # Add empty spacing
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(50, 10, txt=f"{self._domain}:", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(150, 10, txt=domain, ln=True)

            pdf.ln(5)  # Add empty spacing
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(200, 10, txt=f"{self._highlights}:", ln=True)
            pdf.set_font("Arial", size=12)
            for highlight in highlights:
                pdf.multi_cell(150, 10, txt=f"- {highlight}", ln=True)

            pdf.ln(5)  # Add empty spacing
            pdf.set_font("Arial", style="B", size=12)
            pdf.cell(50, 10, txt=f"{self._technologies}:", ln=True)
            pdf.set_font("Arial", size=12)
            pdf.multi_cell(150, 10, txt=technologies, ln=True)

            pdf.ln(5)  # Add empty spacing
            pdf.set_font("Arial", style="B", size=12)
            pdf.multi_cell(50, 10, txt=f"{self._description}:", ln=True)

            pdf.set_font("Arial", size=12)
            pdf.multi_cell(0, 10, txt=description)
            pdf.ln(10)  # Add spacing after each section

        return pdf
