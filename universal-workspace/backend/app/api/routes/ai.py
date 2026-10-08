from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.dependencie import get_current_user
from app.database.session import get_db
from app.models.file import File
from app.models.user import User
from app.services.ai.text_extraction import TextExtractionService
from app.services.ai.summarization import SummarizationService


router = APIRouter(
    prefix="/ai",
    tags=["AI"],
)


# ============================================================
# EXTRACT TEXT FROM FILE
# ============================================================

@router.post("/extract-text/{file_id}")
def extract_text_from_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Get file
    # --------------------------------------------------------

    file_record = db.get(
        File,
        file_id,
    )

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
    # Check MIME type
    # --------------------------------------------------------

    if not file_record.mime_type:
        raise HTTPException(
            status_code=400,
            detail="File MIME type is missing",
        )

    # --------------------------------------------------------
    # Check physical file
    # --------------------------------------------------------

    input_path = Path(
        file_record.file_path
    )

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    # --------------------------------------------------------
    # Extract text
    # --------------------------------------------------------

    try:

        text = TextExtractionService.extract_text(
            input_path,
            file_record.mime_type,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Text extraction failed: {str(exc)}",
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": "Text extracted successfully",
        "file_id": file_record.id,
        "filename": file_record.original_filename,
        "mime_type": file_record.mime_type,
        "text": text,
        "character_count": len(text),
    }


# ============================================================
# SUMMARIZE FILE
# ============================================================

@router.post("/summarize/{file_id}")
def summarize_file(
    file_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # --------------------------------------------------------
    # Get file
    # --------------------------------------------------------

    file_record = db.get(
        File,
        file_id,
    )

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
    # Check MIME type
    # --------------------------------------------------------

    if not file_record.mime_type:
        raise HTTPException(
            status_code=400,
            detail="File MIME type is missing",
        )

    # --------------------------------------------------------
    # Check physical file
    # --------------------------------------------------------

    input_path = Path(
        file_record.file_path
    )

    if not input_path.exists():
        raise HTTPException(
            status_code=404,
            detail="Physical file not found",
        )

    # --------------------------------------------------------
    # Extract text
    # --------------------------------------------------------

    try:

        text = TextExtractionService.extract_text(
            input_path,
            file_record.mime_type,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Text extraction failed: {str(exc)}",
        )

    # --------------------------------------------------------
    # Check extracted text
    # --------------------------------------------------------

    if not text.strip():

        raise HTTPException(
            status_code=400,
            detail="No text could be extracted from this file",
        )

    # --------------------------------------------------------
    # Summarize
    # --------------------------------------------------------

    try:

        summary = SummarizationService.summarize(
            text=text,
            max_length=500,
        )

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        )

    except Exception as exc:

        raise HTTPException(
            status_code=500,
            detail=f"Summarization failed: {str(exc)}",
        )

    # --------------------------------------------------------
    # Response
    # --------------------------------------------------------

    return {
        "message": "File summarized successfully",
        "file_id": file_record.id,
        "filename": file_record.original_filename,
        "summary": summary,
        "original_text_length": len(text),
        "summary_length": len(summary),
    }
