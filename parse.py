from util import Plane, Passenger

def parse_file(file_path):
    f = open(file_path, "r")
    data = f.readlines()

    plane_data = data[:3]
    PlaneInfo = Plane(num_rows=int(data[0].split(" ")[1]), num_cols=int(data[1].split(" ")[1]), num_passengers=int(data[2].split(" ")[1]))

    data = data[3:]

    # Iterate over the passengers
    Passengers = [
        Passenger(
            row=int(data[i].split(" ")[1]),
            column=int(data[i+1].split(" ")[1]),
            settle_time=float(data[i+2].split(" ")[1]),
            move_times=tuple(float(time) for time in data[i+3].split(" ")[1:]),
        )
        for i in range(0, len(data), 4)
    ]

    f.close()

    return Passengers, PlaneInfo
