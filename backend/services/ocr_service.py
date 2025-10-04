import pytesseract
from PIL import Image
import re

def extract_from_receipt(image_path):
    text = pytesseract.image_to_string(Image.open(image_path))
    amount = re.search(r"\d+\.\d{2}", text)
    date = re.search(r"\d{4}-\d{2}-\d{2}", text)
    return {
        "text": text,
        "amount": amount.group() if amount else None,
        "date": date.group() if date else None
    }

