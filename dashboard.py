from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import Range1d, Div, TextInput, FileInput, Dropdown, Paragraph, Button
from bokeh.layouts import grid, row, column
from accelerometer_data_processor import process_accelerometer_file
import base64
import os
import numpy as np

current_data_file = "run_data/testrun2.txt"
current_bike_file = "bike_profiles/wills_megatower.txt"


def load_and_process_data(file_path, bike_data):
    # Load and process accelerometer data from a file.
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

def create_displacement_plot(data, file_name, bike_file):
    # Create a displacement plot using the processed data.
    time_of_run = data["timeOfRun"]
    x_values = data["xValues"]
    y_fork_values = data["yForkValues"]
    y_shock_values = data["yShockValues"]
    fork_peak_times = data["forkPeakTimes"]
    fork_peaks = data["forkPeaks"]
    fork_trough_times = data["forkTroughTimes"]
    fork_troughs = data["forkTroughs"]
    shock_peak_times = data["shockPeakTimes"]
    shock_peaks = data["shockPeaks"]
    shock_trough_times = data["shockTroughTimes"]
    shock_troughs = data["shockTroughs"]

    displacement_graph = figure(
        title=f"Percentage Displacement Plot: {file_name}, {bike_file}",
        sizing_mode="stretch_width",
        height=450,
        x_axis_label="Time (s)",
        y_axis_label="Percentage displacement (%)",
        tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
    )
    displacement_graph.x_range = Range1d(start=0, end=time_of_run, bounds=(0, time_of_run))
    displacement_graph.y_range = Range1d(start=0, end=100, bounds=(0, 100))

    displacement_graph.line(x_values, y_fork_values, legend_label="Front Fork", color="#00FFFF", line_width=0.5)
    displacement_graph.scatter(fork_peak_times, fork_peaks, color="red", size=2, legend_label="Fork Peaks", marker="circle")
    displacement_graph.scatter(fork_trough_times, fork_troughs, color="orange", size=2, legend_label="Fork Troughs", marker="circle")

    displacement_graph.line(x_values, y_shock_values, legend_label="Rear Shock", color="#FF9500", line_width=0.5)
    displacement_graph.scatter(shock_peak_times, shock_peaks, color="red", size=2, legend_label="Shock Peaks", marker="circle")
    displacement_graph.scatter(shock_trough_times, shock_troughs, color="orange", size=2, legend_label="Shock Troughs", marker="circle")

    return displacement_graph

def create_compression_plot(data, file_name):
    # Create a compression scatter plot using the processed data.
    fork_compression_speed = data["forkCompressionSpeed"]
    fork_compression_displacement = data["forkCompressionDisplacement"]
    fork_compression_regress = data["forkCompression_regress"]
    shock_compression_speed = data["shockCompressionSpeed"]
    shock_compression_displacement = data["shockCompressionDisplacement"]
    shock_compression_regress = data["shockCompression_regress"]
    speedFR = sorted(fork_compression_speed)[int(len(fork_compression_speed)*0.9)]
    speedSR = sorted(shock_compression_speed)[int(len(shock_compression_speed)*0.9)]
    rangeSpeed = max(speedFR, speedSR)

    comp_graph = figure(
        title=f"Compression Scatter Plot: {file_name}",
        sizing_mode="stretch_width",
        height=450,
        x_axis_label="Speed of displacement (%/s)",
        y_axis_label="Absolute change in displacement (%)",
        tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
    )

    comp_graph.x_range = Range1d(start=0, end=rangeSpeed * 1.1)
    comp_graph.y_range = Range1d(start=0, end=max(max(fork_compression_displacement), max(shock_compression_displacement)) * 1.1)

    comp_graph.scatter(fork_compression_speed, fork_compression_displacement, color="blue", size=4, legend_label="Fork Compression", marker="circle")
    comp_graph.line(x=fork_compression_regress, y=fork_compression_displacement, color="#00FFFF", legend_label="Fork Regression", line_width=2)

    comp_graph.scatter(shock_compression_speed, shock_compression_displacement, color="orange", size=4, legend_label="Shock Compression", marker="circle")
    comp_graph.line(x=shock_compression_regress, y=shock_compression_displacement, color="red", legend_label="Shock Regression", line_width=2)

    mean_x = [(min(fork_compression_regress)+min(shock_compression_regress))/2,(max(fork_compression_regress)+max(shock_compression_regress))/2]
    mean_y = [(min(fork_compression_displacement)+min(shock_compression_displacement))/2,(max(fork_compression_displacement)+max(shock_compression_displacement))/2]

    comp_graph.line(x=mean_x, y=mean_y, color="white", legend_label="Mean Compression Regression", line_width=2)

    return comp_graph

