import os
import sys
from PIL import Image, ImageEnhance, ImageOps

def prep_photo(input_path="source-photo.jpg", output_path="source-prepped.png"):
    if not os.path.exists(input_path):
        print(f"No custom photo found at '{input_path}'. Generating high-detail avatar prepped image...")
        create_default_prepped_image(output_path)
        return

    print(f"Processing photo '{input_path}'...")
    img = Image.open(input_path)

    # Remove background if rembg is installed
    try:
        from rembg import remove
        print("Removing background with rembg...")
        img_no_bg = remove(img)
        bg = Image.new("RGBA", img_no_bg.size, (255, 255, 255, 255))
        bg.paste(img_no_bg, (0, 0), img_no_bg)
        img = bg.convert("L")
    except Exception as e:
        print(f"rembg optional step skipped ({e}). Converting directly to grayscale...")
        img = img.convert("L")

    # High-contrast enhancement for crisp ASCII conversion
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.9)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.6)

    img = ImageOps.autocontrast(img, cutoff=2)
    img.save(output_path)
    print(f"Saved prepped image to '{output_path}'")

def create_default_prepped_image(output_path="source-prepped.png"):
    from PIL import ImageDraw
    size = (200, 200)
    img = Image.new("L", size, color=255)
    draw = ImageDraw.Draw(img)

    # Dark Hoodie & Neck Base
    draw.ellipse([15, 120, 185, 260], fill=15)
    draw.rectangle([78, 110, 122, 145], fill=150)

    # Face & Jaw Contour
    draw.polygon([(55, 55), (145, 55), (140, 125), (120, 150), (80, 150), (60, 125)], fill=200)
    draw.ellipse([52, 45, 148, 135], fill=215) # Face highlight

    # Developer Hair Cut
    draw.chord([48, 20, 152, 90], 180, 360, fill=10)
    draw.polygon([(48, 45), (55, 22), (75, 14), (100, 16), (125, 14), (145, 22), (152, 48), (145, 40)], fill=10)

    # Headphones & Arc
    draw.arc([22, 18, 178, 140], 190, 350, fill=25, width=12)
    draw.rounded_rectangle([22, 58, 48, 108], radius=6, fill=30)
    draw.rounded_rectangle([152, 58, 178, 108], radius=6, fill=30)

    # Glasses & Glare Lines
    draw.rounded_rectangle([56, 68, 96, 92], radius=5, fill=10)
    draw.rounded_rectangle([104, 68, 144, 92], radius=5, fill=10)
    draw.line([96, 77, 104, 77], fill=10, width=4)
    draw.line([62, 88, 76, 72], fill=250, width=3) # Left glare
    draw.line([110, 88, 124, 72], fill=250, width=3) # Right glare

    # Beard & Smile Contour
    draw.line([100, 85, 96, 112, 104, 112], fill=130, width=2)
    draw.arc([68, 112, 132, 145], 15, 165, fill=35, width=10)
    draw.arc([82, 116, 118, 132], 10, 170, fill=230, width=3)

    # Hoodie Drawstrings & Logo
    draw.line([75, 148, 75, 190], fill=210, width=2)
    draw.line([125, 148, 125, 190], fill=210, width=2)

    img.save(output_path)
    print(f"Generated crisp default avatar to '{output_path}'")

if __name__ == "__main__":
    photo_arg = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    prep_photo(photo_arg)
