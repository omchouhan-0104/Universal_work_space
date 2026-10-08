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
    prefix="/audio",
    tags=["Audio Processing"],
)


processing_service = ProcessingService()


# ============================================================
# GET AUDIO FILE
# ============================================================

def get_audio_file(
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

    if not file_record.mime_type.startswith("audio/"):
        raise HTTPException(
            status_code=400,
            detail="This file is not an audio file",
        )

    input_path = Path(
        file_record.file_path
    )

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical audio file not found",
        )

    return file_record


# ============================================================
# COMMON AUDIO PROCESSING
# ============================================================

def process_audio(
    file_record: File,
    operation: str,
    options: dict,
    db: Session,
    current_user: User,
) -> dict:

    input_path = Path(
        file_record.file_path
    )

    output_directory = (
        input_path.parent / "processed"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # --------------------------------
    # Output extension
    # --------------------------------

    if operation == "convert":

        extension = options.get(
            "format"
        )

        if not extension:
            raise HTTPException(
                status_code=400,
                detail="format is required for convert",
            )

        extension = (
            str(extension)
            .lower()
            .strip()
            .lstrip(".")
        )

    elif operation == "compress":

        extension = (
            input_path.suffix
            .lower()
            .lstrip(".")
        )

        if not extension:
            raise HTTPException(
                status_code=400,
                detail="Audio file extension is missing",
            )

    else:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported audio operation: "
                f"{operation}"
            ),
        )

    # --------------------------------
    # Unique filename
    # --------------------------------

    unique_id = uuid4().hex[:12]

    output_filename = (
        f"{operation}_"
        f"{input_path.stem}_"
        f"{unique_id}."
        f"{extension}"
    )

    output_path = (
        output_directory / output_filename
    )

    # --------------------------------
    # Process
    # --------------------------------

    try:

        processing_service.process(
            file_category="audio",
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
            detail=(
                f"Audio processing failed: "
                f"{str(exc)}"
            ),
        )

    # --------------------------------
    # Check output
    # --------------------------------

    if not output_path.exists():

        raise HTTPException(
            status_code=500,
            detail=(
                "Processed audio file "
                "was not created"
            ),
        )

    processed_file_size = (
        output_path.stat().st_size
    )

    # --------------------------------
    # MIME type
    # --------------------------------

    mime_types = {
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "aac": "audio/aac",
        "flac": "audio/flac",
        "m4a": "audio/mp4",
    }

    output_mime_type = mime_types.get(
        extension,
        file_record.mime_type,
    )

    # --------------------------------
    # Create DB record
    # --------------------------------

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

    # --------------------------------
    # Save DB record
    # --------------------------------

    try:

        db.commit()
        db.refresh(processed_file)

    except Exception:

        db.rollback()

        if output_path.exists():
            output_path.unlink()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to save "
                "processed audio"
            ),
        )
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

    # The output file was already created successfully.
    # History failure should not delete the output file.

        raise HTTPException(
        status_code=500,
        detail=(
            f"Failed to save processing history: "
            f"{str(exc)}"
        ),
    )

    # --------------------------------
    # Response
    # --------------------------------

    return {
        "message": "Audio processed successfully",
        "file_id": processed_file.id,
        "original_file_id": file_record.id,
        "category": "audio",
        "operation": operation,
        "options": options,
        "input_file": (
            file_record.original_filename
        ),
        "output_file": output_path.name,
        "output_path": str(output_path),
        "output_size": processed_file_size,
        "mime_type": output_mime_type,
    }


# ============================================================
# AUDIO CONVERT
# ============================================================

@router.post("/{file_id}/convert")
def convert_audio(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_audio_file(
        file_id=file_id,
        db=db,
        current_user=current_user,
    )

    options = dict(
        request.options or {}
    )

    return process_audio(
        file_record=file_record,
        operation="convert",
        options=options,
        db=db,
        current_user=current_user,
    )


# ============================================================
# AUDIO COMPRESS
# ============================================================

@router.post("/{file_id}/compress")
def compress_audio(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_audio_file(
        file_id=file_id,
        db=db,
        current_user=current_user,
    )

    options = dict(
        request.options or {}
    )

    return process_audio(
        file_record=file_record,
        operation="compress",
        options=options,
        db=db,
        current_user=current_user,
    )