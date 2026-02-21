"""
Gemini Service
Handles Google Gemini interactions for summarization and Q&A
"""
import requests
import json
import time
from app.config import config


class GeminiService:
    """Service for Google Gemini API interactions"""
    
    def __init__(self):
        if not config.GEMINI_API_KEY or config.GEMINI_API_KEY == "your-gemini-api-key-here":
            raise ValueError("GEMINI_API_KEY not configured. Please set it in config.properties")
        
        self.api_key = config.GEMINI_API_KEY
        self.model = config.GEMINI_MODEL
        # Try v1beta first, fallback to v1 if needed
        self.base_url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent"
        self.fallback_url = f"https://generativelanguage.googleapis.com/v1/models/{self.model}:generateContent"
    
    def _call_gemini_api(self, prompt: str, system_instruction: str = None, max_retries: int = 3) -> str:
        """
        Make API call to Gemini with retry logic for rate limits
        
        Args:
            prompt: User prompt
            system_instruction: Optional system instruction (will be prepended to prompt)
            max_retries: Maximum number of retry attempts for rate limit errors
            
        Returns:
            str: Response text from Gemini
        """
        headers = {
            'Content-Type': 'application/json',
            'X-goog-api-key': self.api_key
        }
        
        # Combine system instruction with prompt if provided
        full_prompt = prompt
        if system_instruction:
            full_prompt = f"{system_instruction}\n\n{prompt}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": full_prompt
                        }
                    ]
                }
            ]
        }
        
        for attempt in range(max_retries):
            try:
                # Try v1beta endpoint first
                url = self.base_url
                response = requests.post(url, headers=headers, json=payload)
                
                # If 404, try fallback URL (v1 instead of v1beta)
                if response.status_code == 404:
                    print(f"Model not found in v1beta, trying v1 endpoint...")
                    url = self.fallback_url
                    response = requests.post(url, headers=headers, json=payload)
                
                # Handle rate limit errors (429) with retry
                if response.status_code == 429:
                    error_data = response.json()
                    retry_delay = 60  # Default 60 seconds
                    
                    # Try to extract retry delay from error response
                    if 'error' in error_data and 'details' in error_data['error']:
                        for detail in error_data['error']['details']:
                            if detail.get('@type') == 'type.googleapis.com/google.rpc.RetryInfo':
                                retry_delay = int(float(detail.get('retryDelay', '60s').rstrip('s'))) + 5
                    
                    if attempt < max_retries - 1:
                        print(f"Rate limit exceeded. Retrying in {retry_delay} seconds... (Attempt {attempt + 1}/{max_retries})")
                        time.sleep(retry_delay)
                        continue
                    else:
                        # Last attempt failed - provide helpful message
                        error_msg = (
                            "API quota exceeded. The free tier has limited requests per day. "
                            "Please wait a few minutes and try again, or consider upgrading to a paid plan for higher limits."
                        )
                        print(f"Gemini API Error - Status: 429, Message: {error_msg}")
                        raise Exception(error_msg)
                
                # Handle other errors
                if response.status_code != 200:
                    error_detail = response.text
                    print(f"Gemini API Error - Status: {response.status_code}, Response: {error_detail[:500]}")
                    
                    # Parse error message for user-friendly display
                    try:
                        error_json = response.json()
                        if 'error' in error_json and 'message' in error_json['error']:
                            error_msg = error_json['error']['message']
                        else:
                            error_msg = f"API error: {response.status_code}"
                    except:
                        error_msg = f"API error: {response.status_code}"
                    
                    raise Exception(error_msg)
                
                response.raise_for_status()
                result = response.json()
                
                # Extract text from Gemini response
                if 'candidates' in result and len(result['candidates']) > 0:
                    candidate = result['candidates'][0]
                    
                    # Check for blocking or errors
                    if 'finishReason' in candidate:
                        if candidate['finishReason'] != 'STOP':
                            print(f"Warning: finishReason is {candidate['finishReason']}")
                    
                    if 'content' in candidate:
                        parts = candidate['content'].get('parts', [])
                        if parts and 'text' in parts[0]:
                            return parts[0]['text']
                
                # If we get here, log the full response for debugging
                print(f"Unexpected response format. Full response: {json.dumps(result, indent=2)[:500]}")
                raise Exception(f"Unexpected response format from Gemini API")
                
            except requests.exceptions.RequestException as e:
                if attempt < max_retries - 1:
                    wait_time = (attempt + 1) * 2  # Exponential backoff: 2s, 4s, 6s
                    print(f"Request error. Retrying in {wait_time} seconds... (Attempt {attempt + 1}/{max_retries})")
                    time.sleep(wait_time)
                    continue
                else:
                    error_msg = f"Error calling Gemini API: {str(e)}"
                    if hasattr(e, 'response') and e.response is not None:
                        error_msg += f" - Response: {e.response.text[:200]}"
                    print(error_msg)
                    raise Exception(error_msg)
            except Exception as e:
                # Don't retry for non-rate-limit exceptions
                error_msg = f"Error processing Gemini response: {str(e)}"
                print(error_msg)
                raise Exception(error_msg)
        
        # Should not reach here, but just in case
        raise Exception("Failed to get response from Gemini API after retries")
    
    def summarize_medical_records(self, medical_records_text: str) -> str:
        """
        Generate a summary of medical records
        
        Args:
            medical_records_text: Combined text from all medical records
            
        Returns:
            str: Summary of medical records
        """
        if not medical_records_text.strip():
            return "No medical records found."
        
        system_instruction = """You are a medical assistant helping to summarize medical records. 
Provide a clear, concise summary that includes:
- Key findings and diagnoses
- Important dates and examinations
- Current prescriptions or treatments
- Any recommendations from doctors
- Overall health status

Keep the summary organized and easy to understand."""
        
        prompt = f"Please summarize the following medical records:\n\n{medical_records_text}"
        
        try:
            return self._call_gemini_api(prompt, system_instruction)
        except Exception as e:
            raise Exception(f"Error generating summary: {str(e)}")
    
    def answer_question(self, question: str, medical_records_text: str) -> dict:
        """
        Answer a question based on medical records and provide recommendations
        
        Args:
            question: User's question
            medical_records_text: Combined text from all medical records
            
        Returns:
            dict: Contains 'answer' and 'recommendations' keys
        """
        if not medical_records_text.strip():
            return {
                "answer": "I don't have access to your medical records yet. Please upload your medical records first.",
                "recommendations": []
            }
        
        system_instruction = """You are a medical assistant helping patients understand their medical records. 
When answering questions:
1. Provide accurate answers based on the medical records provided
2. Include TWO types of recommendations:
   a) Medical record-based recommendations (specific to the patient's records)
   b) General health recommendations (best practices, lifestyle advice)
3. Always include medical disclaimers that this is not a substitute for professional medical advice
4. Be clear, helpful, and empathetic

Format your response with:
- Direct answer to the question
- Medical record-based recommendations (if applicable)
- General health recommendations
- Medical disclaimer"""
        
        prompt = f"""Based on the following medical records, please answer this question: {question}

Medical Records:
{medical_records_text}

Please provide:
1. A direct answer to the question
2. Recommendations based on the medical records
3. General health recommendations
4. A medical disclaimer"""
        
        try:
            full_response = self._call_gemini_api(prompt, system_instruction)
            
            # Parse response to extract answer and recommendations
            answer = full_response
            recommendations = []
            
            # Try to extract recommendations if they're clearly marked
            if "Recommendations:" in full_response or "recommendations:" in full_response.lower():
                parts = full_response.split("Recommendations:" if "Recommendations:" in full_response else "recommendations:")
                if len(parts) > 1:
                    answer = parts[0].strip()
                    recommendations_text = parts[1].strip()
                    # Extract bullet points or numbered items
                    for line in recommendations_text.split('\n'):
                        line = line.strip()
                        if line and (line.startswith('-') or line.startswith('•') or line.startswith('*') or 
                                   (len(line) > 2 and line[0].isdigit() and line[1] in ['.', ')'])):
                            rec = line.lstrip('-•*0123456789.) ').strip()
                            if rec:
                                recommendations.append(rec)
            
            # If no recommendations extracted, add the full response as answer
            if not recommendations:
                recommendations = ["Please consult with your healthcare provider for personalized medical advice."]
            
            return {
                "answer": answer,
                "recommendations": recommendations
            }
        except Exception as e:
            raise Exception(f"Error answering question: {str(e)}")
