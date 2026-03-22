import streamlit as st
import pandas as pd
import psycopg
from dotenv import load_dotenv
import os
from datetime import datetime

st.set_page_config(
    page_title="Weather Dashboard",
    page_icon="🌤️",
    layout="wide",
)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
# ---------------- CONNECT DB ----------------
def load_data():
    conn = psycopg.connect(DATABASE_URL)

    query = "SELECT * FROM weather ORDER BY last_updated DESC LIMIT 50"
    df = pd.read_sql(query, conn)

    conn.close()
    return df

# ---------------- THEME LOGIC ----------------
def get_theme(temperature, condition, last_updated):
    """Return CSS gradient + text color based on temp, condition, and time."""
    hour = last_updated.hour if isinstance(last_updated, datetime) else datetime.now().hour
    condition_lower = str(condition).lower()
    is_night = hour >= 19 or hour < 6
    is_rain = any(w in condition_lower for w in ["rain", "drizzle", "shower", "storm", "thunder"])
    is_snow = any(w in condition_lower for w in ["snow", "blizzard", "sleet"])

    if is_night:
        bg = "linear-gradient(160deg, #0a0e1a 0%, #111827 40%, #1a1f35 100%)"
        text = "#e2e8f0"
        card_bg = "rgba(255,255,255,0.05)"
        accent = "#60a5fa"
    elif is_snow:
        bg = "linear-gradient(160deg, #dbeafe 0%, #e0f2fe 50%, #f0f9ff 100%)"
        text = "#1e3a5f"
        card_bg = "rgba(255,255,255,0.55)"
        accent = "#3b82f6"
    elif is_rain:
        bg = "linear-gradient(160deg, #374151 0%, #4b5563 40%, #6b7280 100%)"
        text = "#f1f5f9"
        card_bg = "rgba(255,255,255,0.08)"
        accent = "#93c5fd"
    elif temperature >= 35:
        bg = "linear-gradient(160deg, #7c2d12 0%, #c2410c 40%, #ea580c 100%)"
        text = "#fff7ed"
        card_bg = "rgba(255,255,255,0.10)"
        accent = "#fbbf24"
    elif temperature >= 28:
        bg = "linear-gradient(160deg, #065f46 0%, #0369a1 40%, #0ea5e9 100%)"
        text = "#f0fdf4"
        card_bg = "rgba(255,255,255,0.12)"
        accent = "#34d399"
    elif temperature >= 18:
        bg = "linear-gradient(160deg, #0369a1 0%, #0ea5e9 50%, #38bdf8 100%)"
        text = "#f0f9ff"
        card_bg = "rgba(255,255,255,0.15)"
        accent = "#fde68a"
    elif temperature >= 8:
        bg = "linear-gradient(160deg, #1e3a5f 0%, #1d4ed8 50%, #3b82f6 100%)"
        text = "#eff6ff"
        card_bg = "rgba(255,255,255,0.10)"
        accent = "#a5b4fc"
    else:
        bg = "linear-gradient(160deg, #1e293b 0%, #334155 50%, #475569 100%)"
        text = "#e2e8f0"
        card_bg = "rgba(255,255,255,0.07)"
        accent = "#94a3b8"

    return bg, text, card_bg, accent, is_rain, is_snow, is_night


def condition_emoji(condition):
    c = str(condition).lower()
    if "thunder" in c or "storm" in c: return "⛈️"
    if "rain" in c or "shower" in c or "drizzle" in c: return "🌧️"
    if "snow" in c or "blizzard" in c: return "❄️"
    if "fog" in c or "mist" in c: return "🌫️"
    if "cloud" in c or "overcast" in c: return "☁️"
    if "sunny" in c or "clear" in c: return "☀️"
    if "wind" in c: return "💨"
    return "🌤️"


# ---------------- LOAD ----------------
df = load_data()
latest = df.iloc[0]
temp = float(latest["temperature"])
condition = latest["weather_condition"]
last_updated = latest["last_updated"]
if isinstance(last_updated, str):
    last_updated = datetime.fromisoformat(last_updated)

