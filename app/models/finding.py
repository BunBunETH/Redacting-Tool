from sqlalchemy import Column, String, Integer, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.models.base import BaseModel

class DetectionFinding(BaseModel):
    __tablename__ = "detection_findings"

    message_id = Column(Integer, ForeignKey("messages.id"))
    finding_type = Column(String)  # email, credit_card, private_key, etc.
    original_value = Column(String)
    masked_value = Column(String)
    start_position = Column(Integer)
    end_position = Column(Integer)
    confidence_score = Column(Integer)  # Store as integer (0-100)
    detection_method = Column(String)  # 'regex' or 'ml'
    metadata = Column(JSON)  # Additional context about the finding
    
    # Relationship
    message = relationship("Message", back_populates="findings") 