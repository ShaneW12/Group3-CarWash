
import requests

BASE_URL = "https://vpic.nhtsa.dot.gov/api/vehicles"


def get_vehicle_makes():
    url = f"{BASE_URL}/GetMakesForVehicleType/car?format=json"

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.json()["Results"]


def get_vehicle_models(make, year):
    url = (
        f"{BASE_URL}/GetModelsForMakeYear/"
        f"make/{make}/modelyear/{year}?format=json"
    )

    response = requests.get(url, timeout=10)
    response.raise_for_status()

    return response.json()["Results"]
