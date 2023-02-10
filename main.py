from fastapi import FastAPI, HTTPException, Body
from datetime import date, datetime, timedelta
from pydantic import BaseModel
from pymongo import MongoClient
import dotenv
import os

dotenv.load_dotenv(".env")
usrn = os.getenv("user")
pswd = os.getenv("password")
DATABASE_NAME = "exceed12"
COLLECTION_NAME = "kk devices"
MONGO_DB_URL = f"mongodb://{usrn}:{pswd}@mongo.exceed19.online:8443/?authMechanism=DEFAULT"
MONGO_DB_PORT = 8443

client = MongoClient(f"{MONGO_DB_URL}")
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]
app = FastAPI()

class Device(BaseModel):
    room_id: int            #room id
    tray_level: bool        #1 empty, 0 full
    tank_level: bool        #1 empty, 0 full
    pet_active: bool        #1 active, 0 no
    auto_refill: bool       #1 yes, 0 no
    manual_refill: bool     #1 yes, 0 no
    PIR_on: bool            #1 yes, 0 no

@app.post("/newdevice")
def newdevice(device: Device):
    body = {
        "room_id": device.room_id,
        "tray_level": device.tray_level,
        "tank_level": device.tank_level,
        "pet_active": device.pet_active,
        "auto_refill": device.auto_refill,
        "manual_refill": device.manual_refill,
        "PIR_on": device.PIR_on
    }
    collection.insert_one(body)
    return "inserted room id " + str(device.room_id)

@app.get("/getdata/all/{room_id}")
def get_all(room_id: int):
    result = collection.find_one({"room_id": room_id})
    return {"room_id": room_id,
            "tray_level": result["tray_level"],
            "tank_level": result["tank_level"],
            "pet_active": result["pet_active"],
            "auto_refill": result["auto_refill"],
            "manual_refill": result["manual_refill"],
            "PIR_on": result["PIR_on"]}

@app.get("/getdata/pet_active/{room_id}")
def get_pet_active(room_id: int):
    result = collection.find_one({"room_id": room_id})
    return {"pet_active": result["pet_active"]}


@app.get("/getdata/commands/{room_id}")
def get_commands(room_id: int):
    result = collection.find_one({"room_id": room_id})
    return {"auto_refill": result["auto_refill"],
            "manual_refill": result["manual_refill"],
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

@app.put("/update/manual_refill/{room_id}/{manual_refill}")
def update_manual_refill(room_id: int,manual_refill: bool):
    collection.update_one({"room_id":room_id},{"$set":{"manual_refill": manual_refill}})
    return "set manual refill " + str(manual_refill)

@app.put("/update/PIR_on/{room_id}/{PIR_on}")
def update_PIR_on(room_id: int,PIR_on: bool):
    collection.update_one({"room_id":room_id},{"$set":{"PIR_on": PIR_on}})
    return "set PIR " + str(PIR_on)