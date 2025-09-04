import FreeSimpleGUI as sg
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import math

figure_canvas_agg_dict = {}
score_data_for_canvas = {}
pie_charts = []

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

def get_score_category(value, scale=100):
    print('Raw score:', value)

    # Clamp score to valid range
    if scale == 100:
        value = max(0, min(value, 100))
        norm = value // 10
    elif scale == 10:
        value = max(0, min(value, 10))
        norm = value  # No division needed

    print(f'Normalized (scale={scale}):', norm)

    match norm:
        case 10:
            category = "Low Risk"
            color = "#07DB07"
        case 9:
            category = "Low Risk"
            color = '#39D70B'
        case 8:
            category = "Low Risk"
            color = '#76D210'            
        case 7:
            category = "Low-Medium Risk"
            color = "#AECD15"
        case 6:
            category = "Low-Medium Risk"
            color = "#FFC61B"
        case 5:
            category = "Medium-High Risk"
            color = "#F7A516"
        case 4:
            category = "Medium-High Risk"
            color = "#F77A16"
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
        case _:
            category = "Unknown"
            color = "#000000"

    return category, color

# Create the pie chart figure
def create_pie_chart(score_data, figsize=(3, 3)):
    get_score = int(float(score_data))
    print('get_score', get_score)
    value = min(get_score, 100)
    fontsize_category = 13
    fontsize_score = 40
    category, _ = get_score_category(value, scale=100)
    remainder = 100 - value

    sizes = [20,20,20,20,20,remainder]
    fig, ax = plt.subplots(figsize=figsize, facecolor='#ffffff')
    ax.pie(sizes,
           startangle=90,
           colors=['#ef476f', '#ffd166', '#06d6a0', '#118ab2', '#2e4e5a', "#f5f5f5"])
    centre_circle = plt.Circle((0, 0), 0.85, fc='#ffffff')
    ax.add_artist(centre_circle)
    # score in digit
    ax.text(0, 0.1, f'{value}', ha='center', va='center', fontsize=fontsize_score,  fontfamily='Verdana')
    # score category
    ax.text(0, -0.30, category, ha='center', va='center', fontsize=fontsize_category, fontfamily='monospace')
    ax.text(0, -0.50, 'See Details', ha='center', va='center', fontsize=8, fontfamily='monospace', color="#7C7C7C", fontweight='bold')
    ax.axis('equal')
    fig.tight_layout()
    return fig



