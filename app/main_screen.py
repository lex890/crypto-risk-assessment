import FreeSimpleGUI as sg
import webbrowser
from . import risk_assessment as rsk
from . import plot_graphs as plg
from . import get_images as gim
from . import login_screen as log
from . import loading as lod
from . import csv_handler as csv
from . import feedback as fdb
import os
import re
screen_width, _ = sg.Window.get_screen_size()

def get_page_data(data, page, rows_per_page):
    start = (page - 1) * rows_per_page
    end = start + rows_per_page
    return data[start:end]

def get_percent_data(value):
    value = float(value)
    
    if value < 0:
        number_data=f'{abs(value)}%'
        number_color='red'
    else:
        number_data=f'{abs(value)}%'
        number_color='green'

    return number_data, number_color

def generate_table(i, data):
    font_size = ('Helvetica', 12)
    symbol_font_size = ('Helvetica', 12, 'bold')
    current_data = data[i]

    # Descriptive variable unpacking
    rank, name, price, change_1h, change_24h, change_7d, mcap, icon_path, symbol = current_data[:9]

    # Create a list of frequency price change
    percent_fields = [change_1h, change_24h, change_7d]

    # Filter the retrieved data and color
    (num1, col1), (num2, col2), (num3, col3) = (
        get_percent_data(v) for v in percent_fields
    )

    row = [
            [
                sg.Text( # Rank
                    rank, 
                    key=f'-rank{i}-', font=font_size, size=(4, 1), 
                    justification='right', enable_events=True, 
                    pad=((0, 30), (0, 0))
                ),
                sg.Image( # Icon
                    gim.get_image(icon_path, 1), key=f'-icon{i}-',
                    pad=((0, 0), (0, 0)), enable_events=True
                ),
                sg.Column([
                    [
                        sg.Text( # Name
                            name, key=f'-name{i}-', font=font_size, 
                            pad=((10, 0), (0, 0)), enable_events=True
                        ),
                        sg.Text( # Symbol
                            symbol, key=f'-symbol{i}-', font=symbol_font_size, 
                            size=(6, 1), text_color='#bebebe', pad=((0, 0), (0, 0)), enable_events=True
                        )
                    ]
                    ], pad=((0, 0), (0, 0)), size=(160, 25)
                ),
                sg.Text( # Price
                    price, key=f'-price{i}-', font=font_size, 
                    size=(16, 1), justification='right', pad=((0, 20), (0, 0)), enable_events=True
                ),
                sg.Text( # 1h%
                    num1, text_color=col1, key=f'-hour{i}-', font=font_size, 
                    size=(6, 1), justification='right', pad=((0, 5), (0, 0)), enable_events=True
                ),
                sg.Text( # 24h%
                    num2, text_color=col2, key=f'-day{i}-', font=font_size, 
                    size=(6, 1), justification='right', pad=((0, 5), (0, 0)), enable_events=True
                ),
                sg.Text( # 7d%
                    num3, text_color=col3, key=f'-week{i}-', font=font_size, 
                    size=(6, 1), justification='right', pad=((0, 0), (0, 0)), enable_events=True
                ),
                sg.Text( # Market Cap
                    mcap, key=f'-mcap{i}-', font=font_size, 
                    size=(17, 1), justification='right', pad=((20, 20), (0, 0)), enable_events=True
                )
            ]
        ]
    return row

def generate_table_header():
    font_size = ('Helvetica', 12, 'bold')
    row = [
        [
            sg.Text( # Rank
                '#', font=font_size, pad=((0, 0), (0, 0)), 
                size=(4, 1), justification='right'
            ),
            sg.Text( # Name
                'Name', font=font_size, pad=((25, 0), (0, 0))
            ),
            sg.Text( # Price
                'Price', font=font_size, pad=((125, 12), (0, 0)),
                size=(16, 1), justification='right'
            ),
            sg.Text(# 1h%
                '1h%', font=font_size, pad=((5, 0), (0, 0)),
                size=(6, 1), justification='right'
            ),
            sg.Text(# 24h%
                '24%', font=font_size, pad=((0, 0), (0, 0)),
                size=(6, 1), justification='right'
            ),
            sg.Text(# 7d%
                '7d%', font=font_size, pad=((0, 0), (0, 0)),
                size=(6, 1), justification='right'
            ),
            sg.Text(# Market Cap
                'Market Cap', font=font_size, pad=((0, 20), (0, 0)),
                size=(17, 1), justification='right', expand_x=True
            )
        ]
    ] 
    return row 

