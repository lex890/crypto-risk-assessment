import requests
from io import BytesIO
from PIL import Image

def get_image(url, mode=0):
  response = requests.get(url)
  image = Image.open(BytesIO(response.content))

    # Get and display image size (width, height)
  width, height = image.size
  if mode == 1:
    image = image.resize((32, 32), Image.Resampling.LANCZOS)
  elif width == 250 and height == 250:
    image = image.resize((64, 64), Image.Resampling.LANCZOS)
     
  image_bytes = BytesIO()
  image.save(image_bytes, format='PNG')  # Convert to PNG
  image_bytes.seek(0)  # Reset stream position
  data = image_bytes.read()
  return data

