import os
import json
from datetime import datetime

def generate_info_card():
    width = 490
    height = 360

    # ── Load real stats from contributions.json ──────────────────────────────
    json_path = os.path.join("data", "contributions.json")
    username        = "spect0er"
    handle          = "spect0er"
    total_commits   = 0
    current_streak  = 0
    longest_streak  = 0
    best_day_count  = 0
    best_day_date   = ""

    if os.path.exists(json_path):
        try:
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            username       = data.get("username", username)
            handle         = username.lower()
            total_commits  = data.get("total_contributions", 0)
            current_streak = data.get("current_streak", 0)
            longest_streak = data.get("longest_streak", 0)
            bd             = data.get("best_day", {})
            best_day_count = bd.get("count", 0)
            best_day_date  = bd.get("date", "")
        except Exception as e:
            print(f"Warning: could not read contributions.json: {e}")

    # Format best-day label nicely: "Jun 23" from "2026-06-23"
    best_label = best_day_date
    try:
        dt = datetime.strptime(best_day_date, "%Y-%m-%d")
        best_label = dt.strftime("%b %d")
    except Exception:
        pass

    # ── Info rows (sourced from CV) ──────────────────────────────────────────
    rows = [
        ("User",     "Kartikey Mishra  |  spect0er",                                    "#bc8cff"),
        ("Role",     "Full-Stack Dev  |  ML &amp; GenAI Engineer",                       "#58a6ff"),
        ("Lang",     "C++, JavaScript, Python, Java, C, HTML, CSS",                      "#d2a8ff"),
        ("Stack",    "React, Node.js, Express, TensorFlow, Scikit-learn",                "#e3b341"),
        ("Tools",    "MySQL, MongoDB, Git, Postman, Anaconda",                           "#56d364"),
        ("Commits",  f"{total_commits:,} contributions  |  🔥 {current_streak}d streak", "#ffa116"),
        ("Best Day", f"{best_day_count} commits on {best_label}",                          "#79c0ff"),
        ("Achieve",  "150+ LeetCode  |  ML Anomaly Detection Patent",                     "#ff7b72"),
    ]

    line_svg   = []
    start_y    = 62
    line_height = 25

    for idx, (label, val, color) in enumerate(rows):
        y     = start_y + idx * line_height
        delay = 0.05 + idx * 0.12
        line_svg.append(f'''
    <g id="card-line-{idx}">
      <animate attributeName="opacity" values="0;1" dur="0.55s" begin="{delay:.2f}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate" values="0 7;0 0" dur="0.55s" begin="{delay:.2f}s" fill="freeze" />
      <text x="25"  y="{y}" class="label">{label}:</text>
      <text x="105" y="{y}" class="val" fill="{color}">{val}</text>
    </g>''')

    # Status row
    status_y     = start_y + len(rows) * line_height
    status_delay = 0.05 + len(rows) * 0.12
    line_svg.append(f'''
    <g id="card-line-status">
      <animate attributeName="opacity" values="0;1" dur="0.55s" begin="{status_delay:.2f}s" fill="freeze" />
      <animateTransform attributeName="transform" type="translate" values="0 7;0 0" dur="0.55s" begin="{status_delay:.2f}s" fill="freeze" />
      <text x="25" y="{status_y}" class="label">Status:</text>
      <circle cx="109" cy="{status_y - 4}" r="4" fill="#39d353" />
      <text x="120" y="{status_y}" class="val" fill="#39d353">Open for collabs &amp; building in public</text>
    </g>''')

    # ANSI colour blocks
    color_blocks     = ["#ff7b72","#ffa657","#d2a8ff","#58a6ff","#79c0ff","#56d364","#e3b341","#8b949e"]
    block_start_y    = status_y + 18
    color_delay_base = status_delay + 0.10
    palette_svg      = []

    for idx, c in enumerate(color_blocks):
        delay = color_delay_base + idx * 0.05
        palette_svg.append(
            f'<rect x="{105 + idx * 22}" y="{block_start_y}" width="18" height="12" rx="3" fill="{c}">'
            f'<animate attributeName="opacity" values="0;1" dur="0.4s" begin="{delay:.2f}s" fill="freeze" /></rect>'
        )

    lines_svg_str   = "".join(line_svg)
    palette_svg_str = "".join(palette_svg)

    # ── SVG template ─────────────────────────────────────────────────────────
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    .bg         {{ fill: #0d1117; }}
    .dot-red    {{ fill: #ff5f56; }}
    .dot-yellow {{ fill: #ffbd2e; }}
    .dot-green  {{ fill: #27c93f; }}
    .title-text {{ font-family: "SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace; font-size: 13px; fill: #8b949e; font-weight: 600; }}
    .label      {{ font-family: "SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace; font-size: 11.5px; fill: #8b949e; font-weight: bold; }}
    .val        {{ font-family: "SFMono-Regular",Consolas,"Liberation Mono",Menlo,monospace; font-size: 11.5px; font-weight: 500; }}
  </style>

  <!-- Background -->
  <rect class="bg" width="{width}" height="{height}" rx="12" stroke="#30363d" stroke-width="1" />

  <!-- Terminal title bar -->
  <path d="M0 12 C0 5.37 5.37 0 12 0 L478 0 C484.63 0 490 5.37 490 12 L490 38 L0 38 Z" fill="#161b22" />
  <line x1="0" y1="38" x2="{width}" y2="38" stroke="#30363d" stroke-width="1" />

  <!-- Traffic light dots -->
  <circle cx="20" cy="19" r="6" class="dot-red"    />
  <circle cx="40" cy="19" r="6" class="dot-yellow" />
  <circle cx="60" cy="19" r="6" class="dot-green"  />

  <!-- Title -->
  <text x="{width / 2}" y="23" text-anchor="middle" class="title-text">{handle}@github:~ (neofetch)</text>

  <!-- Info rows -->
  {lines_svg_str}

  <!-- Colour palette -->
  <g>
    <text x="25" y="{block_start_y + 10}" class="label">
      <animate attributeName="opacity" values="0;1" dur="0.4s" begin="{color_delay_base:.2f}s" fill="freeze" />Colors:
    </text>
    {palette_svg_str}
  </g>
</svg>'''

    out_file = "info-card.svg"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"Generated {out_file}  ({width}x{height})")
    print(f"  commits={total_commits}  streak={current_streak}d  best={best_day_count} on {best_label}")

if __name__ == "__main__":
    generate_info_card()
