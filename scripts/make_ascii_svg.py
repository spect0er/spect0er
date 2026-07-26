import os
import sys
import html
from PIL import Image

# 16-level density ramp (space to dense character)
RAMP = " .':;iI+hHMW8$@"

def get_color(val):
    """
    Maps 0..255 pixel luminance to high-contrast cyan/neon/white gradient palette
    255 = White background -> Space (dark/transparent)
    0   = Black pixel      -> Pure White highlight / intense density
    """
    norm = 1.0 - (val / 255.0)
    if norm < 0.12:
        return "#161b22" # Subtle shadow
    elif norm < 0.28:
        return "#30363d" # Dark gray contour
    elif norm < 0.45:
        return "#1f6beb" # Deep navy
    elif norm < 0.65:
        return "#58a6ff" # Terminal blue
    elif norm < 0.82:
        return "#79c0ff" # Electric cyan
    else:
        return "#ffffff" # Glowing white

def make_ascii_svg(prepped_image_path="source-prepped.png", output_svg_path="spect0er-ascii.svg"):
    if not os.path.exists(prepped_image_path):
        print(f"Prepped image '{prepped_image_path}' not found. Running prep_photo.py...")
        from prep_photo import prep_photo
        prep_photo()

    img = Image.open(prepped_image_path).convert("L")

    # Grid dimensions (fits cleanly inside 370x360 SVG terminal card)
    cols = 66
    rows = 38

    img_resized = img.resize((cols, rows), Image.Resampling.BILINEAR)
    pixels = img_resized.load()

    width = 370
    height = 360
    font_size = 7.2
    line_height = 7.6
    start_x = 18
    start_y = 52

    clip_paths = []
    anim_scripts = []
    text_elements = []
    cursors = []

    line_dur = 0.35

    for r in range(rows):
        y_pos = start_y + (r * line_height)
        delay = 0.05 + (r * 0.05) # Staggered typing reveal

        cp_id = f"cp-row-{r}"
        rect_id = f"rect-row-{r}"
        cursor_id = f"cursor-row-{r}"
        text_id = f"text-row-{r}"

        # Group consecutive characters by color to optimize SVG size
        tspans = []
        curr_color = None
        curr_text = []

        for c in range(cols):
            val = pixels[c, r]
            norm = 1.0 - (val / 255.0)
            ramp_idx = int(norm * (len(RAMP) - 1))
            ramp_idx = max(0, min(len(RAMP) - 1, ramp_idx))
            
            ch = RAMP[ramp_idx]
            ch_escaped = html.escape(ch)
            color = get_color(val)

            if color != curr_color:
                if curr_text:
                    t_str = "".join(curr_text)
                    tspans.append(f'<tspan fill="{curr_color}">{t_str}</tspan>')
                curr_color = color
                curr_text = [ch_escaped]
            else:
                curr_text.append(ch_escaped)

        if curr_text:
            t_str = "".join(curr_text)
            tspans.append(f'<tspan fill="{curr_color}">{t_str}</tspan>')

        line_inner_svg = "".join(tspans)

        clip_paths.append(f'''
    <clipPath id="{cp_id}">
      <rect id="{rect_id}" x="{start_x}" y="{y_pos - font_size + 1}" width="338" height="{line_height + 1}" />
    </clipPath>''')

        anim_scripts.append(f'''
    <animate href="#{rect_id}" attributeName="width" values="0;338" dur="{line_dur:.2f}s" begin="{delay:.2f}s" fill="freeze" />
    <animate href="#{cursor_id}" attributeName="x" values="{start_x};{start_x + 330}" dur="{line_dur:.2f}s" begin="{delay:.2f}s" fill="freeze" />
    <animate href="#{cursor_id}" attributeName="opacity" values="1;0" dur="0.1s" begin="{delay + line_dur:.2f}s" fill="freeze" />''')

        text_elements.append(f'<text id="{text_id}" x="{start_x}" y="{y_pos}" clip-path="url(#{cp_id})">{line_inner_svg}</text>')
        cursors.append(f'<rect id="{cursor_id}" x="{start_x}" y="{y_pos - font_size + 1}" width="5" height="{line_height}" fill="#39d353" opacity="0" />')

    clips_str = "".join(clip_paths)
    anims_str = "".join(anim_scripts)
    text_str = "".join(text_elements)
    cursors_str = "".join(cursors)

    title_label = "spect0er@github:~ (ascii-portrait)"

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    .bg {{ fill: #0d1117; rx: 12px; stroke: #30363d; stroke-width: 1px; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .title-text {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 12.5px; fill: #8b949e; font-weight: 600; }}
    
    text {{
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
      font-size: {font_size}px;
      font-weight: 600;
      white-space: pre;
    }}
  </style>

  <defs>
    {clips_str}
  </defs>

  <!-- Background card -->
  <rect class="bg" width="{width}" height="{height}" rx="12" stroke="#30363d" stroke-width="1" />

  <!-- Terminal Window Header -->
  <path d="M 0 12 C 0 5.37 5.37 0 12 0 L 358 0 C 364.63 0 370 5.37 370 12 L 370 38 L 0 38 Z" fill="#161b22" />
  <line x1="0" y1="38" x2="{width}" y2="38" stroke="#30363d" stroke-width="1" />

  <!-- Window Dots -->
  <circle cx="20" cy="19" r="6" class="dot-red" />
  <circle cx="40" cy="19" r="6" class="dot-yellow" />
  <circle cx="60" cy="19" r="6" class="dot-green" />

  <!-- Window Title -->
  <text x="{width / 2}" y="23" text-anchor="middle" class="title-text">{title_label}</text>

  <!-- Shaded ASCII Portrait Lines -->
  <g>
    {text_str}
  </g>

  <!-- Typing Cursors -->
  <g>
    {cursors_str}
  </g>

  <!-- SMIL Typing Animations -->
  {anims_str}
</svg>'''

    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Successfully generated {output_svg_path} ({width}x{height}) with multi-tone ASCII shading & animation!")

if __name__ == "__main__":
    out_name = sys.argv[1] if len(sys.argv) > 1 else "spect0er-ascii.svg"
    make_ascii_svg(output_svg_path=out_name)
