import io
import scheduler
from urllib.parse import quote_plus
from datetime import datetime, timezone
from itertools import groupby

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

    # Check if event of same name already exists in room. Insert new one if not
   
    cursor = db.objects.find(
        {
            "room_id": room_id,
            "event_name": event_name
        }
    )

    try:
        event_id_obj = cursor[0]["_id"]
        # Erase old times-data from existing event
        db.objects.update_one(
            {
                "_id": event_id_obj,
            },
            {   "$set" : {
                    "times": [] 
                }
            })
        event_id = str(event_id_obj)
    except IndexError:
        # Create an all new event-document
        event_id = str(db.objects.insert_one(
            {
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
        times, days = get_relative_times(event_doc["times"])

        result_time = scheduler.scheduler(times, hours)
        if result_time is not None:
            return "'{}': {} {}-{}, osallistujia {}/{}" \
                   .format(event_name, 
                        days[result_time[0][0].day],
                        result_time[0][0].hour, 
                        result_time[0][1].hour+1, 
                        result_time[1], len(times))
        return f"'{event_name}': Ei löydy yhteistä aikaa"

    return f"'{event_name}': Tapahtumaa ei löydy huoneesta"

def kaikki(hours, args, room_id, db):
    # Name for event must be specified
    event_name = args.strip()
    if len(event_name) == 0 or 24 < hours < 1:
        return ""

    event_doc = db.objects.find_one({
        "room_id": room_id,
        "event_name": event_name
    })

    if event_doc is not None:
        times, days = get_relative_times(event_doc["times"])

        result_times = scheduler.scheduler(times, hours, get_all=True)
        if result_times is not None:
            """
            Maanantai 11-12, 12-13, 15-16
            Torstai 11-12
            Sunnuntai 12-13, 15-16


            result_times = [ ((alku1, loppu1), lkm_väli), 
                             ((alku2, loppu2), lkm_väli)  ... ]
            """
            result_times = sorted(result_times, key=lambda x: x[0][0])
            result_times = groupby(result_times, key=lambda x: x[0][0].day)
            result_times = [(k, list(g)) for k,g in result_times]
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

            # Get number of participants here for printing
            n = result_times[0][1][0][1]

            spanstring = "" 
            for day, timesofday in result_times:
                spanstring += "{}: ".format(days[day])
                for time in timesofday:
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

def get_relative_times(dbtimes):
    """"
    Convert db-format suitable for scheduler and create a relative weekday-list
    returns: (list of datetime lists, relative weekdays)
    """

    # Remove object-wrapping
    times = map(lambda obj: obj["date"], dbtimes)

    # Apply the conversion to machine-local-timezone for all datetimes
    times = list(map(lambda ds: 
            list(map(lambda d:d.replace(tzinfo=timezone.utc).astimezone(),ds)),
        times))

    # filter out datetimes that have passed (in hours) on current day
    daynow = datetime.now()
    hournow = daynow.hour
    weekdaynow = daynow.isoweekday() # weekday from 1 to 7

    times = map(lambda ds: 
            filter(lambda d: d.day != weekdaynow or d.hour > hournow, ds),
        times)

    # Change day-values for scheduler's logic:

    """
    Jos Keskiviikko:
    Ma == 1 -> 6
    Ti == 2 -> 7
    Ke == 3 -> 1
    To == 4 -> 2 
    Pe == 5 -> 3
    La == 6 -> 4
    Su == 7 -> 5
    """
    relative_days = list(
        range(7-weekdaynow+2, 7+1)) + list(range(1,7-weekdaynow+2))

    # Apply the conversion to relative day
    times = list(map(lambda ds:
            list(map(lambda d: d.replace(day=relative_days[d.day-1]), ds)),
        times))

    # Make a dict, which tells weekdays from the now converted day-values
    day_names = ["Maanantai", "Tiistai", "Keskiviikko", "Torstai", "Perjantai",
                 "Lauantai", "Sunnuntai"]
    relative_day_names = dict(zip(relative_days, day_names))

    return (times, relative_day_names)
