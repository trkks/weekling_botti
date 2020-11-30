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
        "!tulokset_<kesto tunneissa väliltä 1-24> <tapahtuman nimi>\n" \
        "Lista vaihtoehtoisista ajoista, joissa suurin osallistujamäärä:\n" \
        "!kaikki <tapahtuman nimi>"

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
            return "'{}': {} {}-{}, osallistujia {}/{}" \
                   .format(event_name, 
                        days[result_time[0][0].day-1],
                        result_time[0][0].hour, 
                        result_time[0][1].hour+1, 
                        result_time[1], len(times))
        return f"'{event_name}': Ei löydy yhteistä aikaa"

    return f"'{event_name}': Tapahtumaa ei löydy huoneesta"

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
        if result_times is not None:
            """
            Maanantai 11-12, 12-13, 15-16
            Torstai 11-12
            Sunnuntai 12-13, 15-16


            result_times = [ ((alku1, loppu1), lkm_väli1), 
                             ((alku2, loppu2), lkm_väli2)  ... ]
            """
            result_times = sorted(result_times, key=lambda x: x[0][0])
            result_times = groupby(result_times, key=lambda x: x[0][0].day)
            """
            result_times = [ 
                (pvä1, [
                    ((alku1, loppu1), lkm_väli), 
                    ((alku2, loppu2), lkm_väli) ]),
                (pvä2, [
                    ((alku3, loppu3), lkm_väli), 
                    ((alku4, loppu4), lkm_väli), 
                    ((alku5, loppu5), lkm_väli) ]) 
            ]

            """

            spanstring = "" 
            #NOTE
            n = -1 # STUPID HACK
            #NOTE
            for day, timesofday in result_times:
                spanstring += "{}: ".format(days[day-1])
                for time in timesofday:
                    n = time[1] # save the amount of entries every time
                    spanstring += "{}-{}; ".format(time[0][0].hour,
                                                   time[0][1].hour + 1)
                spanstring += "\n"
                
            return "'{}': Kaikki sopivat ajat osallistujamäärällä {}/{}:\n{}" \
                   .format(event_name, 
                           n,
                           len(times), 
                           spanstring)
        return f"'{event_name}': Ei löydy yhteisiä aikoja"

    return f"'{event_name}': Tapahtumaa ei löydy huoneesta"


def object_to_local_datelist(obj):
    datelist = obj["date"]
    weekday_now = 3 #datetime.now().isoweekday() # weekday from 1 to 7
    
    """
    Tietokanta || Scheduler-logiikka
 [6]Ma == 1    -> Jos Tiistai niin Ma == 7
 [0]Ti == 2
 [1]Ke == 3
 [2]To == 4
 [3]Pe == 5
 [4]La == 6
 [5]Su == 7
    """
    relative_weekdays = []
    for i in range(weekday_now, weekday_now+7):
        k = i % 7
        relative_weekdays.append(k if k != 0 else 7)

    print(relative_weekdays)

    #for date in datelist:
    #    date.replace(tzinfo=timezone.utc).astimezone()
    #    #date.replace()
    #
    #return datelist

    return list(map(lambda d: d.replace(day=relative_weekdays[d.day-1],
                                        tzinfo=timezone.utc)
                                        .astimezone(),
                    datelist))








