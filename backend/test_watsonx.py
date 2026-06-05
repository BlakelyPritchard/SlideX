#!/usr/bin/env python3
"""
Test script to verify WatsonX API integration
"""
import asyncio
import sys
from app.services.ai_tagger import AITagger
from app.core.config import settings

async def test_watsonx():
    """Test WatsonX API connection and tagging"""
    
    print("=" * 60)
    print("WatsonX Integration Test")
    print("=" * 60)
    
    # Check configuration
    print("\n1. Checking Configuration...")
    print(f"   API Key: {'✓ Set' if settings.WATSONX_API_KEY else '✗ Missing'}")
    print(f"   Project ID: {'✓ Set' if settings.WATSONX_PROJECT_ID else '✗ Missing'}")
    print(f"   URL: {settings.WATSONX_URL}")
    
    if not settings.WATSONX_API_KEY or not settings.WATSONX_PROJECT_ID:
        print("\n❌ ERROR: WatsonX credentials not configured!")
        print("   Please check your .env file.")
        return False
    
    # Test tagging
    print("\n2. Testing AI Tagging...")
    tagger = AITagger()
    
    test_content = """Filename: IBM_Verify_Demo.pptx

Title: IBM Verify - Identity and Access Management

Content: IBM Verify provides comprehensive identity and access management solutions for enterprises. 
Key features include:
- Multi-factor authentication
- Single sign-on (SSO)
- Identity governance
- Risk-based authentication
- Cloud and on-premises deployment

Perfect for organizations looking to enhance security and streamline user access."""
    
    try:
        print("   Sending request to WatsonX...")
        tags = await tagger.generate_tags(
            text_content=test_content,
            title="IBM Verify - Identity and Access Management",
            filename="IBM_Verify_Demo.pptx",
            slide_number=1,
            total_slides=10
        )
        
        print(f"\n✓ Success! Generated {len(tags)} tags:")
        
        # Group tags by category (access attributes before session closes)
        tags_by_category = {}
        for tag in tags:
            category = tag.category
            name = tag.name
            if category not in tags_by_category:
                tags_by_category[category] = []
            tags_by_category[category].append(name)
        
        for category, tag_names in sorted(tags_by_category.items()):
            print(f"\n   {category}:")
            for name in tag_names:
                print(f"      - {name}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("\nStarting WatsonX test...\n")
    success = asyncio.run(test_watsonx())
    
    if success:
        print("\n" + "=" * 60)
        print("✓ WatsonX integration is working correctly!")
        print("=" * 60)
        sys.exit(0)
    else:
        print("\n" + "=" * 60)
        print("✗ WatsonX integration test failed")
        print("=" * 60)
        sys.exit(1)

# Made with Bob
