"""
Embedding Service for SlideX
Handles vector embeddings for semantic search using ChromaDB
"""

import os
import logging
from typing import List, Dict, Optional, Tuple
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from sqlalchemy.orm import Session
from app.models.slide import Slide
from app.models.tag import Tag

logger = logging.getLogger(__name__)


class EmbeddingService:
    """Service for managing slide embeddings and semantic search"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        Initialize the embedding service
        
        Args:
            persist_directory: Directory to persist ChromaDB data
        """
        self.persist_directory = persist_directory
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
            )
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name="slides",
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        
        # Initialize sentence transformer model
        # Using all-MiniLM-L6-v2: fast, good quality, 384 dimensions
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        
        logger.info(f"EmbeddingService initialized with {self.collection.count()} embeddings")
    
    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        try:
            embedding = self.model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise
    
    def create_slide_text(self, slide: Slide, tags: List[Tag]) -> str:
        """
        Create combined text representation of a slide for embedding
        
        Args:
            slide: Slide object
            tags: List of tags associated with the slide
            
        Returns:
            Combined text string
        """
        # Combine title, text content, and tags
        parts = []
        
        if slide.title:
            parts.append(f"Title: {slide.title}")
        
        if slide.text_content:
            parts.append(f"Content: {slide.text_content}")
        
        if tags:
            tag_names = [tag.name.replace('_', ' ') for tag in tags]
            parts.append(f"Tags: {', '.join(tag_names)}")
        
        return " | ".join(parts)
    
    def add_slide_embedding(
        self, 
        slide_id: int, 
        slide: Slide, 
        tags: List[Tag]
    ) -> bool:
        """
        Add or update embedding for a slide
        
        Args:
            slide_id: ID of the slide
            slide: Slide object
            tags: List of tags associated with the slide
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Create text representation
            text = self.create_slide_text(slide, tags)
            
            # Generate embedding
            embedding = self.generate_embedding(text)
            
            # Prepare metadata
            metadata = {
                "slide_id": slide_id,
                "title": slide.title or "",
                "filename": slide.original_filename or "",
                "slide_number": slide.slide_number or 0,
                "tag_count": len(tags)
            }
            
            # Add to ChromaDB
            self.collection.upsert(
                ids=[str(slide_id)],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata]
            )
            
            logger.info(f"Added embedding for slide {slide_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error adding slide embedding: {e}")
            return False
    
    def remove_slide_embedding(self, slide_id: int) -> bool:
        """
        Remove embedding for a slide
        
        Args:
            slide_id: ID of the slide to remove
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.collection.delete(ids=[str(slide_id)])
            logger.info(f"Removed embedding for slide {slide_id}")
            return True
        except Exception as e:
            logger.error(f"Error removing slide embedding: {e}")
            return False
    
    def search_similar_slides(
        self, 
        query: str, 
        top_k: int = 10,
        filter_metadata: Optional[Dict] = None
    ) -> List[Tuple[int, float]]:
        """
        Search for slides similar to the query
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filter_metadata: Optional metadata filters
            
        Returns:
            List of tuples (slide_id, similarity_score)
        """
        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)
            
            # Search in ChromaDB
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=filter_metadata
            )
            
            # Extract slide IDs and distances
            slide_results = []
            if results['ids'] and len(results['ids']) > 0:
                for i, slide_id_str in enumerate(results['ids'][0]):
                    slide_id = int(slide_id_str)
                    # ChromaDB returns distance, convert to similarity (1 - distance for cosine)
                    distance = results['distances'][0][i]
                    similarity = 1 - distance
                    slide_results.append((slide_id, similarity))
            
            logger.info(f"Found {len(slide_results)} similar slides for query: {query[:50]}...")
            return slide_results
            
        except Exception as e:
            logger.error(f"Error searching similar slides: {e}")
            return []
    
    def batch_add_slides(
        self, 
        db: Session, 
        slide_ids: Optional[List[int]] = None
    ) -> Dict[str, int]:
        """
        Batch add embeddings for multiple slides
        
        Args:
            db: Database session
            slide_ids: Optional list of specific slide IDs to process.
                      If None, processes all slides.
            
        Returns:
            Dictionary with counts of successful and failed operations
        """
        stats = {"success": 0, "failed": 0, "skipped": 0}
        
        try:
            # Get slides to process
            if slide_ids:
                slides = db.query(Slide).filter(Slide.id.in_(slide_ids)).all()
            else:
                slides = db.query(Slide).all()
            
            logger.info(f"Processing {len(slides)} slides for embeddings")
            
            for slide in slides:
                try:
                    # Get tags for this slide
                    tags = slide.tags
                    
                    # Add embedding
                    if self.add_slide_embedding(slide.id, slide, tags):
                        stats["success"] += 1
                    else:
                        stats["failed"] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing slide {slide.id}: {e}")
                    stats["failed"] += 1
            
            logger.info(f"Batch processing complete: {stats}")
            return stats
            
        except Exception as e:
            logger.error(f"Error in batch processing: {e}")
            return stats
    
    def get_collection_stats(self) -> Dict:
        """
        Get statistics about the embedding collection
        
        Returns:
            Dictionary with collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "total_embeddings": count,
                "collection_name": self.collection.name,
                "persist_directory": self.persist_directory
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {}
    
    def reset_collection(self) -> bool:
        """
        Reset the entire collection (delete all embeddings)
        WARNING: This is destructive!
        
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete_collection(name="slides")
            self.collection = self.client.get_or_create_collection(
                name="slides",
                metadata={"hnsw:space": "cosine"}
            )
            logger.warning("Collection reset - all embeddings deleted")
            return True
        except Exception as e:
            logger.error(f"Error resetting collection: {e}")
            return False


# Global instance
_embedding_service: Optional[EmbeddingService] = None


def get_embedding_service() -> EmbeddingService:
    """
    Get or create the global embedding service instance
    
    Returns:
        EmbeddingService instance
    """
    global _embedding_service
    if _embedding_service is None:
        persist_dir = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
        _embedding_service = EmbeddingService(persist_directory=persist_dir)
    return _embedding_service

# Made with Bob
