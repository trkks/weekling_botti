from datetime import datetime
from itertools import (chain, groupby)

def test_scheduler(scheduler):
    # A shared printing pattern for test-passing
    success = lambda s: print(f"Testing '{s}' - PASSED")


    ### START OF TESTS ###

    # Base cases
    assert scheduler([]) == None, \
           "No entries didn't return `None`"

    assert scheduler([[]]) == None, \
           "Empty entry didn't return `None`"

    d1 = datetime.fromisoformat("2020-11-04T10:00:00.000+00:00")
    d2 = datetime.fromisoformat("2020-11-04T09:00:00.000+00:00")
    d3 = datetime.fromisoformat("2020-11-03T09:00:00.000+00:00")

    assert scheduler([[d1]]) == None, \
           "The only date was not returned"

    assert scheduler([[d1,d1]]) == None, \
           "The duplicate date was not returned"

    result = scheduler([[d1],[d1],[]])
    assert result == (d1, 2), \
           f"The best possible date was not returned: {result}"

    assert scheduler([[d1],[d1],[d1]]) == (d1, 3), \
           "The only date between lists was not returned"

    assert scheduler([[d2,d1], [d1]]) == (d1, 2), \
           "The shared date between lists was not returned"

    assert scheduler([[d1],[d2],[d3]]) == None, \
           "Different dates in every list did not return `None`"

    assert scheduler([ [d1,d1,d1], [], [] ]) == None, \
           "Amount of entries is not equivalent to amount of 'shared' date"


    success("Base cases")
    #####################

    # Time-specific cases
    d4 = datetime.fromisoformat("2020-11-03T12:00:00.000+00:00")

    assert scheduler([[d1,d2], [d3,d1,d2], [d2,d1,d4]]) == (d2, 3), \
           "The earliest shared date was not returned"

    success("Time-specific cases")
    ##############################

    print("All tests done.")


def my_scheduler(entries):
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
    test_scheduler(my_scheduler)
