# plot_functions.py
# Functions used for displacement-time plot and speed-displacement scatter plot using bokeh

from bokeh.plotting import figure
from bokeh.models import Range1d

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