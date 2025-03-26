import re
import json
from typing import List, Dict, Any
from app.models.detection import DetectionFinding
import logging

logger = logging.getLogger(__name__)

class DetectionService:
    def __init__(self):
        self.patterns = {
            'credit_card': r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            'phone': r'\b\+?1?[-.]?\(?\d{3}\)?[-.]?\d{3}[-.]?\d{4}\b',
            'ssn': r'\b\d{3}[-]?\d{2}[-]?\d{4}\b',
            'private_key': r'-----BEGIN\s+PRIVATE\s+KEY-----[^-]+-----END\s+PRIVATE\s+KEY-----',
            'api_key': r'\b(?:api[_-]?key|token)[_-]?(?:[\w\d]{32}|\w{32,})\b'
        }
        
        self.masking_rules = {
            'credit_card': 'XXXX-XXXX-XXXX-****',
            'email': '[EMAIL_REDACTED]',
            'phone': '[PHONE_REDACTED]',
            'ssn': 'XXX-XX-****',
            'private_key': '[PRIVATE_KEY_REDACTED]',
            'api_key': '[API_KEY_REDACTED]'
        }
        
        logger.info("Detection service initialized with regex patterns")

    def detect_sensitive_data(self, text: str) -> List[Dict[str, Any]]:
        """
        Detect sensitive data in text using regex patterns.
        """
        findings = []
        
        try:
            for pattern_type, pattern in self.patterns.items():
                matches = re.finditer(pattern, text)
                for match in matches:
                    finding = {
                        'finding_type': pattern_type,
                        'original_value': match.group(),
                        'masked_value': self.masking_rules[pattern_type],
                        'start_position': match.start(),
                        'end_position': match.end(),
                        'confidence_score': 100,  # Regex matches are always 100% confident
                        'detection_method': 'regex',
                        'finding_metadata': {
                            'pattern_used': pattern,
                            'detection_timestamp': None  # Will be set by the database
                        }
                    }
                    findings.append(finding)
            
            logger.info(f"Found {len(findings)} sensitive data instances")
            return findings
        except Exception as e:
            logger.error(f"Error detecting sensitive data: {e}")
            return []

    def mask_sensitive_data(self, text: str, findings: List[Dict[str, Any]]) -> str:
        """
        Mask sensitive data in text based on findings.
        """
        try:
            # Sort findings by start position in reverse order
            findings.sort(key=lambda x: x['start_position'], reverse=True)
            
            # Create a mutable version of the text
            masked_text = list(text)
            
            # Replace each finding with its mask
            for finding in findings:
                start = finding['start_position']
                end = finding['end_position']
                mask = finding['masked_value']
                masked_text[start:end] = mask
            
            logger.info("Successfully masked sensitive data")
            return ''.join(masked_text)
        except Exception as e:
            logger.error(f"Error masking sensitive data: {e}")
            return text  # Return original text if masking fails 