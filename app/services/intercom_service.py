import httpx
from typing import Dict, Optional
from app.core.config import settings
from app.services.detection_service import DetectionService
import logging

logger = logging.getLogger(__name__)

class IntercomService:
    def __init__(self):
        try:
            self.detection_service = DetectionService()
            self.headers = {
                "Authorization": f"Bearer {settings.INTERCOM_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            self.base_url = "https://api.intercom.io"
            logger.info("IntercomService initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing IntercomService: {e}")
            raise

    async def process_message(self, message_data: Dict) -> Dict:
        """
        Process an incoming Intercom message, detect sensitive data, and return processed version.
        """
        try:
            message_text = message_data.get("body", "")
            logger.info(f"Processing message: {message_data.get('id')}")
            
            # Detect sensitive data
            findings = self.detection_service.detect_sensitive_data(message_text)
            logger.info(f"Found {len(findings)} sensitive data instances")
            
            # Mask sensitive data
            masked_text = self.detection_service.mask_sensitive_data(message_text, findings)
            
            # Check if message should be blocked
            should_block = self._should_block_message(findings)
            
            result = {
                "original_text": message_text,
                "processed_text": masked_text,
                "findings": findings,
                "should_block": should_block,
                "message_id": message_data.get("id"),
                "conversation_id": message_data.get("conversation_id")
            }
            
            logger.info(f"Message processed successfully: {message_data.get('id')}")
            return result
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "original_text": message_text,
                "processed_text": message_text,
                "findings": [],
                "should_block": False,
                "message_id": message_data.get("id"),
                "conversation_id": message_data.get("conversation_id")
            }

    def _should_block_message(self, findings: list) -> bool:
        """
        Determine if a message should be blocked based on findings.
        """
        try:
            if not settings.BLOCK_EXTERNAL_MESSAGES:
                return False
                
            # Block if any high-confidence sensitive data is found
            for finding in findings:
                if finding["confidence"] > settings.MODEL_CONFIDENCE_THRESHOLD:
                    logger.info(f"Message blocked due to high-confidence finding: {finding['type']}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Error determining if message should be blocked: {e}")
            return False

    async def send_message(self, conversation_id: str, message: str) -> Dict:
        """
        Send a message to an Intercom conversation.
        """
        try:
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
                logger.info(f"Message sent successfully to conversation: {conversation_id}")
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error sending message: {e}")
            raise
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise

    async def get_conversation(self, conversation_id: str) -> Dict:
        """
        Retrieve a conversation from Intercom.
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/conversations/{conversation_id}",
                    headers=self.headers
                )
                response.raise_for_status()
                logger.info(f"Conversation retrieved successfully: {conversation_id}")
                return response.json()
        except httpx.HTTPError as e:
            logger.error(f"HTTP error retrieving conversation: {e}")
            raise
        except Exception as e:
            logger.error(f"Error retrieving conversation: {e}")
            raise

    async def notify_admin(self, message_data: Dict, findings: list) -> None:
        """
        Send notification to admin about blocked message.
        """
        try:
            if not settings.NOTIFY_ADMIN_ON_BLOCK:
                return
                
            # TODO: Implement admin notification (e.g., via Slack or email)
            # This is a placeholder for the notification logic
            logger.info(f"Admin notification: Blocked message {message_data.get('id')} with findings: {findings}")
        except Exception as e:
            logger.error(f"Error sending admin notification: {e}") 