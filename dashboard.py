from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import Range1d, Div, TextInput, Button
from bokeh.layouts import grid, row, column
from accelerometer_data_processor import process_accelerometer_file

def load_and_process_data(file_path):
    # Load and process accelerometer data from a file.
    data = process_accelerometer_file(file_path)
    return data

def create_displacement_plot(data, file_name):
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
        title=f"Percentage Displacement Plot: {file_name}",
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

    comp_graph = figure(
        title=f"Compression Scatter Plot: {file_name}",
        sizing_mode="stretch_width",
        height=450,
        x_axis_label="Speed of displacement (%/s)",
        y_axis_label="Absolute change in displacement (%)",
        tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
    )
    comp_graph.x_range = Range1d(start=0, end=max(max(fork_compression_speed), max(shock_compression_speed)) * 1.1)
    comp_graph.y_range = Range1d(start=0, end=max(max(fork_compression_displacement), max(shock_compression_displacement)) * 1.1)

    comp_graph.scatter(fork_compression_speed, fork_compression_displacement, color="blue", size=4, legend_label="Fork Compression", marker="circle")
    comp_graph.line(x=fork_compression_regress, y=fork_compression_displacement, color="#00FFFF", legend_label="Fork Regression", line_width=2)

    comp_graph.scatter(shock_compression_speed, shock_compression_displacement, color="orange", size=4, legend_label="Shock Compression", marker="circle")
    comp_graph.line(x=shock_compression_regress, y=shock_compression_displacement, color="red", legend_label="Shock Regression", line_width=2)

    return comp_graph

def create_rebound_plot(data, file_name):
    # Create a rebound scatter plot using the processed data.
    fork_rebound_speed = data["forkReboundSpeed"]
    fork_rebound_displacement = data["forkReboundDisplacement"]
    fork_rebound_regress = data["forkRebound_regress"]
    shock_rebound_speed = data["shockReboundSpeed"]
    shock_rebound_displacement = data["shockReboundDisplacement"]
    shock_rebound_regress = data["shockRebound_regress"]

    reb_graph = figure(
        title=f"Rebound Scatter Plot: {file_name}",
        sizing_mode="stretch_width",
        height=450,
        x_axis_label="Speed of displacement (%/s)",
        y_axis_label="Absolute change in displacement (%)",
        tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
    )
    reb_graph.x_range = Range1d(start=0, end=max(max(fork_rebound_speed), max(shock_rebound_speed)) * 1.1)
    reb_graph.y_range = Range1d(start=0, end=max(max(fork_rebound_displacement), max(shock_rebound_displacement)) * 1.1)

    reb_graph.scatter(fork_rebound_speed, fork_rebound_displacement, color="blue", size=4, legend_label="Fork Rebound", marker="circle")
    reb_graph.line(x=fork_rebound_regress, y=fork_rebound_displacement, color="#00FFFF", legend_label="Fork Regression", line_width=2)

    reb_graph.scatter(shock_rebound_speed, shock_rebound_displacement, color="orange", size=4, legend_label="Shock Rebound", marker="circle")
    reb_graph.line(x=shock_rebound_regress, y=shock_rebound_displacement, color="red", legend_label="Shock Regression", line_width=2)

    return reb_graph

def create_stats_div(data):
    # Create a Div element to display statistics.
    text_data = data["textData"]
    html_content = f"<pre><strong>{text_data}</strong></pre>"
    stats_div = Div(text=html_content)
    return stats_div

def main(text_file):
    curdoc().clear()
    file_select_layout = row(text_input, submit_button)

    # Load and process data
    data = load_and_process_data(text_file)

    if data is not None:
        # Create plots
        displacement_graph = create_displacement_plot(data, text_file)
        comp_graph = create_compression_plot(data, text_file)
        reb_graph = create_rebound_plot(data, text_file)

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


        layout = column(file_select_layout, dashboard_layout, sizing_mode="stretch_both")
    else:
        layout = column(file_select_layout, sizing_mode="stretch_both")


    # Set theme and display
    curdoc().theme = "dark_minimal"
    curdoc().add_root(layout)

def submit_button_click():
    main(text_input.value)

text_input = TextInput(title="Enter File name: ", placeholder="TestRun1.TXT")
submit_button = Button(label="Load File", button_type="success")
submit_button.on_click(submit_button_click)


main("TestRun2.TXT")