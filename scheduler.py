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

    passert(scheduler([[d1],[d1],[]]), ((d1,d1), 2), 
        "The best possible date was not returned")

    assert scheduler([[d1],[d1],[d1]]) == ((d1,d1), 3), \
           "The only date between lists was not returned"

    assert scheduler([[d2,d1], [d1]]) == ((d1,d1), 2), \
           "The shared date between lists was not returned"

    assert scheduler([[d1],[d2],[d3]]) == None, \
           "Different dates in every list did not return `None`"

    assert scheduler([ [d1,d1,d1], [], [] ]) == None, \
           "Amount of entries is not equivalent to amount of 'shared' date"

    success("Time-specific cases")
    ##############################

    d4 = datetime.fromisoformat("2020-11-03T12:00:00.000+00:00")

    assert scheduler([[d1,d2], [d3,d1,d2], [d2,d1,d4]]) == ((d2,d2), 3), \
           "The earliest shared date was not returned"

    success("Business-logic-specific cases")
    ########################################

    # TODO Add variable-hour -tests

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

    assert find_spans([d1,d2,d3,d4,d5], 2) == [(d1,d2), (d2,d3), (d4,d5)]

    d6 = datetime.fromisoformat("2020-11-04T14:00:00.000+00:00")
    d7 = datetime.fromisoformat("2020-11-04T23:00:00.000+00:00")
    d8 = datetime.fromisoformat("2020-11-05T00:00:00.000+00:00")

    assert find_spans([d1,d2,d6], 2) == [(d1,d2)]
    # NOTE Jos kalenterista tehdään 24h, niin testiä pitää korjata
    assert find_spans([d7,d8], 2) == [] 

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

    spans = []
    for hoursofday in daily_times:
        left, right = 0, 1
        start = left
        while right <= len(hoursofday):
            if right == len(hoursofday) \
            or hoursofday[right].hour - hoursofday[left].hour != 1:
                spans.append(get_spans(hoursofday[start:left+1], hours))
                start = left+1
            left += 1
            right += 1

    return list(chain.from_iterable(spans))

def get_spans(consecutive, hours):
    l, r = 0, 1
    spans = []
    while r < len(consecutive):
        if consecutive[r].hour - consecutive[l].hour == hours-1:
            spans.append((consecutive[l], consecutive[r]))
            l += 1
        r += 1

    return spans
            

# FIXME Jos joku on syöttänyt useampaan "ryhmään" sopivia aikoja, tämä poistuu
# "parhaimmasta" ryhmästä ks. mongon "botteilutesti" 4. entry
def scheduler(entries, hours=1):
    # Remove duplicates from different entries
    all_dates = [list(set(user_entry)) for user_entry in entries]
    # Find the wanted spans from all entries
    all_spans = map(lambda l: find_spans(l, hours), all_dates)
    # Flatten the list of lists of spans, 
    # eg. [[d1],[d2,d3],[d2]] -> [d1,d2,d3,d2]
    all_spans = chain.from_iterable(all_spans)
    # Sort the spans for grouping,
    # eg. [d1,d2,d3,d2] -> [d1,d2,d2,d3]
    all_spans = sorted(all_spans, key=lambda x: x[0])
    # Pick spans by days into their own groups,
    # eg. [d1,d2,d2,d3] -> [(d1, [d1]), (d2, [d2,d2]), (d3, [d3])]
    span_groups = groupby(all_spans)
    span_groups = [(k, list(g)) for k,g in span_groups]
    # Pick the group that has most spans > 1
    shared_span_group = max(span_groups, 
                            key=lambda g: len(list(g[1])),
                            default=None)
    # Select the first span in *time*
    n = len(list(shared_span_group[1])) if shared_span_group is not None else 0
    return (shared_span_group[0], n) \
           if n > 1 \
           else None


if __name__ == "__main__":
    test_scheduler()
    test_find_spans()
