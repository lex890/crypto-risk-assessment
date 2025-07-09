import FreeSimpleGUI as sg
from . import get_images as img
from . import plot_graphs as plg
from .score_dict import descriptions, get_main_desc

sg.theme('LightGrey1')
pie_charts = []

def update_score_window(window, data):
    # Prepare list to hold all charts to update in batch
    chart_data = data[-1]
    print('chart_data', chart_data)

    # Clear previously rendered graph
    if len(pie_charts) > 10:
        pie_charts.clear()

    #Iterate through the score data to create pie charts
    for i in range(11):
        canvas_key = f'-SCORE{i}-' if i > 0 else '-MAINSCORE-'

        if canvas_key == '-MAINSCORE-':
            chart_data = data[-1]
            print('chart_data', chart_data)
            fig = plg.create_pie_chart(chart_data, figsize=(3, 3))
            is_main_score_flag = True
        else:
            chart_data = data[13 + (i - 1)]  # Individual scores
            fig = plg.create_pie_chart(chart_data)
            is_main_score_flag = False
        # Store the figure, canvas key, chart data, and is_main_score flag
        pie_charts.append((canvas_key, fig, chart_data, is_main_score_flag))
    # Second pass: draw all figures (separated from creation)
    for canvas_key, fig, chart_data, is_main_score_flag in pie_charts:
        if canvas_key in window.AllKeysDict:
            canvas_elem = window[canvas_key]
            plg.draw_figure(canvas_elem, fig, canvas_key, chart_data, window, is_main_score_flag)

def main_score_graph_popup(window, chart_data):
    print('pie_charts[0]: ', pie_charts[0])
    _, figure, chart_data, is_main_score = pie_charts[0]
    canvas_key_new = "-MAINSCORE-WINDOW-"
    canvas_elem = window[canvas_key_new]
    plg.draw_figure(canvas_elem, figure, canvas_key_new, chart_data, window, is_main_score)

def update_risk_window(main_window, selected_coin, currency_choice):
    if len(pie_charts) > 10:
        pie_charts.clear()
    warning_image, _ = get_warning_image(selected_coin[23])
    
    main_window['-LOGO-'].update(data=img.get_image(selected_coin[7]), size=(100, 100))
    main_window['-RANK-'].update(value=f'#{selected_coin[0]}')
    main_window['-NAME-'].update(value=selected_coin[1][:13])
    main_window['-SYMB-'].update(value=selected_coin[8])
    main_window['-DATE-'].update(value=f'Date: {selected_coin[10]}')
    main_window['-DESC-'].update(value=f'{selected_coin[9]}')
    main_window['-WARNING-IMG-'].update(filename=warning_image)
    main_window['-PRICE-LABEL-'].update(f'Price ({currency_choice}): {selected_coin[2]}')
    main_window['-MCAP-LABEL-'].update(f'Market Cap ({currency_choice}): {selected_coin[6]}')
    
def get_warning_image(total_score):
    if not isinstance(total_score, int):
        total_score = int(total_score)

    print('this is total score: ',total_score)
    if total_score >= 70:
        warning_image = 'app/assets/images/ref-good.png'
        warning_message = 'Low Risk'
    elif total_score > 50:
        warning_image = 'app/assets/images/ref-warning.png'
        warning_message = 'Med-Low Risk'
    elif total_score > 30:
        warning_image = 'app/assets/images/ref-warning.png'
        warning_message = 'Med-High Risk'
    elif total_score >= 0:
        warning_image = 'app/assets/images/ref-danger.png'
        warning_message = 'High Risk'
    return warning_image, warning_message

