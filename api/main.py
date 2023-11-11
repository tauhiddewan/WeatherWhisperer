import time 
from datetime import datetime, timedelta
import requests, json
import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from pprint import pprint

cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)


def get_dates():
    today = datetime.now()
    seventh_day = today + timedelta(days=8)
    startdate = today.strftime('%Y-%m-%d')
    enddate = seventh_day.strftime('%Y-%m-%d')
    return startdate, enddate


def get_hourly_data(latitude, longitude):
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "timezone": "Asia/Singapore"
    }
    responses = openmeteo.weather_api(url, params=params)
    return responses

def get_weekly_mean_per_district(district_data):
    data = get_hourly_data(longitude=district_data["long"], latitude=district_data["lat"])[0].Hourly()
    hourly_data = {"date": pd.date_range(
        start = pd.to_datetime(data.Time(), unit = "s"),
        end = pd.to_datetime(data.TimeEnd(), unit = "s"),
        freq = pd.Timedelta(seconds = data.Interval()),
        inclusive = "left"
    )}
    hourly_data["temp"] = data.Variables(0).ValuesAsNumpy()
    df = pd.DataFrame(data = hourly_data)
    df['date'] = df['date'].dt.strftime('%Y-%m-%d %H:%M:%S')
    df[['date', 'time']] = df['date'].str.split(' ', expand=True)
    df = df[['date', 'time', 'temp']]

    q_datas = []
    for i, date in enumerate(df['date'].unique()):
        data = {}
        q1_mean = df[(df['date'] == date) & (df['time'] >= "00:00:00") & (df['time'] < "14:00:00")]["temp"].mean()
        q2_mean = df[(df['date'] == date) & (df['time'] >= "14:00:00") & (df['time'] < "24:00:00")]["temp"].mean()
        data[i] = {"date": date , "q1": q1_mean, "q2": q2_mean}
        q_datas.append(data)

    # weekly_data = {}
    weekly_sum = 0
    for i in range(1, len(q_datas)):
        daily_mean = (q_datas[i-1][i-1]["q2"]+q_datas[i][i]["q1"])/2
        weekly_sum+=daily_mean
        # weekly_data[q_datas[i][i]["date"]] = daily_mean
    weekly_mean = weekly_sum/7
    return weekly_mean

def get_10_coolest_districts():
    district_sets = []
    t1 = time.time()
    district_datas = json.loads(requests.get("https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json").text)["districts"]
    print(f"Data collection time : {time.time()-t1}")

    t1 = time.time()
    for i in range(len(district_datas)):
        district_sets.append({district_datas[i]["name"] : get_weekly_mean_per_district(district_datas[i])})
    print(f"Data process time : {time.time()-t1}")
    return district_sets

get_10_coolest_districts()