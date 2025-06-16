import FreeSimpleGUI as sg

def login_screen():
    layout = [
        # logo and main heading
        [
            sg.Image(filename='./images/resizedLogo.png', size=(50, 50)),
            sg.Text('Crypto Fraud Detection Tool', font=('Helvetica', 20), pad=(10, 30))
        ],
        
        [
            sg.Text('API Key', font=('League Spartan', 12), pad=((180, 0), (50, 0))),
            sg.Text('Select Currency', font=('Helvetica', 12), pad=((136, 0), (50, 0))),
            sg.Combo(['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'PHP'], default_value='USD', key='-CURRENCY-', pad=((5, 0), (50, 0)), tooltip='Select Currency')
        ],

        [
            sg.Push(),
            sg.InputText(key='-API-', size=(40, 1), font=('Helvetica', 12), tooltip='Enter API Key', default_text='', pad=((20, 0), (0, 0))),
            sg.Image(filename='./images/resizedCMC.png', size=(50, 50), enable_events=True, key='-CRYPTO-LOGO-TOGGLE-', tooltip='Select your API key provider.'),
            sg.Image(filename='./images/tool-tip.png', size=(20, 20), enable_events=True, key='-HELP-', tooltip='What is an API Key?',
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
            sg.Image(
                './images/keystore.png',
                size=(30, 30),
                key='-KEYSTORE-',
                pad=((0, 0), (35, 0)),
                enable_events=True,
                tooltip='Auto paste API Key'
            )
        ],
        
        [
            sg.Push(),
            sg.Image(
                './images/save-key.png',
                size=(30, 30),
                key='-SAVEKEY-',
                pad=((0, 0), (10, 0)),
                enable_events=True,
                tooltip='Save the API key'
            )
        ]

    ]

    return sg.Window('Crypto Fraud Detection Tool', layout, size=(800, 450))





  

