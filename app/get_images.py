import requests
from io import BytesIO
from PIL import Image

def get_image(url):
  response = requests.get(url)
  # Open with PIL and convert to format Tkinter can handle
  image = Image.open(BytesIO(response.content))
  image_bytes = BytesIO()
  image.save(image_bytes, format='PNG')  # Convert to PNG
  image_bytes.seek(0)  # Reset stream position
  data = image_bytes.read()

  return data

