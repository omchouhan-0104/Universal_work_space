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


router = APIRouter(
    prefix="/process",
    tags=["File Processing"],
)


processing_service = ProcessingService()


@router.post("/{file_id}")
def process_file(
    file_id: int,
    request: ProcessRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    # ========================================
    # 1. FIND FILE
    # ========================================

    file_record = db.get(File, file_id)

    if not file_record:
        raise HTTPException(
            status_code=404,
            detail="File not found",
        )

    # ========================================
    # 2. CHECK OWNERSHIP
    # ========================================

    if file_record.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this file",
        )

    # ========================================
    # 3. CHECK MIME TYPE
    # ========================================

    if not file_record.mime_type:
        raise HTTPException(
            status_code=400,
            detail="File MIME type is missing",
        )

    # ========================================
    # 4. DETECT CATEGORY
    # ========================================

    try:
        category = processing_service.detect_category(
            file_record.mime_type
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    # ========================================
    # 5. SUPPORTED CATEGORIES
    # ========================================

    if category not in {
        "image",
        "pdf",
        "document",
        "audio",
        "video",
    }:
        raise HTTPException(
            status_code=400,
            detail=(
                "This file type is not supported "
                "for processing yet"
            ),
        )

    # ========================================
    # 6. CHECK PHYSICAL FILE
    # ========================================

    input_path = Path(file_record.file_path)

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    # ========================================
    # 7. GET OPERATION AND OPTIONS
    # ========================================

    operation = request.operation.lower().strip()

    options = dict(request.options or {})

    # ========================================
    # 8. ALLOWED OPERATIONS
    # ========================================

    if category == "image":

        allowed_operations = {
            "compress",
            "convert",
            "resize",
            "crop",
        }

    elif category == "pdf":

        allowed_operations = {
            "compress",
            "rotate",
        }

    elif category == "document":

        allowed_operations = {
            "extract_text",
            "convert_pdf",
        }

    elif category == "audio":

        allowed_operations = {
            "compress",
            "convert",
        }

    elif category == "video":

        allowed_operations = {
            "compress",
            "convert",
            "extract_audio",
        }

    else:

        allowed_operations = set()

    # ========================================
    # 9. CHECK OPERATION
    # ========================================

    if operation not in allowed_operations:

        raise HTTPException(
            status_code=400,
            detail=(
                f"Unsupported operation "
                f"'{operation}' for file category "
                f"'{category}'"
            ),
        )

    # ========================================
    # 10. VALIDATE OPTIONS
    # ========================================

    # ----------------------------------------
    # IMAGE / AUDIO / VIDEO COMPRESS
    # ----------------------------------------

    if operation == "compress":

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

    # ----------------------------------------
    # IMAGE CONVERT
    # ----------------------------------------

    elif category == "image" and operation == "convert":

        image_format = options.get("format")

        if not image_format:

            raise HTTPException(
                status_code=400,
                detail="format is required for image convert",
            )

        image_format = (
            str(image_format)
            .lower()
            .strip()
            .lstrip(".")
        )

        allowed_formats = {
            "jpg",
            "jpeg",
            "png",
            "webp",
        }

        if image_format not in allowed_formats:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported image format. "
                    "Use jpg, jpeg, png or webp"
                ),
            )

        options["format"] = image_format

    # ----------------------------------------
    # AUDIO CONVERT
    # ----------------------------------------

    elif category == "audio" and operation == "convert":

        audio_format = options.get("format")

        if not audio_format:

            raise HTTPException(
                status_code=400,
                detail="format is required for audio convert",
            )

        audio_format = (
            str(audio_format)
            .lower()
            .strip()
            .lstrip(".")
        )

        allowed_formats = {
            "mp3",
            "wav",
            "ogg",
            "aac",
            "flac",
            "m4a",
        }

        if audio_format not in allowed_formats:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported audio format. "
                    "Use mp3, wav, ogg, aac, flac or m4a"
                ),
            )

        options["format"] = audio_format

    # ----------------------------------------
    # VIDEO CONVERT
    # ----------------------------------------

    elif category == "video" and operation == "convert":

        video_format = options.get("format")

        if not video_format:

            raise HTTPException(
                status_code=400,
                detail="format is required for video convert",
            )

        video_format = (
            str(video_format)
            .lower()
            .strip()
            .lstrip(".")
        )

        allowed_formats = {
            "mp4",
            "avi",
            "mkv",
            "mov",
            "webm",
        }

        if video_format not in allowed_formats:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Unsupported video format. "
                    "Use mp4, avi, mkv, mov or webm"
                ),
            )

        options["format"] = video_format

    # ----------------------------------------
    # IMAGE RESIZE
    # ----------------------------------------

    elif operation == "resize":

        width = options.get("width")
        height = options.get("height")

        if width is None or height is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "width and height are "
                    "required for resize"
                ),
            )

        try:

            width = int(width)
            height = int(height)

        except (TypeError, ValueError):

            raise HTTPException(
                status_code=400,
                detail=(
                    "width and height "
                    "must be integers"
                ),
            )

        if width <= 0 or height <= 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "width and height "
                    "must be greater than 0"
                ),
            )

        options["width"] = width
        options["height"] = height

    # ----------------------------------------
    # IMAGE CROP
    # ----------------------------------------

    elif operation == "crop":

        required = [
            "left",
            "top",
            "right",
            "bottom",
        ]

        for field in required:

            if field not in options:

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{field} is required "
                        "for crop"
                    ),
                )

            try:

                options[field] = int(
                    options[field]
                )

            except (TypeError, ValueError):

                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"{field} must be an integer"
                    ),
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

    # ----------------------------------------
    # PDF ROTATE
    # ----------------------------------------

    elif operation == "rotate":

        rotation = options.get("rotation")

        if rotation is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "rotation is required "
                    "for PDF rotate"
                ),
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
                detail=(
                    "rotation must be "
                    "90, 180 or 270 degrees"
                ),
            )

        options["rotation"] = rotation

    # ----------------------------------------
    # DOCUMENT EXTRACT TEXT
    # ----------------------------------------

    elif operation == "extract_text":

        if input_path.suffix.lower() != ".docx":

            raise HTTPException(
                status_code=400,
                detail=(
                    "extract_text currently "
                    "supports DOCX files only"
                ),
            )

    # ----------------------------------------
    # DOCUMENT → PDF
    # ----------------------------------------

    elif operation == "convert_pdf":

        if input_path.suffix.lower() != ".docx":

            raise HTTPException(
                status_code=400,
                detail=(
                    "convert_pdf currently "
                    "supports DOCX files only"
                ),
            )

    # ========================================
    # 11. CREATE OUTPUT DIRECTORY
    # ========================================

    output_directory = (
        input_path.parent / "processed"
    )

    output_directory.mkdir(
        parents=True,
        exist_ok=True,
    )

    # ========================================
    # 12. DETERMINE OUTPUT EXTENSION
    # ========================================

    if operation == "convert":

        extension = options["format"]

    elif operation == "convert_pdf":

        extension = "pdf"

    elif operation == "extract_text":

        extension = "txt"

    elif operation == "extract_audio":

        extension = "mp3"

    else:

        extension = input_path.suffix.lstrip(".")

    # ========================================
    # 13. CREATE UNIQUE OUTPUT NAME
    # ========================================

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

    # ========================================
    # 14. PROCESS FILE
    # ========================================

    try:

        processing_service.process(
            file_category=category,
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
            detail=f"Processing failed: {str(exc)}",
        )

    # ========================================
    # 15. CHECK OUTPUT
    # ========================================

    if not output_path.exists():

        raise HTTPException(
            status_code=500,
            detail="Processed file was not created",
        )

    processed_file_size = (
        output_path.stat().st_size
    )

    # ========================================
    # 16. MIME TYPES
    # ========================================

    mime_types = {

        # Images
        "jpg": "image/jpeg",
        "jpeg": "image/jpeg",
        "png": "image/png",
        "webp": "image/webp",

        # PDF
        "pdf": "application/pdf",

        # Document
        "txt": "text/plain",

        # Audio
        "mp3": "audio/mpeg",
        "wav": "audio/wav",
        "ogg": "audio/ogg",
        "aac": "audio/aac",
        "flac": "audio/flac",
        "m4a": "audio/mp4",

        # Video
        "mp4": "video/mp4",
        "avi": "video/x-msvideo",
        "mkv": "video/x-matroska",
        "mov": "video/quicktime",
        "webm": "video/webm",
    }

    output_extension = (
        output_path.suffix
        .lower()
        .lstrip(".")
    )

    output_mime_type = mime_types.get(
        output_extension,
        file_record.mime_type,
    )

    # ========================================
    # 17. CREATE DATABASE FILE RECORD
    # ========================================

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

    # ========================================
    # 18. SAVE DATABASE RECORD
    # ========================================

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

    # ========================================
    # 19. RETURN RESPONSE
    # ========================================

    return {
        "message": "File processed successfully",
        "file_id": processed_file.id,
        "original_file_id": file_record.id,
        "category": category,
        "operation": operation,
        "options": options,
        "input_file": file_record.original_filename,
        "output_file": output_path.name,
        "output_path": str(output_path),
        "output_size": processed_file_size,
        "mime_type": output_mime_type,
    }