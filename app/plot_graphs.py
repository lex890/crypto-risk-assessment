import FreeSimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

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

# Create the pie chart figure
def create_pie_chart(score_data, figsize=(1.75, 1.75)):
    if (figsize == (3, 3)): # Used for the main score
        scores = [int(x) for x in score_data]
        value = round(sum(scores) / 10)
        fontsize_category = 12
        fontsize_score = 32
    else: # Used for individual scores and the score info window
        value = int(score_data)
        fontsize_category = 8
        fontsize_score = 16

    remainder = 10 - value
    match value:
        case 10:
            category = "Low Risk"
            color = "#07DB07"
            image_warning = 'app/assets/images/good.png'
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
    centre_circle = plt.Circle((0, 0), 0.80, fc='white')
    ax.add_artist(centre_circle)
    # score in digit
    ax.text(0, 0.1, f'{value}', ha='center', va='center', fontsize=fontsize_score, weight='bold')

    # score category
    ax.text(0, -0.30, category, ha='center', va='center', fontsize=fontsize_category)
    ax.axis('equal')
    fig.tight_layout()
    return fig