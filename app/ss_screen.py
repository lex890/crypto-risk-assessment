import FreeSimpleGUI as sg
from .score_dict import get_category_desc

def generate_subscr_window(category, score):
    HEADER_CATEGORY_FONT = ("Helvetica", 20, 'bold')
    BODY_FONT            = ("Segoe UI", 14) 

    title, desc = get_category_desc(category, score)

    return [
        [
            sg.Text(title, font=HEADER_CATEGORY_FONT, pad=((30, 0), (40, 10))),
            sg.Push()
        ],
        [
            sg.Text(desc, font=BODY_FONT, justification="left", pad=((50, 0), (10, 0)), size=(48, 9))
        ],

        [
            sg.Text('',pad=((0, 0), (0, 0)), expand_x=True),
            sg.Image('app/assets/images/right-arrow.png', pad=((0, 30), (0, 0)), enable_events=True, key='-EXIT-')
        ]
    ]