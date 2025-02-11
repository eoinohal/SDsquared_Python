from dashboard import load_and_process_data


def print_data():
    text_file = "run_data/testrun1.txt"
    data = load_and_process_data(text_file)
    print(data["textData"])
print_data()