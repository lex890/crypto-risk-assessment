import FreeSimpleGUI as sg
from . import get_images as img
from . import plot_graphs as plg
from . import table as tbl
from .oas_screen  import generate_oas_window
from .ss_screen   import generate_subscr_window
from .plot_graphs import pie_charts

def update_score_window(window, data):
    # Prepare list to hold all charts to update in batch
    chart_data = data[-1]
    print('pie_charts', pie_charts)

    # Clear previously rendered graph
    if pie_charts:
        pie_charts.clear()
    canvas_key = '-MAINSCORE-'
    chart_data = data[-1]
    print('chart_data', chart_data)
    fig = plg.create_pie_chart(chart_data, figsize=(3, 3))
    is_main_score_flag = True
        
    pie_charts.append((canvas_key, fig, chart_data, is_main_score_flag))
    print('pie_charts', pie_charts)
    # Second pass: draw all figures (separated from creation)
    for canvas_key, fig, chart_data, is_main_score_flag in pie_charts:
        if canvas_key in window.AllKeysDict:
            canvas_elem = window[canvas_key]
            plg.draw_figure(canvas_elem, fig, canvas_key, chart_data, window, is_main_score_flag)

def main_score_graph_popup(window, chart_data):
    _, figure, chart_data, is_main_score = pie_charts[0]
    canvas_key_new = "-MAINSCORE-WINDOW-"
    canvas_elem = window[canvas_key_new]
    plg.draw_figure(canvas_elem, figure, canvas_key_new, chart_data, window, is_main_score)

def get_binary(value):
    value = int(value)
    if value == 1:
        return 'app/assets/images/complied.png'
    else:
        return 'app/assets/images/not-complied.png'

def update_risk_window(main_window, selected_coin, currency_choice):
    if len(pie_charts) > 10:
        pie_charts.clear()
    # warning_img, warning_msg = get_warning_image(selected_coin[22])
    
    main_window['-LOGO-'].update(data=img.get_image(selected_coin[7]), size=(100, 100))
    main_window['-RANK-'].update(value=f'#{selected_coin[0]}')
    main_window['-NAME-'].update(value=selected_coin[1][:13])
    main_window['-SYMB-'].update(value=selected_coin[8])
    main_window['-DATE-'].update(value=f'{selected_coin[10]}')
    main_window['-DESC-'].update(value=f'{selected_coin[9]}')
    main_window['-PRICE-CURRENCY-'].update(f'Price ({currency_choice}):')
    main_window['-PRICE-LABEL-'].update(f'{selected_coin[2]}')
    main_window['-MCAP-CURRENCY-'].update(f'Market Cap ({currency_choice}):')
    main_window['-MCAP-LABEL-'].update(f'{selected_coin[6]}')
    
    # Update Numerical Scores (update score and warning image/message)
    v_img, v_msg = get_warning_image(int(selected_coin[13])*10, 'volatility')
    main_window['-VOLATILITY-'].update(f' {selected_coin[13]}')
    main_window['-V-WIMG-'].update(filename=v_img)
    main_window['-V-WMSG-'].update(v_msg)
    l_img, l_msg = get_warning_image(int(selected_coin[14])*10, 'liquidity')
    main_window['-LIQUIDITY-'].update(f' {selected_coin[14]}')
    main_window['-L-WIMG-'].update(filename=l_img)
    main_window['-L-WMSG-'].update(l_msg)
    e_img, e_msg = get_warning_image(int(selected_coin[15])*10, 'exchange')
    main_window['-EXCHANGE-'].update(f' {selected_coin[15]}')
    main_window['-E-WIMG-'].update(filename=e_img)
    main_window['-E-WMSG-'].update(e_msg)
    a_img, a_msg = get_warning_image(int(selected_coin[16])*10, 'anomaly')
    main_window['-ANOMALY-'].update(f' {selected_coin[16]}')
    main_window['-A-WIMG-'].update(filename=a_img)
    main_window['-A-WMSG-'].update(a_msg)

    # Update Binary Scores (update checkmark image)
    main_window['-DT-CHECK-'].update(filename=get_binary(selected_coin[17]))
    main_window['-CP-CHECK-'].update(filename=get_binary(selected_coin[18]))
    main_window['-WA-CHECK-'].update(filename=get_binary(selected_coin[19]))
    main_window['-RC-CHECK-'].update(filename=get_binary(selected_coin[20]))
    main_window['-SC-CHECK-'].update(filename=get_binary(selected_coin[21]))
    
