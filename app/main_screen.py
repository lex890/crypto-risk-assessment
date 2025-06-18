import FreeSimpleGUI as sg
from . import risk_assessment as rsk

def get_page_data(data, page, rows_per_page):
    start = (page - 1) * rows_per_page
    end = start + rows_per_page
    print('start: ', start, 'end: ', end)
    return data[start:end]


def main_screen(headings, data, current_page, rows_per_page):
    print('in the main: ', get_page_data(data, current_page, rows_per_page))
    
    page_nav = [
        [
            
            sg.Button(
                image_filename='app/assets/images/arrow-left-icon.png',
                size=(50, 50),
                key='-PREV-',
                button_color=("#F0F0F0", sg.theme_background_color()),
                border_width=0,
                focus=False
            ),
            sg.Text(
                '1',
                font=('Helvetica', 16, 'bold'),
                pad=((25, 0), (0, 0)),
                enable_events=True,
                key='-PAGENO-'
            ),
            sg.Button(
                image_filename='app/assets/images/arrow-right-icon.png',
                size=(50, 50),
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
                font=('Helvetica', 12, 'bold'),
                hide_vertical_scroll=True,
                enable_events=True,
                alternating_row_color='#f0f0f0'
            )
        ],
        [         
            sg.Column(page_nav)
        ]
    ]

    layout = [
        #header and icon
        [
            sg.Image(filename='app/assets/images/resizedLogo.png', size=(50, 50), pad=((25, 0), (25, 0)), enable_events=True, key='-HEADERICON-'), 
            sg.Text('Cryptocurrency Investment Risk Assessment Tool', font=('Helvetica', 16), pad=((15, 0), (25, 0)), enable_events=True, key='-HEADER-'),
            sg.Push(),
            
        ],
        #search bar and bunch of buttons
        [
            [   
                sg.Button(
                    '', 
                    image_filename='app/assets/images/byalpha.png', 
                    image_size=(50, 50), button_color=("#F0F0F0", 
                    sg.theme_background_color()), border_width=1, 
                    pad=((35, 0), (35, 0)), key=('-ALPHA-'), 
                    tooltip='Sort by Alpha'
                ),
                sg.Button(
                    '', 
                    image_filename='app/assets/images/bynumber.png',
                    image_size=(50, 50), button_color=("#F0F0F0", 
                    sg.theme_background_color()), 
                    border_width=1, 
                    pad=((10, 0), (35, 0)), 
                    key=('-NUMBER-'), 
                    tooltip='Sort by Ranking(#)'
                ),
                sg.Button(
                    '', 
                    image_filename='app/assets/images/byprice.png',
                    image_size=(50, 50), 
                    button_color=("#F0F0F0", sg.theme_background_color()), 
                    border_width=1, 
                    pad=((10, 0), (35, 0)), 
                    key=('-PRICE-'), 
                    tooltip='Sort by Price($)'
                ),

                sg.Text('Select Currency', font=('Helvetica', 12), pad=((50, 0), (35, 0))),
                sg.Combo(['USD', 'EUR', 'GBP', 'JPY', 'AUD', 'CAD', 'CHF', 'CNY', 'INR', 'PHP'], default_value='USD', font=('Helvetica', 14), key='-CURRENCY-', pad=((5, 0), (35, 0)), tooltip='Select Currency'),   

                sg.InputText(
                    default_text='',
                    size=(17, 1),
                    font=('Helvetica', 18),
                    pad=((50, 10), (35, 0)),
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
                    pad=((0, 25), (35, 0))
                )
                
            ],
            # lower part of the main screen
            [
                sg.Column(table, expand_y=True, expand_x=True, pad=((50, 50), (42, 40)), element_justification='center'),
                sg.Column(rsk.score_window(data, headings), expand_y=True, expand_x=True, pad=((50, 50), (42, 40)),)
            ]
        ]
    ]
    window = sg.Window('Main App', layout, finalize=True, resizable=True)
    rsk.risk_assessment_window(window, data)
    window.Maximize()
    
    return window