import re
import json
import os
import urllib.request
from datetime import datetime, timezone

def fetch_html(username):
    url = f"https://github.com/users/{username}/contributions"
    req = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
        }
    )
    with urllib.request.urlopen(req) as response:
        return response.read().decode('utf-8')

def parse_contributions(html, username="spect0er"):
    # Try importing BeautifulSoup
    try:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html, 'html.parser')
        days = []
        
        # Build tooltip map by target id
        tooltips = {}
        for tt in soup.find_all('tool-tip'):
            target_id = tt.get('for')
            if target_id:
                tooltips[target_id] = tt.get_text().strip()
                
        # Find all contribution days
        day_tds = soup.find_all('td', class_=re.compile(r'\bContributionCalendar-day\b'))
        
        for td in day_tds:
            date_str = td.get('data-date')
            if not date_str:
                continue
            
            level = int(td.get('data-level', 0))
            td_id = td.get('id', '')
            tooltip_text = tooltips.get(td_id, '')
            
            # Parse count from tooltip text, e.g., "14 contributions on July 26th." or "No contributions on..."
            count = 0
            if tooltip_text:
                match = re.search(r'(\d+)\s+contribution', tooltip_text, re.IGNORECASE)
                if match:
                    count = int(match.group(1))
                elif 'no contribution' in tooltip_text.lower():
                    count = 0
                else:
                    count = level if level > 0 else 0
            else:
                count = level if level > 0 else 0

            days.append({
                "date": date_str,
                "count": count,
                "level": level
            })
            
        # Parse month labels and positions
        months = []
        month_tds = soup.find_all('td', class_='ContributionCalendar-label')
        # Filter for month headers (they have position or text)
        for td in month_tds:
            text = td.get_text().strip()
            if text in ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']:
                colspan = int(td.get('colspan', 1))
                months.append({'name': text, 'colspan': colspan})
                
    except ImportError:
        # Regex fallback
        days = []
        day_matches = re.findall(
            r'<td[^>]*data-date="([^"]+)"[^>]*id="([^"]+)"[^>]*data-level="(\d+)"[^>]*class="[^"]*ContributionCalendar-day[^"]*"',
            html
        )
        if not day_matches:
            # try alternative attribute order
            day_matches = re.findall(
                r'<td[^>]*data-date="([^"]+)"[^>]*data-level="(\d+)"[^>]*',
                html
            )
            for m in day_matches:
                date_str, level_str = m[0], m[1]
                days.append({"date": date_str, "count": int(level_str), "level": int(level_str)})
        else:
            tooltip_map = dict(re.findall(r'<tool-tip[^>]*for="([^"]+)"[^>]*>(.*?)</tool-tip>', html, re.DOTALL))
            for date_str, td_id, level_str in day_matches:
                level = int(level_str)
                tt = tooltip_map.get(td_id, '')
                c_match = re.search(r'(\d+)\s+contribution', tt, re.IGNORECASE)
                count = int(c_match.group(1)) if c_match else (0 if 'no contribution' in tt.lower() else level)
                days.append({"date": date_str, "count": count, "level": level})
        months = []

    # Sort days by date
    days.sort(key=lambda d: d['date'])
    
    # Compute overall stats
    total_contributions = sum(d['count'] for d in days)
    
    # Streaks calculation
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    
    best_day = {"date": "", "count": 0}
    for d in days:
        if d['count'] > best_day['count']:
            best_day = {"date": d['date'], "count": d['count']}
            
        if d['count'] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Calculate current streak up to today/yesterday
    temp_streak = 0
    for d in reversed(days):
        if d['count'] > 0:
            temp_streak += 1
        else:
            # allow today to be 0 without breaking streak if yesterday had contributions
            if d['date'] == today_str and temp_streak == 0:
                continue
            break
    current_streak = temp_streak

    return {
        "username": username,
        "updated_at": datetime.now(timezone.utc).isoformat(),
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "days": days,
        "months": months
    }

def main():
    import sys
    default_user = "spect0er"
    username = sys.argv[1] if len(sys.argv) > 1 else os.environ.get("GITHUB_USERNAME", default_user)
    print(f"Fetching contribution data for {username}...")
    html = fetch_html(username)
    data = parse_contributions(html, username=username)
    
    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "contributions.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
        
    print(f"Saved {len(data['days'])} days of contributions to {out_path}.")
    print(f"Total Contributions: {data['total_contributions']}")
    print(f"Current Streak: {data['current_streak']} days")
    print(f"Longest Streak: {data['longest_streak']} days")
    print(f"Best Day: {data['best_day']['date']} ({data['best_day']['count']} contributions)")

if __name__ == "__main__":
    main()