bg, text_color, card_bg, accent, is_rain, is_snow, is_night = get_theme(temp, condition, last_updated)

# ---------------- INJECT CSS ----------------
rain_drops = ""
if is_rain:
    import random
    for i in range(60):
        left = random.randint(0, 100)
        delay = round(random.uniform(0, 2), 2)
        dur = round(random.uniform(0.5, 1.2), 2)
        rain_drops += f'.rain-drop:nth-child({i+1}) {{ left: {left}%; animation-delay: {delay}s; animation-duration: {dur}s; }}\n'

snow_flakes = ""
if is_snow:
    import random
    for i in range(40):
        left = random.randint(0, 100)
        delay = round(random.uniform(0, 5), 2)
        dur = round(random.uniform(3, 7), 2)
        size = random.randint(4, 10)
        snow_flakes += f'.snow-flake:nth-child({i+1}) {{ left: {left}%; animation-delay: {delay}s; animation-duration: {dur}s; width: {size}px; height: {size}px; }}\n'

st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=JetBrains+Mono:wght@400;600&display=swap');

/* ---- Global reset & background ---- */
html, body, [data-testid="stAppViewContainer"], [data-testid="stApp"] {{
    background: {bg} !important;
    background-attachment: fixed !important;
    color: {text_color} !important;
    font-family: 'Sora', sans-serif !important;
}}
[data-testid="stHeader"] {{ background: transparent !important; }}
[data-testid="stSidebar"] {{ background: rgba(0,0,0,0.25) !important; }}
[data-testid="stToolbar"] {{ display: none; }}

/* ---- Hide default Streamlit elements ---- */
footer {{ visibility: hidden; }}
#MainMenu {{ visibility: hidden; }}

/* ---- Weather particles container ---- */
.weather-particles {{
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    pointer-events: none;
    z-index: 0;
    overflow: hidden;
}}

/* ---- Rain animation ---- */
.rain-drop {{
    position: absolute;
    top: -20px;
    width: 2px;
    height: 18px;
    background: linear-gradient(to bottom, transparent, rgba(174,214,241,0.7));
    border-radius: 2px;
    animation: fall linear infinite;
}}
@keyframes fall {{
    0%   {{ transform: translateY(-20px) rotate(15deg); opacity: 0.8; }}
    100% {{ transform: translateY(100vh) rotate(15deg); opacity: 0.2; }}
}}
{rain_drops}

/* ---- Snow animation ---- */
.snow-flake {{
    position: absolute;
    top: -10px;
    border-radius: 50%;
    background: rgba(255,255,255,0.85);
    animation: snowfall linear infinite;
}}
@keyframes snowfall {{
    0%   {{ transform: translateY(-10px) translateX(0px); opacity: 1; }}
    50%  {{ transform: translateY(50vh) translateX(20px); }}
    100% {{ transform: translateY(100vh) translateX(-10px); opacity: 0.3; }}
}}
{snow_flakes}

/* ---- Stars for night ---- */
.star {{
    position: absolute;
    background: white;
    border-radius: 50%;
    animation: twinkle ease-in-out infinite;
}}
@keyframes twinkle {{
    0%, 100% {{ opacity: 0.2; transform: scale(1); }}
    50%       {{ opacity: 1;   transform: scale(1.3); }}
}}

/* ---- Main content layer ---- */
.block-container {{
    position: relative;
    z-index: 10;
    padding-top: 2rem !important;
    max-width: 1200px !important;
}}

