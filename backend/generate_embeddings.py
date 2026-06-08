"""
Script to generate embeddings for all slides in the database
Run this after uploading slides to enable AI-powered deck generation
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.core.database import SessionLocal
from app.services.embedding_service import get_embedding_service
from app.models.slide import Slide

def main():
    """Generate embeddings for all slides"""
    print("🚀 Starting embedding generation...")
    
    # Get database session
    db = SessionLocal()
    
    try:
        # Get embedding service
        embedding_service = get_embedding_service()
        
        # Get all slides
        slides = db.query(Slide).all()
        print(f"📊 Found {len(slides)} slides in database")
        
        if len(slides) == 0:
            print("⚠️  No slides found. Please upload some slides first.")
            return
        
        # Process each slide
        success_count = 0
        failed_count = 0
        
        for i, slide in enumerate(slides, 1):
            try:
                print(f"Processing slide {i}/{len(slides)}: {slide.title or 'Untitled'}...", end=" ")
                
                # Get tags for this slide (force load the relationship)
                tags = slide.tags
                
                # Add embedding
                if embedding_service.add_slide_embedding(slide.id, slide, tags):
                    success_count += 1
                    print("✅")
                else:
                    failed_count += 1
                    print("❌")
                    
            except Exception as e:
                failed_count += 1
                print(f"❌ Error: {e}")
        
        print(f"\n📈 Results:")
        print(f"   ✅ Success: {success_count}")
        print(f"   ❌ Failed: {failed_count}")
        
        # Show collection stats
        stats = embedding_service.get_collection_stats()
        print(f"\n📊 Collection Stats:")
        print(f"   Total embeddings: {stats.get('total_embeddings', 0)}")
        print(f"   Collection: {stats.get('collection_name', 'N/A')}")
        print(f"   Directory: {stats.get('persist_directory', 'N/A')}")
        
        if success_count > 0:
            print(f"\n🎉 Successfully generated embeddings for {success_count} slides!")
            print("   You can now use AI-powered deck generation.")
        else:
            print("\n⚠️  No embeddings were generated. Check the errors above.")
            
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        
    finally:
        db.close()


if __name__ == "__main__":
    main()

# Made with Bob
