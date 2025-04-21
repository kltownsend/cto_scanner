import os
import sys
import requests
import feedparser
from pathlib import Path
from dotenv import load_dotenv
from cto_signal_scanner.utils.feed_sources import FEEDS
from cto_signal_scanner.utils.pdf_generator import ReportGenerator
from openai import OpenAI
import httpx

def test_env_variables():
    """Test environment variables configuration"""
    print("\n1. Testing Environment Variables...")
    load_dotenv()
    
    # Check OpenAI API Key
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        print(f"✓ OPENAI_API_KEY found: {api_key[:8]}...")
    else:
        print("✗ OPENAI_API_KEY not found!")
        return False
    
    # Check GPT Model
    model = os.getenv("GPT_MODEL")
    if model:
        print(f"✓ GPT_MODEL found: {model}")
    else:
        print("✗ GPT_MODEL not found! Will use default: gpt-3.5-turbo")
    
    return True

def test_openai_connection():
    """Test OpenAI API connection"""
    print("\n2. Testing OpenAI API Connection...")
    try:
        # Create a clean transport without any proxy configuration
        transport = httpx.HTTPTransport(proxy=None)
        client = httpx.Client(transport=transport)
        
        # Initialize OpenAI client with our clean HTTP client
        openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY"),
            http_client=client
        )
        
        # Simple test completion
        response = openai_client.chat.completions.create(
            model=os.getenv("GPT_MODEL", "gpt-3.5-turbo"),
            messages=[{"role": "user", "content": "Test connection"}],
            max_tokens=5
        )
        print("✓ Successfully connected to OpenAI API")
        return True
    except Exception as e:
        print(f"✗ OpenAI API connection failed: {str(e)}")
        return False

def test_feed_sources():
    """Test RSS feed sources"""
    print("\n3. Testing Feed Sources...")
    all_successful = True
    
    for url in FEEDS:
        print(f"\nTesting feed: {url}")
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            feed = feedparser.parse(url)
            if feed.entries:
                print(f"✓ Successfully parsed feed ({len(feed.entries)} entries found)")
                # Test one entry's required fields
                entry = feed.entries[0]
                print("  First entry:")
                print(f"  - Title: {getattr(entry, 'title', 'Not found')}")
                print(f"  - Link: {getattr(entry, 'link', 'Not found')}")
                print(f"  - Published: {getattr(entry, 'published', 'Not found')}")
            else:
                print("✗ No entries found in feed")
                all_successful = False
                
        except Exception as e:
            print(f"✗ Error accessing feed: {str(e)}")
            all_successful = False
    
    return all_successful

def test_pdf_generation():
    """Test PDF report generation"""
    print("\n4. Testing PDF Generation...")
    try:
        # Create a test report
        pdf_gen = ReportGenerator()
        
        # Test directory creation
        if pdf_gen.reports_dir.exists():
            print("✓ Reports directory created successfully")
        else:
            print("✗ Failed to create reports directory")
            return False
            
        # Test monthly directory creation
        if pdf_gen.current_month_dir.exists():
            print("✓ Monthly directory created successfully")
        else:
            print("✗ Failed to create monthly directory")
            return False
        
        # Test PDF generation with sample content
        pdf_gen.add_header(days_back=7)
        pdf_gen.add_article(
            title="Test Article",
            link="https://example.com",
            summary="This is a test summary",
            rating="8",
            rationale="This is a test rationale"
        )
        
        # Generate the PDF
        pdf_gen.generate()
        
        # Verify the PDF was created
        if Path(pdf_gen.doc.filename).exists():
            print(f"✓ PDF generated successfully at: {pdf_gen.doc.filename}")
            
            # Clean up test PDF
            Path(pdf_gen.doc.filename).unlink()
            print("✓ Test cleanup successful")
        else:
            print("✗ Failed to generate PDF")
            return False
            
        return True
        
    except Exception as e:
        print(f"✗ PDF generation test failed: {str(e)}")
        return False

def test_cache_directory():
    """Test cache file creation and permissions"""
    print("\n5. Testing Cache Management...")
    try:
        cache_file = Path("processed_entries.json")
        
        # Test file creation
        with open(cache_file, 'w') as f:
            f.write("{}")
        print("✓ Successfully created cache file")
        
        # Test file deletion
        cache_file.unlink()
        print("✓ Successfully deleted cache file")
        
        return True
    except Exception as e:
        print(f"✗ Cache file operation failed: {str(e)}")
        return False

def run_all_tests():
    """Run all tests and return overall status"""
    print("=== CTO Signal Scanner Tests ===")
    
    tests = [
        ("Environment Variables", test_env_variables),
        ("OpenAI API Connection", test_openai_connection),
        ("Feed Sources", test_feed_sources),
        ("PDF Generation", test_pdf_generation),
        ("Cache Management", test_cache_directory)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Unexpected error in {test_name}: {str(e)}")
            results.append(False)
    
    print("\n=== Test Summary ===")
    for (test_name, _), result in zip(tests, results):
        status = "✓ Passed" if result else "✗ Failed"
        print(f"{test_name}: {status}")
    
    if all(results):
        print("\n✓ All tests passed! The scanner is ready to run.")
        return 0
    else:
        print("\n✗ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(run_all_tests()) 