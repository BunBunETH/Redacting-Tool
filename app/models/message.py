from sqlalchemy import Column, String, JSON, Boolean, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class Message(BaseModel):
    __tablename__ = "messages"

    intercom_message_id = Column(String, unique=True, index=True)
    conversation_id = Column(String, index=True)
    original_text = Column(String)
    processed_text = Column(String)
    is_blocked = Column(Boolean, default=False)
    confidence_score = Column(Integer)  # Store as integer (0-100)
    detection_method = Column(String)  # 'regex' or 'ml'
    
    # Relationships
    findings = relationship("DetectionFinding", back_populates="message", cascade="all, delete-orphan")
    training_data = relationship("TrainingData", back_populates="message", uselist=False) 