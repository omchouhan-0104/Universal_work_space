from app.services.processors.image import ImageProcessor
from app.services.processors.pdf import PDFProcessor
from app.services.processors.document import DocumentProcessor
from app.services.processors.audio import AudioProcessor
from app.services.processors.video import VideoProcessor


def get_processor(file_type: str):

    if file_type.startswith("image/"):
        return ImageProcessor()

    if file_type == "application/pdf":
        return PDFProcessor()

    if file_type.startswith("audio/"):
        return AudioProcessor()

    if file_type.startswith("video/"):
        return VideoProcessor()

    if file_type.startswith("application/"):
        return DocumentProcessor()

    if file_type.startswith("text/"):
        return DocumentProcessor()

    raise ValueError(
        f"Unsupported file type: {file_type}"
    )