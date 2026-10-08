from pathlib import Path
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencie import get_current_user
from app.database.session import get_db
from app.models.file import File
from app.models.user import User
from app.schemas.processing import ProcessRequest
from app.services.processing_service import ProcessingService
from app.services.processing_history_service import (
    ProcessingHistoryService,
)

router = APIRouter(
    prefix="/document",
    tags=["Document Processing"],
)


processing_service = ProcessingService()


# ============================================================
# GET DOCUMENT FILE
# ============================================================


def get_document_file(
    file_id: int,
    db: Session,
    current_user: User,
) -> File:

    file_record = db.get(File, file_id)

    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    if file_record.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this file",
        )

    if not file_record.mime_type:
        raise HTTPException(
            status_code=400,
            detail="File MIME type is missing",
        )

    # Currently our DocumentProcessor supports DOCX
    if not (
        file_record.mime_type
        == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    ):
        raise HTTPException(
            status_code=400,
            detail="Currently only DOCX documents are supported",
        )

    input_path = Path(file_record.file_path)

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    return file_record


# ============================================================
# COMMON DOCUMENT PROCESSING
# ============================================================


def process_document(
    file_record: File,
    operation: str,
    options: dict,
    db: Session,
    current_user: User,
) -> dict:

    input_path = Path(file_record.file_path)

    output_directory = input_path.parent / "processed"

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------------------------------
    # Output extension
    # --------------------------------------------------------

    if operation == "extract_text":
        extension = "txt"

    elif operation == "convert_pdf":
        extension = "pdf"

    else:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported document operation: {operation}",
        )

    # --------------------------------------------------------
    # Unique filename
    # --------------------------------------------------------

    unique_id = uuid4().hex[:12]

    output_filename = (
        f"{operation}_" f"{input_path.stem}_" f"{unique_id}." f"{extension}"
    )

    output_path = output_directory / output_filename

    # --------------------------------------------------------
    # Process document
    # --------------------------------------------------------

    try:

        processing_service.process(
            file_category="document",
            input_path=input_path,
            output_path=output_path,
            operation=operation,
            **options,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(f"Document processing failed: {str(exc)}"),
        )

    # --------------------------------------------------------
    # Check output
    # --------------------------------------------------------

    if not output_path.exists():

        raise HTTPException(
            status_code=500,
            detail="Processed document was not created",
        )

    processed_file_size = output_path.stat().st_size

    # --------------------------------------------------------
    # MIME type
    # --------------------------------------------------------

    if extension == "txt":
        output_mime_type = "text/plain"
    else:
        output_mime_type = "application/pdf"

    # --------------------------------------------------------
    # Create DB record
    # --------------------------------------------------------

    processed_file = File(
        original_filename=output_path.name,
        stored_filename=output_path.name,
        file_path=str(output_path),
        file_type=extension,
        mime_type=output_mime_type,
        file_size=processed_file_size,
        owner_id=current_user.id,
        is_shared=False,
    )

    db.add(processed_file)

    # --------------------------------------------------------
    # Save DB record
    # --------------------------------------------------------

    try:

        db.commit()
        db.refresh(processed_file)

    except Exception:

        db.rollback()

        if output_path.exists():
            output_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Failed to save processed document",
        )

    # ============================================================
    # CREATE PROCESSING HISTORY
    # ============================================================

    try:

        ProcessingHistoryService.create(
            db=db,
            input_file_id=file_record.id,
            output_file_id=processed_file.id,
            operation=operation,
            options=options,
            status="completed",
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=(f"Failed to save processing history: " f"{str(exc)}"),
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": "Document processed successfully",
        "file_id": processed_file.id,
        "original_file_id": file_record.id,
        "category": "document",
        "operation": operation,
        "options": options,
        "input_file": file_record.original_filename,
        "output_file": output_path.name,
        "output_path": str(output_path),
        "output_size": processed_file_size,
        "mime_type": output_mime_type,
    }


# ============================================================
# EXTRACT TEXT
# ============================================================


@router.post("/{file_id}/extract-text")
def extract_text(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_document_file(
        file_id=file_id,
        db=db,
        current_user=current_user,
    )

    return process_document(
        file_record=file_record,
        operation="extract_text",
        options=dict(request.options or {}),
        db=db,
        current_user=current_user,
    )


# ============================================================
# DOCX → PDF
# ============================================================


@router.post("/{file_id}/convert-pdf")
def convert_pdf(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_document_file(
        file_id=file_id,
        db=db,
        current_user=current_user,
    )

    return process_document(
        file_record=file_record,
        operation="convert_pdf",
        options=dict(request.options or {}),
        db=db,
        current_user=current_user,
    )
