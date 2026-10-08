# from pathlib import Path

# from app.services.processors.image import ImageProcessor
# from app.services.processors.pdf import PDFProcessor
# from app.services.processors.document import DocumentProcessor
# from app.services.processors.audio import AudioProcessor
# from app.services.processors.video import VideoProcessor


# class ProcessingService:

#     def __init__(self):
#         self.processors = {
#             "image": ImageProcessor(),
#             "pdf": PDFProcessor(),
#             "document": DocumentProcessor(),
#             "audio": AudioProcessor(),
#             "video": VideoProcessor(),
#         }

#     def get_processor(
#         self,
#         file_category: str,
#     ):
#         processor = self.processors.get(file_category)

#         if not processor:
#             raise ValueError(
#                 f"Unsupported file category: {file_category}"
#             )

#         return processor

#     def process(
#         self,
#         file_category: str,
#         input_path: Path,
#         output_path: Path,
#         **options,
#     ) -> Path:

#         processor = self.get_processor(
#             file_category
#         )

#         return processor.process(
#             input_path=input_path,
#             output_path=output_path,
#             **options,
#         )
        
#     @staticmethod
#     def detect_category(mime_type: str) -> str:

#         if mime_type.startswith("image/"):
#             return "image"

#         if mime_type == "application/pdf":
#             return "pdf"

#         if mime_type.startswith("audio/"):
#             return "audio"

#         if mime_type.startswith("video/"):
#             return "video"

#         if mime_type.startswith(
#             "application/vnd.openxmlformats"
#         ):
#             return "document"

#         if mime_type.startswith("text/"):
#             return "document"

#         raise ValueError(
#             f"Unsupported MIME type: {mime_type}"
#         )


from pathlib import Path

from app.services.processors.image import ImageProcessor
from app.services.processors.pdf import PDFProcessor
from app.services.processors.document import DocumentProcessor
from app.services.processors.audio import AudioProcessor
from app.services.processors.video import VideoProcessor


class ProcessingService:

    def __init__(self):

        self.processors = {
            "image": ImageProcessor(),
            "pdf": PDFProcessor(),
            "document": DocumentProcessor(),
            "audio": AudioProcessor(),
            "video": VideoProcessor(),
        }

    # --------------------------------
    # GET PROCESSOR
    # --------------------------------

    def get_processor(
        self,
        file_category: str,
    ):

        processor = self.processors.get(
            file_category
        )

        if not processor:
            raise ValueError(
                f"Unsupported file category: "
                f"{file_category}"
            )

        return processor

    # --------------------------------
    # PROCESS
    # --------------------------------

    def process(
        self,
        file_category: str,
        input_path: Path,
        output_path: Path,
        operation: str,
        **options,
    ) -> Path:

        processor = self.get_processor(
            file_category
        )

        return processor.process(
            input_path=input_path,
            output_path=output_path,
            operation=operation,
            **options,
        )

    # --------------------------------
    # DETECT CATEGORY
    # --------------------------------

    @staticmethod
    def detect_category(
        mime_type: str,
    ) -> str:

        if not mime_type:
            raise ValueError(
                "MIME type is missing"
            )

        mime_type = (
            mime_type
            .lower()
            .strip()
        )

        # Images
        if mime_type.startswith("image/"):
            return "image"

        # PDF
        if mime_type == "application/pdf":
            return "pdf"

        # Audio
        if mime_type.startswith("audio/"):
            return "audio"

        # Video
        if mime_type.startswith("video/"):
            return "video"

        # DOCX / XLSX / PPTX
        if mime_type.startswith(
            "application/vnd.openxmlformats"
        ):
            return "document"

        # Old Microsoft Office files
        if mime_type in {
            "application/msword",
            "application/vnd.ms-excel",
            "application/vnd.ms-powerpoint",
        }:
            return "document"

        # Text files
        if mime_type.startswith("text/"):
            return "document"

        raise ValueError(
            f"Unsupported MIME type: {mime_type}"
        )