/* ---- Hero card ---- */
.hero-card {{
    background: {card_bg};
    border: 1px solid rgba(255,255,255,0.15);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 28px;
    padding: 2.5rem 3rem;
    margin-bottom: 2rem;
    box-shadow: 0 25px 60px rgba(0,0,0,0.25), inset 0 1px 0 rgba(255,255,255,0.2);
    animation: slideUp 0.6s cubic-bezier(0.16, 1, 0.3, 1) both;
}}
@keyframes slideUp {{
    from {{ opacity: 0; transform: translateY(30px); }}
    to   {{ opacity: 1; transform: translateY(0); }}
}}
.hero-temp {{
    font-size: 6rem;
    font-weight: 700;
    line-height: 1;
    letter-spacing: -4px;
    color: {text_color};
    text-shadow: 0 4px 20px rgba(0,0,0,0.3);
}}
.hero-location {{
    font-size: 1.5rem;
    font-weight: 600;
    color: {accent};
    letter-spacing: 0.05em;
    text-transform: uppercase;
}}
.hero-condition {{
    font-size: 1.1rem;
    font-weight: 300;
    opacity: 0.8;
    margin-top: 0.25rem;
}}
.hero-emoji {{
    font-size: 5rem;
    line-height: 1;
    filter: drop-shadow(0 4px 10px rgba(0,0,0,0.3));
}}

/* ---- Metric cards ---- */
.metric-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 1rem;
    margin-bottom: 2rem;
    animation: slideUp 0.7s 0.1s cubic-bezier(0.16, 1, 0.3, 1) both;
}}
.metric-card {{
    background: {card_bg};
    border: 1px solid rgba(255,255,255,0.12);
    backdrop-filter: blur(16px);
    -webkit-backdrop-filter: blur(16px);
    border-radius: 20px;
    padding: 1.4rem 1.6rem;
    transition: transform 0.2s, box-shadow 0.2s;
    box-shadow: 0 8px 32px rgba(0,0,0,0.15);
}}
.metric-card:hover {{
    transform: translateY(-4px);
    box-shadow: 0 16px 40px rgba(0,0,0,0.25);
}}
.metric-label {{
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    opacity: 0.6;
    margin-bottom: 0.6rem;
    color: {text_color};
}}
.metric-value {{
    font-size: 2rem;
    font-weight: 700;
    color: {accent};
    font-family: 'JetBrains Mono', monospace;
    line-height: 1;
}}
.metric-unit {{
    font-size: 0.85rem;
    opacity: 0.7;
    margin-left: 4px;
    font-weight: 300;
}}

/* ---- Section headings ---- */
.section-title {{
    font-size: 0.75rem;
    font-weight: 700;
    letter-spacing: 0.18em;
    text-transform: uppercase;
    color: {accent};
    margin-bottom: 1rem;
    opacity: 0.9;
}}

/* ---- Table styling ---- */
[data-testid="stDataFrame"] {{
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid rgba(255,255,255,0.1);
    animation: slideUp 0.8s 0.2s cubic-bezier(0.16, 1, 0.3, 1) both;
}}
[data-testid="stDataFrame"] > div {{
    background: {card_bg} !important;
    backdrop-filter: blur(16px) !important;
}}

/* ---- Chart ---- */
[data-testid="stArrowVegaLiteChart"], .stLineChart {{
    background: {card_bg} !important;
    border-radius: 20px !important;
    border: 1px solid rgba(255,255,255,0.10) !important;
    padding: 1rem !important;
    animation: slideUp 0.9s 0.3s cubic-bezier(0.16, 1, 0.3, 1) both;
}}

/* ---- Updated time badge ---- */
.updated-badge {{
    display: inline-block;
    background: rgba(255,255,255,0.1);
    border: 1px solid rgba(255,255,255,0.2);
    border-radius: 100px;
    padding: 0.3rem 1rem;
    font-size: 0.75rem;
    letter-spacing: 0.05em;
    backdrop-filter: blur(8px);
    color: {text_color};
    opacity: 0.8;
}}

