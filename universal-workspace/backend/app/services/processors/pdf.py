from pathlib import Path

from pypdf import PdfReader, PdfWriter

from app.services.processors.base import BaseProcessor


class PDFProcessor(BaseProcessor):

    def process(
        self,
        input_path: Path,
        output_path: Path,
        operation: str,
        **options,
    ) -> Path:

        operation = operation.lower().strip()

        # --------------------------------
        # COMPRESS
        # --------------------------------

        if operation == "compress":
            return self.compress(
                input_path,
                output_path,
                **options,
            )
        
        # --------------------------------
        # ROTATE
        # --------------------------------

        if operation == "rotate":
            return self.rotate(
                input_path,
                output_path,
                **options,
            )

        raise ValueError(
            f"Unsupported PDF operation: {operation}"
        )

    # ========================================
    # COMPRESS
    # ========================================

    def compress(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        reader = PdfReader(
            str(input_path)
        )

        if reader.is_encrypted:
            raise ValueError(
                "Encrypted PDFs are not supported"
            )

        writer = PdfWriter()

        for page in reader.pages:
            writer.add_page(page)

        writer.add_metadata({})

        with open(
            output_path,
            "wb",
        ) as output_file:

            writer.write(
                output_file
            )

        return output_path

    # ========================================
    # ROTATE
    # ========================================

    def rotate(
        self,
        input_path: Path,
        output_path: Path,
        **options,
    ) -> Path:

        rotation = options.get(
            "rotation"
        )

        if rotation is None:
            raise ValueError(
                "rotation is required for PDF rotate"
            )

        try:
            rotation = int(rotation)

        except (TypeError, ValueError):
            raise ValueError(
                "rotation must be an integer"
            )

        # PDF rotation should normally be
        # 90, 180 or 270 degrees.

        if rotation not in {
            90,
            180,
            270,
        }:
            raise ValueError(
                "rotation must be 90, 180 or 270 degrees"
            )

        reader = PdfReader(
            str(input_path)
        )

        if reader.is_encrypted:
            raise ValueError(
                "Encrypted PDFs are not supported"
            )

        writer = PdfWriter()

        for page in reader.pages:

            page.rotate(
                rotation
            )

            writer.add_page(
                page
            )

        with open(
            output_path,
            "wb",
        ) as output_file:

            writer.write(
                output_file
            )

        return output_path