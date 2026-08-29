"""
merge_real_data.py
--------------------
Aapke paas already outputs/merged_data.csv hai (jisme temperature hai).
Ye script us mein REAL CDC health data (heat_illness_er_rate_per_100k) jod deta hai,
taake dobara API call na karni pade.

Chalane ka tareeqa:
    python merge_real_data.py
"""

import pandas as pd

# Pehle se fetched temperature data
temp_df = pd.read_csv("outputs/merged_data.csv")

# Real CDC health data
health_df = pd.read_csv("data/real_health_outcomes.csv")

# Sirf zaroori columns lo real data se
health_df = health_df[["location_name", "heat_illness_er_rate_per_100k"]]

# location_name ke through jodo (merge/join)
merged = temp_df.merge(health_df, on="location_name", how="left")

# Purana demo outcome column (energy_consumption_kwh) hata do agar hai
if "energy_consumption_kwh" in merged.columns:
    merged = merged.drop(columns=["energy_consumption_kwh"])

merged.to_csv("outputs/merged_data.csv", index=False)
print("✅ Real health data jud gaya! outputs/merged_data.csv update ho gayi.")
print(merged[["location_name", "temperature_c", "heat_illness_er_rate_per_100k"]])
