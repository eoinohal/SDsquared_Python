# compare.py
# Compare fork and shock values from 2 runs in accelerometer reading graph and compression/rebound scatter plots

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import Range1d, Div, TextInput, FileInput, Dropdown, Paragraph
from bokeh.layouts import grid, row, column
from accelerometer_data_processor import process_accelerometer_file
import base64
import os

# Default files
current_file1 = "run_data/testrun1.txt"
current_file2 = "run_data/testrun2.txt"

# Load and process data
def load_and_process_data(file_path, shock_length, fork_length):
    # Load and process accelerometer data from a file
    data = process_accelerometer_file(file_path, shock_length, fork_length)
    return data

# Displacement plot - Uses accelerometer readings to make displacement graph
def decomposed_displacement_plot(vals):
    # Plot 2 accelerometer recordings on a graph
    displacement_graph = figure(
        title=vals["title"],
        sizing_mode="stretch_width",
        height=450,
        x_axis_label="Time (s)",
        y_axis_label="Percentage displacement (%)",
        tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
    )

    displacement_graph.x_range = Range1d(start=0, end=vals["timeOfRun"], bounds=(0, vals["timeOfRun"]))
    displacement_graph.y_range = Range1d(start=0, end=100, bounds=(0, 100))

    displacement_graph.line(vals["x_val1"], vals["y_val1"], legend_label=vals["name1"], color="#00FFFF", line_width=0.5)
    displacement_graph.scatter(vals["peak_times1"], vals["fork_peaks1"], color="red", size=2, legend_label=vals["peaksName1"], marker="circle")
    displacement_graph.scatter(vals["trough_times1"], vals["fork_troughs1"], color="orange", size=2, legend_label=vals["troughsName1"], marker="circle")

    displacement_graph.line(vals["x_val2"], vals["y_val2"], legend_label=vals["name2"], color="#FF0000", line_width=0.5)
    displacement_graph.scatter(vals["peak_times2"], vals["fork_peaks2"], color="red", size=2, legend_label=vals["peaksName2"], marker="circle")
    displacement_graph.scatter(vals["trough_times2"], vals["fork_troughs2"], color="orange", size=2, legend_label=vals["troughsName2"], marker="circle")

    return displacement_graph

# Fork displacement values
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

# Shock displacement values
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

# Regression plot - Uses values to make scatter plot with regression lines
def decomposed_regression_plot(vals):
    # Scatter plot of compression/rebound values with regression lines
    graph = figure(
        title=vals["title"],
        sizing_mode="stretch_width",
        height=450,
        x_axis_label="Speed of displacement (%/s)",
        y_axis_label="Absolute change in displacement (%)",
        tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
    )

    speed1 = vals["speed1"]; speedR1 = sorted(speed1)[int(len(speed1)*0.9)]
    displacement1 = vals["displacement1"]
    regress1 = vals["regress1"]
    speed2 = vals["speed2"]; speedR2 = sorted(speed2)[int(len(speed2)*0.9)]
    displacement2 = vals["displacement2"]
    regress2 = vals["regress2"]

    graph.x_range = Range1d(start=0, end=max(speedR1, speedR2) * 1.1)
    graph.y_range = Range1d(start=0, end=max(max(displacement1), max(displacement2)) * 1.1)

    graph.scatter(speed1, displacement1, color="blue", size=4, legend_label=vals["name1"], marker="circle")
    graph.line(x=regress1, y=displacement1, color="#00FFFF", legend_label=f"{vals['name1']} Regression", line_width=2)

    graph.scatter(speed2, displacement2, color="orange", size=4, legend_label=vals["name2"], marker="circle")
    graph.line(x=regress2, y=displacement2, color="red", legend_label=f"{vals['name2']} Regression", line_width=2)

    mean_x = [(min(regress1) + min(regress2)) / 2, (max(regress1) + max(regress2)) / 2]
    mean_y = [(min(displacement1) + min(displacement2)) / 2, (max(displacement1) + max(displacement2)) / 2]

    graph.line(x=mean_x, y=mean_y, color="white", legend_label="Mean Compression Regression", line_width=2)

    return graph

# Fork compression values
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

# Fork rebound values
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

# Shock compression values
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

# Shock rebound values
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


