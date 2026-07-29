# pyrefly: ignore [missing-import]
import fitz
from docx import Document
from app.services.excel_service import ExcelService

excel_service = ExcelService()


class DocumentParserService:

    def extract_text(
        self,
        file_path: str,
        file_type: str
    ):

        file_type = file_type.lower()

        if file_type == "pdf":
            return self.extract_pdf(file_path)

        elif file_type == "docx":
            return self.extract_docx(file_path)

        elif file_type == "txt":
            return self.extract_txt(file_path)

        elif file_type in ["xlsx", "xls", "csv"]:
            return excel_service.extract_text(file_path, file_type)

        raise Exception("Unsupported file type")

    # --------------------
    # PDF
    # --------------------

    def extract_pdf(
        self,
        file_path: str
    ):

        document = fitz.open(file_path)

        text = ""

        for page in document:

            text += page.get_text()

        document.close()

        return text

    # --------------------
    # DOCX
    # --------------------

    def extract_docx(
        self,
        file_path: str
    ):

        document = Document(file_path)

        text = ""

        for paragraph in document.paragraphs:

            text += paragraph.text + "\n"

        return text

    # --------------------
    # TXT
    # --------------------

    def extract_txt(
        self,
        file_path: str
    ):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as file:

            return file.read()