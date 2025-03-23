from collections import namedtuple

Passenger = namedtuple("Passenger", ["row", "column", "settle_time", "move_times"])
Plane = namedtuple("Plane", ["num_rows", "num_cols", "num_passengers"])
