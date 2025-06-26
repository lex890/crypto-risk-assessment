import requests
from io import BytesIO
from PIL import Image

def get_image(url, test=0):
  print('url', url)
  response = requests.get(url)
  image = Image.open(BytesIO(response.content))
    # Get and display image size (width, height)
  width, height = image.size

  if width > 64 and height > 64:
    image = image.resize((64, 64), Image.Resampling.LANCZOS)
  elif test == 1:
    image = image.resize((24, 24), Image.Resampling.LANCZOS)

  image_bytes = BytesIO()
  image.save(image_bytes, format='PNG')  # Convert to PNG
  image_bytes.seek(0)  # Reset stream position
  data = image_bytes.read()

  return data

