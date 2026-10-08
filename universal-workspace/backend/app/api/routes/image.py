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
    prefix="/image",
    tags=["Image Processing"],
)


processing_service = ProcessingService()


def get_image_file(
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

    if not file_record.mime_type.startswith("image/"):
        raise HTTPException(
            status_code=400,
            detail="The selected file is not an image",
        )

    input_path = Path(file_record.file_path)

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    return file_record


def process_image(
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

    if operation == "convert":
        extension = options["format"]
    else:
        extension = input_path.suffix.lstrip(".").lower()

    unique_id = uuid4().hex[:12]

    output_filename = (
        f"{operation}_" f"{input_path.stem}_" f"{unique_id}." f"{extension}"
    )

    output_path = output_directory / output_filename

    try:

        processing_service.process(
            file_category="image",
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
            detail=f"Image processing failed: {str(exc)}",
        )

    if not output_path.exists():

        raise HTTPException(
            status_code=500,
            detail="Processed file was not created",
        )

    processed_file_size = output_path.stat().st_size

    mime_types = {
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",
        "bmp": "image/bmp",
        "gif": "image/gif",
    }

    output_extension = output_path.suffix.lower().lstrip(".")

    output_mime_type = mime_types.get(
        output_extension,
        file_record.mime_type,
    )

    processed_file = File(
        original_filename=output_path.name,
        stored_filename=output_path.name,
        file_path=str(output_path),
        file_type=output_extension,
        mime_type=output_mime_type,
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
            detail="Failed to save processed file",
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
        "message": "Image processed successfully",
        "file_id": processed_file.id,
        "original_file_id": file_record.id,
        "category": "image",
        "operation": operation,
        "options": options,
        "input_file": file_record.original_filename,
        "output_file": output_path.name,
        "output_path": str(output_path),
        "output_size": processed_file_size,
        "mime_type": output_mime_type,
    }


# ============================================================
# COMPRESS
# ============================================================


@router.post("/{file_id}/compress")
def compress_image(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_image_file(
        file_id,
        db,
        current_user,
    )

    options = dict(request.options or {})

    quality = options.get("quality", 70)

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

    return process_image(
        file_record=file_record,
        operation="compress",
        options=options,
        db=db,
        current_user=current_user,
    )


# ============================================================
# CONVERT
# ============================================================


@router.post("/{file_id}/convert")
def convert_image(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_image_file(
        file_id,
        db,
        current_user,
    )

    options = dict(request.options or {})

    image_format = options.get("format")

    if not image_format:
        raise HTTPException(
            status_code=400,
            detail="format is required for convert",
        )

    image_format = str(image_format).lower().strip().lstrip(".")

    allowed_formats = {
        "jpg",
        "jpeg",
        "png",
        "webp",
    }

    if image_format not in allowed_formats:
        raise HTTPException(
            status_code=400,
            detail=("Unsupported image format. " "Use jpg, jpeg, png or webp"),
        )

    options["format"] = image_format

    return process_image(
        file_record=file_record,
        operation="convert",
        options=options,
        db=db,
        current_user=current_user,
    )


# ============================================================
# RESIZE
# ============================================================


@router.post("/{file_id}/resize")
def resize_image(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_image_file(
        file_id,
        db,
        current_user,
    )

    options = dict(request.options or {})

    width = options.get("width")
    height = options.get("height")

    if width is None or height is None:
        raise HTTPException(
            status_code=400,
            detail="width and height are required",
        )

    try:
        width = int(width)
        height = int(height)
    except (TypeError, ValueError):
        raise HTTPException(
            status_code=400,
            detail="width and height must be integers",
        )

    if width <= 0 or height <= 0:
        raise HTTPException(
            status_code=400,
            detail="width and height must be greater than 0",
        )

    options["width"] = width
    options["height"] = height

    return process_image(
        file_record=file_record,
        operation="resize",
        options=options,
        db=db,
        current_user=current_user,
    )


# ============================================================
# CROP
# ============================================================


@router.post("/{file_id}/crop")
def crop_image(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_image_file(
        file_id,
        db,
        current_user,
    )

    options = dict(request.options or {})

    required_fields = [
        "left",
        "top",
        "right",
        "bottom",
    ]

    for field in required_fields:

        if field not in options:
            raise HTTPException(
                status_code=400,
                detail=f"{field} is required for crop",
            )

        try:
            options[field] = int(options[field])
        except (TypeError, ValueError):
            raise HTTPException(
                status_code=400,
                detail=f"{field} must be an integer",
            )

    if options["left"] < 0:
        raise HTTPException(
            status_code=400,
            detail="left cannot be negative",
        )

    if options["top"] < 0:
        raise HTTPException(
            status_code=400,
            detail="top cannot be negative",
        )

    if options["right"] <= options["left"]:
        raise HTTPException(
            status_code=400,
            detail="right must be greater than left",
        )

    if options["bottom"] <= options["top"]:
        raise HTTPException(
            status_code=400,
            detail="bottom must be greater than top",
        )

    return process_image(
        file_record=file_record,
        operation="crop",
        options=options,
        db=db,
        current_user=current_user,
    )
