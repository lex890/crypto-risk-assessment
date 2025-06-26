import re
import app
import os
import webbrowser
import FreeSimpleGUI as sg
import ctypes

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    ctypes.windll.user32.SetProcessDPIAware()

sg.theme('GrayGrayGray')
sg.theme_button_color(('black', 'gainsboro'))

pattern = re.compile(r'^-(ICON|NAME)(\d+)-$')
cmc_img = 'app/assets/images/CMC.png'
cg_img = 'app/assets/images/CG.png'

current_image = {
    '-IMAGE-': cmc_img
}
currency_choice = 'USD'
select_entry = 0

screen_width, screen_height = sg.Window.get_screen_size()

def handle_crypto_toggle(login_window):
    if current_image['-IMAGE-'] == cg_img:
        new_image = cmc_img
        new_name = 'CoinMarketCap'
    else:
        new_image = cg_img
        new_name = 'CoinGecko'
    login_window['-CRYPTO-LOGO-TOGGLE-'].update(filename=new_image)
    login_window['-CRYPTO-NAME-TOGGLE-'].update(value=new_name)
    current_image['-IMAGE-'] = new_image
    print(current_image['-IMAGE-'])



def handle_save_key(lw_values):
    api_key = lw_values.get('-API-', '').strip()
    imagepath = current_image['-IMAGE-']
    api_choice = app.get_api_choice(imagepath)
    cfg_key = app.get_cfg_key(imagepath)
    app.save_api_key(api_choice, api_key, cfg_key)
    sg.popup_auto_close(f'Saved API Key for {api_choice}', auto_close_duration=2)

def link_to_website(api_choice):
    print(api_choice)
    if api_choice == 'CoinMarketCap':
        webbrowser.open('https://coinmarketcap.com/api/')
    else:
        webbrowser.open('https://www.coingecko.com/en/api')

def handle_confirm(login_window, lw_values):
    api_key = lw_values.get('-API-', '').strip()
    print(f"API Key Entered: '{api_key}'")
    api_choice = '1' if current_image['-IMAGE-'] == cmc_img else '2'
    
    if (api_choice == '1'):
        validity = app.is_valid_cmc_api_key(api_key)
    else:
        validity = app.is_valid_cg_api_key(api_key)

    if not validity and api_choice == '1':
        sg.popup('Please enter a valid API key.')
        return False, None, None

    print(validity, api_choice, api_key)
    return True, api_key, api_choice

