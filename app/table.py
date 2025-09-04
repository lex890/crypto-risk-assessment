import FreeSimpleGUI as sg
from . import get_images as gim
from .list import list_24h, list_oas

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
    value = int(float(value)) 

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

def toggle_table(query, oas_window, data):
    if query == 'Market Volume Trend':
        list = get_vol_list(data)
        title = 'Top 5 coins based on Market Volume Trend'
        color = "#ef476f"
    elif query == 'Overall Assessment Score':
        list = get_oas_list(data)
        title = 'Top 5 coins based on Overall Assessment Score'
        color = '#118ab2'
    oas_window['-header-'].update(title, text_color=color)
    for i, row in enumerate(list):
            # Descriptive variable unpacking
            
        _, name, price, _, change_24h, _, mcap, icon_path, symbol, oas = row[:9] + [row[-1]]

        # Filter the retrieved data and color
        num2, col2 = get_percent_data(change_24h)
        oas_color = get_assessment_color(oas)

        oas_window[f'-icon{i}-'].update(data=gim.get_image(icon_path, 1))
        oas_window[f'-name{i}-'].update(name)
        oas_window[f'-symbol{i}-'].update(symbol)
        oas_window[f'-price{i}-'].update(price)
        oas_window[f'-day{i}-'].update(num2, text_color=col2)
        oas_window[f'-mcap{i}-'].update(mcap)
        oas_window[f'-oas{i}-'].update(mcap, text_color=oas_color)


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

def generate_list(i, list):
    font_size = ('Aria', 12)
    font_sizeB =('Aria', 12, 'bold')
    symbol_font_size = ('Helvetica', 12, 'bold')
    current_data = list[i]

    # Descriptive variable unpacking
    _, name, price, _, change_24h, _, mcap, icon_path, symbol, oas = current_data[:9] + [current_data[-1]]

    # Filter the retrieved data and color
    num2, col2 = get_percent_data(change_24h)
    oas_color = get_assessment_color(oas)
    row = [
            [
                sg.Image( # Icon
                    gim.get_image(icon_path, 1), key=f'-icon{i}-',
                    pad=((15, 0), (0, 0)), enable_events=True
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
                    ], pad=((0, 0), (0, 0)), size=(185, 25)
                ),
                sg.Text( # Price
                    price, key=f'-price{i}-', font=font_size, 
                    size=(16, 1), justification='right', pad=((0, 20), (0, 0)), enable_events=True
                ),
                sg.Text( # 24h%
                    num2, text_color=col2, key=f'-day{i}-', font=font_sizeB, 
                    size=(6, 1), justification='right', pad=((0, 5), (0, 0)), enable_events=True
                ),
                sg.Text( # Market Cap
                    mcap, key=f'-mcap{i}-', font=font_size, 
                    size=(17, 1), justification='right', pad=((20, 0), (0, 0)), enable_events=True
                ),
                sg.Text( # OAS
                    oas, text_color=oas_color, key=f'-oas{i}-', font=font_sizeB, 
                    size=(5, 1), justification='right', pad=((20, 30), (0, 0)), enable_events=True
                )
            ]
        ]
    return row

def oas_table_header():
    font_size = ('Helvetica', 12, 'bold')
    row = [
            [
                
                sg.Text( # Name
                    'Name', font=font_size, pad=((15, 155), (0, 0)),
                    tooltip='coin name and ticker symbol'
                ),
                sg.Text( # Price
                    'Price', font=font_size, pad=((0, 12), (0, 0)),
                    size=(16, 1), justification='right',
                    tooltip='closing price at the current time.'
                ),
                sg.Text(# 24h%
                    '24%', font=font_size, pad=((0, 0), (0, 0)),
                    size=(6, 1), justification='right', 
                    tooltip='percentage change over the past 24 hours'
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

table_name_font = ('Segoe UI', 24, 'bold')
table_oas_color = '#118ab2'
table_vol_color = '#ef476f'
def generate_vol_table(list_24h):
    vol_header = oas_table_header()
    vol_list = [
        [sg.Column([
            [sg.Column(generate_list(i, list_24h), pad=((0, 0), (0, 0)))],
            [sg.HorizontalSeparator(pad=((0, 0), (15, 15)), color='#f0f0f0')]
        ], pad=((0, 0), (0, 0)))]
        for i in range(5)
    ]
    vol_table = [
        [sg.Text('Recommended coins based on Market Trend', pad=((0, 0), (0, 20)), font=table_name_font, text_color=table_vol_color)],
        [sg.Column(vol_header, pad=((0, 0), (0, 0)))],
        [sg.HorizontalSeparator(pad=((0, 0), (0, 15)))],
        [sg.Column(vol_list, pad=((0, 0), (0, 0)))],
    ]
    return vol_table 

def generate_oas_table(list_oas):
    oas_header = oas_table_header()
    oas_list = [
        [sg.Column([
            [sg.Column(generate_list(i, list_oas), pad=((0, 0), (0, 0)))],
            [sg.HorizontalSeparator(pad=((0, 0), (15, 15)), color='#f0f0f0')]
        ], pad=((0, 0), (0, 0)))]
        for i in range(5)
    ]
    oas_table = [
        [
            sg.Text('Top 5 coins based on Overall Assessment Score', pad=((0, 0), (40, 20)), font=table_name_font, key='-header-', text_color=table_oas_color)
        ],
        [sg.Column(oas_header, pad=((0, 0), (0, 0)))],
        [sg.HorizontalSeparator(pad=((0, 0), (0, 15)))],
        [sg.Column(oas_list, pad=((0, 0), (0, 0)))],
    ]
    return oas_table    

def get_oas_list(data):
    # Sort the sublists by their OAS
    sorted_data = sorted(data, key=lambda x: int(x[-1]), reverse=True)
    return sorted_data[:5]  # return the top 5

def get_vol_list(data):
    # Sort the sublists by their 24%
    sorted_data = sorted(data, key=lambda x: float(x[4]), reverse=True)
    return sorted_data[:5]  # return the top 5