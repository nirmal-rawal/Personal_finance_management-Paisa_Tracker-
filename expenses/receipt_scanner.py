import base64
from google.generativeai.generative_models import GenerativeModel
from google.generativeai.client import configure
from google.generativeai.types import GenerationConfig
import json
import os
import re

class ReceiptScanner:
    def __init__(self):
        # Configure the API key
        configure(api_key='AIzaSyBHYkp_vw_euBcbyP4XnHgOlVOQK5Lpm8c')
        self.model = GenerativeModel('gemini-1.5-flash')
        self.category_mapping = {
            'groceries': ['grocery', 'supermarket', 'food', 'market', 'mart', 'produce'],
            'dining': ['restaurant', 'cafe', 'fast food', 'coffee', 'bar', 'eat', 'diner'],
            'transportation': ['gas', 'fuel', 'taxi', 'uber', 'lyft', 'public transport', 'transit', 'bus', 'train'],
            'shopping': ['clothing', 'electronics', 'store', 'mall', 'retail', 'shop', 'boutique'],
            'utilities': ['electricity', 'water', 'internet', 'phone', 'utility', 'bill', 'service'],
            'health': ['pharmacy', 'hospital', 'clinic', 'medical', 'drug', 'health'],
            'entertainment': ['movie', 'cinema', 'streaming', 'game', 'concert', 'theater'],
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

    def _map_to_category(self, merchant: str, description: str) -> str:
        """Map merchant/description to the most relevant category"""
        merchant = self._clean_description(merchant)
        description = self._clean_description(description)
        combined_text = f"{merchant} {description}"
        
        # First try to match exact merchant names
        merchant_lower = merchant.lower()
        if 'walmart' in merchant_lower or 'target' in merchant_lower:
            return 'shopping'
        if 'whole foods' in merchant_lower or 'kroger' in merchant_lower:
            return 'groceries'
        if 'starbucks' in merchant_lower or 'mcdonalds' in merchant_lower:
            return 'dining'
        if 'shell' in merchant_lower or 'exxon' in merchant_lower:
            return 'transportation'
        
        # Then try keyword matching
        for category, keywords in self.category_mapping.items():
            if any(keyword in combined_text for keyword in keywords):
                return category
                
        return 'other'

    def scan_receipt(self, image_file):
        try:
            # Read and encode the image
            image_bytes = image_file.read()
            base64_image = base64.b64encode(image_bytes).decode('utf-8')

            prompt = """Analyze this receipt image thoroughly and extract:
            - Total amount (as number, extract the final total including taxes)
            - Date (in YYYY-MM-DD format, find the transaction date)
            - Description (concise summary of main items purchased, 3-5 key items)
            - Merchant name (official store/business name)
            
            Important:
            - Amount must be numeric (no currency symbols)
            - Date must be in exact YYYY-MM-DD format
            - Description should be a comma-separated list of main items
            - Merchant should be the official business name
            
            Return ONLY a JSON object in this exact format:
            {
                "amount": number,
                "date": "string",
                "description": "string",
                "merchant": "string"
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
            if not all(key in result for key in ['amount', 'date', 'description', 'merchant']):
                raise ValueError("Missing required fields in response")
            
            # Convert amount to float if it's a string
            if isinstance(result['amount'], str):
                result['amount'] = float(result['amount'].replace(',', '').replace('$', ''))
            
            # Add category based on merchant and description
            result['category'] = self._map_to_category(
                result['merchant'], 
                result['description']
            )
                
            return result

        except json.JSONDecodeError as e:
            print(f"JSON parsing error: {str(e)}")
            return {'error': 'Failed to parse receipt data'}
        except Exception as e:
            print(f"Scanning error: {str(e)}")
            return {'error': str(e)}