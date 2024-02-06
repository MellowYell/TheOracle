import sys
sys.path.append('/home/oracle/oracle/myenv/lib/python3.9/site-packages')
import time
import openai
from PIL import Image, ImageDraw, ImageFont, ImageEnhance
import argparse
import os
import subprocess

# Argument parsing for zodiac sign
parser = argparse.ArgumentParser(description="Generate and print a horoscope for a given zodiac sign.")
parser.add_argument('zodiac_sign', type=str, help="The zodiac sign to generate a horoscope for.")
args = parser.parse_args()

# OpenAI API key
openai.api_key = 'your key here'

# Generate a horoscope
response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "You are a wise oracle generating a horoscope."},
        {"role": "user", "content": f"Generate a fortune/horoscope that is approximately 75 words long for {args.zodiac_sign} in the literary style of HP Lovecraft and with the rhyme scheme of a Dr. Seuss"}
    ],
    max_tokens=150,
    temperature=0.3
)
horoscope = response['choices'][0]['message']['content'].strip()

# Define the font and size
font_path = 'LiberationMono-Regular.ttf'  # Adjust the font path as needed
font_size = 20  # Adjust the font size as needed
padding = 8  # Adjust as needed
width = 384  # Adjust as needed
height = 0

## Create a new image with a white background
img = Image.new('RGB', (width, height), (255, 255, 255))
draw = ImageDraw.Draw(img)

# Updated text wrapping function
def wrap_text_dynamically(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ''
    for word in words:
        test_line = current_line + word + ' '
        bbox = font.getbbox(test_line)
        line_width = bbox[2] - bbox[0]
        if line_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word + ' '
    if current_line:
        lines.append(current_line)
    return lines

# Function to print an image using CUPS
def print_image_with_cups(file_path):
    try:
        subprocess.run(["lp", "-d", "Printer", file_path], check=True)
        print(f"Print job for {file_path} sent successfully")
    except subprocess.CalledProcessError as e:
        print(f"Failed to print {file_path}: {e}")

def create_text_image(text, font_path, font_size, width, padding):
    font = ImageFont.truetype(font_path, font_size)
    wrapped_lines = wrap_text_dynamically(text, font, width)
    
    # Calculate the total height needed for the text image
    height = sum(font.getbbox(line)[3] - font.getbbox(line)[1] + padding for line in wrapped_lines)

    text_img = Image.new('RGB', (width, height), (255, 255, 255))
    draw = ImageDraw.Draw(text_img)
    y_text = 0
    for line in wrapped_lines:
        line_width, line_height = font.getbbox(line)[2] - font.getbbox(line)[0], font.getbbox(line)[3] - font.getbbox(line)[1]
        x_text = (width - line_width) / 2
        draw.text((x_text, y_text), line, font=font, fill=(0, 0, 0))
        y_text += line_height + padding

    return text_img


# Create the text image from the horoscope
text_img = create_text_image(horoscope, font_path, font_size, width, padding)

# Load the oracle image
oracle_img = Image.open('oracle.bmp')

# Combine the horoscope and oracle images
combined_img = Image.new('RGB', (max(text_img.width, oracle_img.width), text_img.height + oracle_img.height), (255, 255, 255))
combined_img.paste(text_img, (0, 0))
combined_img.paste(oracle_img, (0, text_img.height))

# Save the combined image as a .bmp file
combined_img_path = 'combined.bmp'
if os.path.exists(combined_img_path):
    os.remove(combined_img_path)
combined_img.save(combined_img_path)

# Print the combined image
print_image_with_cups(combined_img_path)

