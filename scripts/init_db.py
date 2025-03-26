import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.database import engine, Base
from app.models.user import User, UserRole
from app.models.message import Message
from app.models.vault import VaultEntry, VaultFeedback
from app.models.detection import DetectionFinding
from app.models.training import TrainingData
from app.services.auth_service import AuthService
from datetime import datetime
import logging
import asyncio
from app.core.database import SessionLocal

logger = logging.getLogger(__name__)

async def init_db():
    """Initialize the database by creating all tables and adding initial data."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully!")

        # Create a session
        db = SessionLocal()

        # Create auth service
        auth_service = AuthService()

        # Create admin user if it doesn't exist
        admin_user = db.query(User).filter(User.username == "admin").first()
        if not admin_user:
            await auth_service.create_user(
                db=db,
                username='admin',
                email='admin@example.com',
                password='admin',
                full_name='Admin User',
                role='ADMIN'
            )
            logger.info("Admin user created successfully!")

        # Create some mock messages
        mock_messages = [
            Message(
                conversation_id="conv_1",
                intercom_message_id="msg_1",
                original_text="Here is my credit card: 4111-1111-1111-1111",
                processed_text="Here is my credit card: XXXX-XXXX-XXXX-XXXX",
                is_blocked=True,
                detection_method="regex",
                confidence_score=1.0
            ),
            Message(
                conversation_id="conv_2",
                intercom_message_id="msg_2",
                original_text="My email is john.doe@example.com",
                processed_text="My email is [email_redacted]",
                is_blocked=False,
                detection_method="regex",
                confidence_score=1.0
            )
        ]

        for message in mock_messages:
            existing = db.query(Message).filter(Message.intercom_message_id == message.intercom_message_id).first()
            if not existing:
                db.add(message)
        
        db.commit()
        logger.info("Mock messages created successfully!")

        # Create some mock vault entries
        mock_vault_entries = [
            VaultEntry(
                message_id=1,
                conversation_id="conv_1",
                user_id="user_1",
                original_message="Here is my credit card: 4111-1111-1111-1111",
                vault_link="https://vault.example.com/view/abc123",
                metadata={
                    "redaction_timestamp": datetime.utcnow().isoformat(),
                    "detection_method": "regex",
                    "confidence_score": 1.0
                }
            ),
            VaultEntry(
                message_id=2,
                conversation_id="conv_2",
                user_id="user_2",
                original_message="My email is john.doe@example.com",
                vault_link="https://vault.example.com/view/def456",
                metadata={
                    "redaction_timestamp": datetime.utcnow().isoformat(),
                    "detection_method": "regex",
                    "confidence_score": 1.0
                }
            )
        ]

        for entry in mock_vault_entries:
            existing = db.query(VaultEntry).filter(VaultEntry.vault_link == entry.vault_link).first()
            if not existing:
                db.add(entry)
        
        db.commit()
        logger.info("Mock vault entries created successfully!")

        # Create some mock feedback
        mock_feedback = [
            VaultFeedback(
                vault_entry_id=1,
                is_positive=True,
                feedback_notes="Correctly identified credit card",
                reviewed_by="admin",
                reviewed_at=datetime.utcnow().isoformat()
            ),
            VaultFeedback(
                vault_entry_id=2,
                is_positive=True,
                feedback_notes="Correctly identified email",
                reviewed_by="admin",
                reviewed_at=datetime.utcnow().isoformat()
            )
        ]

        for feedback in mock_feedback:
            existing = db.query(VaultFeedback).filter(
                VaultFeedback.vault_entry_id == feedback.vault_entry_id
            ).first()
            if not existing:
                db.add(feedback)
        
        db.commit()
        logger.info("Mock feedback created successfully!")

        db.close()
        logger.info("Database initialization completed successfully!")

    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(init_db()) 