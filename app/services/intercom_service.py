import httpx
from typing import Dict, Optional
from app.core.config import settings
from app.services.detection_service import DetectionService

class IntercomService:
    def __init__(self):
        self.detection_service = DetectionService()
        self.headers = {
            "Authorization": f"Bearer {settings.INTERCOM_ACCESS_TOKEN}",
            "Content-Type": "application/json"
        }
        self.base_url = "https://api.intercom.io"

    async def process_message(self, message_data: Dict) -> Dict:
        """
        Process an incoming Intercom message, detect sensitive data, and return processed version.
        """
        message_text = message_data.get("body", "")
        
        # Detect sensitive data
        findings = self.detection_service.detect_sensitive_data(message_text)
        
        # Mask sensitive data
        masked_text = self.detection_service.mask_sensitive_data(message_text, findings)
        
        # Check if message should be blocked
        should_block = self._should_block_message(findings)
        
        return {
            "original_text": message_text,
            "processed_text": masked_text,
            "findings": findings,
            "should_block": should_block,
            "message_id": message_data.get("id"),
            "conversation_id": message_data.get("conversation_id")
        }

    def _should_block_message(self, findings: list) -> bool:
        """
        Determine if a message should be blocked based on findings.
        """
        if not settings.BLOCK_EXTERNAL_MESSAGES:
            return False
            
        # Block if any high-confidence sensitive data is found
        for finding in findings:
            if finding["confidence"] > settings.MODEL_CONFIDENCE_THRESHOLD:
                return True
        return False

    async def send_message(self, conversation_id: str, message: str) -> Dict:
        """
        Send a message to an Intercom conversation.
        """
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/conversations/{conversation_id}/reply",
                headers=self.headers,
                json={
                    "message_type": "comment",
                    "body": message
                }
            )
            response.raise_for_status()
            return response.json()

    async def get_conversation(self, conversation_id: str) -> Dict:
        """
        Retrieve a conversation from Intercom.
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/conversations/{conversation_id}",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()

    async def notify_admin(self, message_data: Dict, findings: list) -> None:
        """
        Send notification to admin about blocked message.
        """
        if not settings.NOTIFY_ADMIN_ON_BLOCK:
            return
            
        # TODO: Implement admin notification (e.g., via Slack or email)
        # This is a placeholder for the notification logic
        print(f"Admin notification: Blocked message {message_data.get('id')} with findings: {findings}") 