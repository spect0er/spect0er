import os
import sys
from PIL import Image

RAMP = " .`:-=+*cs#%@"  # Bright (white background) -> Dark (dense glyphs)

def make_ascii_svg(prepped_image_path="source-prepped.png", output_svg_path="avi-ascii.svg"):
    if not os.path.exists(prepped_image_path):
        print(f"Prepped image '{prepped_image_path}' not found. Running prep_photo.py...")
        from prep_photo import prep_photo
        prep_photo()

    img = Image.open(prepped_image_path).convert("L")

    # Target grid dimensions (fits nicely inside 370px SVG)
    cols = 68
    rows = 38

    # Resize image to grid size
    img_resized = img.resize((cols, rows), Image.Resampling.BILINEAR)
    pixels = img_resized.load()

    ascii_lines = []
    ramp_len = len(RAMP)

    for r in range(rows):
        line_chars = []
        for c in range(cols):
            val = pixels[c, r]  # 0 (black) to 255 (white)
            # Invert: white background -> space (sparse), dark pixels -> dense characters
            # 255 -> index 0 (' ')
            # 0   -> index ramp_len - 1 ('@')
            normalized = 1.0 - (val / 255.0)
            ramp_idx = int(normalized * (ramp_len - 1))
            ramp_idx = max(0, min(ramp_len - 1, ramp_idx))
            
            char = RAMP[ramp_idx]
            # XML escape
            if char == '<':
                char = '&lt;'
            elif char == '>':
                char = '&gt;'
            elif char == '&':
                char = '&amp;'
            elif char == '"':
                char = '&quot;'
            elif char == "'":
                char = '&apos;'
            line_chars.append(char)
            
        ascii_lines.append("".join(line_chars))

    # Build SVG with typing animation
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

    # Total typing animation time per line
    line_dur = 0.55

    for idx, line_text in enumerate(ascii_lines):
        y_pos = start_y + (idx * line_height)
        delay = 0.2 + (idx * 0.10) # Slower, smoother staggered row delay
        
        cp_id = f"cp-row-{idx}"
        rect_id = f"rect-row-{idx}"
        cursor_id = f"cursor-row-{idx}"

        clip_paths.append(f'''
    <clipPath id="{cp_id}">
      <rect id="{rect_id}" x="{start_x}" y="{y_pos - font_size + 1}" width="0" height="{line_height + 1}" />
    </clipPath>''')

        anim_scripts.append(f'''
    <animate href="#{rect_id}" attributeName="width" from="0" to="338" dur="{line_dur:.2f}s" begin="{delay:.2f}s" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1" fill="freeze" />
    <animate href="#{cursor_id}" attributeName="x" from="{start_x}" to="{start_x + 330}" dur="{line_dur:.2f}s" begin="{delay:.2f}s" calcMode="spline" keyTimes="0;1" keySplines="0.25 0.1 0.25 1" fill="freeze" />
    <animate href="#{cursor_id}" attributeName="opacity" from="1" to="0" dur="0.1s" begin="{delay + line_dur:.2f}s" fill="freeze" />''')

        text_elements.append(f'<text x="{start_x}" y="{y_pos}" clip-path="url(#{cp_id})">{line_text}</text>')
        cursors.append(f'<rect id="{cursor_id}" x="{start_x}" y="{y_pos - font_size + 1}" width="5" height="{line_height}" fill="#39d353" opacity="0" />')

    clips_str = "".join(clip_paths)
    anims_str = "".join(anim_scripts)
    text_str = "".join(text_elements)
    cursors_str = "".join(cursors)

    title_label = os.path.basename(output_svg_path)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    .bg {{ fill: #0d1117; rx: 12px; stroke: #30363d; stroke-width: 1px; }}
    .title-bar {{ fill: #161b22; rx: 12px; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .title-text {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 13px; fill: #8b949e; font-weight: 600; }}
    
    text {{
      font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace;
      font-size: {font_size}px;
      fill: #58a6ff;
      letter-spacing: 0px;
      white-space: pre;
    }}
  </style>

  <defs>
    {clips_str}
  </defs>

  <!-- Background card -->
  <rect class="bg" width="{width}" height="{height}" />

  <!-- Terminal Window Header -->
  <path d="M 0 12 C 0 5.37 5.37 0 12 0 L 358 0 C 364.63 0 370 5.37 370 12 L 370 38 L 0 38 Z" fill="#161b22" />
  <line x1="0" y1="38" x2="{width}" y2="38" stroke="#30363d" stroke-width="1" />

  <!-- Window Dots -->
  <circle cx="20" cy="19" r="6" class="dot-red" />
  <circle cx="40" cy="19" r="6" class="dot-yellow" />
  <circle cx="60" cy="19" r="6" class="dot-green" />

  <!-- Window Title -->
  <text x="{width / 2}" y="23" text-anchor="middle" class="title-text">{title_label}</text>

  <!-- ASCII Lines -->
  <g>
    {text_str}
  </g>

  <!-- Active Cursor Blocks -->
  <g>
    {cursors_str}
  </g>

  <!-- SMIL Animations -->
  {anims_str}
</svg>'''

    with open(output_svg_path, "w", encoding="utf-8") as f:
        f.write(svg_content)

    print(f"Successfully generated {output_svg_path} ({width}x{height}) with typing animation!")

if __name__ == "__main__":
    out_name = sys.argv[1] if len(sys.argv) > 1 else "avi-ascii.svg"
    make_ascii_svg(output_svg_path=out_name)
