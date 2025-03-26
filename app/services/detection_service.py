import re
from typing import List, Dict, Tuple
import spacy
from transformers import pipeline
from app.core.config import settings

class DetectionService:
    def __init__(self):
        # Load SpaCy model
        self.nlp = spacy.load("en_core_web_sm")
        
        # Initialize BERT model for sensitive data detection
        self.classifier = pipeline(
            "text-classification",
            model="bert-base-uncased",
            device=-1  # Use CPU
        )
        
        # Regex patterns for structured data
        self.patterns = {
            "email": r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}',
            "credit_card": r'\b\d{4}[- ]?\d{4}[- ]?\d{4}[- ]?\d{4}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "private_key": r'-----BEGIN (?:RSA|DSA|EC|OPENSSH) PRIVATE KEY-----',
            "api_key": r'(?i)(api[_-]?key|apikey|secret)[=:]\s*[\w\-]{20,}'
        }
        
        # Custom patterns for Web3/SRP specific data
        self.web3_patterns = {
            "eth_address": r'0x[a-fA-F0-9]{40}',
            "private_key_hex": r'[a-fA-F0-9]{64}',
            "mnemonic": r'[a-z\s]{10,}'
        }

    def detect_sensitive_data(self, text: str) -> List[Dict]:
        """
        Detect sensitive data in text using both regex and ML approaches.
        Returns a list of detected sensitive data with their types and positions.
        """
        findings = []
        
        # Check structured data using regex
        for data_type, pattern in self.patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                findings.append({
                    "type": data_type,
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 1.0,
                    "method": "regex"
                })
        
        # Check Web3 specific data
        for data_type, pattern in self.web3_patterns.items():
            matches = re.finditer(pattern, text)
            for match in matches:
                findings.append({
                    "type": f"web3_{data_type}",
                    "value": match.group(),
                    "start": match.start(),
                    "end": match.end(),
                    "confidence": 1.0,
                    "method": "regex"
                })
        
        # Use ML model for unstructured data
        doc = self.nlp(text)
        for sent in doc.sents:
            # Use BERT for classification
            result = self.classifier(sent.text)
            if result[0]["label"] == "LABEL_1" and result[0]["score"] > settings.MODEL_CONFIDENCE_THRESHOLD:
                findings.append({
                    "type": "sensitive_content",
                    "value": sent.text,
                    "start": sent.start_char,
                    "end": sent.end_char,
                    "confidence": result[0]["score"],
                    "method": "ml"
                })
        
        return findings

    def mask_sensitive_data(self, text: str, findings: List[Dict]) -> str:
        """
        Mask detected sensitive data in the text.
        """
        masked_text = text
        # Sort findings by start position in reverse order to avoid index issues
        sorted_findings = sorted(findings, key=lambda x: x["start"], reverse=True)
        
        for finding in sorted_findings:
            mask = self._get_mask_for_type(finding["type"])
            masked_text = (
                masked_text[:finding["start"]] +
                mask +
                masked_text[finding["end"]:]
            )
        
        return masked_text

    def _get_mask_for_type(self, data_type: str) -> str:
        """
        Get appropriate mask for different types of sensitive data.
        """
        masks = {
            "email": "[email_redacted]",
            "credit_card": "XXXX-XXXX-XXXX-XXXX",
            "phone": "(XXX) XXX-XXXX",
            "ssn": "XXX-XX-XXXX",
            "private_key": "**********",
            "api_key": "[API_KEY_REDACTED]",
            "web3_eth_address": "0x********",
            "web3_private_key_hex": "[PRIVATE_KEY_REDACTED]",
            "web3_mnemonic": "[MNEMONIC_REDACTED]",
            "sensitive_content": "[SENSITIVE_CONTENT_REDACTED]"
        }
        return masks.get(data_type, "[REDACTED]") 