def main_score_window(chart_data):
    HEADLINE_FONT = ("Helvetica", 20, "bold")
    BODY_FONT     = ("Calibri",   12, "bold")
    MAIN_DESC     = ("Calibri",   15)
    CATEGORY_FONT = ("Calibri",   14, "bold")
    BODY_FONT_COLOR = '#8e8e8e'
    exit_arrow = 'app/assets/images/right-arrow.png'

    score = [
        [  
            sg.Canvas(
                key="-MAINSCORE-WINDOW-", 
                size=(75, 75), 
                tooltip='Overall Assessment Score',
                background_color='#F0F0F0')
        ]
    ]
    
    low_risk_box = [
        [
            sg.Text('', size=(4, 2), background_color='#07DB07', border_width=0, relief='solid', pad=((0, 0), 0)),
            sg.Text('', size=(4, 2), background_color='#39D70B', border_width=0, relief='solid', pad=((0, 0), 0)),
            sg.Text('', size=(4, 2), background_color='#76D210', border_width=0, relief='solid', pad=((0, 0), 0))
        ],
        [
            sg.Text('Low Risk', font=CATEGORY_FONT, text_color='#07DB07', pad=((0, 0), 0))
        ],
        [
            sg.Text('80-100', font=CATEGORY_FONT, pad=((0, 0), 0))
        ]
    ]

    low_medium_risk_box = [
        [
            sg.Text('', size=(4, 2), background_color='#AECD15', border_width=0, relief='solid', pad=((32, 0), 0)),
            sg.Text('', size=(4, 2), background_color='#FFC61B', border_width=0, relief='solid', pad=((0, 0), 0)),
            sg.Text('', size=(4, 2), background_color='#F0F0F0', border_width=0, relief='solid', pad=((0, 0), 0))
        ],
        [
            sg.Text('Low-Medium Risk', font=CATEGORY_FONT, text_color='#AECD15', pad=((30, 0), 0))
        ],
        [
            sg.Text('60-79', font=CATEGORY_FONT, pad=((30, 0), 0))
        ]
    ]

    medium_high_risk_box = [
        [
            sg.Text('', size=(4, 2), background_color='#F7A516', border_width=0, relief='solid', pad=((32, 0), 0)),
            sg.Text('', size=(4, 2), background_color='#EE8311', border_width=0, relief='solid', pad=((0, 0), 0)),
            sg.Text('', size=(4, 2), background_color='#F0F0F0', border_width=0, relief='solid', pad=((0, 0), 0))
        ],
        [
            sg.Text('Medium-High Risk', font=CATEGORY_FONT, text_color='#F7A516', pad=((30, 0), 0))
        ],
        [
            sg.Text('40-59', font=CATEGORY_FONT, pad=((30, 0), 0))
        ]
    ]

    high_risk_box = [
        [
            sg.Text('', size=(4, 2), background_color='#E45D0C', border_width=0, relief='solid', pad=((32, 0), 0)),
            sg.Text('', size=(4, 2), background_color='#DB3807', border_width=0, relief='solid', pad=((0, 0), 0)),
            sg.Text('', size=(4, 2), background_color='#da3200', border_width=0, relief='solid', pad=((0, 0), 0))
        ],
        [
            sg.Text('High Risk', font=CATEGORY_FONT, text_color='#E45D0C', pad=((30, 0), 0))
        ],
        [
            sg.Text('1-39', font=CATEGORY_FONT, pad=((30, 0), 0))
        ]
    ]

    assessment_guide_box = [
        [
            sg.Column(low_risk_box, pad=((0, 32), (0, 0))),
            sg.VerticalSeparator(),
            sg.Column(low_medium_risk_box, pad=((0, 32), (0, 0))),
            sg.VerticalSeparator(),
            sg.Column(medium_high_risk_box, pad=((0, 32), (0, 0))),
            sg.VerticalSeparator(),
            sg.Column(high_risk_box, pad=((0, 0), (0, 0)))
        ]
    ]

    
    layout = [
        [
            sg.Text('Overall Assessment Score', font=HEADLINE_FONT, pad=((30, 0), (20, 0))), 
            sg.Push(), 
            sg.Image(exit_arrow, pad=((0, 30), (20, 0)), enable_events=True, key='-EXIT-')
        ],
        [
            sg.Text('The overall assessment based on the score categories', font=BODY_FONT, text_color=BODY_FONT_COLOR, pad=((30, 0), (0, 0))), 
            sg.Push()
        ],
        [sg.HorizontalSeparator(pad=((30, 30), (10, 0)))],
        [
            sg.Column(score, pad=((25, 0), (20, 0))),
            sg.Push(),
            sg.Text(get_main_desc(pie_charts[0][2]), size=(45, 10), font=MAIN_DESC,
                    pad=((0, 20), (0, 0)))
        ],
        [
            sg.Push(),
            sg.Column(assessment_guide_box, pad=((0, 0), (60, 0))),
            sg.Push()
        ]
    ]

    window = sg.Window(
        "Assessment Score Guide",
        layout,
        size=(850, 650),
        modal=True,
        keep_on_top=True,
        finalize=True,
        no_titlebar=True
    )
    main_score_graph_popup(window, chart_data)

    return window

