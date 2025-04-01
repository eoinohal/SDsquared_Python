# compare.py
# Compare fork and shock values from 2 runs in accelerometer reading graph and compression/rebound scatter plots
# WIP to make dynamic

from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import Range1d, Div, TextInput, FileInput, Dropdown, Paragraph, CheckboxGroup, ColumnDataSource
from bokeh.layouts import grid, row, column
from bokeh.palettes import Category10
from data_processing import load_and_process_data, process_bike_data, multi_displacement_values, multi_regression_values
import base64
import os
# Configuration
MAX_FILES = 10
COLORS = Category10[MAX_FILES]
DEFAULT_FILES = ["../data/run_data/testrun1.txt", "../data/run_data/testrun2.txt"]
DEFAULT_BIKE_FILE = "../data/bike_profiles/wills_megatower.txt"


def initialize_default_files():
    """Load default files if they exist"""
    global active_files
    for file_path in DEFAULT_FILES:
        if os.path.exists(file_path):
            active_files[file_path] = None


def load_bike_data():
    """Load and process bike profile data"""
    if os.path.exists(current_bike_file):
        return process_bike_data(current_bike_file)
    return None


def update_processed_data():
    """Ensure all active files have processed data"""
    bike_data = load_bike_data()
    if bike_data is None:
        print("Error: Could not load bike data")
        return False

    for file_path in list(active_files.keys()):
        if active_files[file_path] is None:
            processed_data = load_and_process_data(file_path, bike_data)
            if processed_data is not None:
                active_files[file_path] = processed_data
            else:
                print(f"Removing invalid file: {file_path}")
                del active_files[file_path]

    return len(active_files) >= 2


def create_displacement_plot(component='fork'):
    """Create displacement plot for fork or shock"""
    if not update_processed_data():
        return Div(text=f"<p style='color:red'>Error: Need at least 2 valid files to compare {component}</p>")

    values = multi_displacement_values(active_files, component=component)
    if not values:
        return Div(text=f"<p style='color:red'>Error generating {component} displacement data</p>")

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


def create_regression_plot(component='fork', movement_type='compression'):
    """Create regression plot for compression/rebound"""
    if not update_processed_data():
        return Div(
            text=f"<p style='color:red'>Error: Need at least 2 valid files to compare {component} {movement_type}</p>")

    values = multi_regression_values(active_files, component=component, movement_type=movement_type)
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


def update_dashboard():
    """Update all dashboard components"""
    curdoc().clear()

    if len(active_files) < 2:
        curdoc().add_root(Div(text="<h2 style='color:orange'>Please select at least 2 files to compare</h2>"))
        return

    # Create plots
    fork_displacement = create_displacement_plot(component='fork')
    fork_compression = create_regression_plot(component='fork', movement_type='compression')
    fork_rebound = create_regression_plot(component='fork', movement_type='rebound')

    shock_displacement = create_displacement_plot(component='shock')
    shock_compression = create_regression_plot(component='shock', movement_type='compression')
    shock_rebound = create_regression_plot(component='shock', movement_type='rebound')

    # Create dashboard layout
    dashboard = column(
        Div(text="<h1 style='text-align:center'>Suspension Performance Comparison</h1>"),
        Div(text="<h2 style='font-size:30px;color:white'>Fork Values</h2>"),
        Div(text="<h3 style='font-size:25px;color:white'>Displacement Plot</h3>"),
        fork_displacement,
        Div(text="<h3 style='font-size:25px;color:white'>Regression Lines</h3>"),
        Div(text="<h3 style='font-size:25px;color:white'>Regression Lines</h3>"),
        row(fork_compression, fork_rebound, sizing_mode='stretch_width'),
        Div(text="<h2 style='font-size:30px;color:white'>Shock Values</h2>"),
        Div(text="<h3 style='font-size:25px;color:white'>Displacement Plot</h3>"),
        shock_displacement,
        Div(text="<h3 style='font-size:25px;color:white'>Regression Lines</h3>"),
        row(shock_compression, shock_rebound, sizing_mode='stretch_width'),
        sizing_mode="stretch_both"
    )

    # Set theme and display
    curdoc().theme = "dark_minimal"
    curdoc().add_root(dashboard)


# Initialize
initialize_default_files()
update_dashboard()