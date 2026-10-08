from typing import Any

from sqlalchemy.orm import Session

from app.models.processing import FileProcessing


class ProcessingHistoryService:

    # ========================================================
    # CREATE HISTORY
    # ========================================================

    @staticmethod
    def create(
        db: Session,
        input_file_id: int,
        output_file_id: int | None,
        operation: str,
        options: dict[str, Any] | None = None,
        status: str = "completed",
    ) -> FileProcessing:

        processing = FileProcessing(
            input_file_id=input_file_id,
            output_file_id=output_file_id,
            operation=operation,
            options=options or {},
            status=status,
        )

        db.add(processing)
        db.commit()
        db.refresh(processing)

        return processing

    # ========================================================
    # GET BY ID
    # ========================================================

    @staticmethod
    def get_by_id(
        db: Session,
        processing_id: int,
    ) -> FileProcessing | None:

        return db.get(
            FileProcessing,
            processing_id,
        )

    # ========================================================
    # GET USER HISTORY
    # ========================================================

    @staticmethod
    def get_user_history(
        db: Session,
        user_id: int,
        page: int = 1,
        limit: int = 20,
        operation: str | None = None,
        status: str | None = None,
    ):

        query = (
            db.query(FileProcessing)
            .join(
                FileProcessing.input_file
            )
            .filter(
                FileProcessing.input_file.has(
                    owner_id=user_id
                )
            )
        )

        # ----------------------------------------------------
        # Operation filter
        # ----------------------------------------------------

        if operation:

            query = query.filter(
                FileProcessing.operation
                == operation
            )

        # ----------------------------------------------------
        # Status filter
        # ----------------------------------------------------

        if status:

            query = query.filter(
                FileProcessing.status
                == status
            )

        # ----------------------------------------------------
        # Total records
        # ----------------------------------------------------

        total = query.count()

        # ----------------------------------------------------
        # Pagination
        # ----------------------------------------------------

        offset = (page - 1) * limit

        history = (
            query
            .order_by(
                FileProcessing.created_at.desc()
            )
            .offset(offset)
            .limit(limit)
            .all()
        )

        return history, total

    # ========================================================
    # DELETE HISTORY
    # ========================================================

    @staticmethod
    def delete(
        db: Session,
        processing: FileProcessing,
    ) -> None:

        db.delete(processing)
        db.commit() 