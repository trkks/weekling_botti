from urllib.parse import quote_plus
from datetime import datetime
from itertools import groupby
import scheduler
import os
import io


NGROK_FILE = "../weekling-web/webback/ngrokosoite.txt"

def aloita(args, room_id, db):
    # Name for event must be specified
    event_name = args.strip()
    if len(event_name) == 0:
        return ""

    db.objects.insert_one({
        "room_id": room_id,
        "event_name": event_name,
        "times": []
    })

    # Get ngrok url
    with io.open(NGROK_FILE, "r", encoding="utf-8") as fp:
        host_name = fp.readline().strip()

    # Pass meta-info to server
    query_string = "?event={}&room={}".format(quote_plus(event_name),
                                              quote_plus(room_id))

    return "Varaa tästä tapahtumaan {} -> {}{}" \
           .format(event_name, host_name, query_string)

def tulokset(args, room_id, db):
    # Name for event must be specified
    event_name = args.strip()
    if len(event_name) == 0:
        return ""

    event_doc = db.objects.find_one({
        "room_id": room_id,
        "event_name": event_name
    })

    if event_doc is not None:
        times = event_doc["times"]
        result_time = scheduler.my_scheduler(times)
        if result_time is not None:
            return "Ensimmäinen vapaa aika tapahtumalle {} on: {}" \
                   .format(event_name, result_time)
        return "Ei löydy yhteistä aikaa"

    return "Ei löydy tapahtumaa huoneesta"

