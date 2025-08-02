import app

api_key = "e28cbf9a-5c08-452e-8099-fa7f832262a3"
api_choice = "CoinMarketCap"
currency_choice="USD"
current_page = 1
rows_per_page = 10
login_window = app.generate_login_window(api_choice)
app.demo_mode_handler(login_window, current_page, rows_per_page)