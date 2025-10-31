import json

import streamlit as st
from weatherclass import WeatherReport

st.set_page_config(page_title="Weather Dashboard", page_icon="🌤️")

st.title("🌤️ Live Weather Dashboard")

city = st.text_input("Enter city", "Stockholm")

error_message = None

if st.button("Get Weather"):
    try:
        report = WeatherReport(city)
        report.fetch_and_store(city=city)
    except Exception as e:
        error_message = str(e)

if error_message:
    st.error(error_message)
    st.stop()

# Load latest weather data
try:
    with open("data.json") as f:
        weather = json.load(f)
except FileNotFoundError:
    st.warning("No weather data yet. Enter a city and click 'Get Weather'.")
    st.stop()

# Extract info
w = weather["data"]
temp = w["main"]["temp"]
feels_like = w["main"]["feels_like"]
humidity = w["main"]["humidity"]
wind = w["wind"]["speed"]
condition = w["weather"][0]["main"]
description = w["weather"][0]["description"].title()
icon_code = w["weather"][0]["icon"]
icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"

# Detect dark/light theme
dark_mode = st.get_option("theme.base") == "dark"
bg = "#1e1e1e" if dark_mode else "#ffffff"
text = "#ffffff" if dark_mode else "#000000"
muted = "#b3b3b3" if dark_mode else "#555555"

icon_code = w["weather"][0]["icon"]
icon_url = f"http://openweathermap.org/img/wn/{icon_code}@2x.png"
description = w["weather"][0]["description"].title()

# CSS
st.markdown(f"""
<style>
.weather-card {{
    background: {bg};
    border-radius: 18px;
    padding: 28px;
    text-align: center;
    margin-top: 20px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.25);
}}
.weather-temp {{
    font-size: 52px;
    font-weight: 800;
    color: {text};
    margin-top: -5px;
}}
.weather-desc {{
    font-size: 22px;
    font-weight: 500;
    color: {muted};
    margin-bottom: 10px;
}}
</style>
""", unsafe_allow_html=True)

# HTML card block
st.markdown(f"""
<div class="weather-card">
    <img src="{icon_url}" width="110">
    <div class="weather-temp">{temp}°C</div>
    <div class="weather-desc">{description}</div>
</div>
""", unsafe_allow_html=True)

# Streamlit metrics BELOW the HTML so they do not break the card container
col1, col2, col3 = st.columns(3)
col1.metric("Feels Like", f"{feels_like}°C")
col2.metric("Humidity", f"{humidity}%")
col3.metric("Wind", f"{wind} m/s")

st.caption(f"City: {weather['city']} · Updated: {weather['fetched_at']}")
