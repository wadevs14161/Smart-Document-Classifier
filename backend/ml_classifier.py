
"""
Document Classifier Module using BART-Large-MNLI
For Smart Document Classifier FastAPI Application
Enhanced with chunking and averaging for large documents
"""

from transformers import pipeline, AutoTokenizer
from typing import Dict, Any, List, Optional
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentClassifier:
    """Document classifier supporting multiple models with chunking support"""

    CATEGORIES = [
        "Technical Documentation",
        "Business Proposal", 
        "Legal Document",
        "Academic Paper",
        "General Article",
        # Removed "Other" as requested in notebook
    ]

    AVAILABLE_MODELS = {
        "bart-large-mnli": {
            "name": "BART Large MNLI",
            "model_id": "facebook/bart-large-mnli",
            "description": "Facebook's BART model fine-tuned for MNLI"
        },
        "mdeberta-v3-base": {
            "name": "mDeBERTa v3 Base",
            "model_id": "MoritzLaurer/mDeBERTa-v3-base-mnli-xnli",
            "description": "Multilingual DeBERTa model for cross-lingual classification"
        }
    }

    def __init__(self, model_key: str = "bart-large-mnli"):
        """Initialize the classifier with specified model"""
        if model_key not in self.AVAILABLE_MODELS:
            raise ValueError(f"Model '{model_key}' not supported. Available models: {list(self.AVAILABLE_MODELS.keys())}")
        
        self.classifier = None
        self.tokenizer = None
        self.model_key = model_key
        self.model_name = self.AVAILABLE_MODELS[model_key]["model_id"]
        self.model_display_name = self.AVAILABLE_MODELS[model_key]["name"]
        self.is_loaded = False
        self.max_chunk_tokens = 800  # Conservative limit for both models

    def load_model(self):
        """Load the specified model and tokenizer"""
        try:
            logger.info(f"Loading {self.model_display_name} ({self.model_name}) model...")
            self.classifier = pipeline(
                "zero-shot-classification", 
                model=self.model_name,
                device=-1  # Use CPU, change to 0 for GPU
            )
            # Load tokenizer for proper chunking
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            self.is_loaded = True
            logger.info(f"{self.model_display_name} model and tokenizer loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load {self.model_display_name} model: {str(e)}")
            raise e

    def classify(self, text: str, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Classify a document using chunking and averaging for large texts

        Args:
            text: Document text to classify
            categories: Optional custom categories (defaults to self.CATEGORIES)

        Returns:
            Classification results with confidence scores averaged across chunks
        """
        if not self.is_loaded:
            self.load_model()

        if not text or not text.strip():
            return {
                "error": "Empty text provided",
                "predicted_category": "Other",
                "confidence_score": 0.0
            }

        categories = categories or self.CATEGORIES

        try:
            # Tokenize the entire text once
            tokens = self.tokenizer.encode(text, add_special_tokens=False)
            full_token_count = len(tokens)
            
            # Initialize lists to store results from each chunk
            all_scores = {category: [] for category in categories}
            total_inference_time = 0
            
            logger.info(f"Processing document with {full_token_count} tokens using {self.max_chunk_tokens} token chunks")
            
            # Chunk the tokens and process each chunk
            chunk_count = 0
            for i in range(0, full_token_count, self.max_chunk_tokens):
                chunk_count += 1
                # Get the tokens for the current chunk
                chunk_tokens = tokens[i:i + self.max_chunk_tokens]
                
                # Decode the chunk of tokens back into text
                chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
                
                # Perform classification for the current chunk
                start_time = time.time()
                result = self.classifier(chunk_text, categories, multi_label=False)
                chunk_inference_time = time.time() - start_time
                total_inference_time += chunk_inference_time
                
                # Aggregate scores from this chunk
                for label, score in zip(result["labels"], result["scores"]):
                    all_scores[label].append(score)
                
                logger.debug(f"Processed chunk {chunk_count}, size: {len(chunk_tokens)} tokens")

            # Average the scores across all chunks
            averaged_scores = {
                category: sum(scores) / len(scores) if scores else 0
                for category, scores in all_scores.items()
            }
            
            # Find the category with the highest average score
            predicted_category = max(averaged_scores, key=averaged_scores.get)
            confidence_score = averaged_scores[predicted_category]

            # Format results
            classification_result = {
                "predicted_category": predicted_category,
                "confidence_score": round(confidence_score, 4),
                "all_scores": {label: round(score, 4) for label, score in averaged_scores.items()},
                "inference_time": round(total_inference_time, 3),
                "model_used": self.model_display_name,
                "model_key": self.model_key,
                "model_id": self.model_name,
                "token_count": full_token_count,
                "chunks_processed": chunk_count,
                "was_chunked": chunk_count > 1
            }

            logger.info(f"Classification completed: {predicted_category} ({confidence_score:.4f}) using {chunk_count} chunks")
            return classification_result

        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return {
                "error": str(e),
                "predicted_category": "Other",
                "confidence_score": 0.0
            }

# Global classifier instances (one per model)
_classifier_instances = {}

def get_classifier(model_key: str = "bart-large-mnli") -> DocumentClassifier:
    """Get or create the classifier instance for the specified model"""
    global _classifier_instances
    if model_key not in _classifier_instances:
        _classifier_instances[model_key] = DocumentClassifier(model_key)
    return _classifier_instances[model_key]

def classify_document_text(text: str, model_key: str = "bart-large-mnli") -> Dict[str, Any]:
    """
    Convenience function to classify document text with specified model

    Args:
        text: Document text to classify
        model_key: Model to use for classification

    Returns:
        Classification results
    """
    classifier = get_classifier(model_key)
    return classifier.classify(text)

def get_available_models() -> Dict[str, Dict[str, str]]:
    """
    Get list of available models
    
    Returns:
        Dictionary of available models with their metadata
    """
    return DocumentClassifier.AVAILABLE_MODELS.copy()

def cleanup_ml_resources():
    """
    Clean up ML resources on application shutdown
    """
    global _classifier_instances
    if _classifier_instances:
        try:
            # Clear all classifier instances
            _classifier_instances.clear()
            logger.info("✅ ML resources cleaned up successfully")
        except Exception as e:
            logger.error(f"❌ Error cleaning up ML resources: {str(e)}")
    else:
        logger.info("ℹ️  No ML resources to clean up")
