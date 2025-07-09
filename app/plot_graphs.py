import FreeSimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

figure_canvas_agg_dict = {}
score_data_for_canvas = {}

def render_figure(canvas_elem, figure, key):
    canvas = canvas_elem.TKCanvas
    # Remove old figure if it exists
    if key in figure_canvas_agg_dict:
        old_agg = figure_canvas_agg_dict[key]
        old_agg.get_tk_widget().forget()
        plt.close(old_agg.figure)

    # Draw and pack new figure
    figure_canvas_agg = FigureCanvasTkAgg(figure, master=canvas)
    figure_canvas_agg.draw()
    widget = figure_canvas_agg.get_tk_widget()
    widget.configure(cursor="hand2", bg="#f9f9f9")
    widget.pack(side='top', fill='both', expand=False)
    # Store reference to the figure canvas
    figure_canvas_agg_dict[key] = figure_canvas_agg
    return widget

def bind_chart_click(widget, key, window):
    def on_click(event, canvas_key=key):
        # Put both the key and the widget inside a dict (or tuple)
        payload = {
            "key": canvas_key,
            "widget": event.widget          # or just `widget`
        } 
        tag = "-MAIN-CLICKED-" if canvas_key == "-MAINSCORE-" else "-SCORE-CLICKED-"
        window.write_event_value(tag, payload)

    widget.bind("<Button-1>", on_click)

def update_chart_state(figure, key, data_for_chart, is_main_score):
    score_data_for_canvas[key] = {
        "figure": figure,
        "data":   data_for_chart,
        "is_main": is_main_score,
    }

def draw_figure(canvas_elem, figure, key, data_for_chart, window, is_main_score=False):
    widget = render_figure(canvas_elem, figure, key)
    bind_chart_click(widget, key, window)
    update_chart_state(figure, key, data_for_chart, is_main_score)

def get_score_category(value):
    
    print('values:', value)
    if value > 10:
        value = (math.ceil(value / 10) * 10) // 10
    print('new values:', value)
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
            category = "Low-Med Risk"
            color = "#AECD15"
        case 6:
            category = "Low-Med Risk"
            color = "#FFC61B"
        case 5:
            category = "High-Med Risk"
            color = "#F7A516"
        case 4:
            category = "High-Med Risk"
            color = "#EE8311"
        case 3:
            category = "High Risk"
            color = "#E45D0C"
        case 2:
            category = "High Risk"
            color = "#DB3807"
        case 1:
            category = "High Risk" 
            color = "#da3200"
        case 0:
            category = "No Rating"
            color = "#DDDDDD"
    return category, color

# Create the pie chart figure
def create_pie_chart(score_data, figsize=(1.75, 1.75)):
    get_score = int(score_data)
    
    if (figsize == (3, 3)): # Used for the main score
        value = min(get_score, 100) 
        fontsize_category = 12
        fontsize_score = 32
        category, color = get_score_category(value)
        remainder = 100 - value
        centre_color = '#ffffff'
        graph_bg = '#ffffff'
    else: # Used for individual scores and the score info window
        value = get_score
        fontsize_category = 8
        fontsize_score = 16
        category, color = get_score_category(value)
        remainder = 10 - value
        centre_color = '#ffffff'
        graph_bg = '#ffffff'
    
    sizes = [value, remainder]
    fig, ax = plt.subplots(figsize=figsize, facecolor=graph_bg)
    ax.pie(sizes,
           startangle=90,
           colors=[color, "#EEEEEE"])
    centre_circle = plt.Circle((0, 0), 0.80, fc=centre_color)
    ax.add_artist(centre_circle)
    # score in digit
    ax.text(0, 0.1, f'{value}', ha='center', va='center', fontsize=fontsize_score, weight='bold')

    # score category
    ax.text(0, -0.30, category, ha='center', va='center', fontsize=fontsize_category)
    ax.axis('equal')
    fig.tight_layout()
    return fig



