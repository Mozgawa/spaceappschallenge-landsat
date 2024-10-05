from fastapi import FastAPI
from pydantic import BaseModel
from datetime import datetime

app = FastAPI()

class Location(BaseModel):
    longitude: float
    latitude: float

@app.post("/landsat/pass")
def get_landsat_pass_time(location: Location):
    pass_time = datetime.now()  # For now, return the current time
    return {
        "longitude": location.longitude,
        "latitude": location.latitude,
        "pass_time": pass_time.isoformat()
    }
