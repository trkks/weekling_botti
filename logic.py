def aloita(args, room_id, db):
    # Name for event must be specified
    if len(args) == 0:
        return ""

    event_name = "".join(args)
    times = db.testi_botti # NOTE Päättäkää collectionien arkkitehtuurista
    times.insert_one({
        "event_name": event_name, # TODO ks ylempi kommentti
        "times": []
    })
    host_name = "e6975d60ee4d.ngrok.io" # TODO get hostname from ngrok
    query_string = "?event={}&room={}".format(event_name, room_id)

    return "Varaa tästä tapahtumaan {} -> http://{}{}" \
           .format(event_name, host_name, query_string)

def tulokset(args, room_id, db):
    # Name for event must be specified
    if len(args) == 0:
        return ""

    event_name = "".join(args)
    # TODO Get list of free times from the database for the event in the room
    event_doc = db.testi_botti.find_one()
    
    if event_doc is not None:
        #times = ["10112020T1500", "10112020T1600"]
        times = event_doc["times"]
        if len(times) > 0:
            return "Ensimmäinen vapaa aika tapahtumalle {} on: {}" \
                   .format(event_name, times[0])

    return str(event_doc)

