import json
import os
from datetime import datetime

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

def render_graph():
    json_path = os.path.join("data", "contributions.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError("data/contributions.json not found. Run fetch_contributions.py first.")

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    username = data.get("username", "spect0er")
    handle = username.lower()
    total_contributions = data.get("total_contributions", 0)

    # Group days into 12 months
    monthly_data = {}
    for d in days:
        date_str = d["date"]
        parts = date_str.split("-")
        if len(parts) == 3:
            yr_mo = f"{parts[0]}-{parts[1]}"
            m_idx = int(parts[1]) - 1
            label = f"{MONTH_NAMES[m_idx]}"
            if yr_mo not in monthly_data:
                monthly_data[yr_mo] = {"label": label, "count": 0, "active_days": 0}
            monthly_data[yr_mo]["count"] += d["count"]
            if d["count"] > 0:
                monthly_data[yr_mo]["active_days"] += 1

    months_list = list(monthly_data.values())
    if not months_list:
        months_list = [{"label": m, "count": 0, "active_days": 0} for m in MONTH_NAMES]

    max_monthly = max((m["count"] for m in months_list), default=1)
    if max_monthly == 0:
        max_monthly = 1

    width = 860
    height = 210
    graph_x = 55
    graph_y = 55
    graph_w = 750
    graph_h = 115

    num_bars = len(months_list)
    slot_w = graph_w / num_bars
    bar_w = slot_w * 0.55

    bar_elements = []
    points = []

    for idx, m in enumerate(months_list):
        cx = graph_x + (idx * slot_w) + (slot_w / 2)
        ratio = m["count"] / max_monthly
        bh = max(4, ratio * graph_h)
        by = graph_y + graph_h - bh
        bx = cx - (bar_w / 2)

        points.append((cx, by))

        delay = 0.2 + (idx * 0.15)

        # Bar element with SMIL height animation
        bar_elements.append(
            f'<g class="bar-group">'
            f'<rect x="{bx:.1f}" y="{graph_y + graph_h:.1f}" width="{bar_w:.1f}" height="0" rx="3" fill="url(#barGradient)" opacity="0.85">'
            f'<animate attributeName="height" from="0" to="{bh:.1f}" dur="1.0s" begin="{delay:.2f}s" calcMode="spline" keyTimes="0;1" keySplines="0.16 1 0.3 1" fill="freeze" />'
            f'<animate attributeName="y" from="{graph_y + graph_h:.1f}" to="{by:.1f}" dur="1.0s" begin="{delay:.2f}s" calcMode="spline" keyTimes="0;1" keySplines="0.16 1 0.3 1" fill="freeze" />'
            f'</rect>'
            f'<text x="{cx:.1f}" y="{by - 6:.1f}" class="bar-val" opacity="0">{m["count"]}'
            f'<animate attributeName="opacity" from="0" to="1" dur="0.6s" begin="{delay + 0.5:.2f}s" fill="freeze" />'
            f'</text>'
            f'<text x="{cx:.1f}" y="{graph_y + graph_h + 16:.1f}" class="month-label">{m["label"]}</text>'
            f'</g>'
        )

    # Build smooth trend polyline
    path_d = [f"M {points[0][0]:.1f} {points[0][1]:.1f}"]
    for p in points[1:]:
        path_d.append(f"L {p[0]:.1f} {p[1]:.1f}")
    line_path_str = " ".join(path_d)

    area_d = path_d + [f"L {points[-1][0]:.1f} {graph_y + graph_h:.1f}", f"L {points[0][0]:.1f} {graph_y + graph_h:.1f}", "Z"]
    area_path_str = " ".join(area_d)

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    .bg {{ fill: #0d1117; rx: 12px; stroke: #30363d; stroke-width: 1px; }}
    .title {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 13.5px; font-weight: 600; fill: #58a6ff; }}
    .stat-badge {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 11.5px; fill: #8b949e; }}
    .highlight {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 11.5px; fill: #39d353; font-weight: 600; }}
    .month-label {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 10.5px; fill: #8b949e; text-anchor: middle; }}
    .bar-val {{ font-family: "SFMono-Regular", Consolas, monospace; font-size: 9.5px; fill: #39d353; text-anchor: middle; font-weight: 600; }}
    .grid-line {{ stroke: #21262d; stroke-width: 1px; stroke-dasharray: 4,4; }}
  </style>

  <defs>
    <linearGradient id="barGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#39d353" stop-opacity="0.9" />
      <stop offset="100%" stop-color="#0e4429" stop-opacity="0.4" />
    </linearGradient>
    <linearGradient id="areaGradient" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#58a6ff" stop-opacity="0.3" />
      <stop offset="100%" stop-color="#58a6ff" stop-opacity="0.0" />
    </linearGradient>
  </defs>

  <!-- Container Box -->
  <rect class="bg" width="{width}" height="{height}" />

  <!-- Title & Stats Header -->
  <g transform="translate(18, 28)">
    <text class="title">{username} / contribution-activity-graph</text>
    <text x="360" class="stat-badge">Total: {total_contributions:,} commits</text>
    <text x="590" class="highlight">📈 Monthly Trend</text>
    <text x="710" class="stat-badge">Peak: {max_monthly} / mo</text>
  </g>

  <!-- Horizontal Grid Lines -->
  <line x1="{graph_x}" y1="{graph_y}" x2="{graph_x + graph_w}" y2="{graph_y}" class="grid-line" />
  <line x1="{graph_x}" y1="{graph_y + graph_h * 0.5:.1f}" x2="{graph_x + graph_w}" y2="{graph_y + graph_h * 0.5:.1f}" class="grid-line" />
  <line x1="{graph_x}" y1="{graph_y + graph_h}" x2="{graph_x + graph_w}" y2="{graph_y + graph_h}" stroke="#30363d" stroke-width="1.5" />

  <!-- Area Fill under trend -->
  <path d="{area_path_str}" fill="url(#areaGradient)" opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.6s" begin="0.4s" fill="freeze" />
  </path>

  <!-- Monthly Bars -->
  <g>
    {''.join(bar_elements)}
  </g>

  <!-- Polyline Trend Overlay -->
  <path d="{line_path_str}" fill="none" stroke="#58a6ff" stroke-width="2" stroke-linejoin="round" opacity="0">
    <animate attributeName="opacity" from="0" to="1" dur="0.5s" begin="0.5s" fill="freeze" />
  </path>
</svg>'''

    out_file = "contrib-graph.svg"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
    print(f"Successfully generated {out_file} ({width}x{height})")

if __name__ == "__main__":
    render_graph()
