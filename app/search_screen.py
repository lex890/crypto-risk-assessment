import FreeSimpleGUI as sg
from fuzzywuzzy import process
import csv
from . import get_images as img

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


def search_crypto(query, data, search_terms, threshold=60, limit=10):
    query = query.strip()
    matches = process.extract(query, search_terms, limit=limit)
    seen = set()
    result_list = []
    
    for match, score in matches:
        if score >= threshold:
            for row in data:
                if (row['Name'] == match or row['Symbol'] == match) and row['Symbol'] not in seen:
                    seen.add(row['Symbol'])
                    result_list.append((
                        row['#'],
                        row['Name'],
                        row['Current Price (USD)'],
                        row['1h%'],
                        row['24h%'],
                        row['7d%'],
                        row['Market Cap (USD)'],
                        row['Logo'],
                        row['Symbol'],
                        row['Description'],
                        row['Creation Date'],
                        row['Website'],
                        row['Source Code']
                    ))

    return result_list if result_list else "No good match found."


def search_screen(user_search, file_path):
    if not user_search.strip():
        return sg.Window("Invalid", [[sg.Text("No search performed.")]], finalize=True)

    csv_data = load_crypto_data(file_path)
    search_terms = get_search_terms(csv_data)
    result = search_crypto(user_search, csv_data, search_terms)
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
                    image_filename='./images/searchSZ.png',
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
                ),
                sg.Button(
                    '',
                    image_filename='./images/closeNR.png',
                    image_size=(35, 35),
                    button_color=(sg.theme_background_color(), sg.theme_background_color()),
                    border_width=0,
                    key='-CBUTTON-',
                    pad=((450, 0), (0, 50))
                )
            ]
        ]
        image_elem = sg.Image(filename='./images/no_result_found.png', key='-NORESULTIMG-', background_color="#dadada")
        canvas_frame = sg.Column([[image_elem]], background_color="#dadada", pad=((185, 0), (125, 0)),)
        canvas_message = sg.Text("It's Not Here...", font=('印品鸿蒙体', 20), background_color="#dadada", pad=((215, 0), (0, 0)), text_color="#838383")
        search_window = [[canvas_frame], [canvas_message]]
        return search_header, search_window, key_to_data
    else:
        search_header = [
            [
                sg.Button(
                    '',
                    image_filename='./images/searchSZ.png',
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
                    image_filename='./images/closeNR.png',
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
