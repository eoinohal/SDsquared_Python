# data_processing.py
# Formats and processes data from accelerometer_data_processor.py and data from files

from accelerometer_data_processor import process_accelerometer_file

def load_and_process_data(file_path, bike_data):
    # Load and process accelerometer data from a file
    data = process_accelerometer_file(file_path, bike_data)
    return data

def process_bike_data(file_path):
    values = []

    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(":")  # Split by ':'
            if len(parts) == 2:  # Ensure there are two parts (key and value)
                key, value = parts[0].strip(), parts[1].strip()
                if key in ["rear_sus_min", "rear_sus_max", "front_sus_min", "front_sus_max"]:
                    values.append(int(value))  # Convert to integer and store

    return values

# Used for compare

def fork_displacement_values(data1, data2, file1_name, file2_name):
    fork_values = {
        "title": f"Fork Displacement Plot: {file1_name} VS {file2_name}",
        "timeOfRun": max(data1["timeOfRun"], data2["timeOfRun"]),
        "x_val1": data1["xValues"],
        "y_val1": data1["yForkValues"],
        "name1": f"fork1: {file1_name}",
        "peak_times1": data1["forkPeakTimes"],
        "fork_peaks1": data1["forkPeaks"],
        "peaksName1": f"fork1 peaks: {file1_name}",
        "trough_times1": data1["forkTroughTimes"],
        "fork_troughs1": data1["forkTroughs"],
        "troughsName1": f"fork1 troughs: {file1_name}",
        "x_val2": data2["xValues"],
        "y_val2": data2["yForkValues"],
        "name2": f"fork2: {file2_name}",
        "peak_times2": data2["forkPeakTimes"],
        "fork_peaks2": data2["forkPeaks"],
        "peaksName2": f"fork2 peaks: {file2_name}",
        "trough_times2": data2["forkTroughTimes"],
        "fork_troughs2": data2["forkTroughs"],
        "troughsName2": f"fork2 troughs: {file2_name}",
    }
    return fork_values

def shock_displacement_values(data1, data2, file1_name, file2_name):
    shock_values = {
        "title": f"Shock Displacement Plot: {file1_name} VS {file2_name}",
        "timeOfRun": max(data1["timeOfRun"], data2["timeOfRun"]),
        "x_val1": data1["xValues"],
        "y_val1": data1["yShockValues"],
        "name1": f"shock1: {file1_name}",
        "peak_times1": data1["shockPeakTimes"],
        "fork_peaks1": data1["shockPeaks"],
        "peaksName1": f"shock1 peaks: {file1_name}",
        "trough_times1": data1["shockTroughTimes"],
        "fork_troughs1": data1["shockTroughs"],
        "troughsName1": f"shock1 troughs: {file1_name}",
        "x_val2": data2["xValues"],
        "y_val2": data2["yShockValues"],
        "name2": f"shock2: {file2_name}",
        "peak_times2": data2["shockPeakTimes"],
        "fork_peaks2": data2["shockPeaks"],
        "peaksName2": f"shock2 peaks: {file2_name}",
        "trough_times2": data2["shockTroughTimes"],
        "fork_troughs2": data2["shockTroughs"],
        "troughsName2": f"shock2 troughs: {file2_name}",
    }
    return shock_values

def fork_compression_values(data1, data2, file1_name, file2_name):
    fork_values = {
        "title": f"Fork Compression Scatter Plot: {file1_name} VS {file2_name}",
        "speed1": data1["forkCompressionSpeed"],
        "displacement1": data1["forkCompressionDisplacement"],
        "regress1": data1["forkCompression_regress"],
        "name1": "fork1: " + file1_name,
        "speed2": data2["forkCompressionSpeed"],
        "displacement2": data2["forkCompressionDisplacement"],
        "regress2": data2["forkCompression_regress"],
        "name2": "fork2: " + file2_name,
    }
    return fork_values

