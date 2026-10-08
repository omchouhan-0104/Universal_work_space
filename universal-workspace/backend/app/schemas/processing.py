# from typing import Literal

# from pydantic import BaseModel, Field


# class ImageProcessRequest(BaseModel):

#     operation: Literal[
#         "convert",
#         "compress",
#         "resize",
#     ]

#     format: str | None = None

#     quality: int = Field(
#         default=70,
#         ge=1,
#         le=100,
#     )

#     width: int | None = Field(
#         default=None,
#         gt=0,
#     )

#     height: int | None = Field(
#         default=None,
#         gt=0,
#     )

from typing import Any

from pydantic import BaseModel, Field


class ProcessRequest(BaseModel):

    operation: str = Field(
        ...,
        description="Processing operation",
    )

    options: dict[str, Any] = Field(
        default_factory=dict,
    )