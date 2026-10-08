from datetime import datetime
from typing import Any

from sqlalchemy import DateTime, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class FileProcessing(Base):
    __tablename__ = "file_processing"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    input_file_id: Mapped[int] = mapped_column(
        ForeignKey(
            "files.id",
            ondelete="CASCADE",
        ),
        nullable=False,
    )

    output_file_id: Mapped[int | None] = mapped_column(
        ForeignKey(
            "files.id",
            ondelete="SET NULL",
        ),
        nullable=True,
    )

    operation: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    options: Mapped[dict[str, Any]] = mapped_column(
        JSONB,
        nullable=False,
        default=dict,
    )

    status: Mapped[str] = mapped_column(
        String(30),
        nullable=False,
        default="pending",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ========================================
    # INPUT FILE
    # ========================================

    input_file = relationship(
        "File",
        foreign_keys=[input_file_id],
        back_populates="processing_inputs",
    )

    # ========================================
    # OUTPUT FILE
    # ========================================

    output_file = relationship(
        "File",
        foreign_keys=[output_file_id],
        back_populates="processing_outputs",
    )