"""
Tags API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.models.tag import Tag

router = APIRouter()


@router.get("/")
async def get_all_tags(db: Session = Depends(get_db)):
    """Get all tags grouped by category"""
    tags = db.query(Tag).all()
    
    # Group tags by category
    tags_by_category = {}
    for tag in tags:
        if tag.category not in tags_by_category:
            tags_by_category[tag.category] = []
        tags_by_category[tag.category].append({
            "id": tag.id,
            "name": tag.name
        })
    
    return {"tags": tags_by_category}


@router.get("/categories")
async def get_categories():
    """Get available tag categories"""
    return {
        "categories": [
            "client_painpoint",
            "client_type",
            "software_type",
            "software_function"
        ]
    }


@router.get("/{tag_id}/slides")
async def get_slides_by_tag(tag_id: int, db: Session = Depends(get_db)):
    """Get all slides associated with a specific tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    
    return {
        "tag": {"id": tag.id, "name": tag.name, "category": tag.category},
        "slides": [
            {
                "id": slide.id,
                "original_filename": slide.original_filename,
                "slide_number": slide.slide_number,
                "thumbnail_path": slide.thumbnail_path,
                "title": slide.title
            }
            for slide in tag.slides
        ]
    }

# Made with Bob
