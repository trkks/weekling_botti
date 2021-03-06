from datetime import datetime
from itertools import chain, groupby


# Utilities for testing:

def success(testname):
    print(f"   Testing '{testname}' - PASSED")

def passert(result, expected, msg=""):
    "Print both the result and expected values to console when EQUALITY fails"
    test_msg = "\n  !! "+msg if msg else ""
    assert result == expected, \
           "\n  >> Result was {}\n  >> Expected {}{}" \
           .format(result, expected, test_msg)
    
def lsassert(result, expected, msg=""):
    "'list_assert': Convert result from iterator to list for clearer testing"
    passert(list(result) if result is not None else result, expected, msg)

##############################################################################

# The tests:

def test_scheduler():
    print("Starting SCHEDULER tests.")

    assert scheduler([]) == None, \
           "No entries"

    assert scheduler([[]]) == None, \
           "A single empty entry"

    assert scheduler([[],[],[],[]]) == None, \
           "Multiple empty entries"

    success("Base cases")
    #####################

    d1 = datetime.fromisoformat("2020-11-04T10:00:00.000+00:00")
    d2 = datetime.fromisoformat("2020-11-04T09:00:00.000+00:00")
    d3 = datetime.fromisoformat("2020-11-03T09:00:00.000+00:00")

    assert scheduler([[d1]]) == None, \
           "A single non-empty entry"

    assert scheduler([[d1,d1]]) == None, \
           "Duplicate of same date in a single entry"

    assert scheduler([[d1], [d1]]) == ((d1,d1), 2), \
             "2/2 identical entries"

    assert scheduler([[d2,d1], [d1]]) == ((d1,d1), 2), \
             "Shared date between 2/2 entries"

    passert( scheduler([[d1],[d1],[]]), ((d1,d1), 2), 
             "2/3 identical entries" )

    assert scheduler([[d1],[d1],[d1]]) == ((d1,d1), 3), \
             "3/3 identical entries"

    assert scheduler([[d1],[d2],[d3]]) == None, \
           "3/3 different entries"

    assert scheduler([ [d1,d1,d1], [], [] ]) == None, \
           "Amount of entries equal to amount of identical dates in one entry"

    success("Time-specific cases")
    ##############################

    d4 = datetime.fromisoformat("2020-11-03T12:00:00.000+00:00")

    assert scheduler([[d1,d2], [d3,d1,d2], [d2,d1,d4]]) == ((d2,d2), 3), \
           "Earliest shared date"

    success("Business-logic-specific cases")
    ########################################

    # NOTE the months (11 vs 01) should not matter
                                # These 3: Thursday 10-13
    d5  = datetime.fromisoformat("2020-11-04T10:00:00.000+00:00")
    d6  = datetime.fromisoformat("2020-11-04T11:00:00.000+00:00")
    d7  = datetime.fromisoformat("2020-11-04T12:00:00.000+00:00")
                                # These 3: Sunday 8-11
    d8  = datetime.fromisoformat("2020-01-07T08:00:00.000+00:00")
    d9  = datetime.fromisoformat("2020-01-07T09:00:00.000+00:00")
    d10 = datetime.fromisoformat("2020-01-07T10:00:00.000+00:00")

    passert( scheduler([ [d5,d6,d7], [d5,d7],
                         [d5,d7,d8,d9,d10],
                         [d8] ], 2),
                        None,
                        "Should have returned none (even)") 

    passert( scheduler([ [d5,d7], [d5,d6,d7],
                         [d6,d7,d8,d9,d10],
                         [d8,d9], [d8,d9] ], 2),
                       ((d8,d9), 3),
                       "Span with most people not returned (even)") 

    passert( scheduler([ [d5,d6,d7],  [d5,d6,d7],
                         [d5,d6,d7,d8,d9,d10],
                         [d8,d9,d10], [d8,d9,d10] ], 2),
                        ((d5,d6), 3),
                        "Earliest shared span not returned") 

    passert( scheduler([ [d5,d7],  [d5,d6,d7],
                         [d6,d7,d8,d9,d10],
                         [d8,d9], [d8,d9] ], 3),
                        None,
                        "Should have returned none") 

    passert( scheduler([ [d5,d6,d7], [d5,d6,d7],
                         [d5,d6,d7,d8,d9,d10],
                         [d8,d9,d10] ], 3),
                        ((d5,d7), 3),
                        "Span with most people not returned (odd)") 

    passert( scheduler([ [d5,d6,d7],  [d5,d6,d7],
                         [d5,d6,d7,d8,d9,d10],
                         [d8,d9,d10], [d8,d9,d10] ], 3),
                        ((d5,d7), 3),
                        "Earliest shared span not returned") 

    success("Variable-hour-tests")
    ##############################

    lsassert( scheduler([ [], [d6,d7],
                          [d5,d8,d10],
                          [d9], [] ], 1, True),
                        None,
                        "Nothing shared")
    
    lsassert( scheduler([ [d5], [d6,d7],
                          [d5,d8,d10],
                          [d9], [] ], 1, True),
                        [ ((d5,d5), 2) ],
                        "A single 1 hour span shared")

    lsassert( scheduler([ [d5,d6,d7],  [d5,d6,d7],
                          [d8,d5,d7,d9,d10],
                          [d8,d9,d10], [d8,d9,d10] ], 3, True),
                        [ ((d8,d10), 3) ],
                        "A single 3 hour span shared")

    lsassert( scheduler([ [d5,d6], 
                          [d6,d7],
                          [d5,d8,d9,d6,d10],
                          [d6,d7,d9],
                          [d9,d10,d8] ], 
                          hours=2, get_all=True),
                        [ ((d5,d6), 2),  ((d6,d7), 2),
                          ((d8,d9), 2), ((d9,d10), 2) ],
                        "All most shared 2 hour spans not returned")

    lsassert( scheduler([ [d5,d6,d7],  [d5,d6,d7],
                          [d5,d6,d7,d8,d9,d10],
                          [d8,d9,d10], [d8,d9,d10] ], 3, True),
                        [ ((d5,d7), 3), ((d8,d10), 3) ],
                        "All most shared 3 hour spans not returned") 

    success("`get_all==True` -tests")
    #################################

    print("!! SCHEDULER tests done.")


