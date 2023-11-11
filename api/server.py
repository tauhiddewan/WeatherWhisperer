import time
from fastapi import FastAPI
from api.services.download import get_district_datas, get_hourly_datas
from api.services.process import get_10_coolest_districts



names, lats, longs = get_district_datas()
app = FastAPI()
@app.get("/")
def get_coolest_10_districts():
    t1 = time.time()
    responses = get_hourly_datas(name_list=names, latitude_list=lats, longitude_list=longs)
    result = get_10_coolest_districts(district_data_responses=responses)
    print(f"Time taken for response : {time.time()-t1}")
    return result