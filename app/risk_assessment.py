import FreeSimpleGUI as sg
import matplotlib.pyplot as plt
from . import get_images as img
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

sg.theme('LightGrey1')

figure_canvas_agg_dict = {}
score_data_for_canvas = {}

def draw_figure(canvas_elem, figure, key, data_for_chart, window, is_main_score=False): 
    canvas = canvas_elem.TKCanvas
    if key in figure_canvas_agg_dict:
        figure_canvas_agg_dict[key].get_tk_widget().forget()
        plt.close('all')  # close previous matplotlib figures

    # Draw new figure
    figure_canvas_agg = FigureCanvasTkAgg(figure, master=canvas)
    figure_canvas_agg.draw()
    widget = figure_canvas_agg.get_tk_widget()
    widget.pack(side='top', fill='both', expand=1)

    widget.configure(cursor="hand2")

    # Store the data and is_main_score status associated with this key
    score_data_for_canvas[key] = {'data': data_for_chart, 'is_main': is_main_score}

    # to allow Canvas Component to be clickable
    def on_click(event, canvas_key=key):
        print('Canvas Key: ',canvas_key)
        if (canvas_key == '-MAINSCORE-'):
            window.write_event_value('-MAIN-CLICKED-', canvas_key)
        else:
            window.write_event_value('-SCORE-CLICKED-', canvas_key)

    widget.bind("<Button-1>", on_click)
    # Store reference
    figure_canvas_agg_dict[key] = figure_canvas_agg