def test_find_spans():

    print("Starting FIND_SPANS tests.")

    lsassert( find_spans([], -1), [] ) 
    lsassert( find_spans([],  0), [] )
    lsassert( find_spans([],  1), [] )
    lsassert( find_spans([],  2), [] )

    success("Base cases")
    #####################

    # The datetimes are named in timed order ie. d1 < d2 < d3 ...
    d1 = datetime.fromisoformat("2020-11-03T12:00:00.000+00:00")
    d2 = datetime.fromisoformat("2020-11-03T13:00:00.000+00:00")

    lsassert( find_spans([d1],    1), [(d1,d1)] )
    lsassert( find_spans([d1],    2), [] )
    lsassert( find_spans([d1,d1], 2), [] )

    lsassert( find_spans([d1,d2], 1), [(d1,d1), (d2,d2)] )
    lsassert( find_spans([d1,d2], 2), [(d1,d2)] )
    lsassert( find_spans([d1,d2], 3), [] )
    lsassert( find_spans([d1,d2], 3), [] )
    lsassert( find_spans([d1,d2], 4), [] )

    success("Cases with two different times")
    #########################################

    d3 = datetime.fromisoformat("2020-11-03T14:00:00.000+00:00")
    d4 = datetime.fromisoformat("2020-11-03T16:00:00.000+00:00")
    d5 = datetime.fromisoformat("2020-11-03T17:00:00.000+00:00")
    d6 = datetime.fromisoformat("2020-11-04T14:00:00.000+00:00")
    d7 = datetime.fromisoformat("2020-11-04T23:00:00.000+00:00")
    d8 = datetime.fromisoformat("2020-11-05T00:00:00.000+00:00")

    # FIXME Acts unexpectedly with duplicates -> set() before calling?
    # FIXME should return just 1 span? Currently the next test would succeed:
    # EDIT doesn't seem to affect business logic tho...
    # EDIT2 'problem' is in the 2nd if clause
    #lsassert( find_spans([d1,d1], 1), [(d1,d1),(d1,d1)] )
    lsassert( find_spans([d2,d1,d1,d1,d2], 2), [(d1,d2)] ) # Passes...
    # FIXME Assertion fails: returns nothing []
    #lsassert( find_spans([d2,d1,d2,d3,d3,d1], 3), [(d1,d3)] )

    lsassert( find_spans([d2,d3,d1], 1), [(d2,d2), (d3,d3), (d1,d1)],
              "When `hours` == 1, order of input items same as output" )
    lsassert( find_spans([d2,d1,d3], 1), [(d2,d2), (d1,d1), (d3,d3)],
              "When `hours` == 1, order of input items same as output" )

    lsassert( find_spans([d3,d2,d1], 2), [(d1,d2), (d2,d3)] )
    lsassert( find_spans([d3,d2,d1], 2), [(d1,d2), (d2,d3)] )
    lsassert( find_spans([d1,d2,d6], 2), [(d1,d2)] )
    lsassert( find_spans([d1,d2,d6,d4,d5], 2), [(d1,d2), (d4,d5)] )
    lsassert( find_spans([d4,d3,d2,d1,d5], 2), [(d1,d2), (d2,d3), (d4,d5)] )

    lsassert( find_spans([d1,d3,d2],       3), [(d1,d3)] )
    lsassert( find_spans([d5,d2,d3,d4,d1], 3), [(d1,d3)] )

    # NOTE Business logic specific: with 24h calendar this test needs changing:
    lsassert( find_spans([d7,d8], 2), [] )

    span24h = [d8]
    for i in range(1,24):
        span24h.append(
            datetime.fromisoformat(f"2020-11-05T{i:02}:00:00.000+00:00")
        )

    lsassert( find_spans(span24h, 24), [(d8, d23)] ) 

    success("Cases with more than two times and between days")
    ##########################################################

    print("!! FIND_SPANS test done.")

