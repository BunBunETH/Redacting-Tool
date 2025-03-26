from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import random
from app.api.deps import get_current_user, get_db
from app.models.user import User
import logging

router = APIRouter()

# Common BIP39 words used in crypto wallets
BIP39_WORDS = [
    "abandon", "ability", "able", "about", "above", "absent", "absorb", "abstract", "absurd", "abuse",
    "access", "accident", "account", "accuse", "achieve", "acid", "acoustic", "acquire", "across", "act",
    "action", "actor", "actual", "adapt", "add", "addict", "address", "adjust", "admit", "adult",
    "advance", "advice", "aerobic", "affair", "afford", "afraid", "again", "age", "agent", "agree",
    "ahead", "aim", "air", "airport", "aisle", "alarm", "album", "alcohol", "alert", "alien",
    "all", "alley", "allow", "almost", "alone", "alpha", "already", "also", "alter", "always"
]

def generate_seed_phrase():
    """Generate a random 12-word seed phrase"""
    return " ".join(random.sample(BIP39_WORDS, 12))

def generate_mock_message():
    """Generate a realistic message with various types of sensitive data"""
    
    # Sample sensitive data templates
    templates = [
        {
            "original": "Hi, my SSN is {ssn} and my credit card number is {cc}. Please help me with my account.",
            "redacted": "Hi, my SSN is [REDACTED-SSN] and my credit card number is [REDACTED-CC]. Please help me with my account.",
            "type": "Financial"
        },
        {
            "original": "My phone number is {phone} and my email is {email}. I'm having trouble with my recent purchase.",
            "redacted": "My phone number is [REDACTED-PHONE] and my email is [REDACTED-EMAIL]. I'm having trouble with my recent purchase.",
            "type": "Contact Info"
        },
        {
            "original": "DOB: {dob}, Account: {account}, IP: {ip}. Can't access my dashboard.",
            "redacted": "DOB: [REDACTED-DOB], Account: [REDACTED-ACCOUNT], IP: [REDACTED-IP]. Can't access my dashboard.",
            "type": "Account Access"
        },
        {
            "original": "My passport number is {passport} and my driver's license is {dl}. Need to verify my identity.",
            "redacted": "My passport number is [REDACTED-PASSPORT] and my driver's license is [REDACTED-DL]. Need to verify my identity.",
            "type": "Identity"
        },
        {
            "original": "Medical record #: {mrn}, Insurance ID: {insurance}. Billing question about recent visit.",
            "redacted": "Medical record #: [REDACTED-MRN], Insurance ID: [REDACTED-INSURANCE]. Billing question about recent visit.",
            "type": "Healthcare"
        },
        {
            "original": "Here's my MetaMask recovery phrase: {seed_phrase}. I need help importing my wallet.",
            "redacted": "Here's my MetaMask recovery phrase: [REDACTED-SEED-PHRASE]. I need help importing my wallet.",
            "type": "Crypto Wallet"
        },
        {
            "original": "Lost access to my wallet. Seed phrase is {seed_phrase} and my private key is {private_key}.",
            "redacted": "Lost access to my wallet. Seed phrase is [REDACTED-SEED-PHRASE] and my private key is [REDACTED-PRIVATE-KEY].",
            "type": "Crypto Wallet"
        }
    ]
    
    # Generate realistic sensitive data
    sensitive_data = {
        "ssn": f"{random.randint(100,999)}-{random.randint(10,99)}-{random.randint(1000,9999)}",
        "cc": f"{random.randint(4000,4999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}-{random.randint(1000,9999)}",
        "phone": f"+1-{random.randint(200,999)}-{random.randint(100,999)}-{random.randint(1000,9999)}",
        "email": f"user{random.randint(100,999)}@example.com",
        "dob": f"{random.randint(1,12)}/{random.randint(1,28)}/{random.randint(1960,2000)}",
        "account": f"ACC-{random.randint(10000,99999)}",
        "ip": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}",
        "passport": f"P{random.randint(10000000,99999999)}",
        "dl": f"DL{random.randint(100000,999999)}",
        "mrn": f"MRN-{random.randint(100000,999999)}",
        "insurance": f"INS-{random.randint(10000,99999)}-{random.randint(10,99)}",
        "seed_phrase": generate_seed_phrase(),
        "private_key": f"0x{''.join(random.choices('0123456789abcdef', k=64))}"
    }
    
    # Select a random template
    template = random.choice(templates)
    
    # Fill in the template with sensitive data
    original = template["original"].format(**sensitive_data)
    redacted = template["redacted"]
    message_type = template["type"]
    
    return original, redacted, message_type

