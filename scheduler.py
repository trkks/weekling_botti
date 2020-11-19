from datetime import (datetime, timedelta)
from itertools import (chain, groupby, dropwhile, combinations, tee)
from functools import reduce

# Utilities for test-related printing
success = lambda s: print(f"   Testing '{s}' - PASSED")

def passert(result, expected, msg=""):
    assert result == expected, \
        "\n  Result was {}\n  Expected {}{}" \
        .format(result, expected, "\n  "+msg if msg else "")

##############################################################################

def test_scheduler():
    print("Starting SCHEDULER tests.")

    assert scheduler([]) == None, \
           "No entries didn't return `None`"

    assert scheduler([[]]) == None, \
           "Empty entry didn't return `None`"

    success("Base cases")
    #####################

    d1 = datetime.fromisoformat("2020-11-04T10:00:00.000+00:00")
    d2 = datetime.fromisoformat("2020-11-04T09:00:00.000+00:00")
    d3 = datetime.fromisoformat("2020-11-03T09:00:00.000+00:00")

    assert scheduler([[d1]]) == None, \
           "The only date was not returned"

    assert scheduler([[d1,d1]]) == None, \
           "The duplicate date was not returned"

    passert(scheduler([[d1],[d1],[]]), (d1, 2), 
        "The best possible date was not returned")

    assert scheduler([[d1],[d1],[d1]]) == (d1, 3), \
           "The only date between lists was not returned"

    assert scheduler([[d2,d1], [d1]]) == (d1, 2), \
           "The shared date between lists was not returned"

    assert scheduler([[d1],[d2],[d3]]) == None, \
           "Different dates in every list did not return `None`"

    assert scheduler([ [d1,d1,d1], [], [] ]) == None, \
           "Amount of entries is not equivalent to amount of 'shared' date"

    success("Time-specific cases")
    ##############################

    d4 = datetime.fromisoformat("2020-11-03T12:00:00.000+00:00")

    assert scheduler([[d1,d2], [d3,d1,d2], [d2,d1,d4]]) == (d2, 3), \
           "The earliest shared date was not returned"

    success("Business-logic-specific cases")
    ########################################

    print("!! SCHEDULER tests done.")


def test_find_spans():
    print("Starting FIND_SPANS tests.")

    # TODO Convert to list in tests, so the function can return any iterable
    passert( find_spans([], -1), [] ) 
    assert find_spans([], 0) == []
    assert find_spans([], 1) == []
    passert(find_spans([], 2), [])


    success("Base cases")
    #####################

    # The datetimes are named in timed order ie. d1 < d2 < d3 ...
    d1 = datetime.fromisoformat("2020-11-03T12:00:00.000+00:00")
    d2 = datetime.fromisoformat("2020-11-03T13:00:00.000+00:00")

    #passert( find_spans([d1], 0), [(d1,d1)] ) ihanmitävaan vai fail?
    # TODO PÄÄTETÄÄN: Pitäiskö palauttaa None toisena alkiona, jos etsitään 1
    # tuntia?
    passert( find_spans([d1], 1), [(d1,d1)] )
    passert( find_spans([d1], 2), [] )
    passert( find_spans([d1,d2], 1), [(d1,d1), (d2,d2)] )
    passert( find_spans([d1,d2], 2), [(d1,d2)] )

    success("Cases with two different times")
    ##############################

    d3 = datetime.fromisoformat("2020-11-03T14:00:00.000+00:00")
    d4 = datetime.fromisoformat("2020-11-03T16:00:00.000+00:00")
    d5 = datetime.fromisoformat("2020-11-03T17:00:00.000+00:00")

    passert( find_spans([d1,d2,d3], 1), [(d1,d1), (d2,d2), (d3,d3)] )
    passert( find_spans([d1,d2,d3], 2), [(d1,d2), (d2,d3)] )

    assert find_spans([d1,d2,d3,d4], 2) == [(d1,d2), (d2,d3), (d4,d5)]

    d6 = datetime.fromisoformat("2020-11-04T14:00:00.000+00:00")
    d7 = datetime.fromisoformat("2020-11-04T23:00:00.000+00:00")
    d8 = datetime.fromisoformat("2020-11-05T00:00:00.000+00:00")

    assert find_spans([d1,d2,d6], 2) == [(d1,d2)]
    # TODO PÄÄTETÄÄN: Etsitäänkö päivänvaihteiden väliltä?, vaatisi varmaan
    # todellisia pvmiä (nyt menee viikkonäkymästä "koordinaattein")
    assert find_spans([d8,d7], 2) == [] 

    success("Cases with more than two times and between days")
    #######################################

    print("!! FIND_SPANS test done.")


