import time 
from datetime import datetime, timedelta
import requests, json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def get_weekly_mean_per_district(district_data_response):
    data = district_data_response.Hourly()
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
    sum = 0
    for i, date in enumerate(df['date'].unique()):
        data = {}
        q1_mean = df[(df['date'] == date) & (df['time'] >= "00:00:00") & (df['time'] < "14:00:00")]["temp"].mean()
        q2_mean = df[(df['date'] == date) & (df['time'] >= "14:00:00") & (df['time'] < "24:00:00")]["temp"].mean()
        if i==0:
            sum+=q2_mean
        elif i==7:
            sum+=q1_mean
        else:
            sum+= q1_mean+q2_mean    
    return sum/14

def get_10_coolest_districts(district_data_responses):
    district_sets = []
    for i in range(len(district_data_responses)):
        district_sets.append({district_data_responses[i]["name"] : get_weekly_mean_per_district(district_data_responses[i]["response"])})
    sorted_data_list = sorted(district_sets, key=lambda x: list(x.values())[0])
    return sorted_data_list[:10]


def process_district(response_data):
    return {response_data["name"]: get_weekly_mean_per_district(response_data["response"])}


def get_10_coolest_districts(district_data_responses):
    with ProcessPoolExecutor() as executor:
        processed_data = list(executor.map(process_district, district_data_responses))
    sorted_data_list = sorted(processed_data, key=lambda x: list(x.values())[0])
    return sorted_data_list[:10]


# if __name__=="__main__":
#     names, lats, longs = get_district_datas()
#     responses = get_hourly_datas(name_list=names, latitude_list=lats, longitude_list=longs)
#     result = get_10_coolest_districts(district_data_responses=responses)