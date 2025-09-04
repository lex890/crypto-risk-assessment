import FreeSimpleGUI as sg
from . import request_api as req
from . import keystore as key
from . import csv_handler as csv
from . import main_screen as msc
from . import loading as ldg
from . import prefix as pre
import webbrowser
sg.theme('LightGrey1')
flag_image = {
    True: 'app/assets/images/arrow-up-small.png',
    False: 'app/assets/images/arrow-down-small.png'
}

def handle_crypto_toggle(login_window):
    """
    Toggle the crypto provider selection between CoinMarketCap and CoinGecko,
    and update the UI elements accordingly.

    Args:
        login_window (PySimpleGUI.Window): The GUI window instance containing input elements.
    """
    # Check the current selection and determine the new values
    if login_window['-CRYPTO-NAME-TOGGLE-'].get() == 'CoinGecko':
        new_image = 'app/assets/images/CMC.png'
        new_name = 'CoinMarketCap'
        new_color = 'blue'  # CMC → blue
    else:
        new_image = 'app/assets/images/CG.png'
        new_name = 'CoinGecko'
        new_color = 'green'  # CG → green

    # Update the crypto logo image
    login_window['-CRYPTO-LOGO-TOGGLE-'].update(filename=new_image)
    # Update the toggle button with new name and color
    login_window['-CRYPTO-NAME-TOGGLE-'].update(value=new_name, text_color=new_color)
    api_choice = login_window['-CRYPTO-NAME-TOGGLE-'].get()
    # Clear any change message
    login_window['-CHANGE-MSG-'].update(value='')
    return api_choice

def link_to_website(api_choice):
    """
    Open the default web browser to the API key signup page for the selected API provider.

    Args:
        api_choice (str): The name of the selected API provider. Expected values are
                          'CoinMarketCap' or anything else (defaults to CoinGecko).
    """
    # Open the CoinMarketCap API signup page if selected
    if api_choice == 'CoinMarketCap':
        webbrowser.open('https://coinmarketcap.com/api/')
    else:
        # Default to CoinGecko API signup page
        webbrowser.open('https://www.coingecko.com/en/api')

def handle_save_key(login_window):
    """
    Save the API key locally based on the selected crypto data provider.

    Args:
        login_window (PySimpleGUI.Window): The GUI window instance containing input elements.
    """
    # Retrieve the trimmed API key from the input field
    api_key = login_window['-API-'].get().strip()

    # Determine the correct image path based on the selected provider
    imagepath = 'app/assets/images/CMC.png' if login_window['-CRYPTO-NAME-TOGGLE-'].get() == 'CoinMarketCap' else 'app/assets/images/CG.png'

    # Get the API identifier based on the image path
    api_choice = req.get_api_choice(imagepath)
    # Get the config key name for storing the API key
    cfg_key = key.get_cfg_key(imagepath)
    # Save the API key using the application logic
    key.save_api_key(api_choice, api_key, cfg_key)
    # Notify the user with a short popup
    sg.popup_auto_close(f'Saved API Key for {api_choice}', auto_close_duration=2)

def handle_confirm(login_window, lw_values):
    """
    Handle the confirmation of the API key input.

    Checks the selected API source (CoinMarketCap or CoinGecko), validates
    the provided API key accordingly, and returns the result along with
    the selected API choice.

    Parameters:
        login_window: The PySimpleGUI window object containing UI elements.
        lw_values: Dictionary of input values from the login window.

    Returns:
        tuple:
            - success (bool): True if the API key is valid, False otherwise.
            - api_key (str or None): The validated API key if successful.
            - api_choice (str or None): '1' for CoinMarketCap, '2' for CoinGecko.
    """
    api_key = lw_values.get('-API-', '').strip()
    api_choice = '1' if login_window['-CRYPTO-NAME-TOGGLE-'].get() == 'CoinMarketCap' else '2'
    
    if (api_choice == '1'):
        validity = req.is_valid_cmc_api_key(api_key)
    else:
        validity = req.is_valid_cg_api_key(api_key)

    if not validity:
        sg.popup('Please enter a valid API key.')
        return False, None, None

    return True, api_key, api_choice

