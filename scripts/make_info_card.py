import os
import json

def generate_info_card():
    width = 490
    height = 360

    # Try reading saved contributions stats
    contributions_count = "Live active"
    username = os.environ.get("GITHUB_USERNAME", "AVIVASHISHTA29")
    handle = "avi" if username.upper() == "AVIVASHISHTA29" else username.lower()

    json_path = os.path.join("data", "contributions.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "total_contributions" in data:
                    contributions_count = f"{data['total_contributions']:,} Contributions this year"
                if "username" in data:
                    username = data["username"]
                    handle = "avi" if username.upper() == "AVIVASHISHTA29" else username.lower()
        except Exception:
            pass

    rows = [
        ("OS", "Linux / Web Ecosystem", "#58a6ff"),
        ("Host", f"{handle} @ FullStack", "#bc8cff"),
        ("Role", "Full-Stack Developer & Software Engineer", "#79c0ff"),
        ("Kernel", "Python • TypeScript • React • Node", "#d2a8ff"),
        ("Uptime", contributions_count, "#56d364"),
        ("Stack", "Next.js • React • Node • Tailwind • PostgreSQL", "#e3b341"),
        ("Focus", "High Performance Web Apps & AI Tools", "#ff7b72"),
        ("Status", "🟢 Open for collaborations & building software", "#39d353"),
    ]

    line_svg = []
    start_y = 65
    line_height = 28

    for idx, (label, val, color) in enumerate(rows):
        y = start_y + (idx * line_height)
        delay = 0.2 + (idx * 0.12)
        line_svg.append(f'''
    <g class="line" style="animation-delay: {delay:.2f}s;">
      <text x="25" y="{y}" class="label">{label}:</text>
      <text x="100" y="{y}" class="val" fill="{color}">{val}</text>
    </g>''')

    # Color palette blocks at the bottom
    color_blocks = ["#ff7b72", "#ffa657", "#d2a8ff", "#58a6ff", "#79c0ff", "#56d364", "#e3b341", "#8b949e"]
    palette_svg = []
    block_start_y = start_y + (len(rows) * line_height) + 12
    for idx, c in enumerate(color_blocks):
        delay = 0.2 + ((len(rows) + idx) * 0.08)
        palette_svg.append(f'<rect class="line" x="{100 + idx * 22}" y="{block_start_y}" width="18" height="14" rx="3" fill="{c}" style="animation-delay: {delay:.2f}s;" />')

    palette_svg_str = "".join(palette_svg)
    lines_svg_str = "".join(line_svg)

    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    .bg {{ fill: #0d1117; rx: 12px; stroke: #30363d; stroke-width: 1px; }}
    .title-bar {{ fill: #161b22; rx: 12px; }}
    .dot-red {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green {{ fill: #27c93f; }}
    .title-text {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 13px; fill: #8b949e; font-weight: 600; }}
    .label {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 12px; fill: #8b949e; font-weight: bold; }}
    .val {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 12.5px; font-weight: 500; }}
    
    .line {{
      opacity: 0;
      animation: fadeInSlide 0.4s cubic-bezier(0.16, 1, 0.3, 1) forwards;
    }}
    
    @keyframes fadeInSlide {{
      from {{
        opacity: 0;
        transform: translateY(6px);
      }}
      to {{
        opacity: 1;
        transform: translateY(0);
      }}
    }}
  </style>

  <!-- Container Box -->
  <rect class="bg" width="{width}" height="{height}" />

  <!-- Terminal Window Header -->
  <path d="M 0 12 C 0 5.37 5.37 0 12 0 L 478 0 C 484.63 0 490 5.37 490 12 L 490 38 L 0 38 Z" fill="#161b22" />
  <line x1="0" y1="38" x2="{width}" y2="38" stroke="#30363d" stroke-width="1" />

  <!-- Window Dots -->
  <circle cx="20" cy="19" r="6" class="dot-red" />
  <circle cx="40" cy="19" r="6" class="dot-yellow" />
  <circle cx="60" cy="19" r="6" class="dot-green" />

  <!-- Window Title -->
  <text x="{width / 2}" y="23" text-anchor="middle" class="title-text">{handle}@github:~ (neofetch)</text>

  <!-- Content Lines -->
  {lines_svg_str}

  <!-- ANSI Color Blocks -->
  <g class="line" style="animation-delay: 1.1s;">
    <text x="25" y="{block_start_y + 11}" class="label">Colors:</text>
  </g>
  {palette_svg_str}
</svg>'''

    out_file = "info-card.svg"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Successfully generated {out_file} ({width}x{height})")

if __name__ == "__main__":
    generate_info_card()
