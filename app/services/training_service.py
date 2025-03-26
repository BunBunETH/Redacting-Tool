from typing import List, Dict, Optional
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer
from app.models.training import TrainingData
from app.models.message import Message
from app.core.config import settings
from sqlalchemy.orm import Session
import numpy as np
from datetime import datetime
import logging
import os

logger = logging.getLogger(__name__)

class TrainingService:
    def __init__(self):
        try:
            self.model_name = "bert-base-uncased"
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(
                self.model_name,
                num_labels=2  # binary classification: sensitive or not
            )
            self.current_version = settings.MODEL_VERSION
            logger.info(f"TrainingService initialized with model version: {self.current_version}")
        except Exception as e:
            logger.error(f"Error initializing TrainingService: {e}")
            raise

    async def prepare_training_data(self, db: Session) -> List[Dict]:
        """
        Prepare training data from approved examples in the database.
        """
        try:
            training_data = db.query(TrainingData).filter(
                TrainingData.training_status == "approved",
                TrainingData.manual_review == True
            ).all()

            data = [
                {
                    "text": data.message.original_text,
                    "label": 1 if data.is_sensitive else 0
                }
                for data in training_data
            ]
            
            logger.info(f"Prepared {len(data)} training examples")
            return data
        except Exception as e:
            logger.error(f"Error preparing training data: {e}")
            return []

    async def train_model(self, training_data: List[Dict]) -> None:
        """
        Train the model on the provided training data.
        """
        try:
            if not training_data:
                logger.warning("No training data provided")
                return

            # Create output directories if they don't exist
            os.makedirs("./results", exist_ok=True)
            os.makedirs("./logs", exist_ok=True)
            os.makedirs("./models", exist_ok=True)

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
            logger.info("Starting model training")
            trainer.train()
            logger.info("Model training completed")

            # Save the model
            model_path = f"./models/version_{self.current_version}"
            self.model.save_pretrained(model_path)
            self.tokenizer.save_pretrained(model_path)
            logger.info(f"Model saved to {model_path}")
        except Exception as e:
            logger.error(f"Error training model: {e}")
            raise

    async def evaluate_model(self, db: Session) -> Dict:
        """
        Evaluate the model's performance on a test set.
        """
        try:
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
            
            result = {
                "accuracy": accuracy,
                "total_samples": len(test_data),
                "timestamp": datetime.utcnow().isoformat(),
                "model_version": self.current_version
            }
            
            logger.info(f"Model evaluation completed: {result}")
            return result
        except Exception as e:
            logger.error(f"Error evaluating model: {e}")
            return {
                "accuracy": 0.0,
                "total_samples": 0,
                "timestamp": datetime.utcnow().isoformat(),
                "model_version": self.current_version,
                "error": str(e)
            }

    async def update_model_version(self, new_version: str) -> None:
        """
        Update the model version and save the current model.
        """
        try:
            self.current_version = new_version
            model_path = f"./models/version_{self.current_version}"
            self.model.save_pretrained(model_path)
            self.tokenizer.save_pretrained(model_path)
            logger.info(f"Model version updated to {new_version}")
        except Exception as e:
            logger.error(f"Error updating model version: {e}")
            raise

    async def load_model_version(self, version: str) -> None:
        """
        Load a specific version of the model.
        """
        try:
            model_path = f"./models/version_{version}"
            if not os.path.exists(model_path):
                raise ValueError(f"Model version {version} not found")
                
            self.current_version = version
            self.model = AutoModelForSequenceClassification.from_pretrained(model_path)
            self.tokenizer = AutoTokenizer.from_pretrained(model_path)
            logger.info(f"Model version {version} loaded successfully")
        except Exception as e:
            logger.error(f"Error loading model version: {e}")
            raise 