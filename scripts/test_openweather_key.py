import os
import requests

api_key = os.environ["OWM_API_KEY"]
params = {"q": "Dublin,IE", "appid": api_key, "units": "metric"}

resp = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params, timeout=30)
print("status", resp.status_code)
print(resp.text[:300])
