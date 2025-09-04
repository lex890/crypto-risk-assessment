import FreeSimpleGUI as sg
import webbrowser
from . import risk_assessment as rsk
from . import plot_graphs as plg
from . import login_screen as log
from . import loading as lod
from . import csv_handler as csv
from . import feedback as fdb
from . import table as tbl
from . import prefix as pre
import os
import re
import threading
from . import request_api as req
screen_width, _ = sg.Window.get_screen_size()

def get_page_data(data, page, rows_per_page):
    start = (page - 1) * rows_per_page
    end = start + rows_per_page
    return data[start:end]

def calculate_current_entry(current_page, rows_per_page, data):
    start = (current_page - 1) * rows_per_page
    end = start + rows_per_page
    current_page_data = data[start:end]
    return current_page_data

def first_column_box():
    # Define header row
    smol_font = ('Segoe UI', 12, 'bold')
    bigga_font = ('Segoe UI', 24, 'bold')
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
                'Blockchain Risk Assessment Tool',
                font=bigga_font,
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
                font=smol_font,
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
            sg.Text('Select Currency: ', font=('Segoe UI', 16), pad=((50, 0), (0, 0))),
            sg.Combo(['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'PHP'], default_value='USD', font=('Segoe UI', 12), key='-CURRENCY-', pad=((0, 0), (0, 0)), tooltip='Select Currency', enable_events=True, readonly=True),
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

    second_layer = [
        [   
            sg.Column(sorting_buttons, pad=(0, 0)),

            sg.Column(combo_currency, pad=(0, 0)),   

            sg.Column(search_bar, pad=(0, 0))
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
            ),
            
        ]
    ]
    timer_container = [
        [
            sg.Image(filename='app/assets/images/timer.png', pad=((0, 10), (0, 0)), key='-TIMER-ICON-'),
            sg.Text('Refreshing in: 60', pad=((0, 0), (0, 0)), font=('Hevetica', 12, 'bold'), key='-TIMER-', enable_events=True)
        ]
    ]

    crypto_header = [
        [
            sg.Column(
                tbl.generate_table_header(),
                pad=((0, 0), (10, 10))
            )
        ]
    ]
    crypto_list = [
        [sg.Column([
            [sg.Column(tbl.generate_table(i, data), pad=((0, 0), (0, 0)))],
            [sg.HorizontalSeparator(pad=((0, 0), (15, 15)), color='#f0f0f0')]
        ], pad=((0, 0), (0, 0)))]
        for i in range(10)
    ]

    sort_by_message = [
        [
            sg.Column([
                [
                    sg.Text('Sort by: Rank', pad=((0, 0), (0, 0)), font=('Hevetica', 12, 'bold'), key='-SORT-BY-MSG-', enable_events=True),
                    sg.Image(filename='app/assets/images/arrow-up-small.png', pad=((5, 0), (0, 0)), key='-FLAG-')
                ]
            ], pad=((0, 0), (0, 0))),
            sg.Push(),
            sg.Column([
                [
                    sg.Text('', size=(2, 1), background_color='#06be8d', border_width=0, relief='solid', pad=((0, 5), 0)),
                    sg.Text('Low Risk', pad=((0, 2), (0, 0)), font=('Hevetica', 10, 'bold'), text_color="#808080"),
                    sg.VerticalSeparator(),
                    sg.Text('', size=(2, 1), background_color='#ffd166', border_width=0, relief='solid', pad=((2, 5), 0)),
                    sg.Text('Low-Medium Risk', pad=((0, 2), (0, 0)), font=('Hevetica', 10, 'bold'), text_color='#808080'),
                    sg.VerticalSeparator(),
                    sg.Text('', size=(2, 1), background_color="#e26641", border_width=0, relief='solid', pad=((2, 5), 0)),
                    sg.Text('Medium-High Risk', pad=((0, 2), (0, 0)), font=('Hevetica', 10, 'bold'), text_color='#808080'),
                    sg.VerticalSeparator(),
                    sg.Text('', size=(2, 1), background_color="#ef476f", border_width=0, relief='solid', pad=((2, 5), 0)),
                    sg.Text('High Risk', pad=((0, 0), (0, 0)), font=('Hevetica', 10, 'bold'), text_color='#808080'),
                    
                ]
            ], pad=((0, 0), (0, 0)))
        ]
    ]

    table = [
        [sg.Column(sort_by_message, pad=((0, 0), (35, 5)), expand_x=True)],
        [sg.HorizontalSeparator(pad=((0, 0), (5, 0)))],
        [sg.Column(crypto_header, pad=((0, 0), (0, 0)))],
        [sg.HorizontalSeparator(pad=((0, 0), (0, 15)))],
        [sg.Column(crypto_list, pad=((0, 0), (0, 0)))],
        [
            sg.Push(), 
            sg.Column(page_nav, pad=((0, 0), (0, 0))), 
            sg.Push()
        ],
        [sg.Column(timer_container, pad=((0, 0), (0, 20))),sg.Push()]
    ]

    risk_assessment_window = rsk.score_window(data)

    third_layer = [
        [
            sg.Push(),
            sg.Column(table, pad=((20, 0), (0, 0))),
            sg.Column(risk_assessment_window, pad=((15, 0), (0, 0))),
            sg.Push()
        ]
    ]

    return third_layer

def main_window(data):

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
    
    # Set the table elements hover effect
    log.setup_hover_effects(main_window)
    
    # Create stop event for timer thread
    stop_event = threading.Event()
    # Start timer thread for countdown display
    timer_thread = req.start_timer_thread(main_window, stop_event)
    
    # Start price monitoring thread (using first coin as reference)
    coin_id = data[0][0] if data and len(data) > 0 else '1'  # Use first coin's ID or default to '1'
    currency_choice = main_window['-CURRENCY-'].get()
    threading.Thread(target=req.start_price_monitoring, args=(api_key, api_choice, currency_choice, coin_id, filepath), daemon=True).start()
    selected_coin = data[0]
    # Main window event loop 
    while True:
        mw_event, mw_values = main_window.read(timeout=120)
        currency_choice = main_window['-CURRENCY-'].get()
        # Individual Score Window
        if isinstance(mw_event, str) and mw_event in pre.ASSESSMENT_PREFIXES:
            # get score from text element 
            if mw_event in pre.KEY_ACCESS:
                assessment_key = pre.KEY_ACCESS[mw_event]
                assessment_value = main_window[assessment_key].DisplayText
            # get score from csv 
            elif mw_event in pre.BINARY_ACCESS:
                assessment_key = pre.BINARY_ACCESS[mw_event]
                if assessment_key   == '-DEVELOPER-':
                    assessment_value = selected_coin[17]
                elif assessment_key == '-COMMUNITY-':
                    assessment_value = selected_coin[18]
                elif assessment_key == '-WHITEPAPER-':
                    assessment_value = selected_coin[19]
                elif assessment_key == '-REGULATORY-':
                    assessment_value = selected_coin[20]
                elif assessment_key == '-CONTRACT-':
                    assessment_value = selected_coin[21]
            
            overlay_win = lod.show_dimmed_overlay()
            # generate Individual Score Window (subs_score_window)
            sub_score_window = rsk.sub_score_window(assessment_key, assessment_value)
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
            main_window.hide()
            current_row = selected_coin
            # generate OAS window
            main_score_window = rsk.main_score_window(chart_data, current_row, selected_coin, data)
            while True:
                event, values = main_score_window.read()
                if event in ('-EXIT-', '-WEXIT-'):
                    main_score_window.close()
                    break
                elif event == '-PRESCRIPTIVE-':
                    query = values[event]
                    print('this is query: ', query)
                    tbl.toggle_table(query, main_score_window, data)
            main_window.UnHide()
            main_window.Maximize()
            
        # Logo click to exit
        elif mw_event in ('-HEADERICON-', 'HEADER'):
            # Stop the timer thread before closing
            stop_event.set()
            if filepath != 'app/assets/data/data.csv':
                os.remove(filepath)
            main_window.close()
            return True
        # Handles table clicks
        elif isinstance(mw_event, str) and mw_event.startswith(pre.TABLE_PREFIXES):
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
                tbl.update_table(main_window, current_page_data, rows_per_page)
                main_window['-PAGENO-'].update(str(current_page))
            # next to load more data from API
            else: 
                # Fetch next set of cryptocurrencies
                try:    
                    current_page += 1
                    stop_event.set()
                    timer_thread.join()
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
                        tbl.update_table(main_window, current_page_data, rows_per_page)
                        main_window['-PAGENO-'].update(str(current_page))
                        stop_event.clear()
                        timer_thread = req.start_timer_thread(main_window, stop_event)
                    else:
                        sg.popup_auto_close('No more cryptocurrencies available.', auto_close_duration=2)
                except Exception as e:
                    fdb.send_automated_report()
        # shift table to the prev 10 entries
        elif mw_event == '-PREV-':
            if current_page > 1:
                current_page -= 1
                current_page_data = calculate_current_entry(current_page, rows_per_page, data)
                tbl.update_table(main_window, current_page_data, rows_per_page)
                main_window['-PAGENO-'].update(str(current_page))
        # combo-box to select currency
        elif mw_event == '-CURRENCY-':
            stop_event.set()
            timer_thread.join()
            overlay_win = lod.show_dimmed_overlay()
            currency = mw_values[mw_event]
            _, data, filepath = lod.login_loading(api_key, api_choice, currency)
            current_page = 1
            current_page_data = calculate_current_entry(current_page, rows_per_page, data)
            tbl.update_table(main_window, current_page_data, rows_per_page)
            main_window['-PAGENO-'].update(str(current_page))        
            overlay_win.close()
            stop_event.clear()
            timer_thread = req.start_timer_thread(main_window, stop_event)
             
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
            tbl.update_table(main_window, current_page_data, rows_per_page)
            main_window['-PAGENO-'].update(str(current_page))
            main_window['-SORT-BY-MSG-'].update('Sort by: Rank')
            
        elif mw_event == '-ALPHA-':
            main_window['-FLAG-'].update(filename=log.flag_image[reverse_flag])
            data.sort(key=lambda x: x[1].lower(), reverse=reverse_flag)
            reverse_flag = not reverse_flag
            current_page = 1
            current_page_data = calculate_current_entry(current_page, rows_per_page, data)
            tbl.update_table(main_window, current_page_data, rows_per_page)
            main_window['-PAGENO-'].update(str(current_page))
            main_window['-SORT-BY-MSG-'].update('Sort by: Alpha')
            
        elif mw_event == '-PRICE-':
            main_window['-FLAG-'].update(filename=log.flag_image[reverse_flag])
            data.sort(key=lambda x: float(x[2].replace(',', '')), reverse=reverse_flag)
            reverse_flag = not reverse_flag
            current_page = 1
            current_page_data = calculate_current_entry(current_page, rows_per_page, data)
            tbl.update_table(main_window, current_page_data, rows_per_page)
            main_window['-PAGENO-'].update(str(current_page))
            main_window['-SORT-BY-MSG-'].update('Sort by: Price')
            

        elif mw_event in ('-SBUTTON-', 'Return', '\r', '\n'):
            stop_event.set()
            timer_thread.join()
            
            search_bar_val = mw_values['-SEARCHBAR-']
            search_query = search_bar_val.strip()

            if not search_query: # Handle empty searches
                continue
            try:
                overlay_win = lod.show_dimmed_overlay()
                search_window, search_terms = lod.search_screen_loading(api_key, api_choice, search_query, currency_choice, filepath)
                log.setup_hover_effects(search_window)
                while True:
                    sw_event, _ = search_window.read()
                    
                    if sw_event == '-CLOSE-':
                        search_window.close()
                        break
                    elif isinstance(sw_event, str) and sw_event.startswith(pre.KEY_PREFIXES):
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
            stop_event.clear()
            timer_thread = req.start_timer_thread(main_window, stop_event)

        elif mw_event in (sg.WIN_CLOSED, 'Exit'):
            # Stop the timer thread before closing
            stop_event.set()
            if filepath != 'app/assets/data/data.csv':
                os.remove(filepath)
            main_window.close()
            return True