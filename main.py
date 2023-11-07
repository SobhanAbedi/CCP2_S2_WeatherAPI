from fastapi import FastAPI
from typing import Dict
import requests
import redis
import os

# To be configurable
REDIS_ADD = os.getenv('REDIS_ADD')
MAIN_LOC = os.getenv('MAIN_LOC')
WEATHER_API_KEY = os.getenv('API_KEY')

r = redis.Redis(host=REDIS_ADD, port=6379, decode_responses=True)
app = FastAPI()


def extract_data(weather_stats: Dict) -> Dict:
    return {'temp_c': weather_stats['current']['temp_c'], 'temp_f': weather_stats['current']['temp_f']}


@app.get("/")
async def get_main_weather():
    resp = await get_weather(MAIN_LOC)
    return resp


@app.get("/{city}")
async def get_weather(city: str):
    cached_resp = r.get(city)
    if cached_resp is not None:
        return cached_resp

    if API_KEY is None:
        return {'message', "Sorry, We can't resolve your request right now. Please retry in a few hours."}

    url = "https://weatherapi-com.p.rapidapi.com/current.json"
    querystring = {"q": city}
    headers = {
        "X-RapidAPI-Key": API_KEY,
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }
    full_resp = requests.get(url, headers=headers, params=querystring)
    print(full_resp)

    new_resp = extract_data(full_resp.json())
    r.setex(city, 300, str(new_resp))

    return new_resp
