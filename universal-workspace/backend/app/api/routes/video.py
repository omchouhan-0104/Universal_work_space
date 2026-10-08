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
    prefix="/video",
    tags=["Video Processing"],
)


processing_service = ProcessingService()


def get_video_file(
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

    if not file_record.mime_type.startswith("video/"):
        raise HTTPException(
            status_code=400,
            detail="This file is not a video file",
        )

    input_path = Path(file_record.file_path)

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    return file_record


def process_video(
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
    # Determine extension
    # --------------------------------------------------------

    if operation == "compress":

        extension = input_path.suffix.lstrip(".").lower()

    elif operation == "convert":

        video_format = options.get("format")

        if not video_format:
            raise HTTPException(
                status_code=400,
                detail="format is required for convert",
            )

        video_format = str(video_format).lower().strip().lstrip(".")

        allowed_formats = {
            "mp4",
            "webm",
            "mkv",
            "avi",
            "mov",
        }

        if video_format not in allowed_formats:
            raise HTTPException(
                status_code=400,
                detail=("Unsupported video format. " "Use mp4, webm, mkv, avi or mov"),
            )

        options["format"] = video_format
        extension = video_format

    elif operation == "extract_audio":

        extension = "mp3"

    elif operation == "thumbnail":

        extension = "jpg"

    else:

        raise HTTPException(
            status_code=400,
            detail=f"Unsupported video operation: {operation}",
        )

    # --------------------------------------------------------
    # Validate CRF
    # --------------------------------------------------------

    if operation == "compress":

        crf = options.get("crf", 28)

        try:
            crf = int(crf)
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=400,
                detail="crf must be an integer",
            )

        if crf < 18 or crf > 40:
            raise HTTPException(
                status_code=400,
                detail="crf must be between 18 and 40",
            )

        options["crf"] = crf

    # --------------------------------------------------------
    # Thumbnail timestamp
    # --------------------------------------------------------

    if operation == "thumbnail":

        timestamp = options.get(
            "timestamp",
            "00:00:01",
        )

        options["timestamp"] = str(timestamp)

    # --------------------------------------------------------
    # Filename
    # --------------------------------------------------------

    unique_id = uuid4().hex[:12]

    output_filename = (
        f"{operation}_" f"{input_path.stem}_" f"{unique_id}." f"{extension}"
    )

    output_path = output_directory / output_filename

    # --------------------------------------------------------
    # Process
    # --------------------------------------------------------

    try:

        processing_service.process(
            file_category="video",
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
            detail=f"Video processing failed: {str(exc)}",
        )

    # --------------------------------------------------------
    # Check output
    # --------------------------------------------------------

    if not output_path.exists():

        raise HTTPException(
            status_code=500,
            detail="Processed video was not created",
        )

    output_size = output_path.stat().st_size

    # --------------------------------------------------------
    # MIME type
    # --------------------------------------------------------

    mime_types = {
        "mp4": "video/mp4",
        "webm": "video/webm",
        "mkv": "video/x-matroska",
        "avi": "video/x-msvideo",
        "mov": "video/quicktime",
        "mp3": "audio/mpeg",
        "jpg": "image/jpeg",
    }

    output_mime_type = mime_types.get(
        extension,
        file_record.mime_type,
    )

    # --------------------------------------------------------
    # Database record
    # --------------------------------------------------------

    processed_file = File(
        original_filename=output_path.name,
        stored_filename=output_path.name,
        file_path=str(output_path),
        file_type=extension,
        mime_type=output_mime_type,
        file_size=output_size,
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
            detail="Failed to save processed video",
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

    return {
        "message": "Video processed successfully",
        "file_id": processed_file.id,
        "original_file_id": file_record.id,
        "category": "video",
        "operation": operation,
        "options": options,
        "input_file": file_record.original_filename,
        "output_file": output_path.name,
        "output_path": str(output_path),
        "output_size": output_size,
        "mime_type": output_mime_type,
    }


# ============================================================
# COMPRESS
# ============================================================


@router.post("/{file_id}/compress")
def compress_video(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_video_file(
        file_id,
        db,
        current_user,
    )

    return process_video(
        file_record=file_record,
        operation="compress",
        options=dict(request.options or {}),
        db=db,
        current_user=current_user,
    )


# ============================================================
# CONVERT
# ============================================================


@router.post("/{file_id}/convert")
def convert_video(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_video_file(
        file_id,
        db,
        current_user,
    )

    return process_video(
        file_record=file_record,
        operation="convert",
        options=dict(request.options or {}),
        db=db,
        current_user=current_user,
    )


# ============================================================
# EXTRACT AUDIO
# ============================================================


@router.post("/{file_id}/extract-audio")
def extract_audio(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_video_file(
        file_id,
        db,
        current_user,
    )

    return process_video(
        file_record=file_record,
        operation="extract_audio",
        options=dict(request.options or {}),
        db=db,
        current_user=current_user,
    )


# ============================================================
# THUMBNAIL
# ============================================================


@router.post("/{file_id}/thumbnail")
def generate_thumbnail(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_video_file(
        file_id,
        db,
        current_user,
    )

    return process_video(
        file_record=file_record,
        operation="thumbnail",
        options=dict(request.options or {}),
        db=db,
        current_user=current_user,
    )
