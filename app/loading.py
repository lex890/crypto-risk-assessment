import threading
import time
import FreeSimpleGUI as sg
from . import request_api as req

# Loading screen window
def show_loading_window():
    layout = [
        [sg.Text('Contacting API...', font=('Helvetica', 14))],
        [sg.ProgressBar(100, orientation='h', size=(30, 20), key='-PROG-')],
        [sg.Text('', key='-STATUS-', font=('Helvetica', 10))]
    ]
    return sg.Window('Loading', layout, finalize=True, keep_on_top=True, no_titlebar=True)

def show_dimmed_overlay():
    # Simulates dimming by showing a transparent black window in the background
    layout = [[sg.Text('', size=(1, 1))]]
    return sg.Window(
        '',
        layout,
        no_titlebar=True,
        alpha_channel=0.3,  # Semi-transparent
        keep_on_top=False,
        finalize=True,
        grab_anywhere=False,
        background_color='black',
        transparent_color=None,
        element_padding=(0, 0),
        margins=(0, 0),
        size=(sg.Window.get_screen_size())
    )

# Main wrapper function
def login_loading(api_key, api_choice, currency_choice):
    result_holder = {}
    progress_holder = {'value': 0, 'status': 'Initializing...'}

    # Create and show the loading screen first
    loading_win = show_loading_window()
    prog_bar = loading_win['-PROG-']
    status_text = loading_win['-STATUS-']

    # Background API thread
    def target():
        try:
            # Create a progress callback function
            def update_progress(progress, status):
                progress_holder['value'] = progress
                progress_holder['status'] = status

            result_holder['value'] = req.api_request(api_key, api_choice, currency_choice, progress_callback=update_progress)
        except Exception as e:
            result_holder['error'] = e

    # Delay thread start to let GUI fully render one cycle
    thread_started = False

    while True:
        event, _ = loading_win.read(timeout=100)
        
        # Update progress bar and status text
        prog_bar.UpdateBar(progress_holder['value'])
        status_text.update(progress_holder['status'])

        if not thread_started:
            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread_started = True

        if not thread.is_alive():
            break

        if event == sg.WIN_CLOSED:
            break

    loading_win.close()

    if 'error' in result_holder:
        raise result_holder['error']

    return result_holder['value']  # => (headings, data, filename)
    
def next_screen_loading(data, api_key, api_choice, currency_choice):
    result_holder = {}
    progress_holder = {'value': 0, 'status': 'Initializing...'}

    # Create and show the loading screen
    overlay_win = show_dimmed_overlay()
    loading_win = show_loading_window()
    prog_bar = loading_win['-PROG-']
    status_text = loading_win['-STATUS-']

    # Background thread for fetching new data
    def target():
        try:
            # Create a progress callback function
            def update_progress(progress, status):
                progress_holder['value'] = progress
                progress_holder['status'] = status

            result_holder['new_data'] = req.fetch_next_cryptocurrencies(
                len(data), 
                api_key, 
                api_choice, 
                currency_choice,
                progress_callback=update_progress
            )
        except Exception as e:
            result_holder['error'] = e

    thread_started = False

    while True:
        event, _ = loading_win.read(timeout=100)
        
        # Update progress bar and status text
        prog_bar.UpdateBar(progress_holder['value'])
        status_text.update(progress_holder['status'])

        if not thread_started:
            thread = threading.Thread(target=target, daemon=True)
            thread.start()
            thread_started = True

        if not thread.is_alive():
            break

        if event == sg.WIN_CLOSED:
            break

    loading_win.close()
    overlay_win.close()

    if 'error' in result_holder:
        raise result_holder['error']

    return result_holder['new_data']


    