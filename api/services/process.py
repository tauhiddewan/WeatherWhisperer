import time 
from datetime import datetime, timedelta
import requests, json
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor

def get_weekly_mean_per_district(district_data_response):
    """
    Calculate the weekly mean temperature for a given district.

    Args:
        district_data_response (openmeteo_requests.Client.Hourly): Hourly weather data for a district.

    Returns:
        float: The weekly mean temperature for the district.
    """
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

def process_district(response_data):
    """
    Process the district data to calculate the weekly mean temperature.

    Args:
        response_data (Dict[str, Union[str, requests.Response]]): Dictionary containing district name and API response.

    Returns:
        Dict[str, float]: Dictionary containing district name and corresponding weekly mean temperature.
    """
    return {response_data["name"]: get_weekly_mean_per_district(response_data["response"])}


def get_10_coolest_districts(district_data_responses):
    """
    Get the 10 coolest districts based on weekly mean temperature using parallel processing.

    Args:
        district_data_responses (List[Dict[str, Union[str, requests.Response]]]): List of dictionaries containing district names and API responses.

    Returns:
        List[Dict[str, float]]: List of dictionaries containing district names and corresponding weekly mean temperatures.
    """
    with ProcessPoolExecutor() as executor:
        processed_data = list(executor.map(process_district, district_data_responses))
    sorted_data_list = sorted(processed_data, key=lambda x: list(x.values())[0])
    return sorted_data_list[:10]


# if __name__=="__main__":
#     names, lats, longs = get_district_datas()
#     responses = get_hourly_datas(name_list=names, latitude_list=lats, longitude_list=longs)
#     result = get_10_coolest_districts(district_data_responses=responses)
