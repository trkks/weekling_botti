from urllib.parse import quote_plus
from datetime import datetime, timezone
from itertools import groupby
import scheduler
import os
import io

def ohje():
    return \
        "Ajanvarauksen aloittaminen:\n" \
        "!aloita <tapahtuman nimi>\n" \
        "Tuloksien pyytäminen:\n" \
        "!tulokset <tapahtuman nimi>\n" \
        "Tuloksien pyytäminen useammalle tunnille:\n" \
        "!tulokset_<kesto tunneissa väliltä 1-24> <tapahtuman nimi>"

NGROK_FILE = "ngrokosoite.txt"

def aloita(args, room_id, db):
    # Name for event must be specified
    event_name = args.strip()
    if len(event_name) == 0:
        return ""

    event_id = str(db.objects.insert_one({
        "room_id": room_id,
        "event_name": event_name,
        "times": []
    }).inserted_id)

    # Get ngrok url
    with io.open(NGROK_FILE, "r", encoding="utf-8") as fp:
        host_name = fp.readline().strip()

    # Pass meta-info to server
    query_string = "?id={}&event={}".format(quote_plus(event_id),
                                            quote_plus(event_name))

    return "Varaa tästä tapahtumaan {} -> {}{}" \
           .format(event_name, host_name, query_string)

def tulokset(hours, args, room_id, db):
    
    # Name for event must be specified
    event_name = args.strip()
    if len(event_name) == 0:
        return ""

    event_doc = db.objects.find_one({
        "room_id": room_id,
        "event_name": event_name
    })

    if event_doc is not None:
        days = ["Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai",
                "Lauantai", "Sunnuntai"]
        times = list(map(object_to_local_datelist, event_doc["times"]))
        result_time = scheduler.scheduler(times, hours)
        if result_time is not None:
            return "'{}': {} {}-{} Osallistujia {}/{}" \
                   .format(event_name, 
                        days[result_time[0][0].day-1],
                        result_time[0][0].hour, 
                        result_time[0][1].hour+1, 
                        result_time[1], len(times))
        return "Ei löydy yhteistä aikaa"

    return f"Tapahtumaa '{event_name}' ei löydy huoneesta"

def kaikki(hours, args, room_id, db):
    # Name for event must be specified
    event_name = args.strip()
    if len(event_name) == 0:
        return ""

    event_doc = db.objects.find_one({
        "room_id": room_id,
        "event_name": event_name
    })

    if event_doc is not None:
        # TODO Make this a dict, when using "relative days"
        days = ["Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai",
                "Lauantai", "Sunnuntai"]
        times = list(map(object_to_local_datelist, event_doc["times"]))
        result_times = scheduler.scheduler(times, hours, get_all=True)
        print(list(result_times))
        if result_times is not None:
            """
            Maanantai 11-12, 12-13, 15-16
            Torstai 11-12
            Sunnuntai 12-13, 15-16
            """
            result_times = sorted(result_times, key=lambda x: x[0])
            result_times = groupby(result_times, key=lambda x: x[0].day)

            spanstring = "" 
            #NOTE
            n = -1 # STUPID HACK
            #NOTE
            for day, timesofday in result_times:
                spanstring += days[day-1]
                n = 0
                for time in timesofday:
                    n += 1
                    spanstring += "{}-{}".format(time[0][0].hour,
                                                 time[0][0].hour+1)
                spanstring += "\n"
                
            return "'{}': Kaikki osallistujilla {}/{}:\n{}" \
                   .format(event_name, 
                           n,#result_times[0][1], 
                           len(times), 
                           spanstring)
        return "Ei löydy yhteistä aikaa"

    return f"Tapahtumaa '{event_name}' ei löydy huoneesta"


def object_to_local_datelist(obj):
    datelist = obj["date"]
    return list(map(lambda d: d.replace(tzinfo=timezone.utc).astimezone(),
                    datelist))