/* ---- Humidity bar ---- */
.hum-bar-bg {{
    background: rgba(255,255,255,0.12);
    border-radius: 100px;
    height: 6px;
    margin-top: 0.6rem;
    overflow: hidden;
}}
.hum-bar-fill {{
    height: 100%;
    border-radius: 100px;
    background: {accent};
    transition: width 1s ease;
}}
</style>
""", unsafe_allow_html=True)

# ---------------- WEATHER PARTICLES ----------------
particles_html = '<div class="weather-particles">'
if is_rain:
    for _ in range(60):
        particles_html += '<div class="rain-drop"></div>'
if is_snow:
    for _ in range(40):
        particles_html += '<div class="snow-flake"></div>'
if is_night:
    import random
    for _ in range(80):
        top = random.randint(0, 80)
        left = random.randint(0, 100)
        size = random.randint(1, 3)
        delay = round(random.uniform(0, 4), 2)
        dur = round(random.uniform(2, 5), 2)
        particles_html += f'<div class="star" style="top:{top}%;left:{left}%;width:{size}px;height:{size}px;animation-delay:{delay}s;animation-duration:{dur}s;"></div>'
particles_html += '</div>'
st.markdown(particles_html, unsafe_allow_html=True)

# ---------------- HERO ----------------
emoji = condition_emoji(condition)
updated_str = last_updated.strftime("%A, %d %b %Y · %H:%M") if isinstance(last_updated, datetime) else str(last_updated)

st.markdown(f"""
<div class="hero-card">
  <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:1rem;">
    <div>
      <div class="hero-location">📍 {latest.get('location','—')}, {latest.get('country','—')}</div>
      <div class="hero-temp">{temp:.1f}°<span style="font-size:3rem;font-weight:300">C</span></div>
      <div class="hero-condition">{condition}</div>
      <br>
      <div class="updated-badge">🕐 Updated {updated_str}</div>
    </div>
    <div class="hero-emoji" style="text-align:right;">{emoji}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- METRIC CARDS ----------------
humidity = int(latest.get("humidity", 0))
wind = float(latest.get("wind_kph", 0))
feels_like = temp - 2.5  # approximate if not in DB

st.markdown(f"""
<div class="metric-grid">
  <div class="metric-card">
    <div class="metric-label">💧 Humidity</div>
    <div class="metric-value">{humidity}<span class="metric-unit">%</span></div>
    <div class="hum-bar-bg"><div class="hum-bar-fill" style="width:{humidity}%"></div></div>
  </div>
  <div class="metric-card">
    <div class="metric-label">💨 Wind Speed</div>
    <div class="metric-value">{wind:.1f}<span class="metric-unit">km/h</span></div>
  </div>
  <div class="metric-card">
    <div class="metric-label">🌡️ Feels Like</div>
    <div class="metric-value">{feels_like:.1f}<span class="metric-unit">°C</span></div>
  </div>
  <div class="metric-card">
    <div class="metric-label">🌍 Country</div>
    <div class="metric-value" style="font-size:1.4rem;">{latest.get('country','—')}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ---------------- TEMPERATURE CHART ----------------
st.markdown('<div class="section-title">📈 Temperature Trend (Latest 50 records)</div>', unsafe_allow_html=True)

chart_df = df[["last_updated", "temperature"]].copy()
chart_df["last_updated"] = pd.to_datetime(chart_df["last_updated"])
chart_df = chart_df.sort_values("last_updated")
chart_df = chart_df.set_index("last_updated")

st.line_chart(chart_df["temperature"], use_container_width=True, height=220)

# ---------------- DATA TABLE ----------------
st.markdown('<div class="section-title">📋 Raw Weather Records</div>', unsafe_allow_html=True)

display_df = df.copy()
display_df["condition"] = display_df["weather_condition"].apply(
    lambda x: f"{condition_emoji(x)} {x}"
)
display_df = display_df[["last_updated", "location", "country", "temperature", "humidity", "wind_kph", "condition"]]
display_df.columns = ["Updated", "Location", "Country", "Temp (°C)", "Humidity (%)", "Wind (km/h)", "Condition"]

st.dataframe(display_df, use_container_width=True, hide_index=True)