def find_spans(times, hours=1):
    """
    From a list of datetimes, find all occurrences of consecutive datetimes in 
    each day, that span the given `hours`.
    Note that here (10,10) is considered 1 hour span, (10, 11) 2 hours and so.
    return: a list of datetime-tuples which describe spans of `hours`
    """

    # Handle special cases
    if hours < 1:
        return []
    if hours == 1:
        return list(map(lambda t: (t, t), times)) # NOTE useless change to list
    if not times or len(times) < hours:
        return []
        
    # Group times by their day
    daily_times = groupby(times, key=lambda d: d.day)
    daily_times = map(lambda t: sorted(list(t[1])), daily_times)

    """
    Algoritmia:

    Alussa aina:
    0. Saadaan aikalista `times` ja kuinka pitkiä pätkiä halutaan etsiä `hours`
    1. 
       1.1 Jos `hours` < 1, niin palautetaan tyhjä lista
       1.2 Jos `hours` == 1, niin palautetaan samat ajat sopivassa muodossa
       1.3 Luokitellaan ajat päivittäisiksi (-> ei tarkastelua päivien välillä)
           ja järjestetään alalistat (tunnit kasvavassa järjestyksessä)
    
    2. Jokaisen päivän tuntilistaa kohti kerätään peräkkäiset pätkät
       peräkkäiset = []
        2.1 Aluksi tarvitaan apumuuttujat: 
            vasen = 0,
            oikea = 1,
            tunteja_putkeen = 1
        2.2 Käydään tuntilistaa t läpi eli while(t and oikea < len(t))
            t = [1,2,3, 5,6,7,8, 10,11]
            Jos t[oikea] - t[vasen] == 1:
                tunteja_putkeen += 1
            Muuten:
                pätkä = t[0:oikea]
                t = [oikea:]
                peräkkäiset.append(pätkä)
                oikea = -1
                vasen = 0
                tunteja_putkeen = 1

            oikea += 1
            vasen += 1
    3. Tiedossa on eripituisia pätkiä, annetaan parametri jossa tietty numero,
       numeron perusteella pitää löytää sen pituisia pätkiä. Pitää ottaa
       huomioon että pidemmistä pätkistä voi saada useampia lyhyempiä pätkiä
 
    """
    return []

def scheduler(entries, hours=1):
    # Remove duplicates from different entries
    all_dates = [list(set(user_entry)) for user_entry in entries]
    # Flatten the list of lists of dates, 
    # eg. [[d1],[d2,d3],[d2]] -> [d1,d2,d3,d2]
    all_dates = chain.from_iterable(all_dates)
    # Sort the dates for grouping,
    # eg. [d1,d2,d3,d2] -> [d1,d2,d2,d3]
    all_dates = sorted(all_dates)
    # Pick same dates into their own groups,
    # eg. [d1,d2,d2,d3] -> [(d1, [d1]), (d2, [d2,d2]), (d3, [d3])]
    date_groups = groupby(all_dates)
    date_groups = [(k, list(g)) for k,g in date_groups]
    # Pick the group that has most dates > 1
    shared_date = max(date_groups, key=lambda g: len(list(g[1])), default=None)
    # Select the first date in *time*
    n = len(list(shared_date[1])) if shared_date is not None else 0
    return (shared_date[0], n) \
           if n > 1 \
           else None


if __name__ == "__main__":
    test_scheduler()
    test_find_spans()

