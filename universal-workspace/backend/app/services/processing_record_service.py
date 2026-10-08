from typing import Any

from sqlalchemy.orm import Session

from app.models.processing import FileProcessing


class ProcessingRecordService:

    @staticmethod
    def create(
        db: Session,
        input_file_id: int,
        operation: str,
        options: dict[str, Any],
    ) -> FileProcessing:

        record = FileProcessing(
            input_file_id=input_file_id,
            operation=operation,
            options=options,
            status="pending",
        )

        db.add(record)
        db.flush()

        return record

    @staticmethod
    def complete(
        db: Session,
        record: FileProcessing,
        output_file_id: int,
    ) -> FileProcessing:

        record.output_file_id = output_file_id
        record.status = "completed"

        db.flush()

        return record

    @staticmethod
    def fail(
        db: Session,
        record: FileProcessing,
    ) -> FileProcessing:

        record.status = "failed"

        db.flush()

        return record