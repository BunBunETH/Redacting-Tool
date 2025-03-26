from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class VaultEntryBase(BaseModel):
    conversation_id: str
    message_id: str
    content: str
    sensitive_data_type: str
    confidence_score: float
    masked_content: Optional[str] = None
    metadata: Optional[dict] = None

class VaultEntryCreate(VaultEntryBase):
    pass

class VaultEntryResponse(VaultEntryBase):
    id: int
    user_id: int
    created_at: datetime
    is_archived: bool = False

    class Config:
        from_attributes = True

class VaultFeedbackBase(BaseModel):
    comment: Optional[str] = None
    is_positive: bool = True

class VaultFeedbackCreate(VaultFeedbackBase):
    pass

class VaultFeedbackResponse(VaultFeedbackBase):
    id: int
    entry_id: int
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True 