import os
import re
from datetime import datetime

class OCRService:
    """
    Service for OCR receipt processing
    Note: This is a placeholder implementation. 
    For production, integrate with Tesseract OCR or cloud OCR services.
    """
    
    def __init__(self):
        self.ocr_enabled = os.getenv('OCR_ENABLED', 'False').lower() == 'true'
    
    def extract_receipt_data(self, image_path):
        """
        Extract data from receipt image
        
        Args:
            image_path: Path to the receipt image
        
        Returns:
            Dictionary with extracted data:
            {
                'amount': float,
                'currency': str,
                'date': str (YYYY-MM-DD),
                'vendor_name': str,
                'category': str,
                'description': str
            }
        """
        if not self.ocr_enabled:
            return {
                'error': 'OCR is not enabled. Set OCR_ENABLED=True in environment'
            }
        
        try:
            # Placeholder for actual OCR implementation
            # In production, you would use:
            # - pytesseract for Tesseract OCR
            # - Google Cloud Vision API
            # - AWS Textract
            # - Azure Computer Vision
            
            # Example with pytesseract (commented out):
            # from PIL import Image
            # import pytesseract
            # 
            # image = Image.open(image_path)
            # text = pytesseract.image_to_string(image)
            # 
            # return self._parse_receipt_text(text)
            
            return {
                'error': 'OCR implementation pending',
                'message': 'Please implement OCR using pytesseract, Google Vision, or AWS Textract'
            }
            
        except Exception as e:
            return {
                'error': f'OCR processing failed: {str(e)}'
            }
    
    def _parse_receipt_text(self, text):
        """
        Parse extracted text to find receipt information
        
        Args:
            text: OCR extracted text
        
        Returns:
            Dictionary with parsed data
        """
        result = {
            'amount': None,
            'currency': None,
            'date': None,
            'vendor_name': None,
            'category': 'Other',
            'description': ''
        }
        
        try:
            lines = text.split('\n')
            
            # Extract amount (looking for currency symbols and numbers)
            amount_pattern = r'(?:USD|INR|EUR|GBP|₹|\$|€|£)\s*(\d+\.?\d*)'
            for line in lines:
                match = re.search(amount_pattern, line, re.IGNORECASE)
                if match:
                    result['amount'] = float(match.group(1))
                    # Determine currency from symbol
                    if '₹' in line or 'INR' in line.upper():
                        result['currency'] = 'INR'
                    elif '$' in line or 'USD' in line.upper():
                        result['currency'] = 'USD'
                    elif '€' in line or 'EUR' in line.upper():
                        result['currency'] = 'EUR'
                    elif '£' in line or 'GBP' in line.upper():
                        result['currency'] = 'GBP'
                    break
            
            # Extract date (various formats)
            date_patterns = [
                r'(\d{2}[-/]\d{2}[-/]\d{4})',  # DD-MM-YYYY or DD/MM/YYYY
                r'(\d{4}[-/]\d{2}[-/]\d{2})',  # YYYY-MM-DD or YYYY/MM/DD
                r'(\d{2}\s+[A-Za-z]{3}\s+\d{4})',  # DD Mon YYYY
            ]
            
            for line in lines:
                for pattern in date_patterns:
                    match = re.search(pattern, line)
                    if match:
                        date_str = match.group(1)
                        try:
                            # Try to parse and standardize to YYYY-MM-DD
                            parsed_date = self._parse_date(date_str)
                            if parsed_date:
                                result['date'] = parsed_date
                                break
                        except:
                            continue
                if result['date']:
                    break
            
            # Extract vendor name (usually first few lines)
            if len(lines) > 0:
                # Take first non-empty line as vendor name
                for line in lines[:5]:
                    line = line.strip()
                    if line and len(line) > 3:
                        result['vendor_name'] = line
                        break
            
            # Determine category based on keywords
            text_lower = text.lower()
            if any(word in text_lower for word in ['restaurant', 'cafe', 'food', 'dining']):
                result['category'] = 'Food'
            elif any(word in text_lower for word in ['hotel', 'booking', 'accommodation']):
                result['category'] = 'Travel'
            elif any(word in text_lower for word in ['taxi', 'uber', 'transport', 'fuel']):
                result['category'] = 'Travel'
            elif any(word in text_lower for word in ['office', 'stationery', 'supplies']):
                result['category'] = 'Office Supplies'
            
            # Create description from text (first 200 chars)
            result['description'] = text[:200].strip()
            
        except Exception as e:
            print(f"Error parsing receipt text: {e}")
        
        return result
    
    def _parse_date(self, date_str):
        """
        Parse various date formats to YYYY-MM-DD
        """
        formats = [
            '%d-%m-%Y',
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%Y/%m/%d',
            '%d %b %Y',
            '%d %B %Y',
        ]
        
        for fmt in formats:
            try:
                date_obj = datetime.strptime(date_str, fmt)
                return date_obj.strftime('%Y-%m-%d')
            except ValueError:
                continue
        
        return None
    
    def process_receipt_file(self, file):
        """
        Process uploaded receipt file
        
        Args:
            file: Flask uploaded file object
        
        Returns:
            Dictionary with extracted data
        """
        if not self.ocr_enabled:
            return {
                'error': 'OCR is not enabled'
            }
        
        try:
            # Save file temporarily
            temp_path = f"/tmp/{file.filename}"
            file.save(temp_path)
            
            # Extract data
            result = self.extract_receipt_data(temp_path)
            
            # Clean up
            if os.path.exists(temp_path):
                os.remove(temp_path)
            
            return result
            
        except Exception as e:
            return {
                'error': f'Failed to process receipt: {str(e)}'
            }