def sub_score_window(chart_data, chart_key):
    HEADER_CATEGORY_FONT = ("Helvetica", 20, 'bold')
    CATEGORY_FONT = ("Helvetica", 12)
    BODY_FONT     = ("Courier New", 14)    
    
    title, low_desc, mid_desc, high_desc = descriptions[chart_key]
    exit_arrow = 'app/assets/images/right-arrow.png'
    
    score_chart = int(chart_data)*10
    
    warning_image, warning_message = get_warning_image(score_chart)
    print('score_chart', score_chart)
    if score_chart >= 70:
        category_desc = low_desc
    elif score_chart > 50:
        category_desc = mid_desc
    elif score_chart > 30:
        category_desc = mid_desc
    elif score_chart >= 0:
        category_desc = high_desc
    else:
        category_desc = 'No Data Available.'

    layout = [
        [
            sg.Text(title, font=HEADER_CATEGORY_FONT, pad=((30, 0), (30, 0))),
            sg.Text('',pad=((0, 0), (30, 0)), expand_x=True),
        ],
        [
            sg.Image(warning_image,pad=((30, 0), (10, 0))),
            sg.Text(warning_message, font=CATEGORY_FONT, pad=((5, 0), (10, 0))),
            sg.Text('',pad=((0, 0), (30, 0)), expand_x=True)
        ],

        [
            sg.Text(category_desc, font=BODY_FONT, justification="left", pad=((50, 0), (10, 0)), size=(48, 10))
        ],

        [
            sg.Text('',pad=((0, 0), (0, 0)), expand_x=True),
            sg.Image(exit_arrow, pad=((0, 30), (0, 0)), enable_events=True, key='-EXIT-')
        ]
    ]

    window = sg.Window(
        "Assessment Score Guide",
        layout,
        size=(650, 400),
        modal=True,
        keep_on_top=True,
        finalize=True,
        no_titlebar=True
    )

    return window

def marquee_effect(main_window, marquee_texts):
    for i, text in enumerate(marquee_texts):
        # Scroll one step to the left
        scrolled_text = text[1:] + text[0]
        marquee_texts[i] = scrolled_text  # Save new state
        main_window[f'-CATEGORY{i}-'].update(scrolled_text)