def setup_hover_effects(window):
    root = window.TKroot
    hovery(window, pre.KEY_PREFIXES, root)

def hovery(main_window, key_prefixes: tuple, root):
    """Bind <Enter>/<Leave> so the mouse becomes a hand on hover"""
    for key, element in main_window.key_dict.items():
        if isinstance(key, str) and key.startswith(key_prefixes):
            widget = element.Widget

            # cursor='hand2' on Windows/macOS/X11‑GTK ‑‑ standard hyperlink hand
            widget.bind('<Enter>',
                        lambda e, w=root: w.configure(cursor='hand2'))
            widget.bind('<Leave>',
                        lambda e, w=root: w.configure(cursor='arrow'))

def demo_mode_handler(login_window, current_page, rows_per_page):
    """
    Handle the logic for launching the application in demo mode.

    Args:
        login_window (PySimpleGUI.Window): The login window instance.
        current_page (int): The current page number for pagination.
        rows_per_page (int): Number of rows to display per page.

    Returns:
        None
    """
    # Hide the login window while in demo mode
    login_window.hide()

    # Load demo data and default API key
    filepath = 'app/assets/data/data.csv'
    api_key = key.load_api_key()
    api_choice = '1'  # Default to CoinMarketCap

    # Read the CSV data
    headings, data = csv.read_csv(filepath)

    # Create the main screen with demo data
    main_window = msc.main_window(data)

    # Handle events on the main screen; if user exits, show login window again
    if msc.main_window_handler(main_window, headings, data, current_page, rows_per_page, filepath, api_key, api_choice):
        login_window.un_hide()

def handle_confirm_event(login_window, lw_values, current_page, rows_per_page):
    success, api_key, api_choice = handle_confirm(login_window, lw_values)
    if success:
        login_window.hide()
        result = ldg.login_loading(api_key, api_choice)    
        # Check if result is a tuple
        if not result or not isinstance(result, tuple) or len(result) != 3:
            sg.popup("Unexpected API response. Please try again.")
            login_window.un_hide()
            return False
        # Unpack the tuple
        headings, data, filepath = result
        main_window = msc.main_window(data)
        if msc.main_window_handler(main_window, headings, data, current_page, rows_per_page, filepath, api_key, api_choice):
            login_window.un_hide()
        return True
    return False