def get_warning_image(total_score, mode):
    try:
        total_score = int(float(total_score))
    except (ValueError, TypeError):
        total_score = 0  # fallback

    # Clamp score between 0 and 100
    total_score = max(0, min(total_score, 100))
    print('this is total score:', total_score)

    # Determine risk level and message
    if total_score >= 70:
        risk_level = 'good'
        warning_message = 'Low Risk'
    elif total_score > 50:
        risk_level = 'warning'
        warning_message = 'Med-Low Risk'
    elif total_score > 30:
        risk_level = 'warning'
        warning_message = 'Med-High Risk'
    else:
        risk_level = 'danger'
        warning_message = 'High Risk'

    # Image file prefix based on mode
    prefix_map = {
        'volatility': 'v',
        'liquidity': 'l',
        'exchange': 'e',
        'anomaly': 'a'
    }
    prefix = prefix_map.get(mode, 'v')  # default to 'v' if unknown mode

    warning_image = f'app/assets/images/{prefix}-{risk_level}.png'
    print('warning_image:', warning_image)

    return warning_image, warning_message

def main_score_window(chart_data, current_row, selected_coin, data):
    current_coin = selected_coin[1]
    # Extract the top 5 entries from the main csv
    list_oas = tbl.get_oas_list(data) # based on OAS (descending)
    list_24h = tbl.get_vol_list(data) # based on 24h vol (descending)
    
    oas_table = tbl.generate_oas_table(list_oas) # list_oas
    # vol_table = tbl.generate_vol_table(list_24h) # list_24h
    
    # store the window first to render the graph for this window
    window = sg.Window(
        "Assessment Score Guide",
        generate_oas_window(current_row, oas_table, current_coin),
        modal=True,
        keep_on_top=True,
        finalize=True,
        no_titlebar=True
    )
    main_score_graph_popup(window, chart_data)
    window.maximize()
    return window

def sub_score_window(category, score):
    # return the sub score window
    return sg.Window(
        "Assessment Score Guide",
        generate_subscr_window(category, score),
        size=(650, 400),
        modal=True,
        keep_on_top=True,
        finalize=True,
        no_titlebar=True,
    )

