"""
Simple test script to verify Gemini API key is working
"""
import requests
import json
from app.config import config

def test_gemini_api():
    """Test Gemini API with a simple request"""
    print("=" * 60)
    print("Testing Gemini API Key")
    print("=" * 60)
    
    # Check if API key is configured
    if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your-gemini-api-key-here":
        print("❌ ERROR: GEMINI_API_KEY not configured in config.properties")
        return False
    
    print(f"✓ API Key found: {config.GEMINI_API_KEY[:20]}...")
    print(f"✓ Model: {config.GEMINI_MODEL}")
    print()
    
    # Prepare API request
    api_key = config.GEMINI_API_KEY
    model = config.GEMINI_MODEL
    base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": "Say 'Hello, Gemini API is working!' in one sentence."
                    }
                ]
            }
        ]
    }
    
    print(f"Making request to: {base_url}")
    print(f"Request payload: {json.dumps(payload, indent=2)}")
    print()
    
    try:
        print("Sending request...")
        response = requests.post(base_url, headers=headers, json=payload, timeout=30)
        
        print(f"Response Status Code: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            # Extract text from response
            if 'candidates' in result and len(result['candidates']) > 0:
                candidate = result['candidates'][0]
                if 'content' in candidate:
                    parts = candidate['content'].get('parts', [])
                    if parts and 'text' in parts[0]:
                        response_text = parts[0]['text']
                        print("✅ SUCCESS! Gemini API is working!")
                        print(f"Response: {response_text}")
                        return True
            
            print("⚠️  WARNING: Unexpected response format")
            print(f"Response: {json.dumps(result, indent=2)}")
            return False
            
        else:
            print("❌ ERROR: API request failed")
            print(f"Status Code: {response.status_code}")
            print(f"Response: {response.text}")
            
            # Try to parse error
            try:
                error_json = response.json()
                if 'error' in error_json:
                    error = error_json['error']
                    print(f"\nError Details:")
                    print(f"  Code: {error.get('code', 'N/A')}")
                    print(f"  Message: {error.get('message', 'N/A')}")
                    print(f"  Status: {error.get('status', 'N/A')}")
            except:
                pass
            
            return False
            
    except requests.exceptions.Timeout:
        print("❌ ERROR: Request timed out (30 seconds)")
        return False
    except requests.exceptions.RequestException as e:
        print(f"❌ ERROR: Request failed: {str(e)}")
        return False
    except Exception as e:
        print(f"❌ ERROR: Unexpected error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_gemini_api()
    print()
    print("=" * 60)
    if success:
        print("✅ API Key is VALID and working!")
    else:
        print("❌ API Key test FAILED - check the error messages above")
    print("=" * 60)
    exit(0 if success else 1)
