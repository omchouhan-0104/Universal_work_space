from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.dependencie import get_current_user
from app.database.session import get_db
from app.models.file import File
from app.models.user import User


router = APIRouter(
    prefix="/files",
    tags=["File Download"],
)


# ============================================================
# GET FILE
# ============================================================

def get_user_file(
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

    # --------------------------------------------------------
    # Ownership check
    # --------------------------------------------------------

    if file_record.owner_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You do not have access to this file",
        )

    # --------------------------------------------------------
    # Physical file check
    # --------------------------------------------------------

    file_path = Path(file_record.file_path)

    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    if not file_path.is_file():
        raise HTTPException(
            status_code=400,
            detail="Invalid file",
        )

    return file_record


# ============================================================
# DOWNLOAD FILE
# ============================================================

@router.get("/{file_id}/download")
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_user_file(
        file_id=file_id,
        db=db,
        current_user=current_user,
    )

    file_path = Path(
        file_record.file_path
    )

    return FileResponse(
        path=str(file_path),
        filename=file_record.original_filename,
        media_type=file_record.mime_type
        or "application/octet-stream",
    )


# ============================================================
# PREVIEW FILE
# ============================================================

@router.get("/{file_id}/preview")
def preview_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):

    file_record = get_user_file(
        file_id=file_id,
        db=db,
        current_user=current_user,
    )

    file_path = Path(
        file_record.file_path
    )

    return FileResponse(
        path=str(file_path),
        media_type=file_record.mime_type
        or "application/octet-stream",
        content_disposition_type="inline",
    )