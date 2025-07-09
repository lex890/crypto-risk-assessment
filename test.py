import app

api_key = 'CG-Y1CthFUh3uNauQ8ehg6TzFCu'
api_choice = 2
search_query = 'OHM'
filepath = 'app/assets/data/data.csv'
currency_choice = 'USD'
search_window = app.search_window(api_key, api_choice, search_query, currency_choice, filepath)
root1 = search_window.TKroot
SEARCH_PREFIXES = ('-srank', '-sicon', '-sname', '-ssymbol',
                '-sprice', '-smcap')
app.hovery(search_window, SEARCH_PREFIXES, root1)
while True:
    sw_event, sw_values = search_window.read()

    if sw_event == '-CLOSE-':
        search_window.close()
        break

