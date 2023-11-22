from fastapi import FastAPI, Request
from typing import Dict
import requests
import json
import redis
import os
import platform

# To be configurable
REDIS_ADD = os.getenv('REDIS_ADD')
MAIN_LOC = os.getenv('MAIN_LOC')
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
CACHE_TIME = os.getenv('CACHE_TIME')

r = redis.Redis(host=REDIS_ADD, port=6379, decode_responses=True)
app = FastAPI()


def extract_data(weather_stats: Dict) -> Dict:
    return {'temp_c': weather_stats['current']['temp_c'], 'temp_f': weather_stats['current']['temp_f']}


@app.get("/")
async def get_main_weather(request: Request):
    resp = await get_weather(request, MAIN_LOC)
    return resp


@app.get("/{city}")
async def get_weather(request: Request, city: str):
    cached_resp = r.get(city)
    if cached_resp is not None:
        resp = json.loads(cached_resp)
        resp['type'] = 'Cached'
        resp['pod'] = request.headers.get('host')
        return resp

    if WEATHER_API_KEY is None:
        return {'message', "Sorry, We can't resolve your request right now. Please retry in a few hours."}

    url = "https://weatherapi-com.p.rapidapi.com/current.json"
    querystring = {"q": city}
    headers = {
        "X-RapidAPI-Key": WEATHER_API_KEY,
        "X-RapidAPI-Host": "weatherapi-com.p.rapidapi.com"
    }
    full_resp = requests.get(url, headers=headers, params=querystring)
    # print(full_resp.json())

    new_resp = extract_data(full_resp.json())
    r.setex(city, CACHE_TIME, json.dumps(new_resp))
    new_resp['type'] = 'Hot'
    new_resp['pod'] = platform.uname()[1]
    return new_resp
