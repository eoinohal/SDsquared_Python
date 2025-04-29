from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import Range1d, Div
from bokeh.layouts import row, column
from data_processing import load_and_process_data, process_bike_data, displacement_values, regression_values
import sys

if len(sys.argv) > 1 and not sys.argv[1].startswith('--'):
    file_names = sys.argv[1].split(',')
    file_names = [f"../data/run_data/{name}" for name in file_names]
else:
    run1 = "../data/run_data/RUN1.txt"
    run2 = "../data/run_data/RUN2.txt"
    run3 = "../data/run_data/RUN3.txt"
    run4 = "../data/run_data/RUN4.txt"
    file_names = [run1, run2, run3, run4]

current_bike_file = "../data/bike_profiles/wills_megatower.txt"


def create_displacement_plot(data, component='fork'):
    # Create displacement plot for fork and shock

    # Generate list of dictionaries of key values for plot
    values = displacement_values(data, component=component)

    plot = figure(
        title=values["title"],
        sizing_mode="stretch_width",
        height=450,
        x_axis_label="Time (s)",
        y_axis_label="Percentage displacement (%)",
        tools="pan,reset,wheel_zoom,xwheel_zoom,fullscreen,examine,crosshair",
    )

    # Set ranges
    plot.x_range = Range1d(start=0, end=values["timeOfRun"], bounds=(0, values["timeOfRun"]))
    max_displacement = max(max(file_data["y_values"]) for file_data in values["files"])
    plot.y_range = Range1d(start=0, end=max_displacement * 1.1, bounds=(0, max_displacement * 1.1))

    # Plot each file's data
    for file_data in values["files"]:
        # Main displacement line
        plot.line(
            file_data["x_values"],
            file_data["y_values"],
            legend_label=file_data["name"],
            color=file_data["color"],
            line_width=0.5
        )

        # Peaks and troughs
        if file_data["peak_times"] and file_data["peaks"]:
            plot.scatter(
                file_data["peak_times"],
                file_data["peaks"],
                color=file_data["color"],
                size=4,
                legend_label=file_data["peaks_name"],
                marker="circle"
            )

        if file_data["trough_times"] and file_data["troughs"]:
            plot.scatter(
                file_data["trough_times"],
                file_data["troughs"],
                color=file_data["color"],
                size=4,
                legend_label=file_data["troughs_name"],
                marker="inverted_triangle"
            )

    plot.toolbar.logo = None
    plot.legend.click_policy = "hide"
    return plot


def create_regression_plot(data, component='fork', movement_type='compression'):
    # Create regression plot for compression and rebound

    values = regression_values(data, component=component, movement_type=movement_type)
    if not values:
        return Div(text=f"<p style='color:red'>Error generating {component} {movement_type} data</p>")

    plot = figure(
        title=values["title"],
        sizing_mode="stretch_width",
        height=450,
        x_axis_label="Speed of displacement (%/s)",
        y_axis_label="Absolute change in displacement (%)",
        tools="pan,reset,wheel_zoom,xwheel_zoom,fullscreen,examine,crosshair",
    )

    # Calculate axis ranges
    all_speeds = [speed for file_data in values["files"] for speed in file_data["speed"]]
    all_displacements = [disp for file_data in values["files"] for disp in file_data["displacement"]]

    if all_speeds and all_displacements:
        speed_r = sorted(all_speeds)[int(len(all_speeds) * 0.9)]
        plot.x_range = Range1d(start=0, end=speed_r * 1.1)
        plot.y_range = Range1d(start=0, end=max(all_displacements) * 1.1)

    # Plot each file's data
    for file_data in values["files"]:
        plot.scatter(
            file_data["speed"],
            file_data["displacement"],
            color=file_data["color"],
            size=4,
            legend_label=file_data["name"],
            marker="circle"
        )

        if file_data["regress"]:
            plot.line(
                x=file_data["regress"],
                y=file_data["displacement"],
                color=file_data["color"],
                legend_label=f"{file_data['name']} Regression",
                line_width=2
            )

    plot.toolbar.logo = None
    plot.legend.click_policy = "hide"
    return plot


def main(run_files, bike_file):
    curdoc().clear()
    nullFile = False
    bike_data = process_bike_data(bike_file)

    # Load and process data for all the files
    data = {}
    for run in run_files:
        processed_data = load_and_process_data(run, bike_data)
        if processed_data is None:
            nullFile = True
            break
        data[run] = processed_data

    if not nullFile:
        # Create plots
        fork_displacement = create_displacement_plot(data, component='fork')
        fork_compression = create_regression_plot(data, component='fork', movement_type='compression')
        fork_rebound = create_regression_plot(data, component='fork', movement_type='rebound')

        shock_displacement = create_displacement_plot(data, component='shock')
        shock_compression = create_regression_plot(data, component='shock', movement_type='compression')
        shock_rebound = create_regression_plot(data, component='shock', movement_type='rebound')

        # Configure graphs
        for graph in [fork_displacement, fork_compression, fork_rebound,
                     shock_displacement, shock_compression, shock_rebound]:
            if graph is not None:  # Handle case where plot creation failed
                graph.toolbar.logo = None
                graph.legend.click_policy = "hide"

        # Create dashboard layout
        dashboard_layout = column(
            Div(text="<h2 style='font-size:30px;color:white'>Fork Values</h2>"),
            Div(text="<h3 style='font-size:25px;color:white'>Displacement Plot</h3>"),
            fork_displacement,
            Div(text="<h3 style='font-size:25px;color:white'>Regression Lines</h3>"),
            row(fork_compression, fork_rebound, sizing_mode='stretch_width'),
            Div(text="<h2 style='font-size:30px;color:white'>Shock Values</h2>"),
            Div(text="<h3 style='font-size:25px;color:white'>Displacement Plot</h3>"),
            shock_displacement,
            Div(text="<h3 style='font-size:25px;color:white'>Regression Lines</h3>"),
            row(shock_compression, shock_rebound, sizing_mode='stretch_width'),
            sizing_mode="stretch_both"
        )

        layout = column(dashboard_layout, sizing_mode="stretch_both")

        # Set theme and display
        curdoc().theme = "dark_minimal"
        curdoc().clear()
        curdoc().add_root(layout)
    else:
        curdoc().add_root(Div(text="<p style='color:red'>Error processing data files</p>"))


main(file_names, current_bike_file)