# Helper function to draw a matplotlib figure on a PySimpleGUI Canvas element
def draw_figure_on_sg_canvas(canvas_elem, figure):
    # This is a generic function to draw a figure on any PySimpleGUI Canvas
    # It ensures the canvas is cleared before drawing a new figure
    for child in canvas_elem.TKCanvas.winfo_children():
        child.destroy()
    figure_canvas_agg = FigureCanvasTkAgg(figure, master=canvas_elem.TKCanvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


# Create the pie chart figure
def create_pie_chart(score_data, figsize=(1.75, 1.75)):
    if (figsize == (3, 3)): # Used for the main score
        scores = [int(x) for x in score_data]
        value = round(sum(scores) / 10)
        fontsize_category = 12
        fontsize_score = 40
    else: # Used for individual scores and the score info window
        value = int(score_data)
        fontsize_category = 8
        fontsize_score = 16

    remainder = 10 - value
    match value:
        case 10:
            category = "Low Risk"
            color = "#07DB07"
        case 9:
            category = "Low Risk"
            color = "#39D70B"
        case 8:
            category = "Low Risk"
            color = "#76D210"
        case 7:
            category = "Low-Mid Risk"
            color = "#AECD15"
        case 6:
            category = "Mid Risk"
            color = "#FFC61B"
        case 5:
            category = "Mid Risk"
            color = "#F7A516"
        case 4:
            category = "Mid Risk"
            color = "#EE8311"
        case 3:
            category = "High Risk"
            color = "#E45D0C"
        case 2:
            category = "High Risk"
            color = "#DB3807"
        case 1:
            category = "High Risk" 
            color = "#DB3807"
        case 0:
            category = "No Data Available"
            color = "#DDDDDD"

        

    sizes = [value, remainder]
    fig, ax = plt.subplots(figsize=figsize, facecolor='none')
    ax.pie(sizes,
           startangle=90,
           colors=[color, "#EEEEEE"])
    centre_circle = plt.Circle((0, 0), 0.70, fc='white')
    ax.add_artist(centre_circle)
    # score in digit
    ax.text(0, 0.1, f'{value}', ha='center', va='center', fontsize=fontsize_score, weight='bold')

    # score category
    ax.text(0, -0.30, category, ha='center', va='center', fontsize=fontsize_category)
    ax.axis('equal')
    fig.tight_layout()
    return fig

def risk_assessment_window(window, data, row=0):
    score_data = data[row]

    for i in range(11):
        canvas_key = f'-SCORE{i}-' if i > 0 else '-MAINSCORE-'

        if canvas_key == '-MAINSCORE-':
            chart_data = score_data[13:23] # This is the data used for the main score
            fig = create_pie_chart(chart_data, figsize=(3, 3))
            is_main_score_flag = True
        else:
            chart_data = score_data[13 + (i - 1)] # Data for individual score
            fig = create_pie_chart(chart_data)
            is_main_score_flag = False

        if canvas_key in window.AllKeysDict:
            canvas_elem = window[canvas_key]

            draw_figure(canvas_elem, fig, canvas_key, chart_data, window, is_main_score_flag) # Pass data and flag


def update_risk_window(main_window, selected_row):
    main_window['-LOGO-'].update(data=img.get_image(selected_row[7]), size=(100, 100))
    main_window['-RANK-'].update(value=f'#{selected_row[0]}')
    main_window['-NAME-'].update(value=selected_row[1])
    main_window['-SYMB-'].update(value=selected_row[8])
    main_window['-DATE-'].update(value=f'Date Added: {selected_row[10]}')
    main_window['-DESC-'].update(value=f'Description: {selected_row[9]}')

def score_window(data, headings):
    # crypto icon/logo
    logo = [[sg.Image(img.get_image(data[0][7]), size=(100, 100), key='-LOGO-')]]
    #crypto info name/symbol/rank/desc
    info = [
        [
         sg.Text(f"#{data[0][0]}",           # crypto ranking
           font='Any 12 bold',
           pad=((10, 0), (13, 0)),
           text_color="#686868",
           key='-RANK-'),

         sg.Text(data[0][1],                   # crypto name
           font='Any 24 bold',
           key='-NAME-',
           pad=((5, 0), (20, 0))),

         sg.Text(data[0][8],                   # crypto symbol
           font='Any 12 bold',
           text_color='#a1a3a6',
           pad=((3, 0), (20, 5)),
           key='-SYMB-'),

         sg.Push(),
         sg.Text(f'Date Added: {data[0][10]}',   # date added
           font='Any 12 bold',
           text_color='#a1a3a6',
           pad=((0, 0), (0, 25)),
           key='-DATE-')
        ],

        [sg.Text(f'{data[0][9]}',   # crypto desc
           background_color="#fefefe",
           font=('Courier New', 12),
           size=(50, 12),
           auto_size_text=False,
           justification='left',
           pad=((40, 0), (15, 5)),
           key='-DESC-')]
    ]
    assessment_criteria = headings[13:23]
    print(assessment_criteria)
    
    assessment_score = [
        # donut graphs scores
        sg.Canvas(key=f"-SCORE{i+1}-", background_color=sg.theme_background_color(), size=(150, 150), expand_y=True, tooltip=assessment_criteria[i])
        for i in range(10)
    ]

    score = [[sg.Canvas(key="-MAINSCORE-", background_color=sg.theme_background_color(), size=(300, 300), tooltip='Overall Assessment Score')]]  # fix canvas space

    upper_content = [
        [
            sg.Column(logo, element_justification='center', vertical_alignment='top'),
            sg.Column(info, element_justification='left', vertical_alignment='top', size=(560, 306)),
            sg.Column(score, element_justification='center', vertical_alignment='top')
        ]
    ]

    upper_window = [
        [
            sg.Column(
            upper_content,
            pad=(0, (0, 50)),
            background_color="#f5f5f5")
        ]
    ]

    lower_window = [
        [
             sg.Column(
             [assessment_score[:5]],
             pad=((0, 0), 0),
             background_color='#f5f5f5')
        ],

        [
             sg.Column(
             [assessment_score[5:]],
             pad=((0, 0), 0),
             background_color="#f5f5f5")
        ]
    ]

    layout = upper_window + lower_window

    return layout


    