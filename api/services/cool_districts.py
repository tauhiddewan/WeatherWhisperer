import time 
from datetime import datetime, timedelta
import requests, json
import openmeteo_requests
import requests_cache
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
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
    t1 = time.time()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude,
        "longitude": longitude,
        "hourly": "temperature_2m",
        "timezone": "Asia/Singapore"
    }
    responses = openmeteo.weather_api(url, params=params)
    print(f"Data scapping time : {time.time()-t1}")
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
    weekly_sum = 0
    for i, date in enumerate(df['date'].unique()):
        data = {}
        q1_mean = df[(df['date'] == date) & (df['time'] >= "00:00:00") & (df['time'] < "14:00:00")]["temp"].mean()
        q2_mean = df[(df['date'] == date) & (df['time'] >= "14:00:00") & (df['time'] < "24:00:00")]["temp"].mean()
        if i==0:
            weekly_sum+=q2_mean
        elif i==7:
            weekly_sum+=q1_mean
        else:
            weekly_sum+= q1_mean+q2_mean    
    return weekly_sum/14

    # q_datas = []
    # for i, date in enumerate(df['date'].unique()):
    #     data = {}
    #     q1_mean = df[(df['date'] == date) & (df['time'] >= "00:00:00") & (df['time'] < "14:00:00")]["temp"].mean()
    #     q2_mean = df[(df['date'] == date) & (df['time'] >= "14:00:00") & (df['time'] < "24:00:00")]["temp"].mean()
    #     data[i] = {"date": date , "q1": q1_mean, "q2": q2_mean}
    #     q_datas.append(data)

    # # weekly_data = {}
    # weekly_sum = 0
    # for i in range(1, len(q_datas)):
    #     daily_mean = (q_datas[i-1][i-1]["q2"]+q_datas[i][i]["q1"])/2
    #     weekly_sum+=daily_mean
    #     # weekly_data[q_datas[i][i]["date"]] = daily_mean
    # weekly_mean = weekly_sum/7
    # return weekly_mean

def process_district(district_data):
    return {district_data["name"]: get_weekly_mean_per_district(district_data)}

def get_10_coolest_districts(district_datas):
    district_sets = []
    with ProcessPoolExecutor() as executor:
        district_sets = list(executor.map(process_district, district_datas))

    sorted_data_list = sorted(district_sets, key=lambda x: list(x.values())[0])
    return sorted_data_list[:10]


# t1 = time.time()
# get_10_coolest_districts()
# print(time.time()-t1)






# def get_weekly_mean_per_district(district_data):
#     data = get_daily_data(longitude=district_data["long"], latitude=district_data["lat"])
#     daily_max_temp = data.Variables(0).ValuesAsNumpy()
#     daily_min_temp = data.Variables(1).ValuesAsNumpy()
#     daily_mean_temp = (daily_max_temp+daily_min_temp)/2
#     return daily_mean_temp.mean()



# def get_10_coolest_districts():
#     district_sets = []
#     district_datas = json.loads(requests.get("https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json").text)["districts"]
#     for i in range(len(district_datas)):
#         district_sets.append({district_datas[i]["name"] : get_weekly_mean_per_district(district_datas[i])})
#     sorted_data_list = sorted(district_sets, key=lambda x: list(x.values())[0])
#     return sorted_data_list[:10]


# def get_daily_data(latitude, longitude):
#     url = "https://api.open-meteo.com/v1/forecast"
#     params = {
#         "latitude": latitude,
#         "longitude": longitude,
#         "daily": ["temperature_2m_max", "temperature_2m_min"],
#         "timezone": "Asia/Singapore"
#     }
#     responses = openmeteo.weather_api(url, params=params)[0].Daily()
#     return responses




# names, longs, lats = [], [], [] 
# district_datas = json.loads(requests.get("https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json").text)["districts"]
# sorted_data = sorted(district_datas, key=lambda x: int(x['id']))

# for i in range(len(sorted_data)):
#     names.append(sorted_data[i]["name"])
#     longs.append(sorted_data[i]["longs"])
#     lats.append(sorted_data[i]["lats"])
# # pprint(sorted_data)
# pprint(names)