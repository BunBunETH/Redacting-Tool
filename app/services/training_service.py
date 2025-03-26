from typing import List, Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from app.models.training import TrainingData
from app.models.message import Message
from app.core.config import settings
from sqlalchemy.orm import Session
import numpy as np
from datetime import datetime

class TrainingService:
    def __init__(self):
        self.model_name = "bert-base-uncased"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            self.model_name,
            num_labels=2  # binary classification: sensitive or not
        )
        self.current_version = "1.0.0"

    async def prepare_training_data(self, db: Session) -> List[Dict]:
        """
        Prepare training data from approved examples in the database.
        """
        training_data = db.query(TrainingData).filter(
            TrainingData.training_status == "approved",
            TrainingData.manual_review == True
        ).all()

        return [
            {
                "text": data.message.original_text,
                "label": 1 if data.is_sensitive else 0
            }
            for data in training_data
        ]

    async def train_model(self, training_data: List[Dict]) -> None:
        """
        Train the model on the provided training data.
        """
        if not training_data:
            return

        # Prepare training arguments
        training_args = TrainingArguments(
            output_dir="./results",
            num_train_epochs=3,
            per_device_train_batch_size=8,
            per_device_eval_batch_size=8,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir="./logs",
        )

        # Create trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=training_data,
        )

        # Train the model
        trainer.train()

        # Save the model
        self.model.save_pretrained(f"./models/version_{self.current_version}")
        self.tokenizer.save_pretrained(f"./models/version_{self.current_version}")

    async def evaluate_model(self, db: Session) -> Dict:
        """
        Evaluate the model's performance on a test set.
        """
        # Get test data (messages not used in training)
        test_data = db.query(Message).filter(
            ~Message.id.in_(
                db.query(TrainingData.message_id)
            )
        ).all()

        predictions = []
        actual_labels = []

        for message in test_data:
            # Get prediction
            inputs = self.tokenizer(
                message.original_text,
                return_tensors="pt",
                truncation=True,
                max_length=512
            )
            outputs = self.model(**inputs)
            prediction = torch.argmax(outputs.logits).item()
            
            predictions.append(prediction)
            actual_labels.append(1 if message.is_blocked else 0)

        # Calculate metrics
        accuracy = np.mean(np.array(predictions) == np.array(actual_labels))
        
        return {
            "accuracy": accuracy,
            "total_samples": len(test_data),
            "timestamp": datetime.utcnow().isoformat(),
            "model_version": self.current_version
        }

    async def update_model_version(self, new_version: str) -> None:
        """
        Update the model version and save the current model.
        """
        self.current_version = new_version
        self.model.save_pretrained(f"./models/version_{self.current_version}")
        self.tokenizer.save_pretrained(f"./models/version_{self.current_version}")

    async def load_model_version(self, version: str) -> None:
        """
        Load a specific version of the model.
        """
        self.current_version = version
        self.model = AutoModelForSequenceClassification.from_pretrained(
            f"./models/version_{version}"
        )
        self.tokenizer = AutoTokenizer.from_pretrained(
            f"./models/version_{version}"
        ) 