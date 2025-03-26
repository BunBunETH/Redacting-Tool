from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.models.vault import VaultEntry, VaultFeedback
from app.services.vault_service import VaultService
from app.schemas.vault import VaultEntryCreate, VaultEntryResponse, VaultFeedbackCreate
import logging

logger = logging.getLogger(__name__)
router = APIRouter()
vault_service = VaultService()

@router.post("/entries", response_model=VaultEntryResponse)
async def create_vault_entry(
    entry: VaultEntryCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new vault entry.
    """
    try:
        if not current_user.has_permission("vault:create"):
            logger.warning(f"User {current_user.username} attempted to create vault entry without permission")
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        
        vault_entry = await vault_service.create_vault_entry(
            db=db,
            user_id=current_user.id,
            **entry.dict()
        )
        logger.info(f"Created vault entry {vault_entry.id}")
        return vault_entry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating vault entry: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/entries/{entry_id}", response_model=VaultEntryResponse)
async def get_vault_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get a specific vault entry.
    """
    try:
        if not current_user.has_permission("vault:read"):
            logger.warning(f"User {current_user.username} attempted to read vault entry without permission")
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        
        entry = await vault_service.get_vault_entry(db, entry_id)
        if not entry:
            logger.warning(f"Vault entry {entry_id} not found")
            raise HTTPException(
                status_code=404,
                detail="Vault entry not found"
            )
        
        logger.info(f"Retrieved vault entry {entry_id}")
        return entry
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving vault entry: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.get("/entries", response_model=List[VaultEntryResponse])
async def list_vault_entries(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    List all vault entries.
    """
    try:
        if not current_user.has_permission("vault:read"):
            logger.warning(f"User {current_user.username} attempted to list vault entries without permission")
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        
        entries = await vault_service.list_vault_entries(
            db=db,
            skip=skip,
            limit=limit
        )
        logger.info(f"Retrieved {len(entries)} vault entries")
        return entries
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error listing vault entries: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/entries/{entry_id}/feedback")
async def add_feedback(
    entry_id: int,
    feedback: VaultFeedbackCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Add feedback to a vault entry.
    """
    try:
        if not current_user.has_permission("vault:feedback"):
            logger.warning(f"User {current_user.username} attempted to add feedback without permission")
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        
        await vault_service.add_feedback(
            db=db,
            entry_id=entry_id,
            user_id=current_user.id,
            **feedback.dict()
        )
        logger.info(f"Added feedback to vault entry {entry_id}")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding feedback: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@router.post("/entries/{entry_id}/archive")
async def archive_vault_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Archive a vault entry.
    """
    try:
        if not current_user.has_permission("vault:archive"):
            logger.warning(f"User {current_user.username} attempted to archive vault entry without permission")
            raise HTTPException(
                status_code=403,
                detail="Not enough permissions"
            )
        
        await vault_service.archive_vault_entry(db, entry_id)
        logger.info(f"Archived vault entry {entry_id}")
        return {"status": "success"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error archiving vault entry: {e}")
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )