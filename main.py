from fastapi import FastAPI, HTTPException, Body, APIRouter
from datetime import date, datetime, timedelta
from pydantic import BaseModel
from pymongo import MongoClient
import dotenv
import os
from fastapi.middleware.cors import CORSMiddleware

dotenv.load_dotenv(".env")
usrn = os.getenv("user")
pswd = os.getenv("password")
DATABASE_NAME = "exceed12"
COLLECTION_NAME = "kk devices"
LOG_COLLECTION_NAME = "time"
MONGO_DB_URL = f"mongodb://{usrn}:{pswd}@mongo.exceed19.online:8443/?authMechanism=DEFAULT"
MONGO_DB_PORT = 8443

client = MongoClient(f"{MONGO_DB_URL}")
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
log_collection = db[LOG_COLLECTION_NAME]
app = FastAPI()
router = APIRouter()

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Device(BaseModel):
    room_id: int            #room id
    tray_level: bool        #1 empty, 0 full :20%
    tank_level: bool        #1 empty, 0 full :25%
    pet_active: bool        #1 active, 0 no
    auto_refill: bool       #1 yes, 0 no
    open_door: bool         #1 open door, 0 close door
    PIR_on: bool            #1 yes, 0 no

@app.get("/")
def homepage():
    return "home"

@app.post("/newdevice")
def newdevice(device: Device):
    if collection.find({"room_id":device.room_id}):
        return "device already exists"
    body = {
        "room_id": device.room_id,
        "tray_level": device.tray_level,
        "tank_level": device.tank_level,
        "pet_active": device.pet_active,
        "auto_refill": device.auto_refill,
        "open_door": device.open_door,
        "PIR_on": device.PIR_on
    }
    collection.insert_one(body)
    return "inserted room id " + str(device.room_id)

@app.delete("/removedevice/{room_id}")
def removedevice(room_id: int):
    collection.delete_one({"room_id":room_id})
    log_collection.delete_many({"room_id":room_id})
    return "deleted room id " + str(room_id) + " and all timestamp logs"

@app.get("/getdata/all/{room_id}")
def get_all(room_id: int):
    result = collection.find_one({"room_id": room_id})
    return {"room_id": room_id,
            "tray_level": result["tray_level"],
            "tank_level": result["tank_level"],
            "pet_active": result["pet_active"],
            "auto_refill": result["auto_refill"],
            "open_door": result["open_door"],
            "PIR_on": result["PIR_on"]}

@app.get("/getdata/pet_active/{room_id}")
def get_pet_active(room_id: int):
    result = collection.find_one({"room_id": room_id})
    return result["pet_active"]

@app.get("/getdata/commands/{room_id}")
def get_commands(room_id: int):
    result = collection.find_one({"room_id": room_id})
    return {"auto_refill": result["auto_refill"],
            "open_door": result["open_door"],
            "PIR_on": result["PIR_on"]}

@app.get("/getdata/levels/{room_id}")
def get_levels(room_id: int):
    result = collection.find_one({"room_id": room_id})
    return {"tray_level": result["tray_level"],
            "tank_level": result["tank_level"]}

@app.put("/update/tray_level/{room_id}/{tray_level}")
def update_tray_level(room_id: int,tray_level: bool):
    collection.update_one({"room_id":room_id},{"$set":{"tray_level": tray_level}})
    return "set tray level " + str(tray_level)

@app.put("/update/tank_level/{room_id}/{tank_level}")
def update_tank_level(room_id: int,tank_level: bool):
    collection.update_one({"room_id":room_id},{"$set":{"tank_level": tank_level}})
    return "set tank level " + str(tank_level)

@app.put("/update/pet_active/{room_id}/{pet_active}")
def update_pet_active(room_id: int,pet_active: bool):
    collection.update_one({"room_id":room_id},{"$set":{"pet_active": pet_active}})
    return "set pet active " + str(pet_active)

@app.put("/update/auto_refill/{room_id}/{auto_refill}")
def update_auto_refill(room_id: int,auto_refill: bool):
    collection.update_one({"room_id":room_id},{"$set":{"auto_refill": auto_refill}})
    return "set auto refill " + str(auto_refill)

@app.put("/update/open_door/{room_id}/{open_door}")
def update_open_door(room_id: int,open_door: bool):
    collection.update_one({"room_id":room_id},{"$set":{"open_door": open_door}})
    return "set door " + str(open_door)

@app.put("/update/PIR_on/{room_id}/{PIR_on}")
def update_PIR_on(room_id: int,PIR_on: bool):
    collection.update_one({"room_id":room_id},{"$set":{"PIR_on": PIR_on}})
    return "set PIR " + str(PIR_on)

class Time(BaseModel):
    room_id: int
    timestamp: int

def format_time(total_time_in_seconds):
    time_in_seconds = int(total_time_in_seconds)
    minutes, seconds = divmod(time_in_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    time_string = ""
    if days > 0:
        time_string = f"{days} day{'s' if days > 1 else ''}"
    if hours > 0:
        time_string = time_string + f" {hours} hour{'s' if hours > 1 else ''}"
    if minutes > 0:
        time_string = time_string + f" {minutes} minute{'s' if minutes > 1 else ''}"
    if seconds > 0 or not time_string:
        time_string = time_string + f" {seconds} second{'s' if seconds > 1 else ''}"

    return time_string


@app.get("/rooms/time")
async def get_room_time():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(weeks=1)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)

    rooms_time = []
    rooms = log_collection.distinct("room_id")
    for room in rooms:
        total_time_today = 0
        total_time_yesterday = 0
        total_time_week = 0
        total_time_month = 0
        total_time_year = 0
        room_data = log_collection.find({"room_id": room})
        last_timestamp = None
        for data in room_data:
            timestamp = datetime.fromtimestamp(float(data["timestamp"]))
            if last_timestamp:
                time_diff = (timestamp - last_timestamp).total_seconds()
                if timestamp.date() == today:
                    total_time_today += time_diff
                elif timestamp.date() == yesterday:
                    total_time_yesterday += time_diff
                elif timestamp.date() >= week_ago:
                    total_time_week += time_diff
                elif timestamp.date() >= month_ago:
                    total_time_month += time_diff
                elif timestamp.date() >= year_ago:
                    total_time_year += time_diff
            last_timestamp = timestamp

        rooms_time.append({
            "room_id": room,
            "total_time_today": format_time(total_time_today),
            "total_time_yesterday": format_time(total_time_yesterday),
            "total_time_week": format_time(total_time_week),
            "total_time_month": format_time(total_time_month),
            "total_time_year": format_time(total_time_year)
        })

    return rooms_time