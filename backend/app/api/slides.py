"""
Slides API endpoints
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Body
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
import os
import shutil

from app.core.database import get_db
from app.models.slide import Slide
from app.services.slide_processor import SlideProcessor
from app.services.ai_tagger import AITagger
from pptx import Presentation
from pptx.util import Inches

router = APIRouter()


class ExportRequest(BaseModel):
    slide_ids: List[int]
    filename: str = "exported_slides.pptx"


class DeleteBatchRequest(BaseModel):
    slide_ids: List[int]


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
    
    # Check for duplicate filename
    existing_slides = db.query(Slide).filter(
        Slide.original_filename == file.filename
    ).count()
    
    if existing_slides > 0:
        raise HTTPException(
            status_code=409,
            detail=f"File '{file.filename}' already uploaded ({existing_slides} slides exist). Please delete existing slides first or rename the file."
        )
    
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
        total_slides = len(slides_data)
        
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
            db.commit()  # Commit slide first to ensure it's in the database
            db.refresh(slide)  # Refresh to get the ID and ensure it's in session
            
            # Generate and assign tags (include filename, slide position, and image path for better tagging)
            tags = await ai_tagger.generate_tags(
                slide_data["text_content"],
                slide_data.get("title", ""),
                db,
                filename=file.filename,
                slide_number=slide_data["slide_number"],
                total_slides=total_slides,
                image_path=slide_data["image_path"]
            )
            
            # Link tags to slide (deduplicate to avoid constraint violations)
            unique_tags = []
            seen_tag_ids = set()
            for tag in tags:
                if tag.id not in seen_tag_ids:
                    unique_tags.append(tag)
                    seen_tag_ids.add(tag.id)
            
            for tag in unique_tags:
                slide.tags.append(tag)
            
            db.commit()  # Commit the tag relationships
            
            created_slides.append({
                "id": slide.id,
                "slide_number": slide.slide_number,
                "thumbnail_path": slide.thumbnail_path
            })
        
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
                "image_path": slide.image_path,
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




@router.get("/{slide_id}/image")
async def get_slide_image(slide_id: int, db: Session = Depends(get_db)):
    """Get the image file for a specific slide"""
    slide = db.query(Slide).filter(Slide.id == slide_id).first()
    if not slide:
        raise HTTPException(status_code=404, detail="Slide not found")
    
    if not slide.image_path or not os.path.exists(slide.image_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    return FileResponse(slide.image_path, media_type="image/png")


@router.delete("/batch")
async def delete_slides_batch(
    request: DeleteBatchRequest,
    db: Session = Depends(get_db)
):
    """
    Delete multiple slides at once
    - Accepts list of slide IDs
    - Removes all from database
    - Deletes all associated files
    """
    if not request.slide_ids:
        raise HTTPException(status_code=400, detail="No slide IDs provided")
    
    slides = db.query(Slide).filter(Slide.id.in_(request.slide_ids)).all()
    
    if not slides:
        raise HTTPException(status_code=404, detail="No slides found with provided IDs")
    
    deleted_count = 0
    deleted_files = []
    
    try:
        for slide in slides:
            # Store file paths
            image_path = slide.image_path
            thumbnail_path = slide.thumbnail_path
            
            # Delete from database
            db.delete(slide)
            deleted_count += 1
            
            # Delete files
            if image_path and os.path.exists(image_path):
                os.remove(image_path)
                deleted_files.append(image_path)
            
            if thumbnail_path and os.path.exists(thumbnail_path):
                os.remove(thumbnail_path)
                deleted_files.append(thumbnail_path)
        
        db.commit()
        
        return {
            "message": f"Successfully deleted {deleted_count} slides",
            "deleted_count": deleted_count,
            "deleted_files_count": len(deleted_files)
        }
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error deleting slides: {str(e)}")


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
