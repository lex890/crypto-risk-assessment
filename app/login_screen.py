import FreeSimpleGUI as sg

def login_screen(api_choice):
    layout = [
        # logo and main heading
        [
            sg.Image(filename='app/assets/images/resizedLogo.png', size=(50, 50)),
            sg.Text('Crypto Fraud Detection Tool', font=('Helvetica', 20), pad=(10, 30))
        ],
        
        [
            sg.Text('API Key', font=('League Spartan', 12), pad=((180, 0), (50, 0)))
        ],

        [
            sg.Push(),
            sg.InputText(key='-API-', size=(40, 2), font=('Helvetica', 12), tooltip='Enter API Key', default_text='', pad=((20, 0), (0, 0))),
            sg.Image(filename='app/assets/images/CMC.png', size=(50, 50), enable_events=True, key='-CRYPTO-LOGO-TOGGLE-', tooltip='Select your API key provider.'),
            sg.Image(filename='app/assets/images/tool-tip.png', size=(20, 20), enable_events=True, key='-HELP-', tooltip='What is an API Key?',
            pad=((0, 0), (0, 45))),
            sg.Push()
        ],

        [
            sg.Text('Enter your API key to access the service.', font=('Helvetica', 10),
                    pad=((176, 0), (0, 0))),
        ],

        [
            sg.Button('Clear', size=(10, 1), pad=((360, 0), (0, 0))),
            sg.Button('Confirm', size=(10, 1), pad=(5, 20))
        ],

        [
            sg.Push(),
            sg.Button(
                f'\n\n\nPaste Key',
                image_filename='app/assets/images/keystore.png',
                image_size=(75, 75),
                button_color=("black", sg.theme_background_color()),
                border_width=0,
                key='-KEYSTORE-',
                pad=((0, 0), (35, 0)),
                tooltip=f'Paste API Key {api_choice}'
            ),
            sg.Button(
                f'\n\n\nSave Key',
                image_filename='app/assets/images/save-key.png',
                image_size=(75, 75),
                button_color=("black", sg.theme_background_color()),
                border_width=0,
                key='-SAVEKEY-',
                pad=((10, 0), (35, 0)),
                tooltip='Save the API key'
            ),
            sg.Button(
                f'\n\n\nDemo Mode',
                image_filename='app/assets/images/demo-image.png',
                image_size=(75, 75),
                button_color=("black", sg.theme_background_color()),
                border_width=0,
                key='-DEMOMODE-',
                pad=((10, 0), (35, 0)),
                tooltip='Demo Mode'
            )
        ],

    ]

    return sg.Window('Crypto Fraud Detection Tool', layout, size=(800, 450))





  

