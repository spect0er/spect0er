import os
import sys
from PIL import Image, ImageEnhance, ImageOps

def prep_photo(input_path="source-photo.jpg", output_path="source-prepped.png"):
    if not os.path.exists(input_path):
        print(f"No custom photo found at '{input_path}'. Creating default prepped avatar...")
        create_default_prepped_image(output_path)
        return

    print(f"Processing '{input_path}'...")
    img = Image.open(input_path)

    # Remove background if rembg is available
    try:
        from rembg import remove
        print("Removing background with rembg...")
        img_no_bg = remove(img)
        # Create white background
        bg = Image.new("RGBA", img_no_bg.size, (255, 255, 255, 255))
        bg.paste(img_no_bg, (0, 0), img_no_bg)
        img = bg.convert("L")
    except Exception as e:
        print(f"rembg optional step skipped ({e}). Converting directly to grayscale...")
        img = img.convert("L")

    # Boost contrast & sharpness
    enhancer = ImageEnhance.Contrast(img)
    img = enhancer.enhance(1.8)
    enhancer = ImageEnhance.Sharpness(img)
    img = enhancer.enhance(1.5)

    # Normalize histogram
    img = ImageOps.autocontrast(img, cutoff=2)
    img.save(output_path)
    print(f"Saved prepped image to '{output_path}'")

def create_default_prepped_image(output_path="source-prepped.png"):
    # Generate a clean 160x160 dark avatar silhouette with headphones & terminal elements
    from PIL import ImageDraw, ImageFont
    size = (200, 200)
    img = Image.new("L", size, color=255)
    draw = ImageDraw.Draw(img)

    # Draw face contour & head shape
    draw.ellipse([40, 30, 160, 150], fill=60) # Face/Head
    draw.ellipse([50, 45, 150, 140], fill=180) # Inner skin
    # Hair / Cap
    draw.chord([38, 25, 162, 110], 180, 360, fill=30)
    # Glasses / Visor
    draw.rounded_rectangle([60, 70, 95, 90], radius=4, fill=20)
    draw.rounded_rectangle([105, 70, 140, 90], radius=4, fill=20)
    draw.line([95, 78, 105, 78], fill=20, width=4)
    # Smile / Beard
    draw.arc([75, 100, 125, 125], 10, 170, fill=30, width=3)
    # Hoodie / Shoulders
    draw.ellipse([20, 130, 180, 250], fill=40)
    # Code brackets on hoodie
    draw.line([85, 160, 75, 170, 85, 180], fill=220, width=3)
    draw.line([115, 160, 125, 170, 115, 180], fill=220, width=3)

    img.save(output_path)
    print(f"Generated default avatar to '{output_path}'")

if __name__ == "__main__":
    photo_arg = sys.argv[1] if len(sys.argv) > 1 else "source-photo.jpg"
    prep_photo(photo_arg)
