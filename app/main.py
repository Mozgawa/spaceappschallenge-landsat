from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from datetime import datetime, timedelta


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


def send_email(email: str, pass_time: datetime):
    # Placeholder email sending logic (replace with real email API)
    print(f"Sending email to {email} about satellite pass at {pass_time}")


@app.post("/landsat/pass")
def get_landsat_pass_time(request: Request):
    pass_time = datetime.now() + timedelta(hours=1)

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
        "pass_time": pass_time.isoformat(),
        "notify_time": notify_time,
    }


@app.get("/landsat/check_notifications")
def check_notifications():
    current_time = datetime.now()
    for notification in notifications_db:
        if current_time >= notification["notify_time"]:
            send_email(notification["email"], notification["pass_time"])
    return {"message": "Checked notifications"}
