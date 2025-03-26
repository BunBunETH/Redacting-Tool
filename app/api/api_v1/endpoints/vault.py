from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.services.vault_service import VaultService
from app.models.vault import VaultEntry, VaultFeedback
from datetime import datetime

router = APIRouter()
vault_service = VaultService()

@router.get("/entries", response_model=List[VaultEntry])
async def list_vault_entries(
    conversation_id: Optional[str] = None,
    user_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """
    List vault entries with optional filtering.
    """
    return await vault_service.list_vault_entries(
        db,
        conversation_id=conversation_id,
        user_id=user_id,
        page=page,
        page_size=page_size
    )

@router.get("/entries/{vault_link}", response_model=VaultEntry)
async def get_vault_entry(
    vault_link: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific vault entry by its secure link.
    """
    entry = await vault_service.get_vault_entry(db, vault_link)
    if not entry:
        raise HTTPException(status_code=404, detail="Vault entry not found")
    return entry

@router.post("/entries/{vault_entry_id}/feedback", response_model=VaultFeedback)
async def add_vault_feedback(
    vault_entry_id: int,
    is_positive: bool,
    feedback_notes: str,
    reviewed_by: str,
    db: Session = Depends(get_db)
):
    """
    Add feedback for a vault entry.
    """
    return await vault_service.add_feedback(
        db,
        vault_entry_id=vault_entry_id,
        is_positive=is_positive,
        feedback_notes=feedback_notes,
        reviewed_by=reviewed_by
    )

@router.post("/entries/{vault_entry_id}/archive")
async def archive_vault_entry(
    vault_entry_id: int,
    db: Session = Depends(get_db)
):
    """
    Archive a vault entry.
    """
    success = await vault_service.archive_vault_entry(db, vault_entry_id)
    if not success:
        raise HTTPException(status_code=404, detail="Vault entry not found")
    return {"status": "success", "message": "Vault entry archived"}

@router.get("/stats")
async def get_vault_stats(db: Session = Depends(get_db)):
    """
    Get statistics about the vault.
    """
    total_entries = db.query(VaultEntry).filter(VaultEntry.is_archived == False).count()
    total_feedback = db.query(VaultFeedback).count()
    positive_feedback = db.query(VaultFeedback).filter(VaultFeedback.is_positive == True).count()
    
    return {
        "total_entries": total_entries,
        "total_feedback": total_feedback,
        "positive_feedback": positive_feedback,
        "feedback_ratio": positive_feedback / total_feedback if total_feedback > 0 else 0,
        "last_updated": datetime.utcnow().isoformat()
    } 