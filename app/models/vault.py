from sqlalchemy import Column, String, Integer, ForeignKey, JSON, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class VaultEntry(BaseModel):
    __tablename__ = "vault_entries"

    message_id = Column(Integer, ForeignKey("messages.id"), unique=True)
    conversation_id = Column(String, index=True)
    user_id = Column(String, index=True)
    original_message = Column(String)
    vault_link = Column(String, unique=True)  # Generated secure link
    is_archived = Column(Boolean, default=False)
    metadata = Column(JSON)  # Additional context about the redaction
    
    # Relationships
    message = relationship("Message", backref="vault_entry")
    feedback = relationship("VaultFeedback", back_populates="vault_entry", uselist=False)

class VaultFeedback(BaseModel):
    __tablename__ = "vault_feedback"

    vault_entry_id = Column(Integer, ForeignKey("vault_entries.id"), unique=True)
    is_positive = Column(Boolean)  # True for like, False for dislike
    feedback_notes = Column(String)
    reviewed_by = Column(String)  # Admin username
    reviewed_at = Column(String)  # ISO timestamp
    
    # Relationship
    vault_entry = relationship("VaultEntry", back_populates="feedback") 