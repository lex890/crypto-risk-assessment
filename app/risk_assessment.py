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
            chart_data = score_data[13:23]  # Main score uses 10 values
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

def update_risk_window(main_window, selected_row):
    main_window['-LOGO-'].update(data=img.get_image(selected_row[7]), size=(100, 100))
    main_window['-RANK-'].update(value=f'#{selected_row[0]}')
    main_window['-NAME-'].update(value=selected_row[1])
    main_window['-SYMB-'].update(value=selected_row[8])
    main_window['-DATE-'].update(value=f'{selected_row[10]}')
    main_window['-DESC-'].update(value=f'{selected_row[9]}')


def get_warning_image(total_score):
    total_score = int(total_score)
    if total_score >= 7:
        warning_image = 'app/assets/images/good.png'
    elif total_score >= 4:
        warning_image = 'app/assets/images/warning.png'
    else:
        warning_image = 'app/assets/images/danger.png'
    return warning_image

def get_warning_msg(total_score):
    total_score = int(total_score)
    if total_score >= 7:
        warning_msg = 'Good'
    elif total_score >= 4:
        warning_msg = 'Caution'
    else:
        warning_msg = 'Warning'
    return warning_msg

def score_window(data, headings):
    # crypto icon/logo
    logo = [
        [
            sg.Image(img.get_image(data[0][7]), size=(100, 100), key='-LOGO-',
                     background_color='#F0F0F0')
        ]
    ]

    ranking = [
        [
            sg.Text(f"#{data[0][0]}",           # crypto ranking
            font='Any 16 bold',
            pad=((10, 0), (0, 40)),
            text_color="#686868",
            key='-RANK-',
            background_color='#F0F0F0')
        ]
    ]

    name = [
        [
            sg.Text(data[0][1],                   # crypto name
            font='Any 24 bold',
            key='-NAME-',
            pad=((5, 0), (0, 40))),

            sg.Text(data[0][8],                   # crypto symbol
            font='Any 12 bold',
            text_color='#a1a3a6',
            pad=((3, 0), (0, 55)),
            key='-SYMB-')
        ]
    ]
    date_box = [
        [
            sg.Text(f'Date: {data[0][10]}',   # date added
            font='Any 12 bold',
            text_color='#a1a3a6',
            pad=((5, 0), (0, 40)),
            key='-DATE-',
            background_color='#F0F0F0')  
        ]
    ]

    price_box = [
        [
            sg.Text(f'Price: {data[0][2]}',   # date added
            font='Any 12 bold',
            text_color='#a1a3a6',
            pad=((5, 0), (0, 40)),
            key='-DATE-',
            background_color='#F0F0F0')             
        ]   
    ]
    hyperlink = [
        [
            sg.Image(filename = 'app/assets/images/hyperlink.png', size=(30, 30), pad=((0, 0),(0, 0)))
        ]
    ]

    information_box = [
        [
            sg.Column(ranking, size=(50, 50)),
            sg.Column(name, size=(350, 50))
        ],
        [
            sg.Column(date_box, element_justification='left', size=(150, 50)),
            sg.Column(price_box, element_justification='left', size=(250, 50)),
        ]
    ]

    description_box = [
        [
            sg.Text(f'{data[0][9]}',   # crypto desc
            background_color="#fefefe",
            font=('Courier New', 12),
            size=(51, 9),
            auto_size_text=False,
            justification='left',
            pad=((0, 0), (0, 0)),
            key='-DESC-')
        ]

    ]


    warning_image_box = [
        [
            sg.Image(get_warning_image(data[0][23]), size=(50, 50), key='-LOGO-', pad=((0, 0), (0, 0))),   
        ],
        [
            sg.Text(get_warning_msg(data[0][23]))
        ]
    ]
    #crypto info name/symbol/rank/desc

    upper_info = [
        [
            sg.Column(logo, size=(110, 110)),
            sg.Column(information_box, size=(430, 110)),
            sg.Column(warning_image_box, size=(65, 100))
        ]
    ]

    lower_info = [
        [
            sg.Column(description_box, element_justification='left', size=(530, 290), background_color='#F0F0F0'),
            sg.Column(hyperlink, size=(80, 280))
        ]   
    ]

    info = [
        [sg.Column(upper_info, size=(630, 115))],   
        [sg.Column(lower_info, size=(630, 400))]

    ]

    assessment_criteria = headings[13:23]
    print(assessment_criteria)
    
    assessment_score = [
        # donut graphs scores
        sg.Canvas(key=f"-SCORE{i+1}-", background_color=sg.theme_background_color(), size=(100, 100), expand_y=True, tooltip=assessment_criteria[i])
        for i in range(10)
    ]
    criteria_text = [
        sg.Text(
                assessment_criteria[i],
                font='Any 8 bold',
                size=(25, 1),
                pad=((0, 10), (0, 0))
        )
        for i in range(10)
    ]

    score = [
                [
                    sg.Canvas(
                        key="-MAINSCORE-", 
                        background_color=sg.theme_background_color(), 
                        size=(80, 80), 
                        tooltip='Overall Assessment Score')
                ],
                [   
                    sg.Text('Overall Score', font='Any 12 bold')
                ]
            ]  # fix canvas space

    upper_content = [
        [
            sg.Column(info, element_justification='left', size=(630, 305)),
            sg.Column(score, element_justification='center', vertical_alignment='top')
        ]
    ]

    upper_window = [
        [
            sg.Column(
            upper_content,
            background_color="#f5f5f5")
        ]
    ]

    lower_window = [
        [
            sg.Column(
               [criteria_text[:5]]
            )
        ],
        [
             sg.Column(
             [assessment_score[:5]],
             background_color='#f5f5f5')
        ],
        [
            sg.Column(
               [criteria_text[5:]],
            )
        ],
        [
             sg.Column(
             [assessment_score[5:]],
             background_color="#f5f5f5")
        ]
    ]

    layout = upper_window + lower_window

    return layout


    