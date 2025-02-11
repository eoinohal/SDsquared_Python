from dashboard import load_and_process_data

def print_data():
    text_file = "run_data/testrun1.txt"
    data = load_and_process_data(text_file)

    selected_keys = ["timeOfRun","forkCompression_regress", "forkRebound_regress", "shockCompression_regress", "shockRebound_regress"]

    if data:
        for key in selected_keys:
            print(f"{key}: {data[key]}")

print_data()