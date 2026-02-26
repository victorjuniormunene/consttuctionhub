from PIL import Image, ImageDraw, ImageFont
import os

def create_construction_logo():
    # Create a 400x200 image with orange background
    width, height = 400, 200
    background_color = (255, 127, 49)  # Orange color

    # Create image
    img = Image.new('RGB', (width, height), background_color)
    draw = ImageDraw.Draw(img)

    # Try to use a font, fallback to default if not available
    try:
        font = ImageFont.truetype("arial.ttf", 40)
        small_font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
        small_font = ImageFont.load_default()

    # Draw construction elements
    # Hard hat
    draw.ellipse([50, 50, 100, 80], fill=(255, 255, 255))
    draw.rectangle([60, 80, 90, 100], fill=(255, 255, 255))
    draw.rectangle([65, 85, 85, 95], fill=(0, 0, 0))

    # Hammer
    draw.rectangle([150, 120, 180, 140], fill=(139, 69, 19))  # Handle
    draw.rectangle([180, 110, 200, 150], fill=(128, 128, 128))  # Head

    # Wrench
    draw.rectangle([250, 100, 270, 120], fill=(128, 128, 128))
    draw.rectangle([270, 110, 290, 130], fill=(128, 128, 128))

    # Text
    text = "Construction Hub"
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    text_x = (width - text_width) // 2
    text_y = height - text_height - 20

    # Draw text with shadow
    draw.text((text_x + 2, text_y + 2), text, fill=(0, 0, 0, 128), font=font)
    draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)

    # Subtitle
    subtitle = "Professional Construction Materials"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=small_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]

    subtitle_x = (width - subtitle_width) // 2
    subtitle_y = text_y + text_height + 5

    draw.text((subtitle_x, subtitle_y), subtitle, fill=(255, 255, 255), font=small_font)

    # Save the image
    static_dir = os.path.join(os.path.dirname(__file__), 'static', 'images')
    os.makedirs(static_dir, exist_ok=True)

    logo_path = os.path.join(static_dir, 'construction_logo.png')
    img.save(logo_path, 'PNG')

    print(f"Logo created successfully at: {logo_path}")
    return logo_path

if __name__ == "__main__":
    create_construction_logo()
