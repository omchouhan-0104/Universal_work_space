from datetime import datetime

from pydantic import BaseModel


class FileResponse(BaseModel):
    id: int
    original_filename: str
    file_type: str
    mime_type: str | None
    file_size: int
    owner_id: int
    is_shared: bool
    created_at: datetime
    
class FileRenameRequest(BaseModel):
    filename: str
    


class ShareResponse(BaseModel):
    file_id: int
    share_token: str
    share_url: str