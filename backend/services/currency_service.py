import requests
from flask import current_app

class CurrencyService:
    """
    Service for currency conversion using ExchangeRate API
    """
    
    def __init__(self):
        self.base_url = "https://api.exchangerate-api.com/v4/latest/"
        self.cache = {}  # Simple cache for rates
    
    def get_exchange_rates(self, base_currency):
        """
        Get all exchange rates for a base currency
        """
        try:
            # Check cache first
            if base_currency in self.cache:
                return self.cache[base_currency]
            
            # Fetch from API
            response = requests.get(f"{self.base_url}{base_currency}", timeout=5)
            response.raise_for_status()
            
            data = response.json()
            rates = data.get('rates', {})
            
            # Cache the rates
            self.cache[base_currency] = rates
            
            return rates
        except Exception as e:
            print(f"Error fetching exchange rates: {e}")
            return {}
    
    def convert(self, amount, from_currency, to_currency):
        """
        Convert amount from one currency to another
        
        Args:
            amount: Amount to convert
            from_currency: Source currency code (e.g., 'USD')
            to_currency: Target currency code (e.g., 'INR')
        
        Returns:
            Converted amount or None if conversion fails
        """
        try:
            # If same currency, return original amount
            if from_currency == to_currency:
                return float(amount)
            
            # Get exchange rates for base currency
            rates = self.get_exchange_rates(from_currency)
            
            if not rates or to_currency not in rates:
                return None
            
            # Convert
            rate = rates[to_currency]
            converted_amount = float(amount) * rate
            
            return round(converted_amount, 2)
        except Exception as e:
            print(f"Error converting currency: {e}")
            return None
    
    def get_supported_currencies(self):
        """
        Get list of supported currency codes
        """
        try:
            # Use USD as base to get all currencies
            rates = self.get_exchange_rates('USD')
            return list(rates.keys()) if rates else []
        except Exception as e:
            print(f"Error getting supported currencies: {e}")
            return []
    
    def clear_cache(self):
        """
        Clear the exchange rate cache
        """
        self.cache = {}