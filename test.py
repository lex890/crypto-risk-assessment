import FreeSimpleGUI as sg
from app.get_images import get_image
from app.csv_handler import *
from app.main_screen import get_percent_data

headings, data = read_csv('app/assets/data/data.csv')

layout = []

# Step 1: Create layout with placeholder values
for i in range(14):
    row = [
        sg.Text(data[i][0], key=f'-rank{i}-', font=('Helvetica', 12), size=(5, 1), justification='right', enable_events=True),
        sg.Image(get_image(data[i][7], 1)),
        sg.Text(data[i][1], key=f'-name{i}-', font=('Helvetica', 12), size=(13, 1)),
        sg.Text(data[i][2], key=f'-price{i}-', font=('Helvetica', 12), size=(10, 1), justification='right'),
        sg.Text('', key=f'-1h{i}-', font=('Helvetica', 12), size=(5, 1), justification='right'),
        sg.Text('', key=f'-24h{i}-', font=('Helvetica', 12), size=(5, 1), justification='right'),
        sg.Text('', key=f'-7d{i}-', font=('Helvetica', 12), size=(5, 1), justification='right'),
        sg.Text(data[i][6], key=f'-mcap{i}-', font=('Helvetica', 12), size=(17, 1), justification='right')
    ]
    layout.append(row)

# Navigation
next = 'app/assets/images/arrow-right-icon.png'
prev = 'app/assets/images/arrow-left-icon.png'
nav_buttons = [
    [
        sg.Image(prev),
        sg.Text('1'),
        sg.Image(next)
    ]
]
layout.append(nav_buttons)

# Step 2: Create the window
window = sg.Window("Marquee Demo", layout, finalize=True)

# Step 3: Now update the percent data using the window object
for i in range(14):
    percent_text = get_percent_data(data[i][3], f'-1h{i}-', window)
    window[f'-1h{i}-'].update(percent_text)
    percent_text = get_percent_data(data[i][4], f'-24h{i}-', window)
    window[f'-24h{i}-'].update(percent_text)
    percent_text = get_percent_data(data[i][5], f'-7d{i}-', window)
    window[f'-7d{i}-'].update(percent_text)

# Event loop
while True:
    event, values = window.read(timeout=100)
    if event == sg.WIN_CLOSED:
        break
    if event.startswith('-rank'):
        row_index = int(event.replace('-rank', '').replace('-', ''))
        print(f"You clicked on row {row_index}")
        print("Row data:", data[row_index])
        # You can do something specific for this row
window.close()
