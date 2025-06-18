from forex_python.converter import CurrencyRates

c = CurrencyRates()
rate = c.get_rate('USD', 'EUR')  # Live rate
converted = c.convert('USD', 'EUR', 100)  # Convert 100 USD to EUR

print(rate)