def create_rebound_plot(data, file_name):
    # Create a rebound scatter plot using the processed data.
    fork_rebound_speed = data["forkReboundSpeed"]
    fork_rebound_displacement = data["forkReboundDisplacement"]
    fork_rebound_regress = data["forkRebound_regress"]
    shock_rebound_speed = data["shockReboundSpeed"]
    shock_rebound_displacement = data["shockReboundDisplacement"]
    shock_rebound_regress = data["shockRebound_regress"]
    speedFR = sorted(fork_rebound_speed)[int(len(fork_rebound_speed)*0.9)]
    speedSR = sorted(shock_rebound_speed)[int(len(shock_rebound_speed)*0.9)]
    rangeSpeed = max(speedFR, speedSR)


    reb_graph = figure(
        title=f"Rebound Scatter Plot: {file_name}",
        sizing_mode="stretch_width",
        height=450,
        x_axis_label="Speed of displacement (%/s)",
        y_axis_label="Absolute change in displacement (%)",
        tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
    )
    reb_graph.x_range = Range1d(start=0, end=rangeSpeed * 1.1)
    reb_graph.y_range = Range1d(start=0, end=max(max(fork_rebound_displacement), max(shock_rebound_displacement)) * 1.1)

    reb_graph.scatter(fork_rebound_speed, fork_rebound_displacement, color="blue", size=4, legend_label="Fork Rebound", marker="circle")
    reb_graph.line(x=fork_rebound_regress, y=fork_rebound_displacement, color="#00FFFF", legend_label="Fork Regression", line_width=2)

    reb_graph.scatter(shock_rebound_speed, shock_rebound_displacement, color="orange", size=4, legend_label="Shock Rebound", marker="circle")
    reb_graph.line(x=shock_rebound_regress, y=shock_rebound_displacement, color="red", legend_label="Shock Regression", line_width=2)

    mean_x = [(min(fork_rebound_regress)+min(shock_rebound_regress))/2,(max(fork_rebound_regress)+max(shock_rebound_regress))/2]
    mean_y = [(min(fork_rebound_displacement)+min(shock_rebound_displacement))/2,(max(fork_rebound_displacement)+max(shock_rebound_displacement))/2]

    reb_graph.line(x=mean_x, y=mean_y, color="white", legend_label="Mean Rebound Regression", line_width=2)

    return reb_graph

def create_stats_div(data):
    # Create a Div element to display statistics.
    text_data = data["textData"]
    html_content = f"<pre><strong>{text_data}</strong></pre>"
    stats_div = Div(text=html_content)
    return stats_div

def main(run_data_file, bike_file):
    global current_data_file
    current_data_file = run_data_file
    curdoc().clear()
    top_select_layout = row(file_select_text,file_input, file_dropdown, bike_select_text, bike_dropdown)
    # Load and process data
    bike_data = process_bike_data(bike_file)
    data = load_and_process_data(run_data_file, bike_data)

    if data is not None:
        # Create plots
        displacement_graph = create_displacement_plot(data, run_data_file, bike_file)
        comp_graph = create_compression_plot(data, run_data_file)
        reb_graph = create_rebound_plot(data, run_data_file)

        # Create stats div
        stats_div = create_stats_div(data)

        # Configure graphs
        for graph in [displacement_graph, comp_graph, reb_graph]:
            graph.toolbar.logo = None
            graph.legend.click_policy = "hide"

        # Create dashboard layout
        dashboard_layout = grid(
            [[displacement_graph], [comp_graph, reb_graph], [stats_div]],
            sizing_mode="stretch_both"
        )


        layout = column(top_select_layout, dashboard_layout, sizing_mode="stretch_both")
    else:

        layout = column(top_select_layout, sizing_mode="stretch_both")


    # Set theme and display
    curdoc().theme = "dark_minimal"
    curdoc().clear()
    curdoc().add_root(layout)


run_folder_path = "run_data"
if os.path.exists(run_folder_path):  # Check if folder exists
    run_txt_files = [(file, file) for file in os.listdir(run_folder_path) if file.lower().endswith(".txt")]
else:
    run_txt_files = []

file_dropdown = Dropdown(label="Select a file", menu=run_txt_files)

bike_folder_path = "bike_profiles"
if os.path.exists(bike_folder_path):  # Check if folder exists
    bike_txt_files = [(file, file) for file in os.listdir(bike_folder_path) if file.lower().endswith(".txt")]
else:
    bike_txt_files = []

bike_dropdown = Dropdown(label="Select a file", menu=bike_txt_files)


def file_selected(event):
    main(run_folder_path+"/"+event.item, current_bike_file)

def bike_selected(event):
    main(current_data_file, bike_folder_path+"/"+event.item)

def on_suspension_change(attr, old, new):
    main(current_data_file)

def upload_callback(attr, old, new):
    global current_data_file

    # Decode the uploaded file content
    decoded = base64.b64decode(new)
    file_content = decoded.decode("utf-8")

    # Save the file temporarily
    temp_file_path = "run_data/uploaded_file.txt"
    with open(temp_file_path, "w", newline="") as f:
        f.write(file_content)

    # Update the current file and refresh the dashboard
    current_data_file = temp_file_path
    main(current_data_file, current_bike_file)


file_input = FileInput(accept=".txt")
file_input.on_change("value", upload_callback)

file_dropdown.on_event("menu_item_click", file_selected)
file_select_text = Paragraph(text="Select file here: ")

bike_dropdown.on_event("menu_item_click", bike_selected)
bike_select_text = Paragraph(text="Select bike here: ")

main(current_data_file, current_bike_file)