def fork_rebound_values(data1, data2, file1_name, file2_name):
    fork_values = {
        "title": f"Fork Rebound Scatter Plot: {file1_name} VS {file2_name}",
        "speed1": data1["forkReboundSpeed"],
        "displacement1": data1["forkReboundDisplacement"],
        "regress1": data1["forkRebound_regress"],
        "name1": "fork1: " + file1_name,
        "speed2": data2["forkReboundSpeed"],
        "displacement2": data2["forkReboundDisplacement"],
        "regress2": data2["forkRebound_regress"],
        "name2": "fork2: " + file2_name,
    }
    return fork_values

def shock_compression_values(data1, data2, file1_name, file2_name):
    shock_values = {
        "title": f"Shock Compression Scatter Plot: {file1_name} VS {file2_name}",
        "speed1": data1["shockCompressionSpeed"],
        "displacement1": data1["shockCompressionDisplacement"],
        "regress1": data1["shockCompression_regress"],
        "name1": "shock1: " + file1_name,
        "speed2": data2["shockCompressionSpeed"],
        "displacement2": data2["shockCompressionDisplacement"],
        "regress2": data2["shockCompression_regress"],
        "name2": "shock2: " + file2_name,
    }
    return shock_values

def shock_rebound_values(data1, data2, file1_name, file2_name):
    shock_values = {
        "title": f"Shock Rebound Scatter Plot: {file1_name} VS {file2_name}",
        "speed1": data1["shockReboundSpeed"],
        "displacement1": data1["shockReboundDisplacement"],
        "regress1": data1["shockRebound_regress"],
        "name1": "shock1: " + file1_name,
        "speed2": data2["shockReboundSpeed"],
        "displacement2": data2["shockReboundDisplacement"],
        "regress2": data2["shockRebound_regress"],
        "name2": "shock2: " + file2_name,
    }
    return shock_values

# Used for single run

def displacement_values(data1, data2, file_name):
    displacement_values = {
        "title": f"Percentage Displacement Plot: {file_name} ",
        "timeOfRun": max(data1["timeOfRun"], data2["timeOfRun"]),
        "x_val1": data1["xValues"],
        "y_val1": data1["yForkValues"],
        "name1": f"Front Fork: {file_name}",
        "peak_times1": data1["forkPeakTimes"],
        "fork_peaks1": data1["forkPeaks"],
        "peaksName1": f"Fork Peaks: {file_name}",
        "trough_times1": data1["forkTroughTimes"],
        "fork_troughs1": data1["forkTroughs"],
        "troughsName1": f"Fork Troughs: {file_name}",
        "x_val2": data2["xValues"],
        "y_val2": data2["yForkValues"],
        "name2": f"Front Fork: {file_name}",
        "peak_times2": data2["forkPeakTimes"],
        "fork_peaks2": data2["forkPeaks"],
        "peaksName2": f"Fork Peaks: {file_name}",
        "trough_times2": data2["forkTroughTimes"],
        "fork_troughs2": data2["forkTroughs"],
        "troughsName2": f"Fork Troughs: {file_name}",
    }
    return displacement_values

def compression_values(data, file_name):
    compression_values = {
        "title": f"Compression Scatter Plot: {file_name}",
        "speed1": data["forkCompressionSpeed"],
        "displacement1": data["forkCompressionDisplacement"],
        "regress1": data["forkCompression_regress"],
        "name1": "Fork Compression",
        "speed2": data["shockCompressionSpeed"],
        "displacement2": data["shockCompressionDisplacement"],
        "regress2": data["shockCompression_regress"],
        "name2": "Shock Compression",
    }
    return compression_values

def rebound_values(data, file_name):
    rebound_values = {
        "title": f"Rebound Scatter Plot: {file_name}",
        "speed1": data["forkReboundSpeed"],
        "displacement1": data["forkReboundDisplacement"],
        "regress1": data["forkRebound_regress"],
        "name1": "Fork Rebound",
        "speed2": data["shockReboundSpeed"],
        "displacement2": data["shockReboundDisplacement"],
        "regress2": data["shockRebound_regress"],
        "name2": "Shock Rebound",
    }
    return rebound_values