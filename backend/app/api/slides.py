"""
Slides API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
import os

from app.core.database import get_db
from app.models.slide import Slide
from app.services.slide_processor import SlideProcessor
from app.services.ai_tagger import AITagger

router = APIRouter()


@router.post("/upload")
async def upload_presentation(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Upload a PowerPoint file and process it
    - Extracts individual slides
    - Converts to images
    - Extracts text content
    - Generates AI tags
    """
    # Validate file type
    if not file.filename.endswith(('.pptx', '.ppt')):
        raise HTTPException(status_code=400, detail="Only PowerPoint files (.pptx, .ppt) are allowed")
    
    try:
        # Initialize processors
        slide_processor = SlideProcessor()
        ai_tagger = AITagger()
        
        # Save uploaded file temporarily
        temp_path = f"./uploads/{file.filename}"
        with open(temp_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        # Process the presentation
        slides_data = await slide_processor.process_presentation(temp_path, file.filename)
        
        # Store slides in database and generate tags
        created_slides = []
        for slide_data in slides_data:
            # Create slide record
            slide = Slide(
                original_filename=file.filename,
                slide_number=slide_data["slide_number"],
                image_path=slide_data["image_path"],
                thumbnail_path=slide_data["thumbnail_path"],
                text_content=slide_data["text_content"],
                title=slide_data.get("title")
            )
            db.add(slide)
            db.flush()  # Get the slide ID
            
            # Generate and assign tags
            tags = await ai_tagger.generate_tags(slide_data["text_content"], slide_data.get("title", ""), db)
            slide.tags = tags
            
            created_slides.append({
                "id": slide.id,
                "slide_number": slide.slide_number,
                "thumbnail_path": slide.thumbnail_path
            })
        
        db.commit()
        
        # Clean up temp file
        os.remove(temp_path)
        
        return {
            "message": f"Successfully processed {len(created_slides)} slides",
            "slides": created_slides
        }
        
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error processing presentation: {str(e)}")


@router.get("/")
async def get_all_slides(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Get all slides with pagination"""
    slides = db.query(Slide).offset(skip).limit(limit).all()
    return {
        "slides": [
            {
                "id": slide.id,
                "original_filename": slide.original_filename,
                "slide_number": slide.slide_number,
                "thumbnail_path": slide.thumbnail_path,
                "title": slide.title,
                "tags": [{"name": tag.name, "category": tag.category} for tag in slide.tags]
            }
            for slide in slides
        ]
    }


@router.get("/{slide_id}")
async def get_slide(slide_id: int, db: Session = Depends(get_db)):
    """Get a specific slide by ID"""
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    return {
        "id": slide.id,
        "original_filename": slide.original_filename,
        "slide_number": slide.slide_number,
        "image_path": slide.image_path,
        "thumbnail_path": slide.thumbnail_path,
        "text_content": slide.text_content,
        "title": slide.title,
        "tags": [{"id": tag.id, "name": tag.name, "category": tag.category} for tag in slide.tags],
        "created_at": slide.created_at
    }


@router.delete("/{slide_id}")
async def delete_slide(slide_id: int, db: Session = Depends(get_db)):
    """Delete a slide"""
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    # Delete associated files
    try:
        if os.path.exists(slide.image_path):
            os.remove(slide.image_path)
        if os.path.exists(slide.thumbnail_path):
            os.remove(slide.thumbnail_path)
    except Exception as e:
        print(f"Error deleting files: {e}")
    
    db.delete(slide)
    db.commit()
    
    return {"message": "Slide deleted successfully"}

# Made with Bob
