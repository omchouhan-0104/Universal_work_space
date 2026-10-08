from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    File as FastAPIFile,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from fastapi.responses import FileResponse as FastAPIFileResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.api.dependencie import get_current_user
from app.database.session import get_db
from app.models.file import File
from app.models.user import User
from app.schemas.file import (
    FileRenameRequest,
    FileResponse,
    ShareResponse,
)
from app.services.file_service import (
    create_share_token,
    revoke_share_token,
    save_uploaded_file,
)


router = APIRouter(
    prefix="/files",
    tags=["Files"],
)


# ============================================================
# UPLOAD FILE
# ============================================================

@router.post(
    "/upload",
    response_model=FileResponse,
    status_code=status.HTTP_201_CREATED,
)
def upload_file(
    upload_file: UploadFile = FastAPIFile(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):
    return save_uploaded_file(
        db=db,
        upload_file=upload_file,
        owner_id=current_user.id,
    )


# ============================================================
# LIST MY FILES
# ============================================================

@router.get("/")
def get_my_files(
    page: int = Query(
        1,
        ge=1,
        description="Page number",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of files per page",
    ),
    search: str | None = Query(
        None,
        description="Search files by filename",
    ),
    file_type: str | None = Query(
        None,
        description="Filter by file type, e.g. pdf, jpg, mp3",
    ),
    mime_type: str | None = Query(
        None,
        description="Filter by MIME type, e.g. application/pdf",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    # --------------------------------------------------------
    # Base query
    # --------------------------------------------------------

    query = select(File).where(
        File.owner_id == current_user.id
    )

    # --------------------------------------------------------
    # Search by filename
    # --------------------------------------------------------

    if search:

        search_value = search.strip()

        if search_value:

            query = query.where(
                File.original_filename.ilike(
                    f"%{search_value}%"
                )
            )

    # --------------------------------------------------------
    # File type filter
    # --------------------------------------------------------

    if file_type:

        query = query.where(
            File.file_type
            == file_type.strip().lower()
        )

    # --------------------------------------------------------
    # MIME type filter
    # --------------------------------------------------------

    if mime_type:

        query = query.where(
            File.mime_type
            == mime_type.strip()
        )

    # --------------------------------------------------------
    # Total count
    # --------------------------------------------------------

    count_query = select(
        func.count(File.id)
    ).where(
        File.owner_id == current_user.id
    )

    # Apply same filters to count query
    if search:

        search_value = search.strip()

        if search_value:

            count_query = count_query.where(
                File.original_filename.ilike(
                    f"%{search_value}%"
                )
            )

    if file_type:

        count_query = count_query.where(
            File.file_type
            == file_type.strip().lower()
        )

    if mime_type:

        count_query = count_query.where(
            File.mime_type
            == mime_type.strip()
        )

    total = db.scalar(count_query) or 0

    # --------------------------------------------------------
    # Pagination
    # --------------------------------------------------------

    offset = (page - 1) * limit

    query = (
        query
        .order_by(
            File.created_at.desc()
        )
        .offset(offset)
        .limit(limit)
    )

    files = list(
        db.scalars(query).all()
    )

    # --------------------------------------------------------
    # Total pages
    # --------------------------------------------------------

    total_pages = (
        (total + limit - 1) // limit
        if total > 0
        else 0
    )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": "Files fetched successfully",

        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        },

        "filters": {
            "search": search,
            "file_type": file_type,
            "mime_type": mime_type,
        },

        "items": [
            {
                "id": file.id,
                "filename": file.original_filename,
                "file_type": file.file_type,
                "mime_type": file.mime_type,
                "file_size": file.file_size,
                "is_shared": file.is_shared,
                "created_at": file.created_at,
            }
            for file in files
        ],
    }


# ============================================================
# SEARCH FILES
# ============================================================

@router.get(
    "/search",
    response_model=list[FileResponse],
)
def search_files(
    q: str = Query(
        ...,
        min_length=1,
        description="Filename search query",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    statement = (
        select(File)
        .where(
            File.owner_id == current_user.id,
            File.original_filename.ilike(
                f"%{q.strip()}%"
            ),
        )
        .order_by(
            File.created_at.desc()
        )
    )

    return list(
        db.scalars(statement).all()
    )


# ============================================================
# ACCESS SHARED FILE
# ============================================================

@router.get(
    "/share/{share_token}",
)
def access_shared_file(
    share_token: str,
    db: Session = Depends(get_db),
):

    statement = select(File).where(
        File.share_token == share_token,
        File.is_shared.is_(True),
    )

    file_record = db.scalar(
        statement
    )

    if not file_record:

        raise HTTPException(
            status_code=404,
            detail="Shared file not found",
        )

    file_path = Path(
        file_record.file_path
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    return FastAPIFileResponse(
        path=file_path,
        filename=file_record.original_filename,
        media_type=file_record.mime_type,
    )


# ============================================================
# GET SINGLE FILE
# ============================================================

@router.get(
    "/{file_id}",
    response_model=FileResponse,
)
def get_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    file_record = db.get(
        File,
        file_id,
    )

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

    return file_record


# ============================================================
# DOWNLOAD FILE
# ============================================================

@router.get(
    "/{file_id}/download",
)
def download_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    file_record = db.get(
        File,
        file_id,
    )

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

    file_path = Path(
        file_record.file_path
    )

    if not file_path.exists():

        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    return FastAPIFileResponse(
        path=file_path,
        filename=file_record.original_filename,
        media_type=file_record.mime_type,
    )


# ============================================================
# RENAME FILE
# ============================================================

@router.patch(
    "/{file_id}/rename",
    response_model=FileResponse,
)
def rename_file(
    file_id: int,
    data: FileRenameRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    file_record = db.get(
        File,
        file_id,
    )

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

    new_name = data.filename.strip()

    if not new_name:

        raise HTTPException(
            status_code=400,
            detail="Filename cannot be empty",
        )

    file_record.original_filename = new_name

    try:

        db.commit()
        db.refresh(file_record)

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to rename file",
        )

    return file_record


# ============================================================
# DELETE FILE
# ============================================================

@router.delete(
    "/{file_id}",
)
def delete_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    file_record = db.get(
        File,
        file_id,
    )

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

    file_path = Path(
        file_record.file_path
    )

    # --------------------------------------------------------
    # Delete physical file
    # --------------------------------------------------------

    try:

        if file_path.exists():
            file_path.unlink()

    except OSError as exc:

        raise HTTPException(
            status_code=500,
            detail=(
                f"Failed to delete physical file: {exc}"
            ),
        )

    # --------------------------------------------------------
    # Delete database record
    # --------------------------------------------------------

    try:

        db.delete(file_record)
        db.commit()

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Failed to delete file record",
        )

    return {
        "message": "File deleted successfully",
        "file_id": file_id,
    }


# ============================================================
# CREATE SHARE LINK
# ============================================================

@router.post(
    "/{file_id}/share",
    response_model=ShareResponse,
)
def share_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    file_record = db.get(
        File,
        file_id,
    )

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

    file_record = create_share_token(
        db,
        file_record,
    )

    return {
        "file_id": file_record.id,
        "share_token": file_record.share_token,
        "share_url": (
            f"/api/v1/files/share/"
            f"{file_record.share_token}"
        ),
    }


# ============================================================
# REVOKE SHARE LINK
# ============================================================

@router.delete(
    "/{file_id}/share",
)
def revoke_share(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    file_record = db.get(
        File,
        file_id,
    )

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

    revoke_share_token(
        db,
        file_record,
    )

    return {
        "message": "File sharing disabled",
        "file_id": file_id,
    }