import FreeSimpleGUI as sg
from .request_api import search_cmc, search_coingecko
from .get_images import get_image
from .csv_handler import read_csv
from .feedback import send_automated_report

def get_csv_search_terms(csv_data, search_query):
    """Return rows where rank, name or symbol contains search_query."""
    search_query = search_query.lower()
    results = []

    for idx, row in enumerate(csv_data):
        try:
            rank, name, symbol = (str(row[0]).lower(),
                                  str(row[1]).lower(),
                                  str(row[8]).lower())
        except IndexError:
            # Row too short — skip and optionally log
            print(f"Row {idx} malformed: {row}")
            send_automated_report()
            continue

        if (search_query in rank or
            search_query in name or
            search_query in symbol):
            results.append(row)

    return results

def get_api_search_terms(api_key, api_choice, search_query, currency_choice):
    api_choice = str(api_choice)
    if api_choice == '1':
        # CoinMarketCap
        return search_cmc(api_key, search_query, currency_choice)
    elif api_choice == '2':
        # CoinGecko
        return search_coingecko(api_key, search_query, currency_choice)
    return None

def handle_search_query(api_key, api_choice, search_query, currency_choice, filepath):
    # Handle Empty 
    if not search_query.strip():
        return sg.Window("Invalid", [[sg.Text("No search performed.")]], finalize=True)
    _, csv_data = read_csv(filepath)
    
    # this receives the whole row of matched crypto within the csv
    search_terms = get_csv_search_terms(csv_data, search_query)
    if not search_terms:
        # this receives the whole row of matched crypto retrieved from API
        search_terms = get_api_search_terms(api_key, api_choice, search_query, currency_choice)
        if search_terms:
            return search_terms
        else:
            return []
    return search_terms

def gen_result_box(row, i):
    HEADER_FONT = ('Helvetica', 12)
    name_col = sg.Column([
        [sg.Text(row[1][:12], size=(15, 1), font=HEADER_FONT, key=f'-name{row[0]}-', enable_events=True)],          # coin name
        [sg.Text(row[8], size=(7, 1), font=HEADER_FONT, key=f'-symbol{row[0]}-', enable_events=True)]           # symbol
    ], pad=((5, 0), (0, 0)))

    search_results = sg.Column(
        [[
            sg.Text(row[0], size=(4, 1), font=HEADER_FONT, pad=((0, 5), (0, 0)), key=f'-rank{row[0]}-', enable_events=True),
            sg.Image(get_image(row[7], 1), pad=((5, 0), (0, 0)), key=f'-icon{row[0]}-', enable_events=True),  # icon
            name_col,
            sg.Text(f"{float(row[2]):.5f}", size=(12, 1), font=HEADER_FONT, pad=((0, 0), (0, 0)),key=f'-price{row[0]}-', enable_events=True),   # price
            sg.Text(row[6], size=(15, 1), font=HEADER_FONT, pad=((0, 0), (0, 0)), key=f'-mcap{row[0]}-', enable_events=True)    # market‑cap
        ]]
    )

    return [[search_results],
            [sg.HorizontalSeparator(color='#dadada', pad=((0, 0), (0, 0)))]]

def gen_search_header(search_query):
    HEADER_FONT = ('Helvetica', 18, 'bold')
    close_button_box = [
        [
            sg.Text(f'Search Result: {search_query}', expand_x=True, font=HEADER_FONT, pad=((15, 0), (30, 0))),
            sg.Text('', expand_x=True),
            sg.Button('',
                      image_filename='app/assets/images/closeNR.png',
                      image_size=(35, 35),
                      button_color=(sg.theme_background_color(),
                                    sg.theme_background_color()),
                      border_width=0,
                      key='-CLOSE-',
                      pad=((0, 15), (10, 0)))
        ]
    ]
    return close_button_box

def gen_crypto_header(currency_choice):
    HEADER_FONT = ('Helvetica', 12, 'bold')
    FONT_COLOR = '#a6a6a6'
    crypto_header = [
        [
            sg.Text('#', font=HEADER_FONT, size=(4, 1), pad=((5, 0), (0, 0)), text_color=FONT_COLOR),
            sg.Text('Name', font=HEADER_FONT, pad=((5, 0), (0, 0)), text_color=FONT_COLOR),
            sg.Text('', expand_x=True, pad=((135, 0), (0, 0))),
            sg.Text(f'Price ({currency_choice})', font=HEADER_FONT, pad=((0, 0), (0, 0)), text_color=FONT_COLOR),
            sg.Text('', expand_x=True, pad=((0, 0), (0, 0))),
            sg.Text('Market Cap', font=HEADER_FONT, pad=((12, 0), (0, 0)), size=(14,1), text_color=FONT_COLOR)
        ],
        [sg.HorizontalSeparator(pad=((0, 0), (10, 0)))]
    ]
    return crypto_header

def render_search_window(search_terms, currency_choice, search_query):
    if not search_terms:
        return [
            [sg.Column(
                gen_search_header(search_query),
                expand_x=True,
                pad=((0, 0), (0, 100)),
                background_color=''
            )],
            [
                sg.Text('', expand_x=True),
                sg.Column([
                [
                    sg.Image(filename='app/assets/images/no_result_found.png', key='-NORESULTIMG-', pad=((10, 10), (40, 0)))
                ],
                [
                    sg.Text('', expand_x=True),
                    sg.Text("It's Not Here...", font=('印品鸿蒙体', 20), pad=((0, 0), (30, 30)), text_color="#838383"),
                    sg.Text('', expand_x=True)
                ]
                ], pad=((0, 0), (0, 0))),
                sg.Text('', expand_x=True)
            ],
        ]
    
    close_button_box = [
        sg.Column(
        gen_search_header(search_query),
        expand_x=True,
        pad=(0, 0),
        background_color=''
        )
    ]

    crypto_header = [
        sg.Column(gen_crypto_header(currency_choice), pad=((10, 0), (40, 0)))
    ]
    
    result_box = [
        [sg.Column(gen_result_box(entry, i), pad=((0, 0), (0, 0)))]for i, entry in enumerate(search_terms[:6])
    ]
    result_container = [
        sg.Column(result_box, pad=((10, 0), (0, 0)))
    ]
    
    layout = [
        [close_button_box],
        [crypto_header],
        [result_container]
    ]
    return layout

def search_window(api_key, api_choice, search_query, currency_choice, filepath):
    search_terms = handle_search_query(api_key, api_choice, search_query, currency_choice, filepath)

    print('search_terms', search_terms)
    search_win_layout = render_search_window(search_terms, currency_choice, search_query)
    
    return search_win_layout, search_terms

