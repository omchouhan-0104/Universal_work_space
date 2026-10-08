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
    prefix="/pdf",
    tags=["PDF Processing"],
)


processing_service = ProcessingService()


# ============================================================
# GET PDF FILE
# ============================================================


def get_pdf_file(
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

    if file_record.mime_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="The selected file is not a PDF",
        )

    input_path = Path(file_record.file_path)

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    return file_record


# ============================================================
# COMMON PDF PROCESSING
# ============================================================


def process_pdf(
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

    extension = "pdf"

    unique_id = uuid4().hex[:12]

    output_filename = (
        f"{operation}_" f"{input_path.stem}_" f"{unique_id}." f"{extension}"
    )

    output_path = output_directory / output_filename

    # --------------------------------------------------------
    # Process PDF
    # --------------------------------------------------------

    try:

        processing_service.process(
            file_category="pdf",
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
            detail=f"PDF processing failed: {str(exc)}",
        )

    # --------------------------------------------------------
    # Check output
    # --------------------------------------------------------

    if not output_path.exists():

        raise HTTPException(
            status_code=500,
            detail="Processed PDF was not created",
        )

    processed_file_size = output_path.stat().st_size

    # --------------------------------------------------------
    # Create database record
    # --------------------------------------------------------

    processed_file = File(
        original_filename=output_path.name,
        stored_filename=output_path.name,
        file_path=str(output_path),
        file_type="pdf",
        mime_type="application/pdf",
        file_size=processed_file_size,
        owner_id=current_user.id,
        is_shared=False,
    )

    db.add(processed_file)

    try:

        db.commit()
        db.refresh(processed_file)

    except Exception:

        db.rollback()

        if output_path.exists():
            output_path.unlink()

        raise HTTPException(
            status_code=500,
            detail="Failed to save processed PDF",
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
        "message": "PDF processed successfully",
        "file_id": processed_file.id,
        "original_file_id": file_record.id,
        "category": "pdf",
        "operation": operation,
        "options": options,
        "input_file": file_record.original_filename,
        "output_file": output_path.name,
        "output_path": str(output_path),
        "output_size": processed_file_size,
        "mime_type": "application/pdf",
    }


# ============================================================
# COMPRESS PDF
# ============================================================


@router.post("/{file_id}/compress")
def compress_pdf(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_pdf_file(
        file_id=file_id,
        db=db,
        current_user=current_user,
    )

    options = dict(request.options or {})

    quality = options.get(
        "quality",
        70,
    )

    try:

        quality = int(quality)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=400,
            detail="Quality must be an integer",
        )

    if quality < 1 or quality > 100:

        raise HTTPException(
            status_code=400,
            detail="Quality must be between 1 and 100",
        )

    options["quality"] = quality

    return process_pdf(
        file_record=file_record,
        operation="compress",
        options=options,
        db=db,
        current_user=current_user,
    )


# ============================================================
# ROTATE PDF
# ============================================================


@router.post("/{file_id}/rotate")
def rotate_pdf(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_pdf_file(
        file_id=file_id,
        db=db,
        current_user=current_user,
    )

    options = dict(request.options or {})

    rotation = options.get("rotation")

    if rotation is None:

        raise HTTPException(
            status_code=400,
            detail=("rotation is required " "for PDF rotate"),
        )

    try:

        rotation = int(rotation)

    except (TypeError, ValueError):

        raise HTTPException(
            status_code=400,
            detail="rotation must be an integer",
        )

    if rotation not in {
        90,
        180,
        270,
    }:

        raise HTTPException(
            status_code=400,
            detail=("rotation must be " "90, 180 or 270 degrees"),
        )

    options["rotation"] = rotation

    return process_pdf(
        file_record=file_record,
        operation="rotate",
        options=options,
        db=db,
        current_user=current_user,
    )