def render_upper_content(data):
    ucontent_bg = "#f0f0f0"
    smol_font = ('Segoe UI', 12, 'bold')
    bigga_font = ('Segoe UI', 24, 'bold')
    # crypto icon/logo
    logo = [
        [
            sg.Image(img.get_image(data[0][7]), size=(100, 100), key='-LOGO-',
                     background_color='#ffffff')
        ]
    ]
    image_box = [
        [
            sg.Column(logo, pad=((0, 0),(0, 0)), background_color=ucontent_bg)
        ]
    ]
    ranking_text = [
        [ 
            sg.Text(f"#{data[0][0]}",           # crypto ranking
            font=smol_font,
            pad=((0, 0), (0, 0)),
            text_color="#686868",
            key='-RANK-',
            background_color=ucontent_bg)
        ]
    ]
    ranking_container = [
        [
            sg.Column(ranking_text, pad=((0, 0), (0, 0)), background_color=ucontent_bg)
        ]
    ]
    ranking_box = [
        [
            sg.Column(ranking_container, pad=((15, 0), (9, 0)), background_color=ucontent_bg)
        ]
    ]
    name = [
        [
            sg.Text(data[0][1],                   # crypto name
            font=bigga_font,
            key='-NAME-',
            pad=((0, 0), (0, 55)), 
            background_color=ucontent_bg),

            sg.Text(data[0][8],                   # crypto symbol
            font=smol_font,
            text_color='#a1a3a6',
            pad=((3, 0), (0, 70)),
            key='-SYMB-', 
            background_color=ucontent_bg)
        ]
    ]
    price_text = [
        [
            sg.Text('Price (USD):',
                font=smol_font,
                text_color='#a1a3a6',
                pad=((0, 0), (0, 0)),
                key='-PRICE-CURRENCY-',
                background_color=ucontent_bg),
            sg.Text(f'{data[0][2]}',
                font=smol_font,
                text_color="#000000",
                pad=((0, 0), (0, 0)),
                key='-PRICE-LABEL-',
                background_color=ucontent_bg) 
        ]
    ]
    price_box = [
        [
           sg.Column(price_text, pad=((0, 0),(0, 0)),
                     background_color=ucontent_bg) 
        ]   
    ]
    mcap_text = [
        [
            sg.Text('Market Cap (USD):',
                font=smol_font,
                text_color='#a1a3a6',
                pad=((0, 0), (0, 0)),
                key='-MCAP-CURRENCY-',
                background_color=ucontent_bg), 
            sg.Text(f'{data[0][6]}',   
                font=smol_font,
                text_color="#000000",
                pad=((0, 0), (0, 0)),
                key='-MCAP-LABEL-',
                background_color=ucontent_bg)             
        ]
    ]
    mcap_box = [
        [
            sg.Column(mcap_text, pad=((0, 0),(0, 0)),
                      background_color=ucontent_bg)
        ]
    ]
    date_text = [
        [
            sg.Text('Date:',   # date added
            font=smol_font,
            text_color='#a1a3a6',
            pad=((0, 0), (0, 0)),
            background_color=ucontent_bg),
            sg.Text(f'{data[0][10]}',   # date added
            font=smol_font,
            text_color="#000000",
            pad=((0, 0), (0, 0)),
            key='-DATE-',
            background_color=ucontent_bg)   
        ]
    ]
    date_box = [
        [
            sg.Column(date_text, pad=((0, 0),(0, 0)),
                      background_color=ucontent_bg)
        ]
    ]

    information_box = [
        [
            sg.Column(ranking_box, size=(65, 50), pad=((0, 0),(0, 0)), background_color=ucontent_bg),
            sg.Column(name, size=(350, 50), pad=((0, 0),(0, 0)), background_color=ucontent_bg)
        ],
        [
            sg.Column(price_box, size=(250, 28), pad=((18, 0),(0, 0)), background_color=ucontent_bg),
            sg.Column(date_box, size=(150, 28), pad=((0, 0),(0, 0)), background_color=ucontent_bg)
        ],
        [
            sg.Column(mcap_box, size=(400, 28), pad=((18, 0),(0, 0)), background_color=ucontent_bg)
        ]

    ]

    description_box = [
        [
            sg.Multiline(f'{data[0][9]}',
            font=('Segoe UI', 13),
            size=(48, 9),
            auto_size_text=False,
            justification='left',
            pad=((110, 0), (0, 0)),
            key='-DESC-', background_color=ucontent_bg,
            no_scrollbar=True,
            border_width=0) 
        ]

    ]

    hyperlink = [
        [
            sg.Image(filename='app/assets/images/hyperlink.png', 
                    size=(30, 30), 
                    pad=((0, 0),(0, 0)), 
                    enable_events=True, 
                    key='-HYPERLINK-',
                    tooltip="Click to visit website",background_color=ucontent_bg)
        ]
    ]


    upper_info = [
        [
            sg.Column(image_box, pad=((0, 0), (0, 0)), background_color=ucontent_bg),
            sg.Column(information_box, pad=((0, 0), (0, 0)), background_color=ucontent_bg),
            sg.Column(hyperlink, pad=((0, 0), (0, 70)), background_color=ucontent_bg)
        ]
    ]

    lower_info = [
        [
            sg.Column(description_box, element_justification='left', size=(550, 290), pad=((0, 0), (0, 0)), background_color=ucontent_bg)
        ]   
    ]

    info_container = [
        [sg.Column(upper_info, size=(620, 115), background_color=ucontent_bg)],   
        [sg.Column(lower_info, size=(620, 190), background_color=ucontent_bg)]
    ]

    info = [
        [
            sg.Column(info_container,size=(590, 330), pad=((0, 0), (0, 0)), background_color=ucontent_bg)
        ]

    ]

    score = [
        [
            sg.Canvas(
                key="-MAINSCORE-", 
                size=(75, 75), 
                tooltip='Overall Assessment Score',background_color=ucontent_bg)
        ]
    ]

    return [
        [
            sg.Text('', expand_x=True, background_color=ucontent_bg),
            sg.Text('Overall Assessment Score',pad=((0, 40), (0, 0)), font=("Segoe UI", 16, "bold"), background_color=ucontent_bg,)
        ],
        [
            sg.Column(info, pad=((0, 10), (0, 0)), background_color=ucontent_bg),
            sg.Column(score, pad=((0, 20), (0, 0)),element_justification='center', background_color=ucontent_bg)
        ]
    ]
