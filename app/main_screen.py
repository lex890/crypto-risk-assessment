import FreeSimpleGUI as sg
from . import risk_assessment as rsk


screen_width, _ = sg.Window.get_screen_size()

def get_page_data(data, page, rows_per_page):
    start = (page - 1) * rows_per_page
    end = start + rows_per_page
    print('start: ', start, 'end: ', end)
    return data[start:end]


def main_screen(headings, data, current_page, rows_per_page):
    print('in the main: ', get_page_data(data, current_page, rows_per_page))
    
    sorting_buttons = [
        [
            sg.Button(
                '', 
                image_filename='app/assets/images/byalpha.png', 
                image_size=(50, 50), button_color=("#F0F0F0", 
                sg.theme_background_color()), border_width=1, 
                pad=((0, 10), (0, 0)), key=('-ALPHA-'), 
                tooltip='Sort by Alpha'
            ),
            sg.Button(
                '', 
                image_filename='app/assets/images/bynumber.png',
                image_size=(50, 50), button_color=("#F0F0F0", 
                sg.theme_background_color()), 
                border_width=1, 
                pad=((0, 10), (0, 0)), 
                key=('-NUMBER-'), 
                tooltip='Sort by Ranking(#)'
            ),
            sg.Button(
                '', 
                image_filename='app/assets/images/byprice.png',
                image_size=(50, 50), 
                button_color=("#F0F0F0", sg.theme_background_color()), 
                border_width=1, 
                pad=((0, 0), (0, 0)), 
                key=('-PRICE-'), 
                tooltip='Sort by Price($)'
            )
        ]
    ]

    combo_currency = [
        [
            sg.Text('Select Currency', font=('Helvetica', 12), pad=((0, 10), (15, 0))),
            sg.Combo(['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'PHP'], default_value='USD', font=('Helvetica', 14), key='-CURRENCY-', pad=((0, 0), (15, 0)), tooltip='Select Currency', enable_events=True),
        ]
    ]

    search_bar = [
        [
            sg.InputText(
                default_text='',
                size=(17, 1),
                font=('Helvetica', 18),
                pad=((0, 0), (0, 0)),
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
                pad=((10, 0), (0, 0))
            )
        ]
    ]

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
                font=('Helvetica', 24, 'bold'),
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

    nav_buttons = [
        [
            sg.Column(page_nav, pad=((350, 0), 0))
        ]
    ]

    table = [
        [
            sg.Table(
                values=get_page_data(data, current_page, rows_per_page),
                headings=headings[:7],
                max_col_width=10,
                auto_size_columns=False,
                justification='center',
                col_widths=[5, 12, 16, 6, 6, 6, 18],
                num_rows=rows_per_page,
                key='-TABLE-',
                row_height=51,
                font=('Helvetica', 12, 'bold'),
                hide_vertical_scroll=True,
                enable_events=True,
                alternating_row_color='#f0f0f0'
            )
        ]
    ]

    header = [
        [
            sg.Image(filename='app/assets/images/resizedLogo.png', size=(50, 50), pad=((0, 10), (0, 0)), enable_events=True, key='-HEADERICON-'), 
            sg.Text('Cryptocurrency Investment Risk Assessment Tool', font=('Helvetica', 16), pad=((0, 0), (0, 0)), enable_events=True, key='-HEADER-')
        ]
    ]

    upper_tools = [
        [   
            sg.Column(sorting_buttons, size=(190, 55)),

            sg.Column(combo_currency, size=(185, 55)),   

            sg.Column(search_bar, size=(290, 55))
            
        ]
    ]

    first_layer = [
        [
            sg.Column(header, size=(600, 55), pad=((35, 0), (0, 0)))
        ]
    ]

    second_layer = [
        [
            sg.Column(upper_tools, size=(750, 60), pad=((35, 0), (0, 0)))
        ]
    ]

    third_layer = [
        [
            sg.Column(table, pad=((35, 0), (0, 0))),
            sg.Column(rsk.score_window(data, headings), pad=((70, 0), (0, 0)))
        ]
    ]

    fourth_layer = [
        [         
            sg.Column(nav_buttons, pad=((0, 0), (0, 0)))
        ]
    ]

    layout = [
        #header and icon
        [
            sg.Column(first_layer, expand_x=True)
        ],
        
        [
            sg.Column(second_layer, expand_x=True)   
        ],

        [
            sg.Column(third_layer, background_color='#F0F0F0', expand_y=True)
        ],
        [
            sg.Column(fourth_layer, background_color='#F0F0F0'), 
        ]
    ]
    window = sg.Window('Main App', layout, finalize=True, resizable=True)
    rsk.risk_assessment_window(window, data)
    window.Maximize()
    
    return window