# data_processing.py
# To dynamically handle 2-10 file comparisons
# WIP

import os
from collections import OrderedDict
from bokeh.palettes import Category10, Category20

from accelerometer_data_processor import process_accelerometer_file

MAX_FILES = 10
COLORS = Category10[10] if MAX_FILES <= 10 else Category20[20]


def load_and_process_data(file_path, bike_data):
    """Load and process accelerometer data from a file"""
    try:
        data = process_accelerometer_file(file_path, bike_data)
        return data
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return None


def process_bike_data(file_path):
    """Process bike profile data"""
    values = []
    with open(file_path, 'r') as file:
        for line in file:
            parts = line.strip().split(":")
            if len(parts) == 2:
                key, value = parts[0].strip(), parts[1].strip()
                if key in ["rear_sus_min", "rear_sus_max", "front_sus_min", "front_sus_max"]:
                    values.append(int(value))
    return values


def validate_data_files(all_data):
    """Ensure all files have required suspension data"""
    valid_data = OrderedDict()
    required_keys = [
        'xValues', 'yForkValues', 'yShockValues',
        'forkPeaks', 'forkTroughs', 'shockPeaks', 'shockTroughs'
    ]

    for file_path, data in all_data.items():
        if data is None:
            continue
        if all(key in data for key in required_keys):
            valid_data[file_path] = data
        else:
            print(f"Warning: {file_path} missing required data keys")

    return valid_data


def multi_displacement_values(all_data, component='fork'):
    """
    Generate displacement values for N files
    component: 'fork' or 'shock'
    """
    valid_data = validate_data_files(all_data)
    if not valid_data:
        return None

    values = {
        "title": f"{component.capitalize()} Displacement Comparison",
        "timeOfRun": max(data["timeOfRun"] for data in valid_data.values()),
        "files": []
    }

    for i, (file_path, data) in enumerate(valid_data.items()):
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


def multi_regression_values(all_data, component='fork', movement_type='compression'):
    """
    Generate regression values for N files
    component: 'fork' or 'shock'
    movement_type: 'compression' or 'rebound'
    """
    valid_data = validate_data_files(all_data)
    if not valid_data:
        return None

    values = {
        "title": f"{component.capitalize()} {movement_type.capitalize()} Comparison",
        "files": []
    }

    for i, (file_path, data) in enumerate(valid_data.items()):
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


def calculate_comparison_stats(all_data):
    """Generate aggregate statistics for all files"""
    stats = {
        'fork': {
            'avg_compression': [],
            'avg_rebound': [],
            'max_displacement': []
        },
        'shock': {
            'avg_compression': [],
            'avg_rebound': [],
            'max_displacement': []
        }
    }

    for data in all_data.values():
        if data is None:
            continue

        # Fork stats
        if data.get('forkCompressionDisplacement'):
            stats['fork']['avg_compression'].append(
                sum(data['forkCompressionDisplacement']) / len(data['forkCompressionDisplacement'])
            )
        if data.get('forkReboundDisplacement'):
            stats['fork']['avg_rebound'].append(
                sum(data['forkReboundDisplacement']) / len(data['forkReboundDisplacement'])
            )
        if data.get('yForkValues'):
            stats['fork']['max_displacement'].append(max(data['yForkValues']))

        # Shock stats
        if data.get('shockCompressionDisplacement'):
            stats['shock']['avg_compression'].append(
                sum(data['shockCompressionDisplacement']) / len(data['shockCompressionDisplacement'])
            )
        if data.get('shockReboundDisplacement'):
            stats['shock']['avg_rebound'].append(
                sum(data['shockReboundDisplacement']) / len(data['shockReboundDisplacement'])
            )
        if data.get('yShockValues'):
            stats['shock']['max_displacement'].append(max(data['yShockValues']))

    return stats


# Backward compatibility functions
def fork_displacement_values(data1, data2, file1_name, file2_name):
    return multi_displacement_values({
        file1_name: data1,
        file2_name: data2
    }, component='fork')


def shock_displacement_values(data1, data2, file1_name, file2_name):
    return multi_displacement_values({
        file1_name: data1,
        file2_name: data2
    }, component='shock')


def fork_compression_values(data1, data2, file1_name, file2_name):
    return multi_regression_values({
        file1_name: data1,
        file2_name: data2
    }, component='fork', movement_type='compression')


def fork_rebound_values(data1, data2, file1_name, file2_name):
    return multi_regression_values({
        file1_name: data1,
        file2_name: data2
    }, component='fork', movement_type='rebound')


def shock_compression_values(data1, data2, file1_name, file2_name):
    return multi_regression_values({
        file1_name: data1,
        file2_name: data2
    }, component='shock', movement_type='compression')


def shock_rebound_values(data1, data2, file1_name, file2_name):
    return multi_regression_values({
        file1_name: data1,
        file2_name: data2
    }, component='shock', movement_type='rebound')


# Single run functions remain unchanged
def displacement_values(data1, data2, file_name):
    """Single run displacement values (unchanged)"""
    return {
        "title": f"Percentage Displacement Plot: {file_name}",
    }


def compression_values(data, file_name):
    """Single run compression values (unchanged)"""
    return {
        "title": f"Compression Scatter Plot: {file_name}",
    }


def rebound_values(data, file_name):
    """Single run rebound values (unchanged)"""
    return {
        "title": f"Rebound Scatter Plot: {file_name}",
    }