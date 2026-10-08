from pathlib import Path


class TextExtractionService:

    @staticmethod
    def extract_text(
        file_path: Path,
        mime_type: str | None = None,
    ) -> str:
        """
        Extract text from supported files.

        Supported:
        - TXT
        - DOCX
        - PDF
        """

        if not file_path.exists():
            raise FileNotFoundError(
                f"File not found: {file_path}"
            )

        mime_type = (
            mime_type.lower().strip()
            if mime_type
            else ""
        )

        # ====================================================
        # TEXT FILE
        # ====================================================

        if (
            mime_type.startswith("text/")
            or file_path.suffix.lower() == ".txt"
        ):
            return file_path.read_text(
                encoding="utf-8",
                errors="ignore",
            )

        # ====================================================
        # DOCX
        # ====================================================

        if (
            mime_type
            == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            or file_path.suffix.lower() == ".docx"
        ):
            return TextExtractionService._extract_docx(
                file_path
            )

        # ====================================================
        # PDF
        # ====================================================

        if (
            mime_type == "application/pdf"
            or file_path.suffix.lower() == ".pdf"
        ):
            return TextExtractionService._extract_pdf(
                file_path
            )

        raise ValueError(
            f"Unsupported file type: {mime_type or file_path.suffix}"
        )

    # ========================================================
    # DOCX EXTRACTION
    # ========================================================

    @staticmethod
    def _extract_docx(
        file_path: Path,
    ) -> str:

        try:
            from docx import Document

        except ImportError:
            raise RuntimeError(
                "python-docx is not installed. "
                "Run: pip install python-docx"
            )

        document = Document(
            str(file_path)
        )

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        return "\n".join(paragraphs)

    # ========================================================
    # PDF EXTRACTION
    # ========================================================

    @staticmethod
    def _extract_pdf(
        file_path: Path,
    ) -> str:

        try:
            from pypdf import PdfReader

        except ImportError:
            raise RuntimeError(
                "pypdf is not installed. "
                "Run: pip install pypdf"
            )

        reader = PdfReader(
            str(file_path)
        )

        pages = []

        for page in reader.pages:

            text = page.extract_text()

            if text:
                pages.append(
                    text.strip()
                )

        return "\n\n".join(pages)
