from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, EmailStr
from skyfield.api import Topos, load

app = FastAPI()


class Location(BaseModel):
    longitude: float
    latitude: float


class Request(BaseModel):
    email: EmailStr
    longitude: float
    latitude: float
    lead_time: int


notifications_db = []


def get_pass_time(latitude: float, longitude: float, landsat_version: int = 9):
    url = "https://celestrak.org/NORAD/elements/resource.txt"
    satellites = load.tle_file(url)

    try:
        satellite = {sat.name: sat for sat in satellites}[f"LANDSAT {landsat_version}"]
    except KeyError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No Landsat version {landsat_version}",
        )

    # Define the location (latitude, longitude)
    location = Topos(latitude, longitude)

    # Load timescale and start time
    ts = load.timescale()
    t = ts.now()

    # Loop over future times to find when the satellite will pass overhead
    for minutes_ahead in range(0, 1440, 10):  # Check every 10 minutes for the next 24 hours
        time_to_check = t + timedelta(minutes=minutes_ahead)
        difference = satellite - location
        topocentric = difference.at(time_to_check)
        alt, az, distance = topocentric.altaz()

        # If satellite is overhead (altitude > 0)
        if alt.degrees > 0:
            return time_to_check.utc_iso()

    return "No overpass within the next 24 hours"


def send_email(email: str, pass_time: datetime):
    # Placeholder email sending logic (replace with real email API)
    print(f"Sending email to {email} about satellite pass at {pass_time}")


@app.post("/pass")
def get_landsat_pass_time(request: Request):
    pass_time = datetime.strptime(
        get_pass_time(request.latitude, request.longitude), "%Y-%m-%dT%H:%M:%SZ"
    )

    notify_time = pass_time - timedelta(minutes=request.lead_time)

    notification = {
        "email": request.email,
        "longitude": request.longitude,
        "latitude": request.latitude,
        "notify_time": notify_time,
        "pass_time": pass_time,
    }
    notifications_db.append(notification)

    return {
        "longitude": request.longitude,
        "latitude": request.latitude,
        "pass_time": pass_time,
        "notify_time": notify_time,
    }


@app.get("/check_notifications")
def check_notifications():
    current_time = datetime.now()
    for notification in notifications_db:
        if current_time >= notification["notify_time"]:
            send_email(notification["email"], notification["pass_time"])
    return {"message": "Checked notifications"}
