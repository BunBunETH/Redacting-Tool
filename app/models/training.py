from sqlalchemy import Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class TrainingData(BaseModel):
    __tablename__ = "training_data"

    message_id = Column(Integer, ForeignKey("messages.id"), unique=True)
    label = Column(String)  # The classification label
    is_validated = Column(Boolean, default=False)
    validation_notes = Column(String, nullable=True)
    
    # Relationships
    message = relationship("Message", back_populates="training_data") 