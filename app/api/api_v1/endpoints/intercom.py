from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Dict, List
from app.services.intercom_service import IntercomService
from app.services.detection_service import DetectionService
from app.core.config import settings
import hmac
import hashlib
import json

router = APIRouter()
intercom_service = IntercomService()
detection_service = DetectionService()

async def verify_intercom_signature(request: Request) -> bool:
    """
    Verify the Intercom webhook signature.
    """
    signature = request.headers.get("X-Hub-Signature")
    if not signature:
        return False
    
    body = await request.body()
    expected_signature = hmac.new(
        settings.INTERCOM_ACCESS_TOKEN.encode(),
        body,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(signature, expected_signature)

@router.post("/webhook")
async def handle_intercom_webhook(request: Request):
    """
    Handle incoming Intercom webhook events.
    """
    if not await verify_intercom_signature(request):
        raise HTTPException(status_code=401, detail="Invalid signature")
    
    payload = await request.json()
    topic = request.headers.get("X-Intercom-Topic")
    
    if topic == "conversation.created" or topic == "conversation.replied":
        message_data = payload.get("data", {}).get("item", {})
        processed_data = await intercom_service.process_message(message_data)
        
        if processed_data["should_block"]:
            # Block the message and notify admin
            await intercom_service.notify_admin(message_data, processed_data["findings"])
            return {"status": "blocked", "message": "Message blocked due to sensitive content"}
        
        # If message is not blocked, update it with masked content
        await intercom_service.send_message(
            processed_data["conversation_id"],
            processed_data["processed_text"]
        )
        
        return {"status": "processed", "findings": processed_data["findings"]}
    
    return {"status": "ignored", "topic": topic}

@router.get("/stats")
async def get_detection_stats():
    """
    Get statistics about sensitive data detection.
    """
    # TODO: Implement statistics gathering from database
    return {
        "total_messages_processed": 0,
        "total_sensitive_data_found": 0,
        "blocked_messages": 0,
        "detection_types": {}
    }

@router.post("/train")
async def train_model(training_data: List[Dict]):
    """
    Train the ML model with new data.
    """
    # TODO: Implement model training logic
    return {"status": "training_started", "samples": len(training_data)}

@router.get("/patterns")
async def get_detection_patterns():
    """
    Get current detection patterns.
    """
    return {
        "regex_patterns": detection_service.patterns,
        "web3_patterns": detection_service.web3_patterns
    }

@router.post("/patterns")
async def update_detection_patterns(patterns: Dict):
    """
    Update detection patterns.
    """
    # TODO: Implement pattern update logic
    return {"status": "patterns_updated"} 