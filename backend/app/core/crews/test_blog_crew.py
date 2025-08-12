#!/usr/bin/env python3
"""
Standalone test script for blog crew functionality
Place this file in your project root: E:\omni-leap-final\test_blog_crew.py
"""

import os
import sys
from pathlib import Path

# Add the backend directory to Python path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

def test_environment():
    """Test that all required environment variables are set"""
    print("🔧 Testing Environment Setup...")
    
    required_vars = {
        'GOOGLE_API_KEY': 'Required for Gemini LLM',
        'SERPER_API_KEY': 'Optional for enhanced search (get from serper.dev)'
    }
    
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: Configured ({description})")
        else:
            print(f"⚠️  {var}: Missing ({description})")
    
    print()

def test_imports():
    """Test that all required packages can be imported"""
    print("📦 Testing Package Imports...")
    
    required_imports = [
        ('crewai', 'CrewAI framework'),
        ('langchain_google_genai', 'Google Gemini integration'),
        ('crewai_tools', 'CrewAI tools'),
    ]
    
    for package, description in required_imports:
        try:
            __import__(package)
            print(f"✅ {package}: Available ({description})")
        except ImportError as e:
            print(f"❌ {package}: Missing ({description}) - {e}")
    
    print()

def test_blog_crew_import():
    """Test importing the blog crew module"""
    print("🤖 Testing Blog Crew Import...")
    
    try:
        from app.core.crews.blog_crew import create_blog_post_crew
        print("✅ Blog crew imported successfully")
        return create_blog_post_crew
    except ImportError as e:
        print(f"❌ Failed to import blog crew: {e}")
        print("\nTroubleshooting:")
        print("1. Make sure blog_crew.py is in backend/app/core/crews/")
        print("2. Check that all imports in blog_crew.py work")
        print("3. Verify your project structure matches the imports")
        return None
    except Exception as e:
        print(f"❌ Error importing blog crew: {e}")
        return None

def test_blog_creation(create_blog_post_crew, test_topic="Artificial Intelligence in Healthcare"):
    """Test creating a blog post"""
    print(f"📝 Testing Blog Post Creation for: '{test_topic}'...")
    
    try:
        print("Starting blog creation process...")
        result = create_blog_post_crew(test_topic)
        
        if result and len(str(result)) > 100:
            print("✅ Blog post created successfully!")
            print(f"📊 Result length: {len(str(result))} characters")
            
            # Show preview
            result_str = str(result)
            preview = result_str[:300] + "..." if len(result_str) > 300 else result_str
            print(f"\n📋 Preview:\n{'-'*50}")
            print(preview)
            print('-'*50)
            
            # Save to file for inspection
            output_file = Path("test_blog_output.md")
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(str(result))
            print(f"💾 Full output saved to: {output_file.absolute()}")
            
            return True
        else:
            print(f"⚠️  Blog creation returned minimal content: {result}")
            return False
            
    except Exception as e:
        print(f"❌ Error creating blog post: {e}")
        print(f"Error type: {type(e).__name__}")
        import traceback
        print("\n📋 Full traceback:")
        traceback.print_exc()
        return False

def main():
    """Main test function"""
    print("🚀 Blog Crew Testing Suite")
    print("=" * 60)
    
    # Test 1: Environment
    test_environment()
    
    # Test 2: Package imports
    test_imports()
    
    # Test 3: Blog crew import
    create_blog_post_crew = test_blog_crew_import()
    if not create_blog_post_crew:
        print("❌ Cannot proceed with testing - import failed")
        return False
    
    # Test 4: Blog creation
    success = test_blog_creation(create_blog_post_crew)
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Your blog crew is working correctly.")
        print("\nNext steps:")
        print("1. Check test_blog_output.md for the generated content")
        print("2. Test with different topics")
        print("3. Integrate with your FastAPI application")
    else:
        print("❌ Tests failed. Please fix the issues above before proceeding.")
    
    print("=" * 60)
    return success

if __name__ == "__main__":
    main()