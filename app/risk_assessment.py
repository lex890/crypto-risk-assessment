import FreeSimpleGUI as sg
from . import get_images as img
from . import plot_graphs as plg

sg.theme('LightGrey1')

def risk_assessment_window(window, data, row=0):
    if row < len(data):
        score_data = data[row] if data[row] else data[-1]
    else:
        score_data = data[-1]
    pie_charts = []  # Prepare list to hold all charts to update in batch

    #iterate through the score data to create pie charts
    for i in range(11):
        canvas_key = f'-SCORE{i}-' if i > 0 else '-MAINSCORE-'

        if canvas_key == '-MAINSCORE-':
            chart_data = score_data[-1]  # Main score uses 10 values
            fig = plg.create_pie_chart(chart_data, figsize=(3, 3))
            is_main_score_flag = True
        else:
            chart_data = score_data[13 + (i - 1)]  # Individual scores
            fig = plg.create_pie_chart(chart_data)
            is_main_score_flag = False
        # Store the figure, canvas key, chart data, and is_main_score flag
        pie_charts.append((canvas_key, fig, chart_data, is_main_score_flag))

    # Second pass: draw all figures (separated from creation)
    for canvas_key, fig, chart_data, is_main_score_flag in pie_charts:
        if canvas_key in window.AllKeysDict:
            canvas_elem = window[canvas_key]
            plg.draw_figure(canvas_elem, fig, canvas_key, chart_data, window, is_main_score_flag)

def update_risk_window(main_window, selected_row, currency_choice):
    main_window['-LOGO-'].update(data=img.get_image(selected_row[7]), size=(100, 100))
    main_window['-RANK-'].update(value=f'#{selected_row[0]}')
    main_window['-NAME-'].update(value=selected_row[1])
    main_window['-SYMB-'].update(value=selected_row[8])
    main_window['-DATE-'].update(value=f'Date: {selected_row[10]}')
    main_window['-DESC-'].update(value=f'{selected_row[9]}')
    main_window['-WARNING-IMG-'].update(filename=get_warning_image(selected_row[23]))
    main_window['-PRICE-LABEL-'].update(f'Price ({currency_choice}): {selected_row[2]}')
    main_window['-MCAP-LABEL-'].update(f'Market Cap ({currency_choice}): {selected_row[6]}') 

def get_warning_image(total_score):
    total_score = int(total_score)
    print('this is total score: ',total_score)
    if total_score >= 75:
        warning_image = 'app/assets/images/good.png'
    elif total_score >= 40:
        warning_image = 'app/assets/images/warning.png'
    elif total_score >= 0:
        warning_image = 'app/assets/images/danger.png'
    return warning_image

def get_warning_msg(total_score):
    total_score = int(total_score)
    if total_score >= 75:
        warning_msg = 'Good'
    elif total_score >= 40:
        warning_msg = 'Caution'
    elif total_score >= 0:
        warning_msg = 'Warning'
    return warning_msg

def score_window(data, headings):
    # crypto icon/logo
    logo = [
        [
            sg.Image(img.get_image(data[0][7]), size=(100, 100), key='-LOGO-',
                     background_color='#FFFFFF')
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
            sg.Column(ranking_container, pad=((18, 0), (9, 0)))
        ]
    ]

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
            key='-SYMB-')
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
            sg.Column(ranking_box, size=(50, 50), pad=((0, 0),(0, 0))),
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
                    pad=((25, 0),(0, 0)), 
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


    warning_image_box = [
        [
            sg.Image(get_warning_image(data[0][23]), size=(50, 50), key='-WARNING-IMG-', pad=((30, 0), (0, 0))),   
        ]
    ]
    #crypto info name/symbol/rank/desc

    upper_info = [
        [
            sg.Column(image_box, size=(110, 110), pad=((0, 0), (0, 0))),
            sg.Column(information_box, size=(410, 110), pad=((0, 0), (0, 0))),
            sg.Column(warning_image_box, size=(85, 110), pad=((0, 0), (0, 0)))
        ]
    ]

    lower_info = [
        [
            sg.Column(description_box, element_justification='left', size=(550, 290), pad=((0, 0), (0, 0))),
            sg.Column(hyperlink, size=(80, 290), pad=((0, 0), (0, 0)))
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


    assessment_criteria = headings[13:23]
    print(assessment_criteria)
    
    assessment_score = [
        # donut graphs scores
        sg.Canvas(key=f"-SCORE{i+1}-", size=(80, 80), tooltip=assessment_criteria[i])
        for i in range(10)
    ]
    criteria_text = [
        [
            sg.Text(
                assessment_criteria[i],
                font='Any 9 bold',
                size=(26, 1)
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
                ],
                [   
                    sg.Text('Overall Score', font='Any 12 bold')
                ]
            ]  # fix canvas space

    score_labels_width = 180
    score_labels_height = 30

    up_pads = [(0, 0), (3, 0), (6, 0), (6, 0), (0, 0)]

    score_labels_upper = [[
        sg.Column(
            [criteria_text[i]],
            background_color='#F0F0F0',
            size=(score_labels_width, score_labels_height),
            pad=(up_pads[i], (0, 0))
        )
        for i in range(5)
    ]]

    d_pads = [(0, 0), (3, 0), (6, 0), (6, 0), (0, 0)]

    score_labels_lower = [[
        sg.Column(
            [criteria_text[i]],
            background_color='#F0F0F0',
            size=(score_labels_width, score_labels_height),
            pad=(d_pads[i - 5], (0, 0))
        )
        for i in range(5, 10)
    ]]

    upper_content = [
        [
            sg.Column(info),
            sg.Column(score, element_justification='center', vertical_alignment='top')
        ]
    ]


    lower_content = [
        [
            sg.Column(score_labels_upper, pad=((0, 0), (0, 0)), background_color='#F0F0F0')
        ],
        [
            sg.Column(
            [assessment_score[:5]],
            background_color='#f5f5f5', pad=((0, 0), (0, 0)))
        ],
        [
            sg.Column(score_labels_lower, pad=((0, 0), (0, 0)),background_color='#F0F0F0')
        ],
        [
            sg.Column(
            [assessment_score[5:]],
            background_color="#f5f5f5", pad=((0, 0), (0, 0))
            )
        ]
    ]

    upper_window = [
        [
            sg.Column(
            upper_content,
            background_color="#f5f5f5", pad=((70, 0), (0, 0)))
        ]
    ]

    lower_window = [
        [
            sg.Column(
            lower_content,
            background_color="#f5f5f5", pad=((70, 0), (0, 0)))
        ]
    ]

    layout = upper_window + lower_window

    return layout


    