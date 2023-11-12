import requests, json
import openmeteo_requests
import requests_cache
from retry_requests import retry
from datetime import datetime, timedelta
cache_session = requests_cache.CachedSession('.cache', expire_after = -1)
retry_session = retry(cache_session, retries = 5, backoff_factor = 0.2)
openmeteo = openmeteo_requests.Client(session = retry_session)

def get_dates():
    """
    Get the start and end dates for a seven-day forecast.

    Returns:
        Tuple[str, str]: A tuple containing the start date and end date in the format 'YYYY-MM-DD'.
    """
    today = datetime.now()
    seventh_day = today + timedelta(days=6)
    startdate = today.strftime('%Y-%m-%d')
    enddate = seventh_day.strftime('%Y-%m-%d')
    return startdate, enddate

def get_district_datas():
    """
    Get district data including names, latitudes, and longitudes from an external JSON file.

    Returns:
        Tuple[List[str], List[float], List[float]]: A tuple containing lists of district names, latitudes, and longitudes.
    """
    names, lats, longs = [], [], [] 
    district_datas = json.loads(requests.get("https://raw.githubusercontent.com/strativ-dev/technical-screening-test/main/bd-districts.json").text)["districts"]
    sorted_data = sorted(district_datas, key=lambda x: int(x['id']))
    for i in range(len(sorted_data)):
        names.append(sorted_data[i]["name"])
        lats.append(sorted_data[i]["lat"])
        longs.append(sorted_data[i]["long"])
    return names, lats, longs

def get_hourly_datas(name_list, latitude_list, longitude_list):
    """
    Get hourly weather data for given districts.

    Args:
        name_list (List[str]): List of district names.
        latitude_list (List[float]): List of district latitudes.
        longitude_list (List[float]): List of district longitudes.

    Returns:
        List[Dict[str, Union[str, requests.Response]]]: A list of dictionaries containing district names and corresponding API responses.
    """
    startdate, enddate = get_dates()
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": latitude_list,
        "longitude": longitude_list,
        "hourly": "temperature_2m",
        "timezone": ["Asia/Singapore" for _ in range(len(latitude_list))],
        "start_date": [startdate for _ in range(len(latitude_list))],
        "end_date" : [enddate for _ in range(len(latitude_list))]
    }
    responses = openmeteo.weather_api(url, params=params)
    response_list = [{"name":name_list[i], "response":responses[i]} for i in range(len(responses))]
    return response_list