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

    assert scheduler([[d1]]) == d1, \
           "The only date was not returned"

    assert scheduler([[d1,d1]]) == d1, \
           "The duplicate date was not returned"

    # TODO What is our business logic here?
    assert scheduler([[d1],[d1],[]]) == None, \
           "An empty list was not included"

    assert scheduler([[d1],[d1],[d1]]) == d1, \
           "The only date between lists was not returned"

    assert scheduler([[d2,d1], [d1]]) == d1, \
           "The shared date between lists was not returned"

    assert scheduler([[d1],[d2],[d3]]) == None, \
           "Different dates in every list did not return `None`"

    # TODO
    """
    - jos tietokannassa times == [ [d1,d1,d1], [], [] ]
      niin tällähetkellä d1 tulkitaan kaikille vastanneille sopivaksi ajaksi
    """


    success("Base cases")
    #####################

    # Time-specific cases
    d4 = datetime.fromisoformat("2020-11-03T12:00:00.000+00:00")

    # TODO What is our business logic here?
    assert scheduler([[d1,d2], [d3,d1,d2], [d2,d1,d4]]) == d2, \
           "The earliest shared date was not returned"

    success("Time-specific cases")
    ##############################

    print("All tests done.")


def my_scheduler(entries):
    # Number of people who inputted their times
    entry_count = len(entries)
    # Flatten the list of lists of dates, 
    # eg. [[d1],[d2,d3],[d2]] -> [d1,d2,d3,d2]
    all_dates = chain.from_iterable(entries)
    # Sort the dates for grouping,
    # eg. [d1,d2,d3,d2] -> [d1,d2,d2,d3]
    all_dates = sorted(all_dates)
    # Pick same dates into their own groups,
    # eg. [d1,d2,d2,d3] -> [(d1, [d1]), (d2, [d2,d2]), (d3, [d3])]
    date_groups = groupby(all_dates)
    # Pick the groups that have entry_count worth of dates
    # TODO Should duplicate dates in entries be checked, 
    #      eg. person1_entry == [d1,d1] -> Error?
    # TODO
    counts = []
    def check_count(x):
        count = len(list(x[1]))
        counts.append(count)
        if count >= entry_count or count > 1:
            return x[0] 
        return None
    # TODO
    shared_dates = map(check_count, date_groups)
    # Remove `None`s
    shared_dates = list(filter(bool, shared_dates))
    # Select the first date TODO specify first in *list* or in *time*?
    return (shared_dates[0] \
           if len(shared_dates) > 0 \
           else None


if __name__ == "__main__":  
    test_scheduler(my_scheduler)