def generate_login_window(api_choice):
    lower_msg_box = [
        [
            sg.Text(
                'CoinMarketCap',
                key='-CRYPTO-NAME-TOGGLE-',
                font=('Helvetica', 16),
                pad=((0, 0), (0, 0)),
                enable_events=True,
                tooltip='Click here to get your API Key.',
                text_color='blue'
            ),
            sg.Push()
        ],
        [
            sg.Text(
                'Click here to get your API Key.',
                key='-CRYPTO-LINKER-',
                font=('Helvetica', 8, 'bold'),
                pad=((0, 0), (0, 0)),
                enable_events=True
            ),
            sg.Push()
        ]
    ]

    login_buttons = [
        [
            sg.Button(
                f'\n\n\nPaste Key',
                image_filename='app/assets/images/keystore.png',
                image_size=(75, 75),
                button_color=("#808080", sg.theme_background_color()),
                border_width=0,
                key='-KEYSTORE-',
                pad=((0, 0), (35, 5)),
                tooltip=f'Paste API Key {api_choice}',
                font=('Helvetica', 10, 'bold') 
            ),
            sg.Button(
                f'\n\n\nSave Key',
                image_filename='app/assets/images/save-key.png',
                image_size=(75, 75),
                button_color=("#808080", sg.theme_background_color()),
                border_width=0,
                key='-SAVEKEY-',
                pad=((10, 0), (35, 5)),
                tooltip='Save the API key',
                font=('Helvetica', 10, 'bold') 
            ),
            sg.Button(
                f'\n\n\nDemo Mode',
                image_filename='app/assets/images/demo-image.png',
                image_size=(75, 75),
                button_color=("#808080", sg.theme_background_color()),
                border_width=0,
                key='-DEMOMODE-',
                pad=((10, 10), (35, 5)),
                font=('Helvetica', 10, 'bold'),
                tooltip='Demo Mode'
            )
        ]
    ]
    
    layout = [
        # logo and main heading
        [
            sg.Image(filename='app/assets/images/resizedLogo.png', size=(50, 50), pad=((30, 10), 0)),
            sg.Text('Blockchain Risk Assessment Tool', font=('Gotham', 20), pad=(0, 30))
        ],
        [sg.VPush()],
        [
            sg.Push(),
            sg.Text('Click the icon to switch API', font=('Helvetica', 8, 'bold'), pad=((300, 0), (30, 0)), key='-CHANGE-MSG-'),
            sg.Push()
        ],
            
        [
            sg.Push(),
            sg.Image(filename='app/assets/images/tool-tip.png', size=(20, 20), enable_events=True, key='-HELP-', tooltip='What is an API Key?',
            pad=((0, 6), (0, 0))),
            sg.Text('Enter API key to access the service.', font=('Helvetica', 12, 'bold'), pad=((0, 110), (0, 0))),
            sg.Push()
        ],
        [
            sg.Push(),
            sg.InputText(key='-API-', size=(30, 1), font=('Helvetica', 16), tooltip='Enter API Key', default_text='', pad=((20, 0), (0, 0))),
            sg.Image(filename='app/assets/images/CMC.png', size=(50, 50), enable_events=True, key='-CRYPTO-LOGO-TOGGLE-', tooltip='Select your API key provider.', pad=((10, 0), (0, 0))),
            sg.Push()
        ],

        [
            sg.Push(),
            sg.Button('Clear', size=(10, 1), pad=((142, 0), (0, 0)), font=('Gotham', 10, 'bold'), border_width=0, button_color=("#E8F9FD", '#FF1E00')),
            sg.Button('Confirm', size=(10, 1), pad=((8, 0), (0, 0)), font=('Gotham', 10, 'bold'), border_width=0, button_color=("#E8F9FD", '#59CE8F')),
            sg.Push()
        ],
        [
            sg.Checkbox('Auto-update on Price change', pad=((190, 0), (0, 0)), key='-TOGGLE-UPDATE-', visible=False),
            sg.Push(),
        ],
        [
            sg.Combo(['60', '120', '300', '600'], default_value='60', pad=((195, 0), (0, 0)), key='-SECONDS-', visible=False, readonly=True),
            sg.Text('Seconds', visible=False),
            sg.Push(),
        ],
        

        [sg.VPush()],
        [
            sg.Column(lower_msg_box, pad=((10, 0), (40, 0))),
            sg.Push(),
            sg.Column(login_buttons, pad=((0, 0),(0, 0)))
        ],

    ]

    return sg.Window('Blockchain Risk Assessment Tool', layout, size=(800, 450), finalize=True)

def run_app():
    current_page = 1
    rows_per_page = 10
    api_choice = 'CoinMarketCap'
    login_window = generate_login_window(api_choice)

    setup_hover_effects(login_window)
    while True:
        lw_event, lw_values = login_window.read()
        check_box_val = login_window['-TOGGLE-UPDATE-'].get()
        seconds_val = login_window['-SECONDS-'].get()
        if lw_event in (sg.WIN_CLOSED, 'Exit'):
            break
        elif lw_event == '-CRYPTO-LOGO-TOGGLE-':
           api_choice = handle_crypto_toggle(login_window)           
        elif lw_event == '-CRYPTO-NAME-TOGGLE-' or lw_event == '-CRYPTO-LINKER-':
            link_to_website(api_choice)
        elif lw_event == '-KEYSTORE-':
            key.handle_keystore(login_window)
        elif lw_event == '-SAVEKEY-':  
            handle_save_key(login_window)            
        elif lw_event == 'Clear':
            login_window['-API-'].update('')
        elif lw_event == 'Confirm':
            handle_confirm_event(login_window, lw_values, current_page, rows_per_page)
        elif lw_event == '-DEMOMODE-':
            demo_mode_handler(login_window, current_page, rows_per_page)
        elif lw_event == '-HELP-':
            sg.popup('Your API Key allows the app to access data from providers like CoinGecko or CoinMarketCap. Keep it private.')

    login_window.close()


  

