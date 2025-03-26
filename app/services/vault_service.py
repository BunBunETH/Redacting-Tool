from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from app.models.vault import VaultEntry, VaultFeedback
from app.models.message import Message
import uuid
from datetime import datetime
import json

class VaultService:
    def __init__(self):
        self.vault_base_url = "https://vault.example.com"  # Replace with actual vault URL

    async def create_vault_entry(self, db: Session, message: Message) -> VaultEntry:
        """
        Create a new vault entry for a redacted message.
        """
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
        return vault_entry

    async def get_vault_entry(self, db: Session, vault_link: str) -> Optional[VaultEntry]:
        """
        Retrieve a vault entry by its secure link.
        """
        return db.query(VaultEntry).filter(
            VaultEntry.vault_link == vault_link,
            VaultEntry.is_archived == False
        ).first()

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
        query = db.query(VaultEntry).filter(VaultEntry.is_archived == False)
        
        if conversation_id:
            query = query.filter(VaultEntry.conversation_id == conversation_id)
        if user_id:
            query = query.filter(VaultEntry.user_id == user_id)
            
        return query.offset((page - 1) * page_size).limit(page_size).all()

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
        return feedback

    async def archive_vault_entry(self, db: Session, vault_entry_id: int) -> bool:
        """
        Archive a vault entry.
        """
        entry = db.query(VaultEntry).filter(VaultEntry.id == vault_entry_id).first()
        if entry:
            entry.is_archived = True
            db.commit()
            return True
        return False

    def generate_intercom_note(self, vault_link: str) -> str:
        """
        Generate the Intercom note text with the vault link.
        """
        return f"""⚠️ Sensitive data was redacted from this message.
View the original message in the secure vault: {vault_link}

This message has been automatically redacted to protect sensitive information.
Only authorized administrators can view the original content.""" 