import requests

def convert_currency(amount, from_currency, to_currency):
    res = requests.get(f"https://api.exchangerate-api.com/v4/latest/{from_currency}").json()
    rate = res["rates"].get(to_currency, 1)
    return round(amount * rate, 2)

