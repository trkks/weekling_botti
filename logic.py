def aloita(args, room_id):
    # Name for event must be specified
    if len(args) == 0:
        return ""

    domain = "lipaston_lappari.fi" # TODO
    event_name = "".join(args)
    query_string = "?event={}&room={}".format(event_name, room_id)

    return "Varaa tästä tapahtumaan {} -> http://{}{}"\
           .format(event_name, domain, query_string)

def tulokset(args, room_id):
    # Name for event must be specified
    if len(args) == 0:
        return ""

    # TODO Get list of free times from the database for the event in the room
    times = ["10112020T1500", "10112020T1600"]

    return "Ensimmäinen vapaa aika tapahtumalle {} on: {}"\
           .format("".join(args), times[0])