def handle_main_window_events(main_window, data, current_page, rows_per_page, filepath, api_key, api_choice):
    global currency_choice
    global select_entry
    reverse_flag = True
    while True:
        mw_event, mw_values = main_window.read()
        if mw_event == '-SCORE-CLICKED-':
            key = mw_values[mw_event]
            if key in app.descriptions:
                title, msg = app.descriptions[key]
                sg.popup(title, msg, title=title, font=("Helvetica", 12), keep_on_top=True)

        elif mw_event == '-MAIN-CLICKED-':
            sg.Window(
                "Risk Score Guide",
                [
                    [sg.Text("Score Interpretation", font=("Helvetica", 14, "bold"))],
                    [sg.Text("1 - 3   : High-Risk/Fraudulent (Avoid)", text_color="red", font=("Calibri", 10, "bold"))],
                    [sg.Text("4 - 6   : Medium Risk (Caution)", text_color="orange", font=("Calibri", 10, "bold"))],
                    [sg.Text("7 - 10  : Trustworthy (Safe to interact with)", text_color="green", font=("Calibri", 10, "bold"))],
                    [sg.Button("OK", size=(10, 1))]
                ],
                modal=True,
                keep_on_top=True
            ).read(close=True)

        elif mw_event in ('-HEADERICON-', 'HEADER'):
            if filepath != 'app/assets/data/data.csv':
                os.remove(filepath)
            main_window.close()
            return True

        elif mw_event == '-TABLE-':
            selected_row_indices = mw_values['-TABLE-']
            if selected_row_indices:
                selected_index = selected_row_indices[0]
                page_data = app.get_page_data(data, current_page, rows_per_page)
                selected_row = page_data[selected_index]
                current_row = (current_page - 1) * rows_per_page + selected_index
                app.update_risk_window(main_window, selected_row, currency_choice)
                app.risk_assessment_window(main_window, data, current_row)
                select_entry = current_row
        elif mw_event == '-CURRENCY-':
            new_currency_choice = mw_values[mw_event]
            current_csv = filepath
            app.currency_conversion(current_csv, currency_choice, new_currency_choice)
            currency_choice = new_currency_choice
            print('this is new:', currency_choice)
            _, data = app.read_csv(filepath)
            main_window['-TABLE-'].update(
                values=app.get_page_data(data, current_page, rows_per_page))
            main_window['-PAGENO-'].update('1')
            main_window['-PRICE-LABEL-'].update(f'Price ({currency_choice}): {data[select_entry][2]}')
            main_window['-MCAP-LABEL-'].update(f'Market Cap ({currency_choice}): {data[select_entry][6]}')
             
        elif mw_event == '-HYPERLINK-':
            webbrowser.open(data[select_entry][11])  # Replace with your URL

        elif mw_event == '-FEEDBACK-ICON-':
            if app.feedback_screen():
                sg.popup('Feedback submitted successfully!', title='Thank you for your feedback.')

        elif mw_event == '-NEXT-':
            max_pages = (len(data) - 1) // rows_per_page + 1

            if current_page < max_pages:
                current_page += 1
                main_window['-TABLE-'].update(values=app.get_page_data(data, current_page, rows_per_page))
                main_window['-PAGENO-'].update(str(current_page))
            else:
                # Fetch next set of cryptocurrencies
                try:    
                    current_page += 1
                    new_data = app.next_screen_loading(data, api_key, api_choice, currency_choice)
                    print('new_data: ', new_data, type(new_data))
                    if new_data:
                        # creates new csv file with new data
                        app.export_to_csv(new_data)
                        #appends new data to main csv then deletes the created csv file
                        _, new_data_list = app.read_csv('app/assets/data/temp.csv')
                        app.append_csv(filepath, new_data_list)
                        print('this is the current data: ', data)

                        _, data = app.read_csv(filepath)
                        main_window['-TABLE-'].update(values=app.get_page_data(data, current_page, rows_per_page))
                        main_window['-PAGENO-'].update(str(current_page))
                    else:
                        sg.popup_auto_close('No more cryptocurrencies available.', auto_close_duration=2)
                except Exception as e:
                    app.send_automated_report()

        elif mw_event == '-PREV-':
            if current_page > 1:
                current_page -= 1
                main_window['-TABLE-'].update(values=app.get_page_data(data, current_page, rows_per_page))
                main_window['-PAGENO-'].update(str(current_page))
        elif mw_event == '-NUMBER-':
            data.sort(key=lambda x: int(x[0]), reverse=reverse_flag)
            reverse_flag = not reverse_flag
            main_window['-TABLE-'].update(values=data)
            main_window['-PAGENO-'].update('1')
        elif mw_event == '-ALPHA-':
            data.sort(key=lambda x: x[1], reverse=reverse_flag)
            reverse_flag = not reverse_flag
            main_window['-TABLE-'].update(values=data)
            main_window['-PAGENO-'].update('1')
        elif mw_event == '-PRICE-':
            data.sort(key=lambda x: float(x[2].replace(',', '')), reverse=reverse_flag)
            reverse_flag = not reverse_flag
            main_window['-TABLE-'].update(values=data)
            main_window['-PAGENO-'].update('1')

        elif mw_event in ('-SBUTTON-', 'Return', '\r', '\n'):
            user_search = mw_values['-SEARCHBAR-']
            if user_search == '':
                continue
            search_window, key_to_data = app.search_screen_loading(main_window, data, current_page, rows_per_page, user_search, filepath, api_key, currency_choice)
            while True:
                sw_event, _ = search_window.read()
                if sw_event == '-CBUTTON-':
                    search_window.close()
                elif user_search == '' or sw_event in (sg.WIN_CLOSED, 'Exit'):
                    search_window.close()
                    break
                elif isinstance(sw_event, str): # image or logo clicked
                    match = pattern.match(sw_event)
                    print('match: ', match)
                    if match:
                        _, data = app.read_csv(filepath)
                        print('this is data: ', data)
                        current_row = int(key_to_data[sw_event][0]) - 1
                        if current_row > len(data):
                            current_row = -1

                        print('this is current row', current_row)
                        app.update_risk_window(main_window, data[current_row], currency_choice)
                        app.risk_assessment_window(main_window, data, current_row)
                        search_window.close()
                        break
                    else:
                        sg.popup('This is from API')

        elif mw_event in (sg.WIN_CLOSED, 'Exit'):
            print('closing now')
            if filepath != 'app/assets/data/data.csv':
                os.remove(filepath)
            main_window.close()
            return True

def main():
    data = []
    current_page = 1
    rows_per_page = 14
    api_choice = 'CoinMarketCap'
    login_window = app.login_screen(api_choice)
    
    while True:
        lw_event, lw_values = login_window.read()
        print(lw_event, lw_values)

        if lw_event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif lw_event == '-CRYPTO-LOGO-TOGGLE-':
            handle_crypto_toggle(login_window)
            api_choice = 'CoinMarketCap' if current_image['-IMAGE-'] == 'app/assets/images/CMC.png' else 'CoinGecko'
        elif lw_event == '-CRYPTO-NAME-TOGGLE-':
            print(current_image)
            link_to_website(api_choice)
        elif lw_event == '-KEYSTORE-':
            app.handle_keystore(login_window, current_image)
        elif lw_event == '-SAVEKEY-':
            handle_save_key(lw_values)
        elif lw_event == 'Clear':
            login_window['-API-'].update('')
        elif lw_event == 'Confirm':
            success, api_key, api_choice = handle_confirm(login_window, lw_values)
            if success:
                login_window.hide()
                result = app.login_loading(api_key, api_choice, currency_choice)    

                if not result or not isinstance(result, tuple) or len(result) != 3:
                    sg.popup("Unexpected API response. Please try again.")
                    login_window.un_hide()
                    continue
                headings, data, filepath = result
                main_window = app.main_screen_handler(headings, data, current_page, rows_per_page)
                print('Data fetched successfully')
                if handle_main_window_events(main_window, data, current_page, rows_per_page, filepath, api_key, api_choice):
                    login_window.un_hide()
        elif lw_event == '-DEMOMODE-':
            login_window.hide()
            filepath = 'app/assets/data/data.csv'
            api_key = ''
            api_choice = ''
            headings, data = app.read_csv(filepath)
            main_window = app.main_screen_handler(headings, data, current_page, rows_per_page)
            
            if handle_main_window_events(main_window, data, current_page, rows_per_page, filepath, api_key, api_choice):
                login_window.un_hide()
        elif lw_event == '-HELP-':
            sg.popup('Your API Key allows the app to access data from providers like CoinGecko or CoinMarketCap. Keep it private.')

    login_window.close()

if __name__ == '__main__':
    main()
