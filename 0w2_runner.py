from dashboard import load_and_process_data, process_bike_data


def print_data():
    text_file = "data/run_data/testrun1.txt"
    bike_file = "data/bike_profiles/full_range_values.txt"
    bike_data = process_bike_data(bike_file)
    data = load_and_process_data(text_file, bike_data)
    print(data["textData"])
print_data()