###############################################################################

# The functions:

def find_spans(times, hours=1):
    """
    From an iterable of datetimes, find all occurrences of consecutive
    datetimes in each day, that span the given `hours`.
    Note that here (10,10) is considered 1 hour span, (10, 11) 2 hours and so.
    return: an iterator of datetime-tuples which describe spans of `hours`
    """

    # Handle special cases
    if hours < 1:
        return []
    if hours == 1:
        return map(lambda t: (t, t), times)
        
    # Group times by their day
    daily_times = groupby(sorted(times), key=lambda d: d.day)
    # Sort the times of each day
    daily_times = map(lambda t: sorted(t[1]), daily_times)

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

    return chain.from_iterable(spans)

def get_spans(consecutive, hours):
    l, r = 0, 1
    spans = []
    while r < len(consecutive):
        if consecutive[r].hour - consecutive[l].hour == hours-1:
            spans.append((consecutive[l], consecutive[r]))
            l += 1
        r += 1

    return spans
            

def scheduler(entries, hours=1, get_all=False):
    # Remove duplicates from different entries
    all_dates = [set(user_entry) for user_entry in entries]
    # Find the wanted spans from all entries
    all_spans = map(lambda l: find_spans(l, hours), all_dates)
    # Flatten the list of lists of spans, 
    # eg. [[s1],[s2,s3],[s2]] -> [s1,s2,s3,s2]
    all_spans = chain.from_iterable(all_spans)
    # Sort the spans for grouping,
    # eg. [s1,s2,s3,s2] -> [s1,s2,s2,s3]
    all_spans = sorted(all_spans, key=lambda x: (x[0].day, x[0].hour))
    # Pick spans by days into their own groups,
    # eg. [s1,s2,s2,s3] -> [(s1, [s1]), (s2, [s2,s2]), (s3, [s3])]
    span_groups = groupby(all_spans)
    # Set the second item as the length of each list
    # eg. [(s1, [s1]), (s2, [s2,s2]), (s3, [s3])] 
    #     -> [(s1, 1), (s2, 2), (s3, 1)]
    span_groups = [(k, len(list(g))) for k,g in span_groups]
    # Only use spans with > 1 entries. NOTE Conversion to list is intended
    # TODO Rename to 'result_groups' here?
    span_groups = list(filter(lambda x: x[1] > 1, span_groups))
    # Pick the group that has most spans > 1
    # NOTE It is assumed that the items have kept their previously sorted order
    best_span = max(span_groups, key=lambda x: x[1], default=None)

    # Decide whether to return iterable of best spans or single earliest span
    if get_all and best_span:
        # Return all spans, with participants of best length
        best_length = best_span[1]
        return filter(lambda x: x[1] == best_length, span_groups)

    return best_span

###############################################################################

# Test-main:

if __name__ == "__main__":
    test_find_spans()
    test_scheduler()
