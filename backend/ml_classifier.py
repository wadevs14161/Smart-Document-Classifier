"""
Document Classifier Module using BART-Large-MNLI
For Smart Document Classifier FastAPI Application
"""

from transformers import pipeline, AutoTokenizer
from typing import Dict, Any, List, Optional
import logging
import time
import atexit
import gc
import torch

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DocumentClassifier:
    """Document classifier using Facebook's BART-Large-MNLI model with proper resource management"""
    
    CATEGORIES = [
        "Technical Documentation",
        "Business Proposal", 
        "Legal Document",
        "Academic Paper",
        "General Article",
        "Other"
    ]
    
    def __init__(self):
        """Initialize the classifier"""
        self.classifier = None
        self.tokenizer = None
        self.model_name = "facebook/bart-large-mnli"
        self.is_loaded = False
        # Register cleanup function
        atexit.register(self.cleanup)
        
    def load_model(self):
        """Load the BART-Large-MNLI model"""
        try:
            logger.info(f"Loading {self.model_name} model...")
            
            # Load both classifier and tokenizer
            self.classifier = pipeline(
                "zero-shot-classification", 
                model=self.model_name,
                device=-1,  # Use CPU to avoid GPU resource issues
                torch_dtype=torch.float32,  # Explicit dtype
                return_all_scores=True
            )
            
            # Load tokenizer for proper text truncation
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
            
            self.is_loaded = True
            logger.info("Model and tokenizer loaded successfully!")
        except Exception as e:
            logger.error(f"Failed to load model: {str(e)}")
            raise e
    
    def cleanup(self):
        """Clean up resources properly"""
        try:
            if self.classifier is not None:
                logger.info("Cleaning up ML model resources...")
                # Clear the classifier and tokenizer
                del self.classifier
                del self.tokenizer
                self.classifier = None
                self.tokenizer = None
                self.is_loaded = False
                
                # Force garbage collection
                gc.collect()
                
                # Clear PyTorch cache if available
                if torch.cuda.is_available():
                    torch.cuda.empty_cache()
                    
                logger.info("ML resources cleaned up successfully")
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")
        except Exception as e:
            logger.warning(f"Error during cleanup: {str(e)}")
    
    def __del__(self):
        """Destructor to ensure cleanup"""
        self.cleanup()
    
    def classify(self, text: str, categories: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Classify a document
        
        Args:
            text: Document text to classify
            categories: Optional custom categories (defaults to self.CATEGORIES)
            
        Returns:
            Classification results with confidence scores
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
            # IMPROVED: Use tokenizer-based truncation instead of character truncation
            max_tokens = 800  # Conservative limit for BART
            original_length = len(text)
            
            # Count actual tokens using the model's tokenizer
            tokens = self.tokenizer.encode(text, add_special_tokens=False)
            
            if len(tokens) > max_tokens:
                # Proper token-based truncation
                truncated_tokens = tokens[:max_tokens]
                text = self.tokenizer.decode(truncated_tokens, skip_special_tokens=True)
                logger.info(f"Text truncated from {len(tokens)} to {max_tokens} tokens (chars: {original_length} → {len(text)})")
            
            # Perform classification
            start_time = time.time()
            result = self.classifier(text, categories)
            inference_time = time.time() - start_time
            
            # Format results with enhanced information
            classification_result = {
                "predicted_category": result["labels"][0],
                "confidence_score": round(result["scores"][0], 4),
                "all_scores": {
                    label: round(score, 4) 
                    for label, score in zip(result["labels"], result["scores"])
                },
                "inference_time": round(inference_time, 3),
                "model_used": self.model_name,
                "text_length_chars": len(text),
                "text_length_tokens": len(tokens),
                "was_truncated": len(tokens) > max_tokens,
                "original_token_count": len(tokens) if len(tokens) <= max_tokens else len(self.tokenizer.encode(text, add_special_tokens=False))
            }
            
            logger.info(f"Classification completed: {result['labels'][0]} ({result['scores'][0]:.4f})")
            return classification_result
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return {
                "error": str(e),
                "predicted_category": "Other",
                "confidence_score": 0.0
            }

# Global classifier instance (singleton pattern)
_classifier_instance = None

def get_classifier() -> DocumentClassifier:
    """Get or create the global classifier instance"""
    global _classifier_instance
    if _classifier_instance is None:
        _classifier_instance = DocumentClassifier()
    return _classifier_instance

def classify_document_text(text: str) -> Dict[str, Any]:
    """
    Convenience function to classify document text
    
    Args:
        text: Document text to classify
        
    Returns:
        Classification results
    """
    classifier = get_classifier()
    return classifier.classify(text)

def cleanup_ml_resources():
    """
    Clean up ML resources - call this during application shutdown
    """
    global _classifier_instance
    if _classifier_instance is not None:
        _classifier_instance.cleanup()
        _classifier_instance = None
        logger.info("Global ML classifier instance cleaned up")
