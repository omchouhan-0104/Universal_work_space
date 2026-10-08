from pathlib import Path
import subprocess

from docx import Document

from app.services.processors.base import BaseProcessor


class DocumentProcessor(BaseProcessor):

    def process(
        self,
        input_path: Path,
        output_path: Path,
        operation: str,
        **options,
    ) -> Path:

        operation = operation.lower().strip()

        if operation == "extract_text":
            return self.extract_text(
                input_path,
                output_path,
                **options,
            )

        if operation == "convert_pdf":
            return self.convert_pdf(
                input_path,
                output_path,
                **options,
            )

        raise ValueError(
            f"Unsupported document operation: {operation}"
        )

    # ========================================
    # EXTRACT TEXT
    # ========================================

    def extract_text(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        extension = input_path.suffix.lower()

        if extension != ".docx":
            raise ValueError(
                "extract_text currently supports "
                "only DOCX files"
            )

        document = Document(
            str(input_path)
        )

        paragraphs = []

        for paragraph in document.paragraphs:

            text = paragraph.text.strip()

            if text:
                paragraphs.append(text)

        if not paragraphs:
            raise ValueError(
                "Document contains no text"
            )

        output_path.write_text(
            "\n\n".join(paragraphs),
            encoding="utf-8",
        )

        return output_path

    # ========================================
    # DOCX → PDF
    # ========================================

    def convert_pdf(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        extension = input_path.suffix.lower()

        if extension != ".docx":
            raise ValueError(
                "convert_pdf currently supports "
                "only DOCX files"
            )

        output_path.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        try:

            subprocess.run(
                [
                    "libreoffice",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(output_path.parent),
                    str(input_path),
                ],
                check=True,
                capture_output=True,
                text=True,
            )

        except FileNotFoundError:

            raise ValueError(
                "LibreOffice is not installed"
            )

        except subprocess.CalledProcessError as exc:

            raise ValueError(
                f"LibreOffice conversion failed: "
                f"{exc.stderr}"
            )

        generated_file = (
            output_path.parent
            / f"{input_path.stem}.pdf"
        )

        if not generated_file.exists():

            raise ValueError(
                "PDF was not generated"
            )

        # Rename generated PDF to our desired name
        if generated_file != output_path:

            generated_file.replace(
                output_path
            )

        return output_path