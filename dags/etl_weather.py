# ---------------- IMPORTS ----------------
import os
from datetime import datetime

# ---------------- CONFIG ----------------
# ⚠️ In Docker, dotenv may not work → fallback to default
DATABASE_URL = os.getenv("DATABASE_URL")
API_KEY = "ebff15146ee14b72be693414261703"
BASE_URL = "http://api.weatherapi.com/v1/current.json"


# ---------------- EXTRACT ----------------
def extract():
    import requests

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
    import pandas as pd

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
    import psycopg2
    from psycopg2.extras import execute_batch

    try:
        print("[LOAD] Connecting to DB...")

        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()

        # Create table
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

        # Batch insert
        execute_batch(cursor, """
            INSERT INTO weather
            (location, country, temperature, humidity, weather_condition, wind_kph, last_updated)
            VALUES (%s,%s,%s,%s,%s,%s,%s)
        """, df.values.tolist())

        conn.commit()
        cursor.close()
        conn.close()

        print("[LOAD] Success")

    except Exception as e:
        print(f"[ERROR][LOAD] {e}")
        raise


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