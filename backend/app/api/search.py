"""
Search API endpoints
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from typing import List, Optional

from app.core.database import get_db
from app.models.slide import Slide
from app.models.tag import Tag

router = APIRouter()


@router.get("/")
async def search_slides(
    q: Optional[str] = Query(None, description="Search query for text content"),
    tags: Optional[List[str]] = Query(None, description="Tag names to filter by"),
    categories: Optional[List[str]] = Query(None, description="Tag categories to filter by"),
    db: Session = Depends(get_db)
):
    """
    Search slides by text content and/or tags
    
    Examples:
    - /api/search?q=analytics
    - /api/search?tags=enterprise&tags=CRM
    - /api/search?categories=client_type&categories=software_type
    - /api/search?q=dashboard&tags=reporting
    """
    query = db.query(Slide)
    
    # Text search
    if q:
        search_filter = or_(
            Slide.text_content.ilike(f"%{q}%"),
            Slide.title.ilike(f"%{q}%")
        )
        query = query.filter(search_filter)
    
    # Filter by tags
    if tags:
        for tag_name in tags:
            query = query.join(Slide.tags).filter(Tag.name == tag_name)
    
    # Filter by categories
    if categories:
        query = query.join(Slide.tags).filter(Tag.category.in_(categories))
    
    # Execute query
    slides = query.distinct().all()
    
    return {
        "count": len(slides),
        "slides": [
            {
                "id": slide.id,
                "original_filename": slide.original_filename,
                "slide_number": slide.slide_number,
                "thumbnail_path": slide.thumbnail_path,
                "image_path": slide.image_path,
                "title": slide.title,
                "text_content": slide.text_content[:200] if slide.text_content else None,  # Preview
                "tags": [
                    {"id": tag.id, "name": tag.name, "category": tag.category}
                    for tag in slide.tags
                ]
            }
            for slide in slides
        ]
    }


@router.post("/export")
async def export_slides(
    slide_ids: List[int],
    db: Session = Depends(get_db)
):
    """
    Export selected slides as a new PowerPoint presentation
    Returns information about the slides to be exported
    """
    slides = db.query(Slide).filter(Slide.id.in_(slide_ids)).all()
    
    if not slides:
        return {"message": "No slides found", "slides": []}
    
    return {
        "message": f"Ready to export {len(slides)} slides",
        "slides": [
            {
                "id": slide.id,
                "original_filename": slide.original_filename,
                "slide_number": slide.slide_number,
                "image_path": slide.image_path
            }
            for slide in slides
        ]
    }

# Made with Bob
