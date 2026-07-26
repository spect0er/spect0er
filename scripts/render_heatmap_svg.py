import json
import os

PALETTE = [
    "#161b22",  # Level 0 (no contribution)
    "#0e4429",  # Level 1
    "#006d32",  # Level 2
    "#26a641",  # Level 3
    "#39d353",  # Level 4
    "#69f0a0",  # Level 5 (top day highlight)
]

MONTH_NAMES = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
DAY_NAMES = ["Mon", "Wed", "Fri"]

def render_heatmap():
    json_path = os.path.join("data", "contributions.json")
    if not os.path.exists(json_path):
        raise FileNotFoundError("data/contributions.json not found. Run fetch_contributions.py first.")
        
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    days = data.get("days", [])
    total_contributions = data.get("total_contributions", 0)
    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)
    best_day = data.get("best_day", {})

    # Grid configuration
    box_size = 11
    box_gap = 3.5
    step = box_size + box_gap
    start_x = 42
    start_y = 58
    
    # 53 weeks x 7 days
    # Organize days into columns (weeks)
    # Each day has a date; we map index to col = idx // 7, row = idx % 7
    total_days = len(days)
    
    # SVG Dimensions
    width = 860
    height = 205
    
    # Determine color levels for each day
    max_count = max((d["count"] for d in days), default=1)
    
    rect_elements = []
    month_labels = []
    current_month = None

    for idx, d in enumerate(days):
        col = idx // 7
        row = idx % 7
        
        x = start_x + col * step
        y = start_y + row * step
        
        count = d["count"]
        level = d.get("level", 0)
        
        # Color pick
        if count == 0:
            color = PALETTE[0]
        elif count >= max_count and max_count > 5:
            color = PALETTE[5]
        else:
            if level <= 0:
                color = PALETTE[1] if count > 0 else PALETTE[0]
            elif level >= len(PALETTE) - 1:
                color = PALETTE[4]
            else:
                color = PALETTE[level]
                
        # Staggered animation delay
        delay = 0.05 + (col * 0.025) + (row * 0.035)
        
        # Check month label
        date_parts = d["date"].split("-")
        if len(date_parts) == 3:
            m_idx = int(date_parts[1]) - 1
            m_name = MONTH_NAMES[m_idx]
            if row == 0 and m_name != current_month:
                current_month = m_name
                # Only add if x position leaves room
                if x < width - 60:
                    month_labels.append(f'<text x="{x:.1f}" y="{start_y - 8}" class="month-label">{m_name}</text>')

        rect_elements.append(
            f'<rect class="day" x="{x:.1f}" y="{y:.1f}" width="{box_size}" height="{box_size}" rx="2.5" fill="{color}">'
            f'<animate attributeName="opacity" values="0;1" dur="0.4s" begin="{delay:.3f}s" fill="freeze" />'
            f'<title>{d["date"]}: {count} contribution{"s" if count != 1 else ""}</title>'
            f'</rect>'
        )

    # Render Day labels (Mon, Wed, Fri) -> rows 1, 3, 5
    day_labels = [
        f'<text x="12" y="{start_y + 1 * step + 9}" class="day-label">Mon</text>',
        f'<text x="12" y="{start_y + 3 * step + 9}" class="day-label">Wed</text>',
        f'<text x="12" y="{start_y + 5 * step + 9}" class="day-label">Fri</text>',
    ]

    # Render Header & Stats
    stats_str = f"{total_contributions:,} contributions in last year"
    streak_str = f"Current Streak: {current_streak} days"
    best_str = f"Best: {best_day.get('count', 0)} ({best_day.get('date', '')})"

    # Color legend boxes
    legend_boxes = []
    legend_start_x = width - 180
    legend_y = height - 20
    for i, c in enumerate(PALETTE):
        legend_boxes.append(f'<rect x="{legend_start_x + i * 14}" y="{legend_y}" width="10" height="10" rx="2" fill="{c}" />')

    username = data.get("username", "AVIVASHISHTA29")
    handle = "avi" if username.upper() == "AVIVASHISHTA29" else username

    svg_content = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
  <style>
    .bg {{ fill: #0d1117; }}
    .title {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; font-size: 14px; font-weight: 600; fill: #58a6ff; }}
    .stat-badge {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 12px; fill: #8b949e; }}
    .highlight {{ font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, Courier, monospace; font-size: 12px; fill: #39d353; font-weight: 600; }}
    .month-label {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 10px; fill: #8b949e; }}
    .day-label {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 10px; fill: #484f58; }}
    .legend-text {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; font-size: 10px; fill: #8b949e; }}
  </style>

  <!-- Background card -->
  <rect class="bg" width="{width}" height="{height}" />

  <!-- Title bar header -->
  <g transform="translate(18, 28)">
    <text class="title">{handle} / contribution-heatmap</text>
    <text x="320" class="stat-badge">{stats_str}</text>
    <text x="590" class="highlight">🔥 {current_streak}d streak</text>
    <text x="700" class="stat-badge">⚡ {best_str}</text>
  </g>

  <!-- Month Labels -->
  <g>
    {''.join(month_labels)}
  </g>

  <!-- Day Labels -->
  <g>
    {''.join(day_labels)}
  </g>

  <!-- Heatmap Boxes -->
  <g>
    {''.join(rect_elements)}
  </g>

  <!-- Legend Footer -->
  <g transform="translate(0, 0)">
    <text x="{legend_start_x - 30}" y="{legend_y + 9}" class="legend-text">Less</text>
    {''.join(legend_boxes)}
    <text x="{legend_start_x + len(PALETTE) * 14 + 6}" y="{legend_y + 9}" class="legend-text">More</text>
  </g>
</svg>'''

    out_file = "contrib-heatmap.svg"
    with open(out_file, "w", encoding="utf-8") as f:
        f.write(svg_content)
        
    print(f"Successfully generated {out_file} ({width}x{height}) with {len(rect_elements)} animated cells!")

if __name__ == "__main__":
    render_heatmap()
