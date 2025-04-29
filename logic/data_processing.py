# data_processing.py
#

import os
from collections import OrderedDict
from bokeh.palettes import Category10, Category20
from accelerometer_data_processor import process_accelerometer_file
COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd","#8c564b", "#e377c2", "#7f7f7f", "#bcbd22", "#17becf"]


def load_and_process_data(file_path, bike_data):
    # Load and process accelerometer data from a file.
    data = process_accelerometer_file(file_path, bike_data)
    return data

def process_bike_data(file_path):
    #Process bike profile data into dict of key vals
    values = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                if key in ["rear_sus_min", "rear_sus_max", "front_sus_min", "front_sus_max"]:
                    values.append(int(value))
    return values


def displacement_values(data_dict, component):
    # Generates dict for displacement graph
    values = {
        "title": f"{component.capitalize()} Displacement Comparison",
        "timeOfRun": max(data["timeOfRun"] for data in data_dict.values()),
        "files": []
    }

    for i, (file_path, data) in enumerate(data_dict.items()):
        file_name = os.path.basename(file_path)
        prefix = component.lower()

        values["files"].append({
            "x_values": data["xValues"],
            "y_values": data[f"y{prefix.capitalize()}Values"],
            "name": f"{prefix}_{i + 1}: {file_name}",
            "peak_times": data[f"{prefix}PeakTimes"],
            "peaks": data[f"{prefix}Peaks"],
            "peaks_name": f"{prefix}_peaks_{i + 1}",
            "trough_times": data[f"{prefix}TroughTimes"],
            "troughs": data[f"{prefix}Troughs"],
            "troughs_name": f"{prefix}_troughs_{i + 1}",
            "color": COLORS[i % len(COLORS)]
        })

    return values


def regression_values(data_dict, component='fork', movement_type='compression'):
    # Generates dict for regression graph
    values = {
        "title": f"{component.capitalize()} {movement_type.capitalize()} Comparison",
        "files": []
    }

    for i, (file_path, data) in enumerate(data_dict.items()):
        file_name = os.path.basename(file_path)
        key_prefix = f"{component.lower()}{movement_type.capitalize()}"

        values["files"].append({
            "speed": data[f"{key_prefix}Speed"],
            "displacement": data[f"{key_prefix}Displacement"],
            "regress": data[f"{key_prefix}_regress"],
            "name": f"{component}_{i + 1}: {file_name}",
            "color": COLORS[i % len(COLORS)]
        })

    return values