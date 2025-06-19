import FreeSimpleGUI as sg
from fuzzywuzzy import process
import csv
from . import get_images as img
from . import request_api as req
from . import csv_handler as han
from . import score_handler as shr
from . import main_screen as msc

def load_crypto_data(csv_path):
    with open(csv_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        data = [row for row in reader]
    return data

def get_search_terms(data):
    terms = []
    for row in data:
        terms.append(row['Name'])
        terms.append(row['Symbol'])
    return terms

def format_large_number(num):
    try:
        num = float(num.replace(',', ''))  # Remove commas and convert to float
    except (ValueError, AttributeError):
        return num  # Return as-is if not a number
    if num >= 1_000_000_000_000:
        return f"{int(num / 1_000_000_000_000)}T"
    elif num >= 1_000_000_000:
        return f"{int(num / 1_000_000_000)}B"
    elif num >= 1_000_000:
        return f"{int(num / 1_000_000)}M"
    elif num >= 1_000:
        return f"{int(num / 1_000)}K"
    else:
        return str(int(num))  # Return whole number if < 1,000


def search_crypto(main_window, data, current_page, rows_per_page, user_search, csvdata, search_terms, api_key, currency_choice, filepath, threshold=85, limit=10):
    query = user_search.strip().upper()  # Convert to uppercase for consistent comparison
    
    # First try exact matches
    exact_matches = []
    for row in csvdata:
        if (row['Name'].upper() == query or row['Symbol'].upper() == query):
            exact_matches.append((
                row['#'],
                row['Name'],
                row[f'Current Price ({currency_choice})'],
                row['1h%'],
                row['24h%'],
                row['7d%'],
                row[f'Market Cap ({currency_choice})'],
                row['Logo'],
                row['Symbol'],
                row['Description'],
                row['Creation Date'],
                row['Website'],
                row['Source Code']
            ))
    
    if exact_matches:
        return exact_matches
    
    # If no exact matches, try fuzzy matching with higher threshold
    matches = process.extract(query, search_terms, limit=limit)
    seen = set()
    result_list = []
    
    for match, score in matches:
        if score >= threshold:
            for row in csvdata:
                if (row['Name'] == match or row['Symbol'] == match) and row['Symbol'] not in seen:
                    seen.add(row['Symbol'])
                    result_list.append((
                        row['#'],
                        row['Name'],
                        row['Current Price'],
                        row['1h%'],
                        row['24h%'],
                        row['7d%'],
                        row['Market Cap'],
                        row['Logo'],
                        row['Symbol'],
                        row['Description'],
                        row['Creation Date'],
                        row['Website'],
                        row['Source Code']
                    ))
    
    if not result_list:
        # Only call API if no matches found in local data
        print(f"Searching API for: {query}")
        output_tuple = req.search_via_api(api_key, query, currency_choice, filepath)
        if output_tuple:  # Only proceed if API call was successful
            result_list.append(output_tuple)
            result_list_dict = han.convert_to_dict(result_list, currency_choice)
            result_list_scores = shr.evaluate_cryptos(result_list_dict, currency_choice)
            han.export_to_csv(result_list_scores)
            _, new_data_list = han.read_csv('app/assets/data/temp.csv')
            han.append_csv(filepath, new_data_list)
            
            _, data = han.read_csv(filepath)
            main_window['-TABLE-'].update(values=msc.get_page_data(data, current_page, rows_per_page))
            main_window['-PAGENO-'].update(str(current_page))

    return result_list if result_list else "No matches found. Please check your spelling or try a different search term."



def search_screen(main_window, data, current_page, rows_per_page, user_search, filepath, api_key, currency_choice):
    if not user_search.strip():
        return sg.Window("Invalid", [[sg.Text("No search performed.")]], finalize=True)

    csv_data = load_crypto_data(filepath)
    search_terms = get_search_terms(csv_data)
    result = search_crypto(main_window, data, current_page, rows_per_page, user_search, csv_data, search_terms, api_key, currency_choice, filepath)
    
    print('this is the result: ', result)
    search_header, search_window, key_to_data = generate_results(result, user_search)

    if key_to_data:
        result_header = [
            sg.Column(
                search_header, 
                size=(950, 100),
                background_color=sg.theme_background_color(),
                pad=((25, 0), (35, 0))
            ),
            sg.Push()
        ]
        result_container = [
            sg.Push(),
            sg.Column(
                search_window, 
                size=(650, 800), 
                background_color="#f6f6f6", 
                scrollable=True,
                vertical_scroll_only=True,
                pad=(0, (0, 45))
            ),
            sg.Push()
        ]
    else:
        result_header = [
            sg.Column(
                search_header, 
                size=(950, 100),
                background_color=sg.theme_background_color(),
                pad=((25, 0), (35, 0)),
            ),
            sg.Push()
        ]
        result_container = [
            sg.Push(),
            sg.Column(
                search_window, 
                size=(650, 800), 
                background_color="#dadada", 
                justification='center',
                pad=(0, (0, 45))
            ),
            sg.Push()
        ]

    layout = [
        result_header,
        result_container
    ]

    return sg.Window('Search Result', layout, size=(850, 650)), key_to_data

def generate_results(result, user_search):

    search_header = []
    search_window = []
    key_to_data = {}

    if not isinstance(result, list):  # Handle no results case
        # Show an image on a Canvas
        search_header = [
            [
                sg.Button(
                    '',
                    image_filename='app/assets/images/searchSZ.png',
                    image_size=(35, 35),
                    button_color=(sg.theme_background_color(), sg.theme_background_color()),
                    border_width=0,
                    key='-SBUTTON-',
                    pad=((0, 15), 0)
                ),
                sg.Text(
                    f'No Results for: {user_search}', 
                    font=('印品鸿蒙体', 16),
                    text_color="#aaa8a8"
                )
            ]
        ]
        image_elem = sg.Image(filename='app/assets/images/no_result_found.png', key='-NORESULTIMG-', background_color="#dadada")
        canvas_frame = sg.Column([[image_elem]], background_color="#dadada", pad=((185, 0), (125, 0)),)
        canvas_message = sg.Text("It's Not Here...", font=('印品鸿蒙体', 20), background_color="#dadada", pad=((215, 0), (0, 0)), text_color="#838383")
        search_window = [[canvas_frame], [canvas_message]]
        return search_header, search_window, key_to_data
    else:
        search_header = [
            [
                sg.Button(
                    '',
                    image_filename='app/assets/images/searchSZ.png',
                    image_size=(35, 35),
                    button_color=(sg.theme_background_color(), sg.theme_background_color()),
                    border_width=0,
                    key='-SBUTTON-',
                    pad=((0, 15), 0)
                ),
                sg.Text(
                    f'Search: {user_search}', 
                    font=('印品鸿蒙体', 16),
                    text_color="#aaa8a8"
                ),
                sg.Button(
                    '',
                    image_filename='app/assets/images/closeNR.png',
                    image_size=(35, 35),
                    button_color=(sg.theme_background_color(), sg.theme_background_color()),
                    border_width=0,
                    key='-CBUTTON-',
                    pad=((550, 0), (0, 50))
                )
            ]
        ]



    for index, item in enumerate(result):
        
        data_tuple = item

        icon_key = f'-ICON{index+1}-'
        name_key = f'-NAME{index+1}-'

        key_to_data[icon_key] = data_tuple
        key_to_data[name_key] = data_tuple

        image = [
            [
                sg.Image(
                    img.get_image(item[7]), 
                    size=(65, 65), 
                    background_color="#eaeaea", 
                    key=f'-ICON{index+1}-', 
                    enable_events=True
                )
            ]
        ]

        info = [
             [
                sg.Button(
                    f'{item[1]}', 
                    font=('League Spartan', 12, 'bold'), button_color="#eaeaea", 
                    border_width=0, 
                    key=f'-NAME{index+1}-',
                    pad=(0, 0),
                    enable_events=True,
                    tooltip=f'{item[1]}'
                ),
                sg.Text(
                    f'#{item[0]}', 
                    font=('League Spartan', 12, 'bold'), background_color="#eaeaea", 
                    text_color='#919191',
                    pad=(0, 0)
                ) 
             ],
             [
                sg.Text(
                    f'{item[8]}', font=('League Spartan', 12, 'bold'), background_color="#eaeaea", 
                    pad=((2, 1), 0),
                    text_color='#919191')
             ]
        ]

        nums = [
            [
                sg.Text(
                    'MCap: ', 
                    font=('League Spartan', 12, 'bold'), background_color="#eaeaea",
                    pad=(0, 0)
                ),
                sg.Text(
                    f'{format_large_number(item[6])}', 
                    font=('League Spartan', 12, 'bold'), text_color="#919191",
                    background_color="#eaeaea",
                    pad=(0, 0)
                )
            ],
            [
                sg.Text(
                    'Vol(24h): ', 
                    font=('League Spartan', 12, 'bold'), background_color="#eaeaea",
                    pad=(0, 0)
                ),
                sg.Text(
                    f'${format_large_number(item[4])}', 
                    font=('League Spartan', 12, 'bold'), text_color="#919191",
                    background_color="#eaeaea",
                    pad=(0, 0)
                )
            ]
        ]

        price = [
            [
                sg.Text(
                    f'${item[2]}', 
                    font=('League Spartan', 12, 'bold'), background_color="#eaeaea"
                )
            ]
        ]

        card = [
            sg.Column(
                image, 
                size=(80, 80), 
                background_color="#eaeaea"
            ),
            sg.Column(
                info, 
                size=(150, 60), 
                background_color="#eaeaea",
                pad=(0, (0, 10)),
                expand_x=True
            ),
            sg.Column(
                nums, 
                size=(180, 60), 
                background_color="#eaeaea",
                pad=((20, 0), (0, 3))
            ),
            sg.Column(
                price, 
                size=(120, 60), 
                background_color="#eaeaea"
            )
        ]

        search_window.append([sg.Column(
                [card], 
                size=(600, 85), 
                background_color="#eaeaea", 
                pad=((20, 0), (10, 7))
            )
        ])

    return search_header, search_window, key_to_data
