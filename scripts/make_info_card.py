import os
import json

def generate_info_card():
    width = 490
    height = 360

    # Try reading saved contributions stats
    contributions_count = "Live active"
    username = os.environ.get("GITHUB_USERNAME", "spect0er")
    handle = username.lower()

    json_path = os.path.join("data", "contributions.json")
    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                if "total_contributions" in data:
                    contributions_count = f"{data['total_contributions']:,} Contributions this year"
                if "username" in data:
                    handle = data["username"].lower()
        except Exception:
            pass

    rows = [
        ("OS", "Linux / Web Ecosystem", "#58a6ff"),
        ("Host", f"{handle} @ FullStack", "#bc8cff"),
        ("Role", "Full-Stack Engineer &amp; Systems Builder", "#79c0ff"),
        ("Languages", "TypeScript, Python, JavaScript, SQL, C++", "#d2a8ff"),
        ("Frontend", "React, Next.js, HTML5/CSS3, Tailwind CSS", "#56d364"),
        ("Backend", "Node.js, Express, FastAPI, PostgreSQL, REST APIs", "#e3b341"),
        ("Uptime", contributions_count, "#79c0ff"),
        ("Focus", "High-Performance Web Apps &amp; AI Agents", "#ff7b72"),
    ]

    line_svg = []
    start_y = 62
    line_height = 25

    for idx, (label, val, color) in enumerate(rows):
        y = start_y + (idx * line_height)
        delay = 0.15 + (idx * 0.10)
        line_svg.append(f'''
    <g id="card-line-{idx}" opacity="0" transform="translate(0, 6)">
      <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{delay:.2f}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate" from="0 6" to="0 0" dur="0.4s" begin="{delay:.2f}s" fill="freeze" />
      <text x="25" y="{y}" class="label">{label}:</text>
      <text x="105" y="{y}" class="val" fill="{color}">{val}</text>
    </g>''')

    # Status row with glowing green dot indicator
    status_y = start_y + (len(rows) * line_height)
    status_delay = 0.15 + (len(rows) * 0.10)
    line_svg.append(f'''
    <g id="card-line-status" opacity="0" transform="translate(0, 6)">
      <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{status_delay:.2f}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate" from="0 6" to="0 0" dur="0.4s" begin="{status_delay:.2f}s" fill="freeze" />
      <text x="25" y="{status_y}" class="label">Status:</text>
      <circle cx="109" cy="{status_y - 4}" r="4" fill="#39d353" />
      <text x="120" y="{status_y}" class="val" fill="#39d353">Open for collaborations &amp; building software</text>
    </g>''')

    # Color palette blocks at the bottom
    color_blocks = ["#ff7b72", "#ffa657", "#d2a8ff", "#58a6ff", "#79c0ff", "#56d364", "#e3b341", "#8b949e"]
    palette_svg = []
    block_start_y = status_y + 18
    color_delay_base = status_delay + 0.15

    for idx, c in enumerate(color_blocks):
        delay = color_delay_base + (idx * 0.05)
        palette_svg.append(
            f'<rect opacity="0" x="{105 + idx * 22}" y="{block_start_y}" width="18" height="12" rx="3" fill="{c}">'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.3s" begin="{delay:.2f}s" fill="freeze" />'
            f'</rect>'
        )

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
    .label {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 11.5px; fill: #8b949e; font-weight: bold; }}
    .val {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 11.5px; font-weight: 500; }}
  </style>

  <!-- Container Box -->
  <rect class="bg" width="{width}" height="{height}" />

  <!-- Terminal Window Header -->
  <path d="M 0 12 C 0 5.37 5.37 0 12 0 L 478 0 C 484.63 0 490 5.37 490 12 L 490 38 L 0 38 Z" fill="#161b22" />
  <line x1="0" y1="38" x2="{width}" y2="38" stroke="#30363d" stroke-width="1" />

  <!-- Window Controls -->
  <circle cx="20" cy="19" r="6" class="dot-red" />
  <circle cx="40" cy="19" r="6" class="dot-yellow" />
  <circle cx="60" cy="19" r="6" class="dot-green" />

  <!-- Window Title -->
  <text x="{width / 2}" y="23" text-anchor="middle" class="title-text">{handle}@github:~ (neofetch)</text>

  <!-- Content Lines -->
  {lines_svg_str}

  <!-- ANSI Color Blocks -->
  <g opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.4s" begin="{color_delay_base:.2f}s" fill="freeze" />
    <text x="25" y="{block_start_y + 10}" class="label">Colors:</text>
  </g>
  {palette_svg_str}
</svg>'''

    out_file = "info-card.svg"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Successfully generated {out_file} ({width}x{height}) with native SMIL animations!")

if __name__ == "__main__":
    generate_info_card()
