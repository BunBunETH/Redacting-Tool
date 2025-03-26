from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.vault import VaultEntry, VaultFeedback
from app.models.message import Message
from app.core.config import settings
import uuid
from datetime import datetime
import json
import logging

logger = logging.getLogger(__name__)

class VaultService:
    def __init__(self):
        try:
            self.vault_base_url = settings.VAULT_BASE_URL
            logger.info("VaultService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing VaultService: {e}")
            raise

    async def create_vault_entry(self, db: Session, message: Message) -> VaultEntry:
        """
        Create a new vault entry for a redacted message.
        """
        try:
            # Generate a secure unique link
            secure_id = str(uuid.uuid4())
            vault_link = f"{self.vault_base_url}/view/{secure_id}"

            vault_entry = VaultEntry(
                message_id=message.id,
                conversation_id=message.conversation_id,
                user_id=message.intercom_message_id.split("_")[0],  # Extract user ID from message ID
                original_message=message.original_text,
                vault_link=vault_link,
                metadata={
                    "redaction_timestamp": datetime.utcnow().isoformat(),
                    "detection_method": message.detection_method,
                    "confidence_score": message.confidence_score
                }
            )

            db.add(vault_entry)
            db.commit()
            db.refresh(vault_entry)
            logger.info(f"Vault entry created successfully: {vault_entry.id}")
            return vault_entry
        except Exception as e:
            logger.error(f"Error creating vault entry: {e}")
            db.rollback()
            raise

    async def get_vault_entry(self, db: Session, vault_link: str) -> Optional[VaultEntry]:
        """
        Retrieve a vault entry by its secure link.
        """
        try:
            entry = db.query(VaultEntry).filter(
                VaultEntry.vault_link == vault_link,
                VaultEntry.is_archived == False
            ).first()
            
            if entry:
                logger.info(f"Vault entry retrieved successfully: {entry.id}")
            else:
                logger.warning(f"Vault entry not found: {vault_link}")
                
            return entry
        except Exception as e:
            logger.error(f"Error retrieving vault entry: {e}")
            return None

    async def list_vault_entries(
        self,
        db: Session,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[VaultEntry]:
        """
        List vault entries with optional filtering.
        """
        try:
            query = db.query(VaultEntry).filter(VaultEntry.is_archived == False)
            
            if conversation_id:
                query = query.filter(VaultEntry.conversation_id == conversation_id)
            if user_id:
                query = query.filter(VaultEntry.user_id == user_id)
                
            entries = query.offset((page - 1) * page_size).limit(page_size).all()
            logger.info(f"Retrieved {len(entries)} vault entries")
            return entries
        except Exception as e:
            logger.error(f"Error listing vault entries: {e}")
            return []

    async def add_feedback(
        self,
        db: Session,
        vault_entry_id: int,
        is_positive: bool,
        feedback_notes: str,
        reviewed_by: str
    ) -> VaultFeedback:
        """
        Add feedback for a vault entry.
        """
        try:
            feedback = VaultFeedback(
                vault_entry_id=vault_entry_id,
                is_positive=is_positive,
                feedback_notes=feedback_notes,
                reviewed_by=reviewed_by,
                reviewed_at=datetime.utcnow().isoformat()
            )

            db.add(feedback)
            db.commit()
            db.refresh(feedback)
            logger.info(f"Feedback added successfully for vault entry: {vault_entry_id}")
            return feedback
        except Exception as e:
            logger.error(f"Error adding feedback: {e}")
            db.rollback()
            raise

    async def archive_vault_entry(self, db: Session, vault_entry_id: int) -> bool:
        """
        Archive a vault entry.
        """
        try:
            entry = db.query(VaultEntry).filter(VaultEntry.id == vault_entry_id).first()
            if entry:
                entry.is_archived = True
                db.commit()
                logger.info(f"Vault entry archived successfully: {vault_entry_id}")
                return True
            logger.warning(f"Vault entry not found for archiving: {vault_entry_id}")
            return False
        except Exception as e:
            logger.error(f"Error archiving vault entry: {e}")
            db.rollback()
            return False

    def generate_intercom_note(self, vault_link: str) -> str:
        """
        Generate the Intercom note text with the vault link.
        """
        try:
            return f"""⚠️ Sensitive data was redacted from this message.
View the original message in the secure vault: {vault_link}

This message has been automatically redacted to protect sensitive information.
Only authorized administrators can view the original content."""
        except Exception as e:
            logger.error(f"Error generating Intercom note: {e}")
            return "⚠️ Sensitive data was redacted from this message." 