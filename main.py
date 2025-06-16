import re
import app
import os
import FreeSimpleGUI as sg

sg.theme('LightGrey1')
sg.theme_button_color(('black', 'gainsboro'))
pattern = re.compile(r'^-(ICON|NAME)(\d+)-$')
cmc_img = './images/resizedCMC.png'
cg_img = './images/resizedCG.png'

current_image = {
    '-IMAGE-': './images/resizedCMC.png',
}
currency_choice = 'USD'

def handle_crypto_toggle(login_window):
    if current_image['-IMAGE-'] == './images/resizedCG.png':
        new_image = cmc_img
    else:
        new_image = cg_img
    login_window['-CRYPTO-LOGO-TOGGLE-'].update(filename=new_image)
    current_image['-IMAGE-'] = new_image

def handle_keystore(login_window):
    imagepath = current_image['-IMAGE-']
    api_choice = app.get_api_choice(imagepath)
    cfg_key = app.get_cfg_key(imagepath)
    new_api_key = app.load_api_key(api_choice, cfg_key)
    print(new_api_key)
    login_window['-API-'].update(value=new_api_key)
    sg.popup_auto_close(f'Pasted the API Key for {'CoinMarketCap' if api_choice == 1 else 'CoinGecko'}', auto_close_duration=2)

def handle_save_key(login_window, lw_values):
    api_key = lw_values.get('-API-', '').strip()
    imagepath = current_image['-IMAGE-']
    api_choice = app.get_api_choice(imagepath)
    cfg_key = app.get_cfg_key(imagepath)
    app.save_api_key(api_choice, api_key, cfg_key)
    sg.popup_auto_close(f'Saved API Key for {api_choice}', auto_close_duration=2)

def handle_confirm(login_window, lw_values):
    api_key = lw_values.get('-API-', '').strip()
    currency_choice = lw_values.get('-CURRENCY-')
    print(f"API Key Entered: '{api_key}'")
    print(f"Currency Choice: '{currency_choice}'")
    api_choice = '1' if current_image['-IMAGE-'] == './images/resizedCMC.png' else '2'
    
    if (api_choice == '1'):
        validity = app.is_valid_cmc_api_key(api_key)
    else:
        validity = app.is_valid_cg_api_key(api_key)

    if not validity and api_choice == '1':
        sg.popup('Please enter a valid API key.')
        return False, None, None, None

    print(validity, api_choice, api_key)
    login_window.hide()
    return True, api_key, api_choice, currency_choice

def handle_main_window_events(main_window, data, current_page, rows_per_page, filepath, api_key, api_choice, currency_choice):
    reverse_flag = True
    while True:
        mw_event, mw_values = main_window.read()
        print(mw_event)

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
            main_window.close()
            return True

        elif mw_event == '-TABLE-':
            selected_row_indices = mw_values['-TABLE-']
            if selected_row_indices:
                selected_index = selected_row_indices[0]
                page_data = app.get_page_data(data, current_page, rows_per_page)
                selected_row = page_data[selected_index]
                current_row = (current_page - 1) * rows_per_page + selected_index
                app.update_risk_window(main_window, selected_row)
                app.risk_assessment_window(main_window, data, current_row)

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
                    print('new_data: ', new_data)
                    if new_data:
                        # creates new csv file with new data
                        app.export_to_csv(new_data)
                        #appends new data to main csv then deletes the created csv file
                        _, new_data_list = app.read_csv('./data/temp.csv')
                        app.append_csv(filepath, new_data_list)
                        print('this is the current data: ', data)

                        _, data = app.read_csv(filepath)
                        main_window['-TABLE-'].update(values=app.get_page_data(data, current_page, rows_per_page))
                        main_window['-PAGENO-'].update(str(current_page))

                        os.remove('./data/temp.csv')  # Clean up temporary file
                    else:
                        sg.popup_auto_close('No more cryptocurrencies available.', auto_close_duration=2)
                except Exception as e:
                    sg.popup_error(f'Error loading more cryptocurrencies: {str(e)}')

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

        elif mw_event == '-SBUTTON-':
            user_search = mw_values['-SEARCHBAR-']
            if user_search == '':
                continue

            search_window, key_to_data = app.search_screen(user_search, filepath)
            while True:
                sw_event, _ = search_window.read()
                if sw_event == '-CBUTTON-':
                    search_window.close()
                elif user_search == '' or sw_event in (sg.WIN_CLOSED, 'Exit'):
                    search_window.close()
                    break
                elif isinstance(sw_event, str):
                    match = pattern.match(sw_event)
                    if match:
                        current_row = int(key_to_data[sw_event][0]) - 1
                        app.update_risk_window(main_window, key_to_data[sw_event])
                        app.risk_assessment_window(main_window, data, current_row)
                        search_window.close()
                        break

        elif mw_event in (sg.WIN_CLOSED, 'Exit'):
            print('closing now')
            main_window.close()
            return True

def main():
    data = []
    current_page = 1
    rows_per_page = 14
    login_window = app.login_screen()
    
    while True:
        lw_event, lw_values = login_window.read()
        print(lw_event, lw_values)

        if lw_event in (sg.WIN_CLOSED, 'Exit'):
            
            break
        elif lw_event == '-CRYPTO-LOGO-TOGGLE-':
            handle_crypto_toggle(login_window)
        elif lw_event == '-KEYSTORE-':
            handle_keystore(login_window)
        elif lw_event == '-SAVEKEY-':
            handle_save_key(login_window, lw_values)
        elif lw_event == 'Clear':
            login_window['-API-'].update('')
        elif lw_event == 'Confirm':
            success, api_key, api_choice, currency_choice = handle_confirm(login_window, lw_values)
            if success:
                result = app.login_loading(api_key, api_choice, currency_choice)    

                if not result or not isinstance(result, tuple) or len(result) != 3:
                    sg.popup("Unexpected API response. Please try again.")
                    login_window.un_hide()
                    continue
                headings, data, filepath = result   
                
                main_window = app.main_screen(headings, data, current_page, rows_per_page)
                print('Data fetched successfully')
                if handle_main_window_events(main_window, data, current_page, rows_per_page, filepath, api_key, api_choice, currency_choice):
                    login_window.un_hide()
        elif lw_event == '-HELP-':
            sg.popup('Your API Key allows the app to access data from providers like CoinGecko or CoinMarketCap. Keep it private.')

    login_window.close()

if __name__ == '__main__':
    main()