def calculate_current_entry(current_page, rows_per_page, data):
    start = (current_page - 1) * rows_per_page
    end = start + rows_per_page
    current_page_data = data[start:end]
    print('current_page_data', current_page_data)
    return current_page_data

def update_table(main_window, current_page_data, rows_per_page):
    for i, row in enumerate(current_page_data):
        # unpack row
        (rank, name, price, change_1h, change_24h, change_7d, mcap, icon_path, symbol) = row[:9]
        # format the % fields
        (num1, col1), (num2, col2), (num3, col3) = (
            get_percent_data(v) for v in (change_1h, change_24h, change_7d)
        )
        # update table
        main_window[f'-rank{i}-'  ].update(rank)
        main_window[f'-icon{i}-'  ].update(data=gim.get_image(icon_path, 1))
        main_window[f'-name{i}-'  ].update(name)
        main_window[f'-symbol{i}-'].update(symbol)
        main_window[f'-price{i}-' ].update(price)
        main_window[f'-hour{i}-'  ].update(num1, text_color=col1)
        main_window[f'-day{i}-'   ].update(num2, text_color=col2)
        main_window[f'-week{i}-'  ].update(num3, text_color=col3)
        main_window[f'-mcap{i}-'  ].update(mcap)

    # Extract the row number
    for leftover in range(len(current_page_data), rows_per_page):
        for prefix in ('-rank', '-icon', '-name', '-symbol',
                       '-price', '-hour', '-day', '-week', '-mcap'):
            key = f'{prefix}{leftover}-'
            element = main_window[key]
            element.update(visible=True)

def first_column_box():
    # Define header row
    header = [
        [
            sg.Image(
                filename='app/assets/images/resizedLogo.png', 
                size=(50, 50), 
                pad=((40, 10), (20, 0)), 
                enable_events=True, 
                key='-HEADERICON-'
            ),
            sg.Text(
                'Cryptocurrency Investment Risk Assessment Tool',
                font=('Helvetica', 16),
                pad=((0, 0), (20, 0)),
                enable_events=True,
                key='-HEADER-',
                expand_x=True  # allow text to take space
            )
        ]
    ]

    # Define feedback row
    feedback = [
        [
            sg.Image(
                filename='app/assets/images/feedback.png',
                size=(50, 50),
                pad=((0, 10), (20, 0)),
                enable_events=True,
                key='-FEEDBACK-ICON-',
                tooltip='Send feedback.'
            ),
            sg.Text(
                'Give us feedback!',
                font=('Helvetica', 12),
                pad=((0, 40), (20, 0)),
                enable_events=True,
                key='-FEEDBACK-',
                tooltip='Help us improve the app by sending a feedback form!'
            )
        ]
    ]

    # Combine header and feedback in one row, with flexible space
    first_layer = [
        [
            sg.Column(header, pad=(0, 0)),
            sg.Push(),  # pushes feedback to the right
            sg.Column(feedback, pad=(0, 0))
        ]
    ]

    return first_layer

