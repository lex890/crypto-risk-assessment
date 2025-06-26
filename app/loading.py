import threading
import FreeSimpleGUI as sg
from . import request_api as req
from .search_screen import search_screen
from PIL import Image, ImageSequence
import io

def show_dimmed_overlay():
    screen_width, screen_height = sg.Window.get_screen_size()
    print(screen_width, 'x', screen_height)
    layout = [[sg.Text('', size=(1, 1))]]
    return sg.Window(
        '',
        layout,
        no_titlebar=True,
        alpha_channel=0.4,
        grab_anywhere=False,
        background_color='black',
        transparent_color=None,
        element_padding=(0, 0),
        margins=(0, 0),
        location=(0, 0),  # Always top-left because the window size is supposed to be the entire screen
        size=(screen_width, screen_height),
        resizable=False,
        modal=True,
        finalize=True
    )

# Loading screen window
def show_loading_window(location=None):
    layout = [
        [sg.Text('Contacting API...', font=('Helvetica', 14))],
        [sg.ProgressBar(100, orientation='h', size=(30, 20), key='-PROG-')],
        [sg.Text('', key='-STATUS-', font=('Helvetica', 10))]
    ]
    return sg.Window('Loading', layout, finalize=True, keep_on_top=True, no_titlebar=True, location=location)

def show_throbber(location=(None, None)):
    layout = [
        [sg.Image(key='-GIF-')]
    ]
    return sg.Window('', layout, location=location, finalize=True, keep_on_top=True, no_titlebar=True, transparent_color=sg.theme_background_color(), background_color=sg.theme_background_color(), element_padding=(0,0), margins=(0,0))

# Main wrapper function
def login_loading(api_key, api_choice, currency_choice):
    result_holder = {}
    progress_holder = {'value': 0, 'status': 'Initializing...'}

    # Create and show the loading screen first
    screen_width, screen_height = sg.Window.get_screen_size()
    window_width, window_height = 400, 120  # Approximate size of your loading window
    center_x = (screen_width - window_width) // 2
    center_y = (screen_height - window_height) // 2

    loading_win = show_loading_window(location=(center_x, center_y))
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
    screen_width, screen_height = sg.Window.get_screen_size()
    window_width, window_height = 400, 120
    center_x = (screen_width - window_width) // 2
    center_y = (screen_height - window_height) // 2

    loading_win = show_loading_window(location=(center_x, center_y))
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

def search_screen_loading(main_window, data, current_page, rows_per_page, user_search, filepath, api_key, currency_choice):
    result_holder = {}

    overlay_win = show_dimmed_overlay()

    # --- GIF animation setup ---
    gif_filename = 'app/assets/images/spin.gif'
    win_location = (None, None)
    try:
        gif = Image.open(gif_filename)
        gif_width, gif_height = gif.size
        screen_width, screen_height = sg.Window.get_screen_size()
        win_location = (screen_width // 2 - gif_width // 2, screen_height // 2 - gif_height // 2)
        frames = [f.copy() for f in ImageSequence.Iterator(gif)]
        # Convert frames to bytes
        byte_frames = []
        for frame in frames:
            with io.BytesIO() as output:
                frame.save(output, format="PNG")
                byte_frames.append(output.getvalue())
        frame_index = 0
    except Exception as e:
        print(f"Error loading GIF: {e}")
        byte_frames = []

    throbber_win = show_throbber(location=win_location)

    # Background thread for search
    def target():
        try:
            result_holder['value'] = search_screen(main_window, data, current_page, rows_per_page, user_search, filepath, api_key, currency_choice)
        except Exception as e:
            result_holder['error'] = e

    thread = threading.Thread(target=target, daemon=True)
    thread.start()

    # --- Animation loop ---
    while thread.is_alive():
        event, _ = throbber_win.read(timeout=50) # Timeout controls frame rate

        if byte_frames:
            # Update image with next frame
            throbber_win['-GIF-'].update(data=byte_frames[frame_index])
            frame_index = (frame_index + 1) % len(byte_frames)
        
        if event == sg.WIN_CLOSED:
            break

    throbber_win.close()
    overlay_win.close()

    if 'error' in result_holder:
        raise result_holder['error']

    search_window, key_to_data = result_holder.get('value', (None, None))
    return search_window, key_to_data