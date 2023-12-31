import time
import json
import pickle
import pandas as pd
from dateutil import parser
from fastapi import FastAPI
from api.services.download import get_district_datas, get_hourly_datas
from api.services.process import get_10_coolest_districts

names, lats, longs = get_district_datas()
with open("api/model/xgb_model.pkl", 'rb') as file:
    model = pickle.load(file)

app = FastAPI()
@app.get("/")
def get_coolest_10_districts():
    t1 = time.time()
    responses = get_hourly_datas(name_list=names, latitude_list=lats, longitude_list=longs)
    result = get_10_coolest_districts(district_data_responses=responses)
    print(f"Time taken for response : {time.time()-t1}")
    return result

@app.post("/predict")
def get_temp_forecast(date: str):
    try:
        date_json = json.loads(date)
        new_date = pd.to_datetime(date_json)
        day_of_year = new_date.dayofyear
        predicted_temperature = model.predict([day_of_year])[0]
        return {"given_date": str(date_json), "predicted_temp": str(predicted_temperature)}
    except:
        return {"error": "Invalid JSON format for the date parameter. Please use quotation marks. Write the date in YYYY:MM:DD or DD:MM:YYYY format."}