def render_lower_content(data):
    sc_text = "#ffffff"
    ov_text = "#ffffff"
    title_size = (28, 2)
    score_font = ("Segoe UI", 36)
    over_font  = ("Segoe UI", 36)
    title_font = ("Segoe UI", 13, 'bold')
    logo_pad = ((0, 20), (0, 0))
    score_size = (3, 1)
    label_size = (25, 1)
    rv_bg     = "#ef476f"
    ol_bg     = '#ffd166'
    el_bg     = '#06d6a0'
    am_bg     = '#118ab2'
    binary_bg = "#2e4e5a"

    realized_volatility = [
        [
            sg.Text('REALIZED VOLATILITY', font=title_font, pad=((12, 0), (10, 0)), background_color=rv_bg, size=title_size, key='-CATEGORY0-', text_color=sc_text, enable_events=True)
        ],
        [
            sg.Text(f' {data[0][13]}', font=score_font, pad=((0, 0), (0, 0)), background_color=rv_bg, size=score_size, text_color=sc_text, key='-VOLATILITY-', enable_events=True),
            sg.Text('/10', font=over_font, pad=((0, 0), (0, 0)), background_color=rv_bg, size=score_size, text_color=ov_text, key='-VOLATILITY1-', enable_events=True),
            sg.Image(filename='app/assets/images/volatility.png', pad=logo_pad, background_color=rv_bg, key='-RV-IMAGE-', enable_events=True)    
        ],
        [   
            sg.Image(filename='app/assets/images/v-good.png', pad=((10, 0), (10, 0)), key='-V-WIMG-', enable_events=True),
            sg.Text('Low Risk', font=("Arial", 12, 'bold'), pad=((10, 0), (10, 0)), background_color=rv_bg, text_color=sc_text, key='-V-WMSG-', enable_events=True, size=label_size)
        ]
    ]
    
    orderbook_liquidity = [
        [
            sg.Text('LIQUIDITY AND ORDER BOOK DEPTH', font=title_font, pad=((12, 0), (10, 0)), background_color=ol_bg, size=title_size, key='-CATEGORY1-', text_color=sc_text, enable_events=True)
        ],
        [
            sg.Text(f' {data[0][14]}', font=score_font, pad=((0, 0), (0, 0)), background_color=ol_bg, size=score_size, text_color=sc_text, key='-LIQUIDITY-', enable_events=True),
            sg.Text('/10', font=over_font, pad=((0, 0), (0, 0)), background_color=ol_bg, size=score_size, text_color=ov_text, key='-LIQUIDITY1-', enable_events=True),
            sg.Image(filename='app/assets/images/liquidity.png', pad=logo_pad, background_color=ol_bg, key='-OL-IMAGE-', enable_events=True)    
        ],
        [   
            sg.Image(filename='app/assets/images/l-good.png', pad=((10, 0), (10, 0)), key='-L-WIMG-', enable_events=True),
            sg.Text('Low Risk', font=("Arial", 12, 'bold'), pad=((10, 0), (10, 0)), background_color=ol_bg, text_color=sc_text, key='-L-WMSG-', enable_events=True, size=label_size)
        ]
    ]
    
    exchange_listings = [
        [
            sg.Text('EXCHANGE LISTINGS AND REPUTATION', font=title_font, pad=((12, 0), (10, 0)), background_color=el_bg, size=title_size, key='-CATEGORY2-', text_color=sc_text, enable_events=True)
        ],
        [
            sg.Text(f' {data[0][15]}', font=score_font, pad=((0, 0), (0, 0)), background_color=el_bg, size=score_size, text_color=sc_text, key='-EXCHANGE-', enable_events=True),
            sg.Text('/10', font=over_font, pad=((0, 0), (0, 0)), background_color=el_bg, size=score_size, text_color=ov_text, key='-EXCHANGE1-', enable_events=True),
            sg.Image(filename='app/assets/images/exchange.png', pad=logo_pad, background_color=el_bg, key='-EL-IMAGE-', enable_events=True)    
        ],
        [   
            sg.Image(filename='app/assets/images/e-good.png', pad=((10, 0), (10, 0)), key='-E-WIMG-', enable_events=True),
            sg.Text('Low Risk', font=("Arial", 12, 'bold'), pad=((10, 0), (10, 0)), background_color=el_bg, text_color=sc_text, key='-E-WMSG-', enable_events=True, size=label_size)
        ]
    ]
    
    anomaly_patterns = [
        [
            sg.Text('TRANSACTION PATTERNS AND ANOMALIES', font=title_font, pad=((12, 0), (10, 0)), background_color=am_bg, size=title_size, key='-CATEGORY3-', text_color=sc_text, enable_events=True)
        ],
        [
            sg.Text(f' {data[0][16]}', font=score_font, pad=((0, 0), (0, 0)), background_color=am_bg, size=score_size, text_color=sc_text, key='-ANOMALY-', enable_events=True),
            sg.Text('/10', font=over_font, pad=((0, 0), (0, 0)), background_color=am_bg, size=score_size, text_color=ov_text, key='-ANOMALY1-', enable_events=True),
            sg.Image(filename='app/assets/images/anomaly.png', pad=logo_pad, background_color=am_bg, key='-AP-IMAGE-', enable_events=True)    
        ],
        [   
            sg.Image(filename='app/assets/images/a-good.png', pad=((10, 0), (10, 0)), key='-A-WIMG-', enable_events=True),
            sg.Text('Low Risk', font=("Arial", 12, 'bold'), pad=((10, 0), (10, 0)), background_color=am_bg, text_color=sc_text, key='-A-WMSG-', enable_events=True, size=label_size)
        ]
    ]  
    numerical_size = (290, 200)
    numerical1_pad = ((15, 5), 5)
    numerical2_pad = (5, 5)
    numerical_score = [
        [
            sg.Column(realized_volatility, pad=numerical1_pad, background_color=rv_bg, size=numerical_size),
            sg.Column(orderbook_liquidity, pad=numerical2_pad, background_color=ol_bg, size=numerical_size)
        ],
        [
            sg.Column(exchange_listings, pad=numerical1_pad, background_color=el_bg, size=numerical_size),
            sg.Column(anomaly_patterns, pad=numerical2_pad, background_color=am_bg, size=numerical_size)
        ]
    ]

    binary_pad =(5, (8, 0))
    bimage_pad =((10, 0), (0, 12))
    binary_size =(29, 1)
    
    binary_text_clr = "#eaeaea"
    binary_font = ('Inter', 10, 'bold')
    binary_sfont = ('Inter', 8, 'bold')
    developer_transparency = [
        [
            sg.Image(filename='app/assets/images/complied.png', pad=((10, 0), (0, 25)), key='-DT-CHECK-', enable_events=True),
            sg.Column([
                [sg.Text('Developer & Team Transparency', pad=binary_pad, background_color=binary_bg, key='-CATEGORY4-', text_color=sc_text, size=binary_size, font=binary_font, enable_events=True)],
                [sg.Text("Knowing who's behind the project builds trust.", font=binary_sfont, background_color=binary_bg, text_color=binary_text_clr, size=(30, 2))]
            ], pad=(0,0), background_color=binary_bg)
        ]
    ]
    community_presence = [
        [
            sg.Image(filename='app/assets/images/complied.png', pad=bimage_pad, key='-CP-CHECK-', enable_events=True),
            sg.Column([
                [sg.Text('Community & Social Media Presence', pad=binary_pad, background_color=binary_bg, key='-CATEGORY5-', text_color=sc_text, size=binary_size, font=binary_font, enable_events=True)],
                [sg.Text('Active community means more trust.', font=binary_sfont, background_color=binary_bg, text_color=binary_text_clr)]
            ], pad=(0,0), background_color=binary_bg)
        ]
    ]
    whitepaper_assessment = [
        [
            sg.Image(filename='app/assets/images/complied.png', pad=bimage_pad, key='-WA-CHECK-', enable_events=True),
            sg.Column([
                [sg.Text('Whitepaper & Roadmap Execution', pad=binary_pad, background_color=binary_bg, key='-CATEGORY6-', text_color=sc_text, size=binary_size, font=binary_font, enable_events=True)],
                [sg.Text('Clear plans show serious intent.', font=binary_sfont, background_color=binary_bg, text_color=binary_text_clr)]
            ], pad=(0,0), background_color=binary_bg)
        ]
    ]
    regulatory_compliance = [
        [
            sg.Image(filename='app/assets/images/complied.png', pad=((10, 0), (0, 25)), key='-RC-CHECK-', enable_events=True),
            sg.Column([
                [sg.Text('Regulatory Compliance & Legal Standing', pad=binary_pad, background_color=binary_bg, key='-CATEGORY7-', text_color=sc_text, size=(29, 2), font=binary_font, enable_events=True)],
                [sg.Text('Following laws reduces risk.', font=binary_sfont, background_color=binary_bg, text_color=binary_text_clr)]
            ], pad=(0,0), background_color=binary_bg)
        ]
    ]
    smart_contract = [
        [
            sg.Image(filename='app/assets/images/complied.png', pad=bimage_pad, key='-SC-CHECK-', enable_events=True),
            sg.Column([
                [sg.Text('Smart Contract Audit & Security', pad=binary_pad, background_color=binary_bg, key='-CATEGORY8-', text_color=sc_text, size=binary_size, font=binary_font, enable_events=True)],
                [sg.Text('Audits help prevent hacks.', font=binary_sfont, background_color=binary_bg, text_color=binary_text_clr)]
            ], pad=(0,0), background_color=binary_bg)
        ]
    ]

    binary_size = (300, 75)
    bscore_pad = ((0, 0), (0, 5))
    
    binary_score = [
        [ sg.Column(developer_transparency, pad=bscore_pad, background_color=binary_bg, size=binary_size) ],
        [ sg.Column(community_presence, pad=bscore_pad, background_color=binary_bg, size=binary_size) ],
        [ sg.Column(whitepaper_assessment, pad=bscore_pad, background_color=binary_bg, size=binary_size) ],
        [ sg.Column(regulatory_compliance, pad=bscore_pad, background_color=binary_bg, size=binary_size) ],
        [ sg.Column(smart_contract, pad=bscore_pad, background_color=binary_bg, size=binary_size) ]
    ]

    return [
        [
            sg.Column(numerical_score, pad=(0, 10), background_color='#f0f0f0'),
            sg.Column(binary_score, pad=((5, 15), (15, 0)), background_color='#f0f0f0', vertical_alignment='top')
        ]
    ]

def score_window(data):
    upper_window = [
        [
            sg.Column(
            render_upper_content(data), pad=((0, 0), (0, 0)), background_color='#f0f0f0')
        ]
    ]

    lower_window = [
        [
            sg.Column(
            render_lower_content(data), pad=((0, 0), (0, 0)), background_color='#f0f0f0')
        ]
    ]

    return upper_window + lower_window


    