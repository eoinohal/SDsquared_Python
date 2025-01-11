from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import Range1d, Div
from bokeh.layouts import grid
from accelerometer_data_processor import process_accelerometer_file

# Load and process data
text_file = "TestRun1.TXT"
data = process_accelerometer_file(text_file)

# Extract variables
text_data = data["textData"]
time_of_run = data["timeOfRun"]
x_values = data["xValues"]
y_fork_values = data["yForkValues"]
y_shock_values = data["yShockValues"]
fork_peak_times = data["forkPeakTimes"]
fork_peaks = data["forkPeaks"]
fork_trough_times = data["forkTroughTimes"]
fork_troughs = data["forkTroughs"]
fork_compression_speed = data["forkCompressionSpeed"]
fork_compression_displacement = data["forkCompressionDisplacement"]
fork_compression_regress = data["forkCompression_regress"]
fork_rebound_speed = data["forkReboundSpeed"]
fork_rebound_displacement = data["forkReboundDisplacement"]
fork_rebound_regress = data["forkRebound_regress"]
shock_peak_times = data["shockPeakTimes"]
shock_peaks = data["shockPeaks"]
shock_trough_times = data["shockTroughTimes"]
shock_troughs = data["shockTroughs"]
shock_compression_speed = data["shockCompressionSpeed"]
shock_compression_displacement = data["shockCompressionDisplacement"]
shock_compression_regress = data["shockCompression_regress"]
shock_rebound_speed = data["shockReboundSpeed"]
shock_rebound_displacement = data["shockReboundDisplacement"]
shock_rebound_regress = data["shockRebound_regress"]

# Create displacement plot
displacement_graph = figure(
    title=f"Percentage Displacement Plot: {text_file}",
    sizing_mode="stretch_width",
    height=450,
    x_axis_label="Time (s)",
    y_axis_label="Percentage displacement (%)",
    tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
)
displacement_graph.x_range = Range1d(start=0, end=time_of_run, bounds=(0, time_of_run))
displacement_graph.y_range = Range1d(start=0, end=100, bounds=(0, 100))

# Plot fork data
displacement_graph.line(x_values, y_fork_values, legend_label="Front Fork", color="#00FFFF", line_width=0.5)
displacement_graph.scatter(fork_peak_times, fork_peaks, color="red", size=2, legend_label="Fork Peaks", marker="circle")
displacement_graph.scatter(fork_trough_times, fork_troughs, color="orange", size=2, legend_label="Fork Troughs", marker="circle")

# Plot shock data
displacement_graph.line(x_values, y_shock_values, legend_label="Rear Shock", color="#FF9500", line_width=0.5)
displacement_graph.scatter(shock_peak_times, shock_peaks, color="red", size=2, legend_label="Shock Peaks", marker="circle")
displacement_graph.scatter(shock_trough_times, shock_troughs, color="orange", size=2, legend_label="Shock Troughs", marker="circle")

# Create compression scatter plot
comp_graph = figure(
    title=f"Compression Scatter Plot: {text_file}",
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

# Create rebound scatter plot
reb_graph = figure(
    title=f"Rebound Scatter Plot: {text_file}",
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

# Create HTML stats div
print(text_data)
html_content = f"<pre><strong>{text_data}</strong></pre>"
stats_div = Div(text=html_content)

# Configure graphs
for graph in [displacement_graph, comp_graph, reb_graph]:
    graph.toolbar.logo = None
    graph.legend.click_policy = "hide"

# Create dashboard layout
dashboard_layout = grid(
    [[displacement_graph], [comp_graph, reb_graph], [stats_div]],
    sizing_mode="stretch_both"
)

# Set theme and display
curdoc().theme = "dark_minimal"
show(dashboard_layout)