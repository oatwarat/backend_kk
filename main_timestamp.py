import pymongo
from fastapi import FastAPI
from pymongo import MongoClient
from dotenv import load_dotenv
import os
from datetime import date, datetime, timedelta

app = FastAPI()
load_dotenv(".env")
DATABASE_NAME = "exceed12"
COLLECTION_NAME = "time"
usrn = os.getenv("username")
pswd = os.getenv("password")
print(usrn)
print(pswd)
MONGO_DB_URL = f"mongodb://{usrn}:{pswd}@mongo.exceed19.online:8443/?authMechanism=DEFAULT"
client = MongoClient(MONGO_DB_URL)

db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

def format_time(total_time_in_seconds):
    time_in_seconds = int(total_time_in_seconds)
    minutes, seconds = divmod(time_in_seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)

    time_string = ""
    if days > 0:
        time_string = f"{days} day{'s' if days > 1 else ''}"
    elif hours > 0:
        time_string = f"{hours} hour{'s' if hours > 1 else ''}"
    elif minutes > 0:
        time_string = f"{minutes} minute{'s' if minutes > 1 else ''}"
    else:
        time_string = f"{seconds} second{'s' if seconds > 1 else ''}"

    return time_string


@app.get("/rooms/time")
async def get_room_time():
    today = datetime.now().date()
    yesterday = today - timedelta(days=1)
    week_ago = today - timedelta(weeks=1)
    month_ago = today - timedelta(days=30)
    year_ago = today - timedelta(days=365)

    rooms_time = []
    rooms = collection.distinct("room_id")
    for room in rooms:
        total_time_today = 0
        total_time_yesterday = 0
        total_time_week = 0
        total_time_month = 0
        total_time_year = 0
        room_data = collection.find({"room_id": room})
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
            "today": format_time(total_time_today),
            "yesterday": format_time(total_time_yesterday),
            "week_ago": format_time(total_time_week),
            "month_ago": format_time(total_time_month),
            "year_ago": format_time(total_time_year),
        })

    return {"rooms_time": rooms_time}