def second_column_box():
    
    sorting_buttons = [
        [
            sg.Button(
                '', 
                image_filename='app/assets/images/byalpha.png', 
                image_size=(50, 50), button_color=("#F0F0F0", 
                sg.theme_background_color()), 
                border_width=1, 
                pad=((60, 10), (0, 0)), key=('-ALPHA-'), 
                tooltip='Sort by Alpha'
            ),
            sg.Button(
                '', 
                image_filename='app/assets/images/bynumber.png',
                image_size=(50, 50), button_color=("#F0F0F0", 
                sg.theme_background_color()), 
                border_width=1, 
                pad=((0, 10), (0, 0)), key=('-NUMBER-'), 
                tooltip='Sort by Ranking(#)'
            ),
            sg.Button(
                '', 
                image_filename='app/assets/images/byprice.png',
                image_size=(50, 50), button_color=("#F0F0F0", sg.theme_background_color()), 
                border_width=1, 
                pad=((0, 0), (0, 0)), key=('-PRICE-'), 
                tooltip='Sort by Price($)'
            )
        ]
    ]

    combo_currency = [
        [
            sg.Text('Select Currency', font=('Helvetica', 16), pad=((50, 0), (0, 0))),
            sg.Combo(['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'PHP'], default_value='USD', font=('Helvetica', 14), key='-CURRENCY-', pad=((0, 0), (0, 0)), tooltip='Select Currency', enable_events=True),
        ]
    ]

    search_bar = [
        [
            sg.InputText(
                default_text='',
                size=(22, 1),
                font=('Helvetica', 18),
                pad=((50, 0), (0, 0)),
                key='-SEARCHBAR-',
                tooltip='Search Cryptocurrency',
                text_color='gray'
            ),
            sg.Button(
                '',
                image_filename='app/assets/images/search.png',
                image_size=(50, 50),
                button_color=(sg.theme_background_color(), sg.theme_background_color()),
                border_width=0,
                key='-SBUTTON-',
                pad=((0, 0), (0, 0)),
                bind_return_key=True
            )
        ]
    ]

    ref_danger = [
        [
            sg.Image(
                filename='app/assets/images/ref-danger.png',
                size=(20, 20), 
                pad=((0, 5), (0, 0)), 
                enable_events=True,
                tooltip='High-risk investment identified.' 
            ),
            sg.Text(
                'Danger',
                font=('Helvetica', 12),
                pad=((0, 0), (0, 0)),
            )
        ]
    ]

    ref_warning = [
        [
            sg.Image(
                filename='app/assets/images/ref-warning.png',
                size=(20, 20), 
                pad=((0, 5), (0, 0)), 
                enable_events=True,
                tooltip='Medium-risk invest with caution.' 
            ),
            sg.Text(
                'Warning',
                font=('Helvetica', 12),
                pad=((0, 0), (0, 0)),
            )            
        ]
    ]

    ref_good = [
        [
            sg.Image(
                filename='app/assets/images/ref-good.png',
                size=(20, 20), 
                pad=((0, 5), (0, 0)), 
                enable_events=True,
                tooltip='Investment risk assessed as low.' 
            ),
            sg.Text(
                'Good',
                font=('Helvetica', 12),
                pad=((0, 0), (0, 0)),
            )
        ]
    ]

    ref_danger_box = [
        [
            sg.Column(
                ref_danger,
                pad=((0, 0), (0, 0)))
        ]
    ]

    ref_warning_box = [
        [
            sg.Column(
                ref_warning,
                pad=((0, 0), (0, 0)))            
        ]
    ]

    ref_good_box = [
        [
            sg.Column(
                ref_good,
                pad=((0, 0), (0, 0)))
        ]
    ]

    icon_reference = [
        [
            sg.Column(
                ref_good_box,
                pad=((85, 25), (25, 0))
            ),
            sg.Column(
                ref_warning_box,
                pad=((0, 25), (25, 0))
            ),
            sg.Column(
                ref_danger_box,
                pad=((0, 25), (25, 0))
            ),
        ]
    ]

    second_layer = [
        [   
            sg.Column(sorting_buttons, pad=(0, 0)),

            sg.Column(combo_currency, pad=(0, 0)),   

            sg.Column(search_bar, pad=(0, 0)),

            sg.Column(icon_reference, pad=(0, 0))
        ]
    ]

    return second_layer

def third_column_box(data):
    
    page_nav = [
        [
            
            sg.Button(
                image_filename='app/assets/images/arrow-left-icon.png',
                size=(75, 75),
                key='-PREV-',
                button_color=("#F0F0F0", sg.theme_background_color()),
                border_width=0,
                focus=False
            ),
            sg.Text(
                '1',
                font=('Helvetica', 21, 'bold'),
                pad=((25, 0), (0, 0)),
                enable_events=True,
                key='-PAGENO-'
            ),
            sg.Button(
                image_filename='app/assets/images/arrow-right-icon.png',
                size=(75, 75),
                key='-NEXT-',
                button_color=("#F0F0F0", sg.theme_background_color()),
                border_width=0,
                focus=False,
                pad=((30, 0), 0)
            )
        ]
    ]

    crypto_header = [
        [
            sg.Column(
                generate_table_header(),
                pad=((0, 0), (10, 10))
            )
        ]
    ]
    print('data', data)
    crypto_list = [
        [sg.Column([
            [sg.Column(generate_table(i, data), pad=((0, 0), (0, 0)))],
            [sg.HorizontalSeparator(pad=((0, 0), (15, 15)), color='#f0f0f0')]
        ], pad=((0, 0), (0, 0)))]
        for i in range(10)
    ]

    sort_by_message = [
        [sg.Column([
            [sg.Text('Sort by: Rank', pad=((0, 0), (0, 0)), font=('Hevetica', 12, 'bold'), key='-SORT-BY-MSG-', enable_events=True),
             sg.Image(filename='app/assets/images/arrow-up-small.png', pad=((5, 0), (0, 0)), key='-FLAG-')]
        ], pad=((0, 0), (0, 0)))]
    ]

    table = [
        [sg.Column(sort_by_message, pad=((0, 0), (35, 5)))],
        [sg.HorizontalSeparator(pad=((0, 0), (5, 0)))],
        [sg.Column(crypto_header, pad=((0, 0), (0, 0)))],
        [sg.HorizontalSeparator(pad=((0, 0), (0, 15)))],
        [sg.Column(crypto_list, pad=((0, 0), (0, 0)))],
        [sg.Push(), sg.Column(page_nav, pad=((20, 0), (25, 0))), sg.Push()]
    ]

    risk_assessment_window = rsk.score_window(data)

    third_layer = [
        [
            sg.Push(),
            sg.Column(table, pad=((0, 0), (0, 0))),
            sg.Column(risk_assessment_window, pad=((48, 0), (0, 0))),
            sg.Push()
        ]
    ]

    return third_layer

def main_window(headings, data, current_page, rows_per_page):

    first_layer = first_column_box()

    second_layer = second_column_box()

    third_layer = third_column_box(data)


    layout = [
        #header and icon
        [
            sg.Column(first_layer, expand_x=True, pad=((0, 0), (0, 0)))
        ],
        
        [
            sg.Column(second_layer, expand_x=True, pad=((0, 0), (20, 0)))   
        ],

        [
            sg.Column(third_layer, expand_x=True, pad=((0, 0), (0, 0)))
        ]
    ]

    window = sg.Window('Main App', layout, finalize=True, resizable=True)
    rsk.update_score_window(window, data[0])
    window.Maximize()
    return window

def main_window_handler(main_window, headings, data, current_page, rows_per_page, filepath, api_key, api_choice):
    # Initializing default values
    reverse_flag = True
    hyper_link = data[0][11]
    assessment_criteria = headings[13:23]
    currency_choice = main_window['-CURRENCY-'].get()
    # Set strings from crypto data headers as score headers
    marquee_texts = [f'   {item}   ' for item in assessment_criteria]
    
    # Set the table elements hover effect
    log.setup_hover_effects(main_window)
    
    # Main window event loop 
    while True:
        mw_event, mw_values = main_window.read(timeout=90)
        
        # Individual Score Window
        if mw_event == '-SCORE-CLICKED-':
            chart_key = mw_values[mw_event]['key']
            chart_data = plg.score_data_for_canvas[chart_key]['data']
            overlay_win = lod.show_dimmed_overlay()
            sub_score_window = rsk.sub_score_window(chart_data, chart_key)
            while True:
                event, _ = sub_score_window.read()
                if event == '-EXIT-':
                    sub_score_window.close()
                    break
            overlay_win.close()

        # Overall Assessment Score Window
        elif mw_event == '-MAIN-CLICKED-':
            chart_key = mw_values[mw_event]['key']
            chart_data = plg.score_data_for_canvas[chart_key]['data']
            overlay_win = lod.show_dimmed_overlay()
            main_score_window = rsk.main_score_window(chart_data)
            while True:
                event, _ = main_score_window.read()
                if event == '-EXIT-':
                    overlay_win.close()
                    main_score_window.close()
                    break
        
        # Logo click to exit
        elif mw_event in ('-HEADERICON-', 'HEADER'):
            if filepath != 'app/assets/data/data.csv':
                os.remove(filepath)
            main_window.close()
            return True
        
        # Handles table clicks
        elif isinstance(mw_event, str) and mw_event.startswith(log.KEY_PREFIXES):
            match = re.search(r'\d+', mw_event)
            current_row = (int(match.group())) + ((current_page - 1) * rows_per_page)
            selected_coin = data[current_row]
            hyper_link = selected_coin[11]
            rsk.update_risk_window(main_window, selected_coin, currency_choice)
            rsk.update_score_window(main_window, selected_coin)

        # <-- Page Navigation -->    
        # shift table to the next 10 entries
        elif mw_event == '-NEXT-':
            max_pages = (len(data) - 1) // rows_per_page + 1
            # next if there are available data
            if current_page < max_pages and not len(data) % rows_per_page:
                current_page += 1
                current_page_data = calculate_current_entry(current_page, rows_per_page, data)
                update_table(main_window, current_page_data, rows_per_page)
                main_window['-PAGENO-'].update(str(current_page))
            # next to load more data from API
            else: 
                # Fetch next set of cryptocurrencies
                try:    
                    current_page += 1
                    # Fetch the next 10 coins
                    new_data = lod.next_screen_loading(data, api_key, api_choice, currency_choice)
                    if new_data:
                        # creates temp csv file with new data
                        csv.export_to_csv(new_data)
                        # appends new data to main csv then deletes the created csv file
                        _, new_data_list = csv.read_csv()
                        csv.append_csv(filepath, new_data_list)
                        # reinitialize global variable data
                        _, data = csv.read_csv(filepath)
                        # update page number and table
                        current_page_data = calculate_current_entry(current_page, rows_per_page, data)
                        update_table(main_window, current_page_data, rows_per_page)
                        main_window['-PAGENO-'].update(str(current_page))
                    else:
                        sg.popup_auto_close('No more cryptocurrencies available.', auto_close_duration=2)
                except Exception as e:
                    fdb.send_automated_report()
        # shift table to the prev 10 entries
        elif mw_event == '-PREV-':
            if current_page > 1:
                current_page -= 1
                current_page_data = calculate_current_entry(current_page, rows_per_page, data)
                update_table(main_window, current_page_data, rows_per_page)
                main_window['-PAGENO-'].update(str(current_page))

        elif mw_event == '-CURRENCY-':
            overlay_win = lod.show_dimmed_overlay()
            currency = mw_values[mw_event]
            _, data, filepath = lod.login_loading(api_key, api_choice, currency)
            current_page = 1
            current_page_data = calculate_current_entry(current_page, rows_per_page, data)
            update_table(main_window, current_page_data, rows_per_page)
            main_window['-PAGENO-'].update(str(current_page))        
            overlay_win.close()
             
        elif mw_event == '-HYPERLINK-':
            webbrowser.open(hyper_link)  # Replace with your URL

        elif mw_event == '-FEEDBACK-ICON-':
            if fdb.feedback_screen():
                sg.popup('Feedback submitted successfully!', title='Thank you for your feedback.')

        elif mw_event == '-NUMBER-':
            main_window['-FLAG-'].update(filename=log.flag_image[reverse_flag])
            data.sort(key=lambda x: int(x[0]), reverse=reverse_flag)
            reverse_flag = not reverse_flag
            current_page = 1
            current_page_data = calculate_current_entry(current_page, rows_per_page, data)
            update_table(main_window, current_page_data, rows_per_page)
            main_window['-PAGENO-'].update(str(current_page))
            main_window['-SORT-BY-MSG-'].update('Sort by: Rank')
            
        elif mw_event == '-ALPHA-':
            main_window['-FLAG-'].update(filename=log.flag_image[reverse_flag])
            data.sort(key=lambda x: x[1].lower(), reverse=reverse_flag)
            reverse_flag = not reverse_flag
            current_page = 1
            current_page_data = calculate_current_entry(current_page, rows_per_page, data)
            update_table(main_window, current_page_data, rows_per_page)
            main_window['-PAGENO-'].update(str(current_page))
            main_window['-SORT-BY-MSG-'].update('Sort by: Alpha')
            
        elif mw_event == '-PRICE-':
            main_window['-FLAG-'].update(filename=log.flag_image[reverse_flag])
            data.sort(key=lambda x: float(x[2].replace(',', '')), reverse=reverse_flag)
            reverse_flag = not reverse_flag
            current_page = 1
            current_page_data = calculate_current_entry(current_page, rows_per_page, data)
            update_table(main_window, current_page_data, rows_per_page)
            main_window['-PAGENO-'].update(str(current_page))
            main_window['-SORT-BY-MSG-'].update('Sort by: Price')
            

        elif mw_event in ('-SBUTTON-', 'Return', '\r', '\n'):
            search_bar_val = mw_values['-SEARCHBAR-']
            search_query = search_bar_val.strip()

            if not search_query: # Handle empty searches
                continue
            try:
                overlay_win = lod.show_dimmed_overlay()
                search_window, search_terms = lod.search_screen_loading(api_key, api_choice, search_query, currency_choice, filepath)
                log.setup_hover_effects(search_window)
                while True:
                    sw_event, sw_values = search_window.read()
                    
                    if sw_event == '-CLOSE-':
                        search_window.close()
                        break
                    elif isinstance(sw_event, str) and sw_event.startswith(log.KEY_PREFIXES):
                        match = re.search(r'\d+', sw_event)
                        current_index = str((int(match.group())))
                        current_row = next(
                            (i for i, row in enumerate(search_terms) 
                            if row and row[0] == current_index), 
                            -1
                        )
                        selected_coin = search_terms[current_row]
                        hyper_link = search_terms[current_row][11]
                        search_window.close()
                        rsk.update_risk_window(main_window, selected_coin, currency_choice)
                        rsk.update_score_window(main_window, selected_coin)
                        break
            except Exception as e:
                sg.popup_error(f"Search failed: {e}")
                fdb.send_automated_report()
                continue
            finally:
                if 'overlay_win' in locals():
                    overlay_win.close()

        elif mw_event in (sg.WIN_CLOSED, 'Exit'):
            if filepath != 'app/assets/data/data.csv':
                os.remove(filepath)
            main_window.close()
            return True
        
        rsk.marquee_effect(main_window, marquee_texts)