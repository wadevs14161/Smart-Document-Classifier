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
        Classify a document using chunking strategy for long texts
        
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
            start_time = time.time()
            original_length = len(text)
            tokens = self.tokenizer.encode(text, add_special_tokens=False)
            
            # Strategy: Use chunking for long documents, direct classification for short ones
            max_tokens_per_chunk = 900  # Conservative chunk size
            
            if len(tokens) <= max_tokens_per_chunk:
                # Direct classification for short documents
                logger.info(f"Direct classification: {len(tokens)} tokens, {original_length} characters")
                result = self.classifier(text, categories)
                
                classification_result = {
                    "predicted_category": result["labels"][0],
                    "confidence_score": round(result["scores"][0], 4),
                    "all_scores": {
                        label: round(score, 4) 
                        for label, score in zip(result["labels"], result["scores"])
                    },
                    "inference_time": round(time.time() - start_time, 3),
                    "model_used": self.model_name,
                    "text_length_chars": len(text),
                    "text_length_tokens": len(tokens),
                    "was_truncated": False,
                    "chunks_used": 1,
                    "aggregation_method": "direct"
                }
                
            else:
                # Chunking strategy for long documents
                logger.info(f"Using chunking strategy: {len(tokens)} tokens, {original_length} characters")
                classification_result = self._classify_with_chunking(text, tokens, categories, max_tokens_per_chunk, start_time)
            
            logger.info(f"Classification completed: {classification_result['predicted_category']} ({classification_result['confidence_score']:.4f})")
            return classification_result
            
        except Exception as e:
            logger.error(f"Classification failed: {str(e)}")
            return {
                "error": str(e),
                "predicted_category": "Other",
                "confidence_score": 0.0
            }
    
    def _classify_with_chunking(self, text: str, tokens: List[int], categories: List[str], 
                               max_tokens_per_chunk: int, start_time: float) -> Dict[str, Any]:
        """
        Classify long documents using chunking strategy
        
        Args:
            text: Original text
            tokens: Tokenized text
            categories: Classification categories
            max_tokens_per_chunk: Maximum tokens per chunk
            start_time: Start time for performance measurement
            
        Returns:
            Aggregated classification results
        """
        # Create overlapping chunks (20% overlap for better context preservation)
        overlap_tokens = int(max_tokens_per_chunk * 0.2)
        chunks = []
        chunk_results = []
        
        # Generate chunks with overlap
        i = 0
        while i < len(tokens):
            end_idx = min(i + max_tokens_per_chunk, len(tokens))
            chunk_tokens = tokens[i:end_idx]
            chunk_text = self.tokenizer.decode(chunk_tokens, skip_special_tokens=True)
            chunks.append({
                'text': chunk_text,
                'tokens': chunk_tokens,
                'start_idx': i,
                'end_idx': end_idx
            })
            
            # Move forward with overlap
            if end_idx >= len(tokens):
                break
            i += max_tokens_per_chunk - overlap_tokens
        
        logger.info(f"Created {len(chunks)} overlapping chunks (overlap: {overlap_tokens} tokens)")
        
        # Classify each chunk
        all_scores = {category: [] for category in categories}
        chunk_predictions = []
        
        for idx, chunk in enumerate(chunks):
            try:
                chunk_result = self.classifier(chunk['text'], categories)
                chunk_predictions.append(chunk_result["labels"][0])
                
                # Collect scores for each category
                for label, score in zip(chunk_result["labels"], chunk_result["scores"]):
                    all_scores[label].append(score)
                    
                logger.debug(f"Chunk {idx+1}/{len(chunks)}: {chunk_result['labels'][0]} ({chunk_result['scores'][0]:.4f})")
                
            except Exception as e:
                logger.warning(f"Failed to classify chunk {idx+1}: {str(e)}")
                # Add default scores for failed chunks
                for category in categories:
                    all_scores[category].append(0.0)
        
        # Aggregate results using multiple strategies
        aggregated_scores = {}
        
        # Strategy 1: Average probabilities across all chunks
        for category in categories:
            if all_scores[category]:
                aggregated_scores[category] = sum(all_scores[category]) / len(all_scores[category])
            else:
                aggregated_scores[category] = 0.0
        
        # Sort by aggregated scores
        sorted_categories = sorted(aggregated_scores.items(), key=lambda x: x[1], reverse=True)
        predicted_category = sorted_categories[0][0]
        confidence_score = sorted_categories[0][1]
        
        # Strategy 2: Majority voting for comparison
        majority_vote = max(set(chunk_predictions), key=chunk_predictions.count) if chunk_predictions else "Other"
        
        # Strategy 3: Weighted average (give more weight to chunks with higher confidence)
        weighted_scores = {category: 0.0 for category in categories}
        total_weight = 0.0
        
        for category in categories:
            if all_scores[category]:
                # Weight by confidence (higher confidence chunks have more influence)
                for score in all_scores[category]:
                    weight = score  # Use the score itself as weight
                    weighted_scores[category] += score * weight
                    if category == categories[0]:  # Only count weight once
                        total_weight += weight
        
        if total_weight > 0:
            for category in categories:
                weighted_scores[category] /= total_weight
        
        # Choose the best aggregated result (use weighted average if significantly different)
        sorted_weighted = sorted(weighted_scores.items(), key=lambda x: x[1], reverse=True)
        weighted_prediction = sorted_weighted[0][0]
        weighted_confidence = sorted_weighted[0][1]
        
        # Use weighted result if it's more confident
        if weighted_confidence > confidence_score * 1.1:  # 10% threshold
            predicted_category = weighted_prediction
            confidence_score = weighted_confidence
            aggregation_method = "weighted_average"
        else:
            aggregation_method = "mean_probabilities"
        
        return {
            "predicted_category": predicted_category,
            "confidence_score": round(confidence_score, 4),
            "all_scores": {k: round(v, 4) for k, v in dict(sorted_categories).items()},
            "inference_time": round(time.time() - start_time, 3),
            "model_used": self.model_name,
            "text_length_chars": len(text),
            "text_length_tokens": len(tokens),
            "was_truncated": False,  # No truncation with chunking!
            "chunks_used": len(chunks),
            "chunk_size_tokens": max_tokens_per_chunk,
            "overlap_tokens": overlap_tokens,
            "aggregation_method": aggregation_method,
            "majority_vote": majority_vote,
            "chunk_predictions": chunk_predictions[:5],  # First 5 for debugging
            "weighted_scores": {k: round(v, 4) for k, v in sorted_weighted}
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
