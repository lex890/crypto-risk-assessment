import FreeSimpleGUI as sg
from . import risk_assessment as rsk

screen_width, _ = sg.Window.get_screen_size()

def get_page_data(data, page, rows_per_page):
    start = (page - 1) * rows_per_page
    end = start + rows_per_page
    print('start: ', start, 'end: ', end)
    return data[start:end]

def get_percent_data(data, key, main_window):
    data = float(data)
    
    if data < 0:
        main_window[key].update(value=f'{abs(data)}%')
        main_window[key].update(text_color='red')
    else:
        main_window[key].update(value=f'{abs(data)}%')
        main_window[key].update(text_color='green')

def first_column_box():
    # Define header row
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
                'Cryptocurrency Investment Risk Assessment Tool',
                font=('Helvetica', 16),
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
                font=('Helvetica', 12),
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
                sg.theme_background_color()), border_width=1, 
                pad=((60, 5), (0, 0)), key=('-ALPHA-'), 
                tooltip='Sort by Alpha'
            ),
            sg.Button(
                '', 
                image_filename='app/assets/images/bynumber.png',
                image_size=(50, 50), button_color=("#F0F0F0", 
                sg.theme_background_color()), 
                border_width=1, 
                pad=((0, 5), (0, 0)), 
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
            sg.Text('Select Currency', font=('Helvetica', 12), pad=((50, 0), (0, 0))),
            sg.Combo(['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'PHP'], default_value='USD', font=('Helvetica', 14), key='-CURRENCY-', pad=((0, 0), (0, 0)), tooltip='Select Currency', enable_events=True),
        ]
    ]

    search_bar = [
        [
            sg.InputText(
                default_text='',
                size=(20, 1),
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

    ref_danger = [
        [
            sg.Image(
                filename='app/assets/images/ref-danger.png',
                size=(20, 20), 
                pad=((0, 5), (0, 0)), 
                enable_events=True,
                tooltip='High-risk investment identified.' 
            ),
            sg.Text(
                'Danger',
                font=('Helvetica', 12),
                pad=((0, 0), (0, 0)),
            )
        ]
    ]

    ref_warning = [
        [
            sg.Image(
                filename='app/assets/images/ref-warning.png',
                size=(20, 20), 
                pad=((0, 5), (0, 0)), 
                enable_events=True,
                tooltip='Medium-risk invest with caution.' 
            ),
            sg.Text(
                'Warning',
                font=('Helvetica', 12),
                pad=((0, 0), (0, 0)),
            )            
        ]
    ]

    ref_good = [
        [
            sg.Image(
                filename='app/assets/images/ref-good.png',
                size=(20, 20), 
                pad=((0, 5), (0, 0)), 
                enable_events=True,
                tooltip='Investment risk assessed as low.' 
            ),
            sg.Text(
                'Good',
                font=('Helvetica', 12),
                pad=((0, 0), (0, 0)),
            )
        ]
    ]

    ref_danger_box = [
        [
            sg.Column(
                ref_danger,
                pad=((0, 0), (0, 0)))
        ]
    ]

    ref_warning_box = [
        [
            sg.Column(
                ref_warning,
                pad=((0, 0), (0, 0)))            
        ]
    ]

    ref_good_box = [
        [
            sg.Column(
                ref_good,
                pad=((0, 0), (0, 0)))
        ]
    ]

    icon_reference = [
        [
            sg.Column(
                ref_good_box,
                pad=((85, 25), (25, 0))
            ),
            sg.Column(
                ref_warning_box,
                pad=((0, 25), (25, 0))
            ),
            sg.Column(
                ref_danger_box,
                pad=((0, 25), (25, 0))
            ),
        ]
    ]

    second_layer = [
        [   
            sg.Column(sorting_buttons, pad=(0, 0)),

            sg.Column(combo_currency, pad=(0, 0)),   

            sg.Column(search_bar, pad=(0, 0)),

            sg.Column(icon_reference, pad=(0, 0))
        ]
    ]

    return second_layer

def third_column_box(data, headings, current_page, rows_per_page):
    
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
            )
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
                font=('Helvetica', 12),
                hide_vertical_scroll=True,
                enable_events=True,
                alternating_row_color='#f0f0f0',
                pad=((0, 0), (20, 0))
            )
        ],
        [
            sg.Push(),
            sg.Column(page_nav, pad=((20, 0), (25, 0))),
            sg.Push()
        ]
    ]

    risk_assessment_window = rsk.score_window(data, headings)

    third_layer = [
        [
            sg.Push(),
            sg.Column(table, pad=((0, 0), (0, 0))),
            sg.Column(risk_assessment_window, pad=((0, 0), (0, 0))),
            sg.Push()
        ]
    ]

    return third_layer


def main_screen_handler(headings, data, current_page, rows_per_page):

    first_layer = first_column_box()

    second_layer = second_column_box()

    third_layer = third_column_box(data, headings, current_page, rows_per_page)


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
    rsk.risk_assessment_window(window, data)
    window.Maximize()
    
    return window