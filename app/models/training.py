from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class TrainingData(BaseModel):
    __tablename__ = "training_data"

    message_id = Column(Integer, ForeignKey("messages.id"), unique=True)
    is_sensitive = Column(Boolean, default=False)
    manual_review = Column(Boolean, default=False)
    reviewer_notes = Column(String)
    training_status = Column(String)  # 'pending', 'approved', 'rejected'
    model_version = Column(String)  # Version of the model this was used to train
    training_metadata = Column(JSON)  # Additional training context
    
    # Relationship
    message = relationship("Message", back_populates="training_data") 