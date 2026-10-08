from abc import ABC, abstractmethod
from pathlib import Path
from app.models.processing import FileProcessing

class BaseProcessor(ABC):

    @abstractmethod
    def process(
        self,
        input_path: Path,
        output_path: Path,
        operation: str,
        **options,
    ) -> Path:
        pass
    