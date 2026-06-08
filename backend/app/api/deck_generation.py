"""
API endpoints for AI-powered deck generation
"""

import os
import logging
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.deck_generation import (
    DeckGenerationRequest,
    DeckGenerationResponse,
    DeckPreviewResponse,
    SlideInfo,
    EmbeddingStatsResponse,
    EmbeddingGenerationRequest,
    EmbeddingGenerationResponse
)
from app.services.deck_generator import get_deck_generator
from app.services.deck_assembler import get_deck_assembler
from app.services.embedding_service import get_embedding_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/preview", response_model=DeckPreviewResponse)
async def preview_deck(
    request: DeckGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Preview deck generation without creating the actual PowerPoint file.
    Shows which slides would be selected and in what order.
    """
    try:
        logger.info(f"Previewing deck for request: {request.request}")
        
        # Generate deck structure
        deck_generator = get_deck_generator()
        result = deck_generator.generate_deck(
            db=db,
            user_request=request.request,
            max_slides=request.max_slides
        )
        
        if not result['success']:
            return DeckPreviewResponse(
                success=False,
                message=result.get('error', 'Failed to generate deck preview')
            )
        
        # Convert slides to SlideInfo objects
        slides_info = []
        slide_scores = result.get('slide_scores', {})
        
        for slide in result['slides']:
            slides_info.append(SlideInfo(
                id=slide.id,
                title=slide.title,
                filename=slide.original_filename,
                slide_number=slide.slide_number,
                relevance_score=slide_scores.get(slide.id, 0.0),
                image_url=f"/api/slides/{slide.id}/image"
            ))
        
        # Generate suggested title
        parsed = result.get('parsed_request', {})
        products = parsed.get('products', [])
        audience = parsed.get('audience', '')
        
        if products and audience:
            suggested_title = f"{', '.join(products)} for {audience.title()}"
        elif products:
            suggested_title = f"{', '.join(products)} Overview"
        elif audience:
            suggested_title = f"Presentation for {audience.title()}"
        else:
            suggested_title = "Generated Presentation"
        
        return DeckPreviewResponse(
            success=True,
            slide_count=result['slide_count'],
            estimated_duration_minutes=result['estimated_duration_minutes'],
            parsed_request=result['parsed_request'],
            slides=slides_info,
            suggested_title=suggested_title
        )
        
    except Exception as e:
        logger.error(f"Error previewing deck: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate", response_model=DeckGenerationResponse)
async def generate_deck(
    request: DeckGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate a complete PowerPoint presentation from natural language request.
    Returns download URL for the generated deck.
    """
    try:
        logger.info(f"Generating deck for request: {request.request}")
        
        # Step 1: Generate deck structure (select and order slides)
        deck_generator = get_deck_generator()
        result = deck_generator.generate_deck(
            db=db,
            user_request=request.request,
            max_slides=request.max_slides
        )
        
        if not result['success']:
            return DeckGenerationResponse(
                success=False,
                message=result.get('error', 'Failed to generate deck')
            )
        
        # Step 2: Assemble PowerPoint presentation
        deck_assembler = get_deck_assembler()
        
        # Determine title
        if request.custom_title:
            title = request.custom_title
        else:
            parsed = result.get('parsed_request', {})
            products = parsed.get('products', [])
            audience = parsed.get('audience', '')
            
            if products and audience:
                title = f"{', '.join(products)} for {audience.title()}"
            elif products:
                title = f"{', '.join(products)} Overview"
            else:
                title = "Generated Presentation"
        
        # Create presentation
        output_path = deck_assembler.create_presentation(
            slides=result['slides'],
            title=title,
            add_agenda=request.add_agenda,
            add_notes=request.add_notes,
            client_name=request.client_name
        )
        
        # Get filename from path
        filename = os.path.basename(output_path)
        deck_id = filename.replace('.pptx', '')
        
        # Convert slides to SlideInfo objects
        slides_info = []
        slide_scores = result.get('slide_scores', {})
        
        for slide in result['slides']:
            slides_info.append(SlideInfo(
                id=slide.id,
                title=slide.title,
                filename=slide.original_filename,
                slide_number=slide.slide_number,
                relevance_score=slide_scores.get(slide.id, 0.0),
                image_url=f"/api/slides/{slide.id}/image"
            ))
        
        return DeckGenerationResponse(
            success=True,
            message="Deck generated successfully",
            deck_id=deck_id,
            download_url=f"/api/deck-generation/download/{deck_id}",
            slide_count=result['slide_count'],
            estimated_duration_minutes=result['estimated_duration_minutes'],
            parsed_request=result['parsed_request'],
            slides=slides_info
        )
        
    except Exception as e:
        logger.error(f"Error generating deck: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/download/{deck_id}")
async def download_deck(deck_id: str):
    """
    Download a generated PowerPoint presentation.
    """
    try:
        slides_dir = os.getenv("SLIDES_DIR", "./slides")
        filename = f"{deck_id}.pptx"
        file_path = os.path.join(slides_dir, filename)
        
        if not os.path.exists(file_path):
            raise HTTPException(status_code=404, detail="Deck not found")
        
        return FileResponse(
            path=file_path,
            media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation",
            filename=filename
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error downloading deck: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/embeddings/stats", response_model=EmbeddingStatsResponse)
async def get_embedding_stats():
    """
    Get statistics about the embedding collection.
    """
    try:
        embedding_service = get_embedding_service()
        stats = embedding_service.get_collection_stats()
        
        return EmbeddingStatsResponse(
            total_embeddings=stats.get('total_embeddings', 0),
            collection_name=stats.get('collection_name', ''),
            persist_directory=stats.get('persist_directory', '')
        )
        
    except Exception as e:
        logger.error(f"Error getting embedding stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/embeddings/generate", response_model=EmbeddingGenerationResponse)
async def generate_embeddings(
    request: EmbeddingGenerationRequest,
    db: Session = Depends(get_db)
):
    """
    Generate embeddings for slides.
    If slide_ids is provided, only those slides are processed.
    Otherwise, all slides are processed.
    """
    try:
        logger.info(f"Generating embeddings for slides: {request.slide_ids or 'all'}")
        
        embedding_service = get_embedding_service()
        stats = embedding_service.batch_add_slides(
            db=db,
            slide_ids=request.slide_ids
        )
        
        return EmbeddingGenerationResponse(
            success=True,
            message=f"Processed {stats['success']} slides successfully",
            stats=stats
        )
        
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/embeddings/reset")
async def reset_embeddings():
    """
    Reset the entire embedding collection.
    WARNING: This deletes all embeddings!
    """
    try:
        embedding_service = get_embedding_service()
        success = embedding_service.reset_collection()
        
        if success:
            return {"success": True, "message": "Embedding collection reset successfully"}
        else:
            raise HTTPException(status_code=500, detail="Failed to reset collection")
            
    except Exception as e:
        logger.error(f"Error resetting embeddings: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Made with Bob
