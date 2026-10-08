from pathlib import Path

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Query,
)
from sqlalchemy.orm import Session

from app.api.dependencie import get_current_user
from app.database.session import get_db
from app.models.user import User
from app.services.processing_history_service import (
    ProcessingHistoryService,
)


router = APIRouter(
    prefix="/processing/history",
    tags=["Processing History"],
)


# ============================================================
# FILE DETAILS HELPER
# ============================================================

def file_details(file_record):

    if not file_record:
        return None

    return {
        "id": file_record.id,
        "filename": file_record.original_filename,
        "file_type": file_record.file_type,
        "mime_type": file_record.mime_type,
        "file_size": file_record.file_size,
        "created_at": file_record.created_at,
    }


# ============================================================
# GET PROCESSING HISTORY
# ============================================================

@router.get("")
def get_processing_history(
    page: int = Query(
        1,
        ge=1,
        description="Page number",
    ),
    limit: int = Query(
        20,
        ge=1,
        le=100,
        description="Number of history records per page",
    ),
    operation: str | None = Query(
        None,
        description="Filter by processing operation",
    ),
    status: str | None = Query(
        None,
        description="Filter by processing status",
    ),
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    # --------------------------------------------------------
    # Normalize filters
    # --------------------------------------------------------

    if operation:
        operation = operation.lower().strip()

    if status:
        status = status.lower().strip()

    # --------------------------------------------------------
    # Get processing history
    # --------------------------------------------------------

    history, total = (
        ProcessingHistoryService.get_user_history(
            db=db,
            user_id=current_user.id,
            page=page,
            limit=limit,
            operation=operation,
            status=status,
        )
    )

    # --------------------------------------------------------
    # Calculate total pages
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
        "message": (
            "Processing history fetched successfully"
        ),

        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages,
        },

        "filters": {
            "operation": operation,
            "status": status,
        },

        "items": [
            {
                "id": item.id,

                "input_file_id": (
                    item.input_file_id
                ),

                "output_file_id": (
                    item.output_file_id
                ),

                "operation": item.operation,

                "options": item.options,

                "status": item.status,

                "created_at": item.created_at,

                "input_file": file_details(
                    item.input_file
                ),

                "output_file": file_details(
                    item.output_file
                ),

                "download_url": (
                    f"/api/v1/files/"
                    f"{item.output_file_id}/download"
                    if item.output_file_id
                    else None
                ),

                "preview_url": (
                    f"/api/v1/files/"
                    f"{item.output_file_id}/preview"
                    if item.output_file_id
                    else None
                ),
            }
            for item in history
        ],
    }


# ============================================================
# GET SINGLE PROCESSING HISTORY
# ============================================================

@router.get("/{processing_id}")
def get_processing_history_by_id(
    processing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    processing = (
        ProcessingHistoryService.get_by_id(
            db=db,
            processing_id=processing_id,
        )
    )

    # --------------------------------------------------------
    # Check processing record
    # --------------------------------------------------------

    if not processing:

        raise HTTPException(
            status_code=404,
            detail="Processing history not found",
        )

    # --------------------------------------------------------
    # Ownership check
    # --------------------------------------------------------

    if (
        not processing.input_file
        or processing.input_file.owner_id
        != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "You do not have access to "
                "this processing history"
            ),
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": (
            "Processing history fetched successfully"
        ),

        "id": processing.id,

        "input_file_id": (
            processing.input_file_id
        ),

        "output_file_id": (
            processing.output_file_id
        ),

        "operation": processing.operation,

        "options": processing.options,

        "status": processing.status,

        "created_at": processing.created_at,

        "input_file": file_details(
            processing.input_file
        ),

        "output_file": file_details(
            processing.output_file
        ),

        "download_url": (
            f"/api/v1/files/"
            f"{processing.output_file_id}/download"
            if processing.output_file_id
            else None
        ),

        "preview_url": (
            f"/api/v1/files/"
            f"{processing.output_file_id}/preview"
            if processing.output_file_id
            else None
        ),
    }


# ============================================================
# DELETE PROCESSING HISTORY
# ============================================================

@router.delete("/{processing_id}")
def delete_processing_history(
    processing_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(
        get_current_user
    ),
):

    # --------------------------------------------------------
    # Get processing history
    # --------------------------------------------------------

    processing = (
        ProcessingHistoryService.get_by_id(
            db=db,
            processing_id=processing_id,
        )
    )

    if not processing:

        raise HTTPException(
            status_code=404,
            detail="Processing history not found",
        )

    # --------------------------------------------------------
    # Ownership check
    # --------------------------------------------------------

    if (
        not processing.input_file
        or processing.input_file.owner_id
        != current_user.id
    ):

        raise HTTPException(
            status_code=403,
            detail=(
                "You do not have access to "
                "this processing history"
            ),
        )

    # --------------------------------------------------------
    # Get output file
    # --------------------------------------------------------

    output_file = processing.output_file

    output_path = None

    if output_file:

        output_path = Path(
            output_file.file_path
        )

    # --------------------------------------------------------
    # Delete history record
    # --------------------------------------------------------

    try:

        ProcessingHistoryService.delete(
            db=db,
            processing=processing,
        )

    except Exception:

        db.rollback()

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to delete "
                "processing history"
            ),
        )

    # --------------------------------------------------------
    # Delete generated output file
    # --------------------------------------------------------

    output_file_deleted = False

    if output_path and output_path.exists():

        try:

            output_path.unlink()

            output_file_deleted = True

        except OSError:

            # History is already deleted.
            # Physical file cleanup failure
            # should not fail the API response.

            output_file_deleted = False

    elif output_path:

        output_file_deleted = True

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": (
            "Processing history "
            "deleted successfully"
        ),
        "processing_id": processing_id,
        "output_file_deleted": (
            output_file_deleted
        ),
    }