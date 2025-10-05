import io
import PyPDF2
from docx import Document
from typing import Optional

class DocumentParser:
    @staticmethod
    def parse_text(content: bytes) -> str:
        return content.decode('utf-8')

    @staticmethod
    def parse_pdf(content: bytes) -> str:
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(content))
            text = "\n".join(page.extract_text() for page in pdf_reader.pages)
            return text
        except Exception as e:
            raise ValueError(f"Failed to parse PDF: {str(e)}")

    @staticmethod
    def parse_docx(content: bytes) -> str:
        try:
            doc = Document(io.BytesIO(content))
            text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            return text
        except Exception as e:
            raise ValueError(f"Failed to parse DOCX: {str(e)}")

    @classmethod
    def parse(cls, content: bytes, mime_type: str) -> str:
        if mime_type == 'text/plain':
            return cls.parse_text(content)
        elif mime_type == 'application/pdf':
            return cls.parse_pdf(content)
        elif mime_type in ['application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'application/msword']:
            return cls.parse_docx(content)
        else:
            raise ValueError(f"Unsupported file type: {mime_type}")