def score_window(data):
    # crypto icon/logo
    logo = [
        [
            sg.Image(img.get_image(data[0][7]), size=(100, 100), key='-LOGO-',
                     background_color='#F8F8F8')
        ]
    ]
    image_box = [
        [
            sg.Column(logo, pad=((0, 0),(0, 0)))
        ]
    ]
    ranking_text = [
        [ 
            sg.Text(f"#{data[0][0]}",           # crypto ranking
            font='Any 12 bold',
            pad=((0, 0), (0, 0)),
            text_color="#686868",
            key='-RANK-')
        ]
    ]
    ranking_container = [
        [
            sg.Column(ranking_text, pad=((0, 0), (0, 0)))
        ]
    ]

    ranking_box = [
        [
            sg.Column(ranking_container, pad=((15, 0), (9, 0)))
        ]
    ]
    warning_image, _ = get_warning_image(data[0][23])
    name = [
        [
            sg.Text(data[0][1],                   # crypto name
            font='Any 24 bold',
            key='-NAME-',
            pad=((0, 0), (0, 55))),

            sg.Text(data[0][8],                   # crypto symbol
            font='Any 12 bold',
            text_color='#a1a3a6',
            pad=((3, 0), (0, 70)),
            key='-SYMB-'),

            sg.Image(
                warning_image, 
                size=(30, 30), 
                key='-WARNING-IMG-', 
                pad=((3, 0), (0, 72))
            )
        ]
    ]

    date_text = [
        [
            sg.Text(f'Date: {data[0][10]}',   # date added
            font='Any 12 bold',
            text_color='#a1a3a6',
            pad=((0, 0), (0, 0)),
            key='-DATE-')  
        ]
    ]

    date_box = [
        [
            sg.Column(date_text, pad=((0, 0),(0, 0)))
        ]
    ]

    price_text = [
        [
            sg.Text(f'Price (USD): {data[0][2]}',   # date added
                font='Any 12 bold',
                text_color='#a1a3a6',
                pad=((0, 0), (0, 0)),
                key='-PRICE-LABEL-') 
        ]
    ]

    price_box = [
        [
           sg.Column(price_text, pad=((0, 0),(0, 0))) 
        ]   
    ]

    mcap_text = [
        [
            sg.Text(f'Market Cap (USD): {data[0][6]}',   # date added
                font='Any 12 bold',
                text_color='#a1a3a6',
                pad=((0, 0), (0, 0)),
                key='-MCAP-LABEL-')             
        ]
    ]

    mcap_box = [
        [
            sg.Column(mcap_text, pad=((0, 0),(0, 0)))
        ]
    ]

    information_box = [
        [
            sg.Column(ranking_box, size=(65, 50), pad=((0, 0),(0, 0))),
            sg.Column(name, size=(350, 50), pad=((0, 0),(0, 0)))
        ],
        [
            sg.Column(price_box, size=(250, 28), pad=((18, 0),(0, 0))),
            sg.Column(date_box, size=(150, 28), pad=((0, 0),(0, 0)))
        ],
        [
            sg.Column(mcap_box, size=(400, 28), pad=((18, 0),(0, 0)))
        ]

    ]

    hyperlink = [
        [
            sg.Image(filename='app/assets/images/hyperlink.png', 
                    size=(30, 30), 
                    pad=((0, 0),(0, 0)), 
                    enable_events=True, 
                    key='-HYPERLINK-',
                    tooltip="Click to visit website")
        ]
    ]

    description_box = [
        [
            sg.Text(f'{data[0][9]}',
            font=('Courier New', 12),
            size=(51, 10),
            auto_size_text=False,
            justification='left',
            pad=((10, 0), (0, 0)),
            key='-DESC-')
        ]

    ]
    #crypto info name/symbol/rank/desc

    upper_info = [
        [
            sg.Column(image_box, pad=((0, 0), (0, 0))),
            sg.Column(information_box, pad=((0, 0), (0, 0))),
            sg.Column(hyperlink, pad=((0, 0), (0, 70)))
        ]
    ]

    lower_info = [
        [
            sg.Column(description_box, element_justification='left', size=(550, 290), pad=((0, 0), (0, 0)))
        ]   
    ]

    info_container = [
        [sg.Column(upper_info, size=(620, 115))],   
        [sg.Column(lower_info, size=(620, 190))]
    ]


    info = [
        [
            sg.Column(info_container,size=(615, 330), pad=((0, 0), (0, 0)))
        ]

    ]
    
    assessment_score = [
        # donut graphs scores
        sg.Canvas(key=f"-SCORE{i+1}-", size=(80, 80), tooltip=descriptions[f"-SCORE{i+1}-"][0])
        for i in range(10)
    ]
    criteria_text = [
        [
            sg.Text(
                '',
                font='Any 12 bold',
                size=(26, 1),
                key=f'-CATEGORY{i}-'
            )
        ]
        for i in range(10)
    ]

    score = [
                [
                    sg.Canvas(
                        key="-MAINSCORE-", 
                        size=(75, 75), 
                        tooltip='Overall Assessment Score')
                ]
            ]

    score_labels_width = 180
    score_labels_height = 30

    up_pads = [(0, 0), (3, 0), (6, 0), (6, 0), (0, 0)]

    score_labels_upper = [[
        sg.Column(
            [criteria_text[i]],
            background_color='#ffffff',
            size=(score_labels_width, score_labels_height),
            pad=(up_pads[i], (0, 0))
        )
        for i in range(5)
    ]]

    d_pads = [(0, 0), (3, 0), (6, 0), (6, 0), (0, 0)]

    score_labels_lower = [[
        sg.Column(
            [criteria_text[i]],
            background_color='#ffffff',
            size=(score_labels_width, score_labels_height),
            pad=(d_pads[i - 5], (0, 0))
        )
        for i in range(5, 10)
    ]]

    upper_content = [
        [
            sg.Text('', expand_x=True),
            sg.Text('Overall Assessment Score',pad=((0, 25), (0, 0)), font=("Helvetica", 16, "bold"))
        ],
        [
            sg.Column(info, pad=((0, 0), (0, 0))),
            sg.Column(score, pad=((0, 0), (0, 0)),element_justification='center')
        ]
    ]


    lower_content = [
        [
            sg.Column(score_labels_upper, pad=((0, 0), (0, 0)), background_color='#ffffff')
        ],
        [
            sg.Column(
            [assessment_score[:5]],
            pad=((0, 0), (0, 0)))
        ],
        [
            sg.Column(score_labels_lower, pad=((0, 0), (0, 0)),background_color='#ffffff')
        ],
        [
            sg.Column(
            [assessment_score[5:]],
            pad=((0, 0), (0, 0))
            )
        ]
    ]

    upper_window = [
        [
            sg.Column(
            upper_content, pad=((0, 0), (0, 0)))
        ]
    ]

    lower_window = [
        [
            sg.Column(
            lower_content, pad=((0, 0), (0, 0)))
        ]
    ]

    layout = upper_window + lower_window

    return layout


    