@router.get("/vault/mock")
async def get_mock_vault_entries(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mock recent activity for the dashboard
    """
    # Sample user IDs with roles
    users = [
        {"id": "USR-101", "role": "Support Agent"},
        {"id": "USR-102", "role": "Sales Rep"},
        {"id": "USR-103", "role": "Technical Support"},
        {"id": "USR-104", "role": "Account Manager"},
        {"id": "USR-105", "role": "Customer Success"}
    ]
    
    mock_entries = []
    
    for i in range(limit):
        # Generate a realistic timestamp within the last 48 hours
        hours_ago = random.randint(0, 48)
        minutes_ago = random.randint(0, 59)
        created_at = datetime.utcnow() - timedelta(hours=hours_ago, minutes=minutes_ago)
        
        # Generate random number of redactions (weighted towards lower numbers)
        redaction_count = random.choices(
            [1, 2, 3, 4, 5],
            weights=[0.4, 0.3, 0.15, 0.1, 0.05]
        )[0]
        
        # Generate confidence score (weighted towards higher scores)
        confidence_score = random.uniform(0.85, 1.0)
        if confidence_score > 0.98:  # Adjust perfect scores to be rare
            confidence_score = 1.0
            
        # Determine status (mostly active, some archived)
        is_archived = random.random() < 0.2  # 20% chance of being archived
        
        # Generate message content with sensitive data
        original_message, redacted_message, message_type = generate_mock_message()
        
        mock_entries.append({
            "id": random.randint(10000, 99999),
            "message_id": f"MSG-{random.randint(100000, 999999)}",
            "conversation_id": f"CONV-{random.randint(10000, 99999)}",
            "user_id": random.choice(users)["id"],
            "message_type": message_type,
            "is_archived": is_archived,
            "created_at": created_at.isoformat(),
            "redaction_count": redaction_count,
            "confidence_score": round(confidence_score, 2),
            "processing_time": round(random.uniform(0.8, 2.5), 1),
            "original_message": original_message,
            "redacted_message": redacted_message
        })
    
    # Sort by created_at in descending order (most recent first)
    mock_entries.sort(key=lambda x: x["created_at"], reverse=True)
    return mock_entries

@router.get("/vault/stats")
async def get_mock_vault_stats(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get mock statistics for the dashboard
    """
    return {
        "total_entries": 1247,
        "total_redactions": 892,
        "positive_feedback": 845,
        "feedback_ratio": 0.947,  # 94.7% accuracy
        "avg_processing_time": "1.2s"
    }

@router.post("/vault/feedback/{entry_id}")
async def add_mock_feedback(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mock endpoint for adding feedback
    """
    return {"status": "success"}

@router.post("/vault/archive/{entry_id}")
async def archive_mock_entry(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mock endpoint for archiving entries
    """
    return {"status": "success"}

@router.post("/vault/revert/{entry_id}")
async def revert_mock_redaction(
    entry_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Mock endpoint for reverting a redaction.
    In a real implementation, this would:
    1. Update the message in Intercom to show the original text
    2. Mark this redaction as a false positive in our system
    3. Use this feedback to improve the redaction model
    """
    logger.info(f"Reverting redaction for entry {entry_id}")
    return {
        "status": "success",
        "message": "Redaction reverted successfully. Original message restored in Intercom."
    } 