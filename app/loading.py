import threading
import FreeSimpleGUI as sg
from . import request_api as req
from . import search_screen as ssc
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

def show_throbber(location=(None, None), gif_filename='app/assets/images/spin.gif'):
    """
    Create and return a throbber (loading spinner) window with animated GIF.

    Args:
        location (tuple): Screen coordinates for window placement.
        gif_filename (str): Path to the spinner GIF file.

    Returns:
        tuple: (sg.Window object, list of GIF frames in bytes)
    """
    layout = [[sg.Image(key='-GIF-')]]

    try:
        gif = Image.open(gif_filename)
        frames = [f.convert("RGBA") for f in ImageSequence.Iterator(gif)]

        byte_frames = []
        for frame in frames:
            # Create a clean background
            background = Image.new("RGBA", gif.size, (255, 255, 255, 255))  # White opaque background
            background.paste(frame, (0, 0), mask=frame)
            with io.BytesIO() as output:
                background.save(output, format="PNG")
                byte_frames.append(output.getvalue())

        if location == (None, None):
            gif_width, gif_height = gif.size
            screen_width, screen_height = sg.Window.get_screen_size()
            location = (
                screen_width // 2 - gif_width // 2,
                screen_height // 2 - gif_height // 2
            )

    except Exception as e:
        print(f"[Throbber Error] Failed to load GIF: {e}")
        byte_frames = []

    # Use solid white background — avoid transparency entirely
    window = sg.Window(
        '',
        layout,
        location=location,
        finalize=True,
        keep_on_top=True,
        no_titlebar=True,
        background_color='white',  # match our GIF frame background
        element_padding=(0, 0),
        margins=(0, 0)
    )

    return window, byte_frames



# Main wrapper function
def login_loading(api_key, api_choice, currency_choice='USD'):
    result_holder = {}
    progress_holder = {'value': 0, 'status': 'Initializing...'}

    # Create and show the loading screen
    screen_width, screen_height = sg.Window.get_screen_size()
    window_width, window_height = 400, 120 
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

def search_screen_loading(api_key, api_choice, search_query, currency_choice, filepath):
    # store return values 
    result_holder = {}

    # GIF animation setup 
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
    # Render throbber gif
    throbber_win, byte_frames = show_throbber(location=win_location)

    # Background thread for search
    def target():
        try:
            result_holder['value'] = ssc.search_window(api_key, api_choice, search_query, currency_choice, filepath)
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

    if 'error' in result_holder:
        print('nom nom')
        raise result_holder['error']

    search_win_layout, search_terms = result_holder.get('value', (None, None))
    search_window = sg.Window('Search Result', search_win_layout, size=(540, 565), keep_on_top=True, modal=True, no_titlebar=True, finalize=True)
    return search_window, search_terms