# Main function
def main(text_file1, text_file2):
    global current_file1, current_file2
    current_file1 = text_file1
    current_file2 = text_file2
    curdoc().clear()

    # Load and process data for both files
    data1 = load_and_process_data(text_file1, shock_length_select.value, fork_length_select.value)
    data2 = load_and_process_data(text_file2, shock_length_select.value, fork_length_select.value)

    if data1 is not None and data2 is not None:
        # Create fork plots
        fork_displacement_graph = decomposed_displacement_plot(fork_displacement_values(data1, data2, text_file1, text_file2))
        fork_comp_graph = decomposed_regression_plot(fork_compression_values(data1, data2, text_file1, text_file2))
        fork_reb_graph = decomposed_regression_plot(fork_rebound_values(data1, data2, text_file1, text_file2))

        # Create shock plots
        shock_displacement_graph = decomposed_displacement_plot(shock_displacement_values(data1, data2, text_file1, text_file2))
        shock_comp_graph = decomposed_regression_plot(shock_compression_values(data1, data2, text_file1, text_file2))
        shock_reb_graph = decomposed_regression_plot(shock_rebound_values(data1, data2, text_file1, text_file2))

        # Configure graphs
        for graph in [fork_displacement_graph, fork_comp_graph, fork_reb_graph, shock_displacement_graph,
                      shock_comp_graph, shock_reb_graph]:
            graph.toolbar.logo = None
            graph.legend.click_policy = "hide"

        # Create headers and subheadings
        head = Div(text="<h1 style='font-size:40px;'>Comparison of Accelerometer Data</h1>")
        fork_subheading = Div(text="<h2 style='font-size:30px;'>Fork Values</h2>")
        shock_subheading = Div(text="<h2 style='font-size:30px;'>Shock Values</h2>")
        displacement_subsubheading1 = Div(text="<h3 style='font-size:25px;'>Displacement Plot</h3>")
        regression_subsubheading1 = Div(text="<h3 style='font-size:25px;'>Regression Lines</h3>")
        displacement_subsubheading2 = Div(text="<h3 style='font-size:25px;'>Displacement Plot</h3>")
        regression_subsubheading2 = Div(text="<h3 style='font-size:25px;'>Regression Lines</h3>")

        # Create dashboard layout
        dashboard_layout = column(
            head,
            top_select_layout,
            fork_subheading,
            displacement_subsubheading1,
            fork_displacement_graph,
            regression_subsubheading1,
            row(fork_comp_graph, fork_reb_graph, sizing_mode='stretch_width'),
            shock_subheading,
            displacement_subsubheading2,
            shock_displacement_graph,
            regression_subsubheading2,
            row(shock_comp_graph, shock_reb_graph, sizing_mode='stretch_width'),
            sizing_mode="stretch_both"
        )

        layout = column(dashboard_layout, sizing_mode="stretch_both")
    else:
        layout = column(top_select_layout, sizing_mode="stretch_both")

    # Set theme and display
    curdoc().theme = "dark_minimal"
    curdoc().clear()
    curdoc().add_root(layout)

# File selection dropdowns
folder_path = "run_data"
if os.path.exists(folder_path):  # Check if folder exists
    txt_files = [(file, file) for file in os.listdir(folder_path) if file.lower().endswith(".txt")]
else:
    txt_files = []

dropdown1 = Dropdown(label="Select file 1", menu=txt_files)
dropdown2 = Dropdown(label="Select file 2", menu=txt_files)

def file1_selected(event):
    global current_file1
    current_file1 = folder_path + "/" + event.item
    main(current_file1, current_file2)

def file2_selected(event):
    global current_file2
    current_file2 = folder_path + "/" + event.item
    main(current_file1, current_file2)

dropdown1.on_event("menu_item_click", file1_selected)
dropdown2.on_event("menu_item_click", file2_selected)

# File upload callbacks
def upload_callback1(attr, old, new):
    global current_file1
    decoded = base64.b64decode(new)
    file_content = decoded.decode("utf-8")
    temp_file_path = "run_data/uploaded_file1.txt"
    with open(temp_file_path, "w", newline="") as f:
        f.write(file_content)
    current_file1 = temp_file_path
    main(current_file1, current_file2)

def upload_callback2(attr, old, new):
    global current_file2
    decoded = base64.b64decode(new)
    file_content = decoded.decode("utf-8")
    temp_file_path = "run_data/uploaded_file2.txt"
    with open(temp_file_path, "w", newline="") as f:
        f.write(file_content)
    current_file2 = temp_file_path
    main(current_file1, current_file2)

file_input1 = FileInput(accept=".txt")
file_input1.on_change("value", upload_callback1)

file_input2 = FileInput(accept=".txt")
file_input2.on_change("value", upload_callback2)

# Text inputs for shock and fork length
shock_length_select_text = Paragraph(text="Select shock length: ")
fork_length_select_text = Paragraph(text="Select fork length: ")
shock_length_select = TextInput(value="160")
fork_length_select = TextInput(value="160")

def on_suspension_change(attr, old, new):
    main(current_file1, current_file2)

shock_length_select.on_change("value", on_suspension_change)
fork_length_select.on_change("value", on_suspension_change)

# Layout
file1_select_text = Paragraph(text="Select file 1 here: ")
file2_select_text = Paragraph(text="Select file 2 here: ")

top_select_layout = row(file1_select_text, file_input1, dropdown1, file2_select_text, file_input2, dropdown2, shock_length_select_text, shock_length_select, fork_length_select_text, fork_length_select)

# Initialize the dashboard
main(current_file1, current_file2)