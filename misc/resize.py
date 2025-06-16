from PIL import Image

def resize_image(image_path, new_width, new_height, output_path):
    """Resizes an image to the specified dimensions.

    Args:
        image_path: Path to the input image.
        new_width: Desired width of the resized image.
        new_height: Desired height of the resized image.
        output_path: Path to save the resized image.
    """
    try:
        img = Image.open(image_path)
        resized_img = img.resize((new_width, new_height))
        resized_img.save(output_path)
        print(f"Image successfully resized and saved to {output_path}")
    except FileNotFoundError:
        print(f"Error: Image file not found at {image_path}")
    except Exception as e:
        print(f"An error occurred: {e}")

# Example usage:
image_path = "./images/bookmark.png"  # Replace with your image path
new_width = 30 
new_height = 30
output_path = "./images/save-key.png" # Replace with your desired output path
resize_image(image_path, new_width, new_height, output_path)