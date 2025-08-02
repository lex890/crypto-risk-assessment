import FreeSimpleGUI as sg
from . import get_images as gim

def get_percent_data(value):
    value = float(value)
    
    if value < 0:
        number_data=f'{abs(value)}%'
        number_color='#ef476f'
    else:
        number_data=f'{abs(value)}%'
        number_color='#06d6a0'

    return number_data, number_color
def get_assessment_color(value):
    value = int(value)

    if value >= 80:
        color = "#06be8d"
    elif value >= 60:
        color = "#ebc15f"
    elif value >= 40:
        color = "#e29247"
    elif value >= 1:
        color = "#da4165"
    return color

def generate_table(i, data):
    font_size = ('Aria', 12)
    font_sizeB =('Aria', 12, 'bold')
    symbol_font_size = ('Helvetica', 12, 'bold')
    current_data = data[i]

    # Descriptive variable unpacking
    rank, name, price, change_1h, change_24h, change_7d, mcap, icon_path, symbol, oas = current_data[:9] + [current_data[-1]]

    # Create a list of frequency price change
    percent_fields = [change_1h, change_24h, change_7d]

    # Filter the retrieved data and color
    (num1, col1), (num2, col2), (num3, col3) = (
        get_percent_data(v) for v in percent_fields
    )
    oas_color = get_assessment_color(oas)
    row = [
            [
                sg.Text( # Rank
                    rank, 
                    key=f'-rank{i}-', font=font_size, size=(4, 1), 
                    justification='right', enable_events=True, 
                    pad=((0, 30), (0, 0))
                ),
                sg.Image( # Icon
                    gim.get_image(icon_path, 1), key=f'-icon{i}-',
                    pad=((0, 0), (0, 0)), enable_events=True
                ),
                sg.Column([
                    [
                        sg.Text( # Name
                            name, key=f'-name{i}-', font=symbol_font_size, 
                            pad=((10, 0), (0, 0)), enable_events=True
                        ),
                        sg.Text( # Symbol
                            symbol, key=f'-symbol{i}-', font=symbol_font_size, 
                            size=(6, 1), text_color='#bebebe', pad=((0, 0), (0, 0)), enable_events=True
                        )
                    ]
                    ], pad=((0, 0), (0, 0)), size=(160, 25)
                ),
                sg.Text( # Price
                    price, key=f'-price{i}-', font=font_size, 
                    size=(16, 1), justification='right', pad=((0, 20), (0, 0)), enable_events=True
                ),
                sg.Text( # 1h%
                    num1, text_color=col1, key=f'-hour{i}-', font=font_sizeB, 
                    size=(6, 1), justification='right', pad=((0, 5), (0, 0)), enable_events=True
                ),
                sg.Text( # 24h%
                    num2, text_color=col2, key=f'-day{i}-', font=font_sizeB, 
                    size=(6, 1), justification='right', pad=((0, 5), (0, 0)), enable_events=True
                ),
                sg.Text( # 7d%
                    num3, text_color=col3, key=f'-week{i}-', font=font_sizeB, 
                    size=(6, 1), justification='right', pad=((0, 0), (0, 0)), enable_events=True
                ),
                sg.Text( # Market Cap
                    mcap, key=f'-mcap{i}-', font=font_size, 
                    size=(17, 1), justification='right', pad=((20, 0), (0, 0)), enable_events=True
                ),
                sg.Text( # Market Cap
                    oas, text_color=oas_color, key=f'-oas{i}-', font=font_sizeB, 
                    size=(5, 1), justification='right', pad=((20, 30), (0, 0)), enable_events=True
                )
            ]
        ]
    return row

def generate_table_header():
    font_size = ('Helvetica', 12, 'bold')
    row = [
        [
            sg.Text( # Rank
                '#', font=font_size, pad=((0, 0), (0, 0)), 
                size=(4, 1), justification='right',
                tooltip='ranking'
            ),
            sg.Text( # Name
                'Name', font=font_size, pad=((25, 0), (0, 0)),
                tooltip='coin name and ticker symbol'
            ),
            sg.Text( # Price
                'Price', font=font_size, pad=((125, 12), (0, 0)),
                size=(16, 1), justification='right',
                tooltip='closing price at the current time.'
            ),
            sg.Text(# 1h%
                '1h%', font=font_size, pad=((5, 0), (0, 0)),
                size=(6, 1), justification='right', 
                tooltip='percentage change over the past 1 hour'
            ),
            sg.Text(# 24h%
                '24%', font=font_size, pad=((0, 0), (0, 0)),
                size=(6, 1), justification='right', 
                tooltip='percentage change over the past 24 hours'
            ),
            sg.Text(# 7d%
                '7d%', font=font_size, pad=((0, 0), (0, 0)),
                size=(6, 1), justification='right',
                tooltip='percentage change over the past 7 days'
            ),
            sg.Text(# Market Cap
                'Market Cap', font=font_size, pad=((0, 0), (0, 0)),
                size=(17, 1), justification='right', expand_x=True, tooltip='Market Capitalization'
            ),
            sg.Text(# Overall Assessment Score
                'OAS', font=font_size, pad=((0, 0), (0, 0)),
                size=(9, 1), justification='right', expand_x=True, tooltip='Overall Assessment Score'
            )
        ]
    ] 
    return row 

def update_table(main_window, current_page_data, rows_per_page):
    for i, row in enumerate(current_page_data):
        # unpack row
        (rank, name, price, change_1h, change_24h, change_7d, mcap, icon_path, symbol, oas) = row[:9] + [row[-1]]
        # format the % fields
        (num1, col1), (num2, col2), (num3, col3) = (
            get_percent_data(v) for v in (change_1h, change_24h, change_7d)
        )
        oas_color = get_assessment_color(oas)
        # update table
        main_window[f'-rank{i}-'  ].update(rank)
        main_window[f'-icon{i}-'  ].update(data=gim.get_image(icon_path, 1))
        main_window[f'-name{i}-'  ].update(name)
        main_window[f'-symbol{i}-'].update(symbol)
        main_window[f'-price{i}-' ].update(price)
        main_window[f'-hour{i}-'  ].update(num1, text_color=col1)
        main_window[f'-day{i}-'   ].update(num2, text_color=col2)
        main_window[f'-week{i}-'  ].update(num3, text_color=col3)
        main_window[f'-mcap{i}-'  ].update(mcap)
        main_window[f'-oas{i}-'   ].update(oas, text_color=oas_color)

    # Extract the row number
    for leftover in range(len(current_page_data), rows_per_page):
        for prefix in ('-rank', '-icon', '-name', '-symbol',
                       '-price', '-hour', '-day', '-week', '-mcap'):
            key = f'{prefix}{leftover}-'
            element = main_window[key]
            element.update(visible=True)