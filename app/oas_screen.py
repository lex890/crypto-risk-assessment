import FreeSimpleGUI as sg
from .score_dict import get_main_desc
from .plot_graphs import pie_charts
# generate OAS
def generate_oas_window():
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
            sg.Text('', size=(4, 2), background_color='#ffffff', border_width=0, relief='solid', pad=((0, 0), 0))
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
            sg.Text('', size=(4, 2), background_color='#F77A16', border_width=0, relief='solid', pad=((0, 0), 0)),
            sg.Text('', size=(4, 2), background_color='#ffffff', border_width=0, relief='solid', pad=((0, 0), 0))
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

    return [
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
            sg.Text(get_main_desc(pie_charts[0][2]), size=(45, 10), font=MAIN_DESC,pad=((0, 20), (0, 0)))
        ],
        [
            sg.Push(),
            sg.Column(assessment_guide_box, pad=((0, 0), (60, 0))),
            sg.Push()
        ]
    ]