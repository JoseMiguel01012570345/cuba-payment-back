import requests
import os


def route_distance(lat1, lon1, lat2, lon2):
    API_KEY = os.getenv("OPENSTREET_API_KEY")

    url = "https://api.openrouteservice.org/v2/directions/driving-car"
    headers = {
        "Authorization": API_KEY,
        "Content-Type": "application/json"
    }
    body = {
        "coordinates": [[lon1, lat1], [lon2, lat2]]
    }

    res = requests.post(url, json=body, headers=headers)
    data = res.json()

    distance_m = data["routes"][0]["summary"]["distance"]
    duration_s = data["routes"][0]["summary"]["duration"]

    return distance_m, duration_s
