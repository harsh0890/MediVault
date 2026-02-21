"""
Script to check which Gemini models are available for your API key
"""
import requests
import json
from app.config import config

def check_available_models():
    """List all available models for the API key"""
    print("=" * 60)
    print("Checking Available Gemini Models")
    print("=" * 60)
    
    if not config.GEMINI_API_KEY:
        print("❌ ERROR: GEMINI_API_KEY not configured")
        return
    
    api_key = config.GEMINI_API_KEY
    base_url = "https://generativelanguage.googleapis.com/v1beta/models"
    
    headers = {
        'Content-Type': 'application/json',
        'X-goog-api-key': api_key
    }
    
    print(f"API Key: {api_key[:20]}...")
    print(f"Requesting models from: {base_url}")
    print()
    
    try:
        response = requests.get(base_url, headers=headers, timeout=30)
        
        print(f"Response Status: {response.status_code}")
        print()
        
        if response.status_code == 200:
            result = response.json()
            
            if 'models' in result:
                models = result['models']
                print(f"✅ Found {len(models)} available models:")
                print()
                
                # Group by model family
                model_families = {}
                for model in models:
                    name = model.get('name', 'unknown')
                    # Extract base name (e.g., 'gemini-2.0-flash' from 'models/gemini-2.0-flash')
                    if '/' in name:
                        base_name = name.split('/')[-1]
                    else:
                        base_name = name
                    
                    # Get supported methods
                    methods = model.get('supportedGenerationMethods', [])
                    display_name = model.get('displayName', base_name)
                    description = model.get('description', '')
                    
                    # Check if generateContent is supported
                    supports_generate = 'generateContent' in methods
                    
                    if supports_generate:
                        print(f"  ✓ {base_name}")
                        print(f"    Display Name: {display_name}")
                        if description:
                            print(f"    Description: {description[:100]}...")
                        print(f"    Methods: {', '.join(methods)}")
                        print()
                
                # Test a few common models
                print("=" * 60)
                print("Testing Common Models:")
                print("=" * 60)
                
                test_models = [
                    'gemini-2.0-flash',
                    'gemini-1.5-flash',
                    'gemini-1.5-pro',
                    'gemini-pro'
                ]
                
                for model_name in test_models:
                    test_url = f"{base_url}/{model_name}:generateContent"
                    test_payload = {
                        "contents": [{
                            "parts": [{"text": "Hi"}]
                        }]
                    }
                    
                    try:
                        test_response = requests.post(
                            test_url, 
                            headers=headers, 
                            json=test_payload,
                            timeout=10
                        )
                        
                        if test_response.status_code == 200:
                            print(f"  ✅ {model_name} - WORKS!")
                        elif test_response.status_code == 404:
                            print(f"  ❌ {model_name} - Not found (404)")
                        elif test_response.status_code == 429:
                            print(f"  ⚠️  {model_name} - Quota exceeded (429) - Model exists but quota issue")
                        else:
                            error_data = test_response.json() if test_response.text else {}
                            error_msg = error_data.get('error', {}).get('message', 'Unknown error')
                            print(f"  ❌ {model_name} - Error {test_response.status_code}: {error_msg[:50]}")
                    except Exception as e:
                        print(f"  ❌ {model_name} - Request failed: {str(e)[:50]}")
                
            else:
                print("⚠️  No models found in response")
                print(f"Response: {json.dumps(result, indent=2)}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_available_models()
