import base64
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.client import configure
from google.generativeai.types import GenerationConfig
import json
import re

class IncomeReceiptScanner:
    def __init__(self):
        # Configure the API key
        configure(api_key='AIzaSyBHYkp_vw_euBcbyP4XnHgOlVOQK5Lpm8c')
        self.model = GenerativeModel('gemini-1.5-flash')
        self.source_mapping = {
            'salary': ['salary', 'payroll', 'paycheck', 'wages', 'income'],
            'freelance': ['freelance', 'contract', 'consulting', 'gig'],
            'business': ['business', 'enterprise', 'company', 'llc', 'inc'],
            'investments': ['dividend', 'investment', 'stocks', 'bonds', 'interest'],
            'rental': ['rental', 'property', 'lease', 'landlord'],
            'other': []
        }

    def _clean_description(self, description: str) -> str:
        """Clean and normalize the description text"""
        if not description:
            return ""
        
        # Remove special characters and normalize spaces
        description = re.sub(r'[^\w\s]', '', description)
        description = ' '.join(description.split())
        return description.lower()

    def _map_to_source(self, payer: str, description: str) -> str:
        """Map payer/description to the most relevant income source"""
        payer = self._clean_description(payer)
        description = self._clean_description(description)
        combined_text = f"{payer} {description}"
        
        # First try to match exact payer names
        payer_lower = payer.lower()
        if 'employer' in payer_lower or 'company' in payer_lower:
            return 'salary'
        if 'client' in payer_lower or 'customer' in payer_lower:
            return 'freelance'
        if 'dividend' in payer_lower or 'investment' in payer_lower:
            return 'investments'
        if 'rent' in payer_lower or 'tenant' in payer_lower:
            return 'rental'
        
        # Then try keyword matching
        for source, keywords in self.source_mapping.items():
            if any(keyword in combined_text for keyword in keywords):
                return source
                
        return 'other'

    def scan_receipt(self, image_file):
        try:
            # Read and encode the image
            image_bytes = image_file.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            prompt = """Analyze this income receipt/document image thoroughly and extract:
            - Total amount (as number, extract the final total)
            - Date (in YYYY-MM-DD format, find the transaction date)
            - Description (concise summary of payment purpose)
            - Payer name (who paid this income)
            
            Important:
            - Amount must be numeric (no currency symbols)
            - Date must be in exact YYYY-MM-DD format
            - Description should briefly explain the income source
            - Payer should be the official name of the paying entity
            
            Return ONLY a JSON object in this exact format:
            {
                "amount": number,
                "date": "string",
                "description": "string",
                "payer": "string"
            }"""

            # Create proper GenerationConfig object
            generation_config = GenerationConfig(
                temperature=0.2,
                top_p=0.8,
                top_k=40,
                max_output_tokens=200
            )

            # Make the API call with proper configuration
            response = self.model.generate_content(
                contents=[
                    {"mime_type": "image/jpeg", "data": base64_image},
                    prompt
                ],
                generation_config=generation_config
            )

            # Process the response
            text = response.text.strip()
            
            # Clean JSON response (handle different markdown formats)
            text = text.replace('```json', '').replace('```', '').strip()
            
            # Parse and validate the response
            result = json.loads(text)
            if not all(key in result for key in ['amount', 'date', 'description', 'payer']):
                raise ValueError("Missing required fields in response")
            
            # Convert amount to float if it's a string
            if isinstance(result['amount'], str):
                result['amount'] = float(result['amount'].replace(',', '').replace('$', ''))
            
            # Add source based on payer and description
            result['source'] = self._map_to_source(
                result['payer'], 
                result['description']
            )
                
            return result

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return {'error': 'Failed to parse receipt data'}
        except Exception as e:
            print(f"Scanning error: {str(e)}")
            return {'error': str(e)}