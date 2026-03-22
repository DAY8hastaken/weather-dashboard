import requests
import pandas as pd
import psycopg
from dotenv import load_dotenv
import os
from datetime import datetime

# ---------------- CONFIG ----------------
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

API_KEY = "ebff15146ee14b72be693414261703" 
BASE_URL = "http://api.weatherapi.com/v1/current.json"


# ---------------- EXTRACT ----------------
def extract():
    params = {
        "key": API_KEY,
        "q": "Phnom Penh"
    }

    response = requests.get(BASE_URL, params=params, timeout=10)

    if response.status_code != 200:
        raise Exception(f"API failed: {response.status_code} - {response.text}")

    print("[EXTRACT] Success")
    return response.json()


# ---------------- TRANSFORM ----------------
def transform(data):
    df = pd.DataFrame([{
        "location": data["location"]["name"],
        "country": data["location"]["country"],
        "temperature": data["current"]["temp_c"],
        "humidity": data["current"]["humidity"],
        "weather_condition": data["current"]["condition"]["text"],
        "wind_kph": data["current"]["wind_kph"],
        "last_updated": datetime.strptime(
            data["current"]["last_updated"], "%Y-%m-%d %H:%M"
        )
    }])

    print("[TRANSFORM] Success")
    return df


# ---------------- LOAD ----------------
def load(df):
    conn = None
    cursor = None

    try:
        print("[LOAD] Connecting to DB...")
        conn = psycopg.connect(DATABASE_URL)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS weather (
                id SERIAL PRIMARY KEY,
                location TEXT,
                country TEXT,
                temperature FLOAT,
                humidity INT,
                weather_condition TEXT,
                wind_kph FLOAT,
                last_updated TIMESTAMP
            )
        """)

        for row in df.itertuples(index=False):
            cursor.execute("""
                INSERT INTO weather
                (location, country, temperature, humidity, weather_condition, wind_kph, last_updated)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, tuple(row))

        conn.commit()
        print("[LOAD] Success")

    except Exception as e:
        print(f"[ERROR][LOAD] {e}")
        raise

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


# ---------------- PIPELINE ----------------
def run_weather_pipeline():
    print("🚀 Running Weather Pipeline...")

    data = extract()
    df = transform(data)
    load(df)

    print("✅ Pipeline finished!")


# ---------------- RUN ----------------
if __name__ == "__main__":
    run_weather_pipeline()
