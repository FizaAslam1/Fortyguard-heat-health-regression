"""
fetch_temperatures.py
----------------------
Ye script data/sample_outcomes.csv padhta hai (har row mein: location, lat, lon, date, time, outcome value)
Har row ke liye FortyGuard Temperature API (/v1/heatmap) ko call karta hai, us jagah ka temperature nikalta hai,
aur sab kuch ek merged CSV mein save kar deta hai: outputs/merged_data.csv

Chalane ka tareeqa:
    python fetch_temperatures.py
"""

import os
import time
import requests
import pandas as pd
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("FORTYGUARD_API_KEY")
BASE_URL = os.getenv("FORTYGUARD_BASE_URL", "https://api.fortyguard.com")

if not API_KEY or "yahan_apni_key" in API_KEY:
    raise SystemExit(
        "❌ API key nahi mili. .env.example ko .env mein copy karo aur apni asal "
        "FortyGuard API key FORTYGUARD_API_KEY= ke aage paste karo."
    )

HEADERS = {"api-key": API_KEY, "Content-Type": "application/json"}

# Har location ke around kitna chota box banana hai (degrees mein).
# 0.005 degree ~ 500 meters — itna kaafi hai ek "point" jaisa temperature lene ke liye.
BOX_HALF_SIZE = 0.005


def build_small_polygon(lat: float, lon: float) -> dict:
    """Ek location ke around chota polygon (box) banata hai, kyunke API polygon maangti hai."""
    d = BOX_HALF_SIZE
    return {
        "type": "Polygon",
        "coordinates": [[
            [lon - d, lat - d],
            [lon + d, lat - d],
            [lon + d, lat + d],
            [lon - d, lat + d],
            [lon - d, lat - d],
        ]],
    }


def submit_heatmap_request(lat: float, lon: float, date: str, time_str: str) -> str:
    """API ko request bhejta hai aur activity_id wapas deta hai."""
    payload = {
        "polygon_aoi": build_small_polygon(lat, lon),
        "date_time": {
            "start_date": date,
            "start_time": time_str,
            "filter_type": 1,  # single hour
        },
        "granularity": 60,  # sabse fine granularity, kyunke area chota hai
    }
    resp = requests.post(f"{BASE_URL}/v1/heatmap", headers=HEADERS, json=payload)
    resp.raise_for_status()
    data = resp.json()
    return data["data"]["activity_id"]


def poll_until_done(activity_id: str, timeout: int = 120, interval: int = 3) -> dict:
    """Activity_id ka status check karta rehta hai jab tak result na mil jaye."""
    waited = 0
    url = f"{BASE_URL}/v1/status/{activity_id}"
    while waited < timeout:
        resp = requests.get(url, headers=HEADERS)
        resp.raise_for_status()
        data = resp.json()
        status = str(data.get("data", data).get("status", "")).lower()
        if status in ("completed", "succeeded"):
            return data.get("data", data)
        if status == "failed":
            raise RuntimeError(f"Activity {activity_id} FAILED: {data}")
        time.sleep(interval)
        waited += interval
    raise TimeoutError(f"Activity {activity_id} timeout ho gaya ({timeout}s).")


def extract_mean_temperature(result: dict) -> float:
    """Result JSON se average temperature nikalta hai."""
    # Pehle stats_data mein dhoondo
    stats = result.get("result", result).get("stats_data", {})
    temp_stats = stats.get("temperature_stats")
    if isinstance(temp_stats, dict) and "mean" in temp_stats:
        return float(temp_stats["mean"])

    # Fallback: map_data ke tiles se average nikalo
    map_data = result.get("result", result).get("map_data", {})
    features = map_data.get("features", [])
    temps = [
        f["properties"]["average_temperature"]
        for f in features
        if "average_temperature" in f.get("properties", {})
    ]
    if temps:
        return sum(temps) / len(temps)

    raise ValueError(f"Temperature nahi mili result mein: {result}")


def main():
    df = pd.read_csv("data/sample_outcomes.csv")
    temperatures = []

    print(f"📡 {len(df)} locations ke liye FortyGuard se temperature mangwa rahe hain...\n")

    for idx, row in df.iterrows():
        name = row["location_name"]
        print(f"  [{idx + 1}/{len(df)}] {name} ... ", end="", flush=True)
        try:
            activity_id = submit_heatmap_request(
                row["latitude"], row["longitude"], row["date"], row["time"]
            )
            result = poll_until_done(activity_id)
            mean_temp = extract_mean_temperature(result)
            temperatures.append(mean_temp)
            print(f"✅ {mean_temp:.1f}°C")
        except Exception as e:
            print(f"❌ Fail ho gaya: {e}")
            temperatures.append(None)

    df["temperature_c"] = temperatures

    os.makedirs("outputs", exist_ok=True)
    out_path = "outputs/merged_data.csv"
    df.to_csv(out_path, index=False)
    print(f"\n✅ Done! Merged data save ho gaya: {out_path}")


if __name__ == "__main__":
    main()
