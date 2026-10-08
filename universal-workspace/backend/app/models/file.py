from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class File(Base):
    __tablename__ = "files"

    # ========================================
    # PRIMARY KEY
    # ========================================

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True,
    )

    # ========================================
    # FILE INFORMATION
    # ========================================

    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    file_path: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    file_type: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    mime_type: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    file_size: Mapped[int] = mapped_column(
        nullable=False,
    )

    # ========================================
    # USER
    # ========================================

    owner_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
    )

    # ========================================
    # SHARING
    # ========================================

    share_token: Mapped[str | None] = mapped_column(
        String(255),
        unique=True,
        nullable=True,
    )

    is_shared: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )

    # ========================================
    # TIMESTAMP
    # ========================================

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    # ========================================
    # USER RELATIONSHIP
    # ========================================

    owner = relationship(
        "User",
        back_populates="files",
    )

    # ========================================
    # PROCESSING INPUT RELATIONSHIP
    # ========================================

    processing_inputs = relationship(
        "FileProcessing",
        foreign_keys="FileProcessing.input_file_id",
        back_populates="input_file",
        cascade="all, delete-orphan",
    )

    # ========================================
    # PROCESSING OUTPUT RELATIONSHIP
    # ========================================

    processing_outputs = relationship(
        "FileProcessing",
        foreign_keys="FileProcessing.output_file_id",
        back_populates="output_file",
    )


# from datetime import datetime

# from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
# from sqlalchemy.orm import Mapped, mapped_column, relationship

# from app.database.base import Base


# class File(Base):
#     __tablename__ = "files"

#     id: Mapped[int] = mapped_column(
#         primary_key=True,
#         index=True,
#     )

#     original_filename: Mapped[str] = mapped_column(
#         String(255),
#         nullable=False,
#     )

#     stored_filename: Mapped[str] = mapped_column(
#         String(255),
#         unique=True,
#         nullable=False,
#     )

#     file_path: Mapped[str] = mapped_column(
#         String(500),
#         nullable=False,
#     )

#     file_type: Mapped[str] = mapped_column(
#         String(100),
#         nullable=False,
#     )

#     mime_type: Mapped[str | None] = mapped_column(
#         String(255),
#         nullable=True,
#     )

#     file_size: Mapped[int] = mapped_column(
#         nullable=False,
#     )

#     owner_id: Mapped[int] = mapped_column(
#         ForeignKey("users.id"),
#         nullable=False,
#     )

#     share_token: Mapped[str | None] = mapped_column(
#         String(255),
#         unique=True,
#         nullable=True,
#     )

#     is_shared: Mapped[bool] = mapped_column(
#         Boolean,
#         default=False,
#         nullable=False,
#     )

#     created_at: Mapped[datetime] = mapped_column(
#         DateTime(timezone=True),
#         server_default=func.now(),
#         nullable=False,
#     )

#     # ========================================
#     # USER RELATIONSHIP
#     # ========================================

#     owner = relationship(
#         "User",
#         back_populates="files",
#     )

#     # ========================================
#     # PROCESSING RELATIONSHIPS
#     # ========================================

#     processing_inputs = relationship(
#         "FileProcessing",
#         foreign_keys="FileProcessing.input_file_id",
#         back_populates="input_file",
#         cascade="all, delete-orphan",
#     )

#     processing_outputs = relationship(
#         "FileProcessing",
#         foreign_keys="FileProcessing.output_file_id",
#         back_populates="output_file",
#     )