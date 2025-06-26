import FreeSimpleGUI as sg
import app.get_images as g_img

url = 'https://s2.coinmarketcap.com/static/img/coins/64x64/1.png'
img_data = g_img.get_image(url, 1)
crypto_data = ['1', 'Bitcoin', '107,015.48', '0.01', '1.60', '2.54', '2,149,004,817,947']
crypto_layout = [
  [
    sg.Text(crypto_data[0], font=('Hevetica', 12), key='-CRYPTO-RANK-',background_color='#F0F0F0', pad=((0, 0), (0, 0))),
    sg.Image(img_data),
    sg.Text(crypto_data[1], font=('Hevetica', 12), key='-CRYPTO-NAME-',background_color='#F0F0F0', pad=((0, 0), (0, 0))),
    sg.Text(crypto_data[2], font=('Hevetica', 12), key='-CURRENT-PRICE-',background_color='#F0F0F0', pad=((0, 0), (0, 0))),
    sg.Text(crypto_data[3], font=('Hevetica', 12), key='-1HOUR-',background_color='#F0F0F0', pad=((0, 0), (0, 0))),
    sg.Text(crypto_data[4], font=('Hevetica', 12), key='-24HOUR-',background_color='#F0F0F0', pad=((0, 0), (0, 0))),
    sg.Text(crypto_data[5], font=('Hevetica', 12), key='-7DAYS-',background_color='#F0F0F0', pad=((0, 0), (0, 0)))
  ],
]

entry_layout = [
  [sg.Column(crypto_layout, pad=((0, 0), (0, 0)), background_color='#F0F0F0')]
]


window = sg.Window('My App', entry_layout, size=(800, 400))

while True:
  event, values = window.read()

  if event == sg.WINDOW_CLOSED or event == 'Cancel':
    break

  if event == "OK":
    user_input = values['-INPUT-']
    window['-OUTPUT-'].update(f'You entered: {user_input}')
