# FortyGuard Regression Toolkit — Track 7

Temperature (FortyGuard API) ko kisi bhi outcome data (energy, crime, foot-traffic, etc.) ke sath correlate karne wala tool.

## Kaise chalayein (5 steps)

### 1. Dependencies install karo
```bash
pip install -r requirements.txt --break-system-packages
```

### 2. API key set karo
```bash
cp .env.example .env
```
Ab `.env` file kholo aur apni asal FortyGuard API key `FORTYGUARD_API_KEY=` ke aage paste kar do.

### 3. (Optional) Apna data use karo
`data/sample_outcomes.csv` mein 20 US cities ka demo data hai (energy consumption).
Agar apna real data hai, isi format mein CSV banao:
```
location_name,latitude,longitude,date,time,energy_consumption_kwh
```
> Column ka naam `energy_consumption_kwh` chahe jo bhi outcome ho, us naam ko
> `analyze_regression.py` mein `OUTCOME_COLUMN` variable mein bhi update kar dena.

### 4. Temperature data fetch karo
```bash
python fetch_temperatures.py
```
Ye har location ke liye FortyGuard API se temperature mangwayega aur
`outputs/merged_data.csv` mein save kar dega.

### 5. Regression/analysis chalao
```bash
python analyze_regression.py
```
Ye output dega:
- Terminal mein correlation, p-value, R-squared
- `outputs/regression_result.txt` — text results
- `outputs/scatter_plot.png` — chart (temperature vs outcome)

## Project files
```
fortyguard_regression/
├── data/sample_outcomes.csv     # input: locations + outcome data
├── fetch_temperatures.py        # Step 1: API se temperature mangwana
├── analyze_regression.py        # Step 2: correlation/regression nikalna
├── outputs/                     # results yahan save hote hain
├── .env.example                 # API key template
└── requirements.txt
```

## Note
- API sirf **US locations** ke liye kaam karti hai
- Date range: **2021-01-01 se aaj tak**
- Agar `fetch_temperatures.py` chalate waqt koi row fail ho, wo `None` temperature ke sath
  save hoti hai — `analyze_regression.py` khud usko skip kar deta hai
