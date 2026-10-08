import shutil
import uuid
from pathlib import Path

from fastapi import UploadFile
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.file import File


UPLOAD_DIR = settings.storage_dir / "uploads"

UPLOAD_DIR.mkdir(
    parents=True,
    exist_ok=True,
)


def get_file_category(
    content_type: str | None,
) -> str:
    if not content_type:
        return "other"

    if content_type.startswith("image/"):
        return "image"

    if content_type.startswith("video/"):
        return "video"

    if content_type.startswith("audio/"):
        return "audio"

    if content_type in {
        "application/pdf",
    }:
        return "pdf"

    if (
        "word" in content_type
        or "document" in content_type
        or "text" in content_type
    ):
        return "document"

    if (
        "spreadsheet" in content_type
        or "excel" in content_type
    ):
        return "spreadsheet"

    if (
        "presentation" in content_type
        or "powerpoint" in content_type
    ):
        return "presentation"

    return "other"


def save_uploaded_file(
    db: Session,
    upload_file: UploadFile,
    owner_id: int,
) -> File:

    original_filename = (
        upload_file.filename
        or "unknown_file"
    )

    extension = Path(
        original_filename
    ).suffix

    stored_filename = (
        f"{uuid.uuid4()}{extension}"
    )

    file_path = (
        UPLOAD_DIR / stored_filename
    )

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(
            upload_file.file,
            buffer,
        )

    file_size = file_path.stat().st_size

    file_record = File(
        original_filename=original_filename,
        stored_filename=stored_filename,
        file_path=str(file_path),
        file_type=get_file_category(
            upload_file.content_type
        ),
        mime_type=upload_file.content_type,
        file_size=file_size,
        owner_id=owner_id,
    )

    db.add(file_record)
    db.commit()
    db.refresh(file_record)

    return file_record

def generate_share_token() -> str:
    return uuid.uuid4().hex

def create_share_token(
    db: Session,
    file_record: File,
) -> File:

    file_record.share_token = generate_share_token()
    file_record.is_shared = True

    db.commit()
    db.refresh(file_record)

    return file_record

def revoke_share_token(
    db: Session,
    file_record: File,
) -> File:

    file_record.share_token = None
    file_record.is_shared = False

    db.commit()
    db.refresh(file_record)

    return file_record