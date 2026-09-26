"""Create the README's descriptive daily-profile chart from the derived CSV."""

from pathlib import Path
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
data = pd.read_csv(ROOT / "data" / "clean_hourly_data.csv", parse_dates=["ds"])
profile = (data.assign(kwh=data["y"] / 60).groupby(data["ds"].dt.hour)["kwh"].mean())

width, height = 960, 360
left, right, top, bottom = 86, 908, 106, 278
max_value = max(2.0, float(profile.max()) * 1.15)


def point(hour, value):
    x = left + (right - left) * hour / 23
    y = bottom - (bottom - top) * value / max_value
    return x, y


points = [point(hour, float(profile.loc[hour])) for hour in range(24)]
line = " ".join(f"{'M' if i == 0 else 'L'} {x:.1f} {y:.1f}" for i, (x, y) in enumerate(points))
area = line + f" L {right} {bottom} L {left} {bottom} Z"
grid = []
for value in (0, 0.5, 1.0, 1.5, 2.0):
    y = point(0, value)[1]
    if y < top:
        continue
    grid.append(f'<line x1="{left}" y1="{y:.1f}" x2="{right}" y2="{y:.1f}" stroke="#e4eaf3"/>')
    grid.append(f'<text x="{left - 14}" y="{y + 4:.1f}" text-anchor="end" class="tick">{value:.1f}</text>')
for hour in (0, 4, 8, 12, 16, 20, 23):
    x = point(hour, 0)[0]
    grid.append(f'<text x="{x:.1f}" y="{bottom + 27}" text-anchor="middle" class="tick">{hour:02d}:00</text>')

svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-label="Average hourly electricity use by time of day">
<defs>
  <linearGradient id="fill" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4f7cff" stop-opacity="0.25"/><stop offset="1" stop-color="#4f7cff" stop-opacity="0.02"/></linearGradient>
</defs>
<style>text {{ font-family: Arial, Helvetica, sans-serif; }} .tick {{ fill: #607089; font-size: 13px; }} </style>
<rect width="{width}" height="{height}" rx="18" fill="#f8faff"/>
<text x="{left}" y="44" fill="#172b4d" font-size="22" font-weight="700">Typical daily consumption profile</text>
<text x="{left}" y="69" fill="#607089" font-size="14">Mean energy per hour · reconstructed household series · 2006–2010</text>
{''.join(grid)}
<path d="{area}" fill="url(#fill)"/>
<path d="{line}" fill="none" stroke="#345ee8" stroke-width="3.5" stroke-linecap="round" stroke-linejoin="round"/>
{''.join(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.2" fill="#345ee8"/>' for x, y in points)}
<text x="{left}" y="{height - 24}" fill="#607089" font-size="12">kWh per hour (derived from summed minute-level kW)</text>
</svg>
'''
output = ROOT / "assets" / "daily-profile.svg"
output.parent.mkdir(parents=True, exist_ok=True)
output.write_text(svg, encoding="utf-8")
print(output)
