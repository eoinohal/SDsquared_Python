from bokeh.plotting import figure
from bokeh.models import Range1d, Div
from bokeh.layouts import row, column
from bokeh.palettes import Category20
from data_processing import load_and_process_data, process_bike_data, displacement_values, regression_values
import json
import os
from tornado import web
from bokeh.server.server import Server
from bokeh.application import Application
from bokeh.application.handlers import FunctionHandler
from functools import partial

# Path configuration
run_path_prefix = os.path.normpath("../data/run_data/")
rider_path_prefix = os.path.normpath("../data/bike_profiles/")

# Graph colour palette
COLOR_PALETTE = Category20[20]

# Visualization class - handles plot updates
class VisualizationUpdater:
    def __init__(self):
        self.doc = None
        self.run_colors = {}

    # Initialize Bokeh document
    def initialize_document(self, doc):
        self.doc = doc
        doc.title = "SD² Suspension Analysis"
        doc.theme = "dark_minimal"
        doc.add_root(Div(text="<p style='font-size:16px'>Select runs in the frontend to visualize data</p>"))

    # Update plots based on frontend input
    def safe_update(self, json_config):
        if not self.doc:
            return

        try:
            visible_runs = []
            new_run_colors = {}

            run_items = list(json_config.get("runs", {}).items())

            for json_index, (run_file, props) in enumerate(run_items):
                if props.get("visible"):
                    normalized_path = os.path.normpath(run_file).replace("\\", "/")
                    full_path = os.path.join(run_path_prefix, normalized_path)
                    visible_runs.append((json_index, full_path))

                    color = COLOR_PALETTE[json_index % len(COLOR_PALETTE)]
                    new_run_colors[full_path] = color

            self.run_colors = new_run_colors

            if not visible_runs:
                self.doc.add_root(Div(text="<p style='color:orange'>No runs selected for display</p>"))
                return

            rider_file = os.path.normpath(json_config["riderFile"]).replace("\\", "/")
            bike_file = os.path.join(rider_path_prefix, rider_file)
            bike_data = process_bike_data(bike_file)
            processed_data = {}

            for json_index, run_path in visible_runs:
                data = load_and_process_data(run_path, bike_data)
                if data:
                    data['path'] = run_path
                    data['color'] = self.run_colors[run_path]
                    processed_data[run_path] = data

            if not processed_data:
                self.doc.add_root(Div(text="<p style='color:red'>No valid data could be processed</p>"))
                return

            fork_plots = column(
                Div(text="<h2 style='color:white'>Fork Analysis</h2>"),
                self.create_displacement_plot(processed_data, 'fork'),
                row(
                    self.create_regression_plot(processed_data, 'fork', 'compression'),
                    self.create_regression_plot(processed_data, 'fork', 'rebound'),
                    sizing_mode="stretch_width"
                ),
                sizing_mode="stretch_width"
            )

            shock_plots = column(
                Div(text="<h2 style='color:white'>Shock Analysis</h2>"),
                self.create_displacement_plot(processed_data, 'shock'),
                row(
                    self.create_regression_plot(processed_data, 'shock', 'compression'),
                    self.create_regression_plot(processed_data, 'shock', 'rebound'),
                    sizing_mode="stretch_width"
                ),
                sizing_mode="stretch_width"
            )

            layout = column(
                fork_plots,
                shock_plots,
                sizing_mode="stretch_width"
            )

            self.doc.clear()
            self.doc.add_root(layout)

        except Exception as e:
            error_msg = f"Error updating visualization: {str(e)}"
            self.doc.add_root(Div(text=f"<p style='color:red'>{error_msg}</p>"))

    def create_displacement_plot(self, data, component='fork'):
        """Create displacement plot for specified component"""
        values = displacement_values(data, component=component)
        if not values or not values.get("files"):
            return Div(text=f"<p style='color:orange'>No {component} displacement data available</p>")

        plot = figure(
            title=values["title"],
            sizing_mode="stretch_width",
            height=450,
            x_axis_label="Time (s)",
            y_axis_label="Displacement (%)",
            tools="pan,reset,wheel_zoom,box_zoom,save"
        )

        # Set axis ranges
        plot.x_range = Range1d(start=0, end=values["timeOfRun"])
        if values["files"]:
            max_disp = max(max(f["y_values"]) for f in values["files"] if f["y_values"])
            plot.y_range = Range1d(start=0, end=max(max_disp * 1.1, 10))

        # Plot data
        for file_data in values["files"]:
            run_color = file_data["color"]

            # Main displacement line
            plot.line(
                file_data["x_values"],
                file_data["y_values"],
                legend_label=file_data["name"],
                color=run_color,
                line_width=1
            )

            # Peaks
            if file_data["peak_times"]:
                plot.scatter(
                    file_data["peak_times"],
                    file_data["peaks"],
                    color=run_color,
                    legend_label=f"{file_data['name']} Peaks",
                    size=4,
                    marker="circle"
                )

            # Troughs
            if file_data["trough_times"]:
                plot.scatter(
                    file_data["trough_times"],
                    file_data["troughs"],
                    color=run_color,
                    legend_label=f"{file_data['name']} Troughs",
                    size=4,
                    marker="inverted_triangle"
                )

        plot.legend.click_policy = "hide"
        plot.toolbar.logo = None
        return plot

    def create_regression_plot(self, data, component='fork', movement_type='compression'):
        """Create regression plot for specified component and movement type"""
        values = regression_values(data, component=component, movement_type=movement_type)
        if not values or not values.get("files"):
            return Div(text=f"<p style='color:orange'>No {component} {movement_type} data available</p>")

        plot = figure(
            title=values["title"],
            sizing_mode="stretch_width",
            height=450,
            x_axis_label="Speed (%/s)",
            y_axis_label="Displacement Change (%)",
            tools="pan,reset,wheel_zoom,box_zoom,save"
        )

        # Set dynamic axis ranges
        if values["files"]:
            all_speeds = [s for f in values["files"] for s in f["speed"] if f["speed"]]
            all_disps = [d for f in values["files"] for d in f["displacement"] if f["displacement"]]

            if all_speeds and all_disps:
                plot.x_range = Range1d(start=0, end=max(all_speeds) * 1.1)
                plot.y_range = Range1d(start=0, end=max(all_disps) * 1.1)

        # Plot data
        for file_data in values["files"]:
            run_color = file_data["color"]

            if file_data["speed"] and file_data["displacement"]:
                # Data points
                plot.scatter(
                    file_data["speed"],
                    file_data["displacement"],
                    color=run_color,
                    legend_label=file_data["name"],
                    size=4
                )

                # Regression line
                if file_data.get("regress") and len(file_data["regress"]) == len(file_data["displacement"]):
                    plot.line(
                        file_data["regress"],
                        file_data["displacement"],
                        color=run_color,
                        legend_label=f"{file_data['name']} Regression",
                        line_width=2
                    )

        plot.legend.click_policy = "hide"
        plot.toolbar.logo = None
        return plot


# Create the visualization updater
updater = VisualizationUpdater()


class UpdateHandler(web.RequestHandler):
    """Handles POST requests from the frontend"""

    def set_default_headers(self):
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Content-Type", "application/json")

    def post(self):
        try:
            # Parse incoming JSON
            data = json.loads(self.request.body)

            if updater.doc:
                updater.doc.add_next_tick_callback(partial(updater.safe_update, data))
                self.write({"status": "success", "message": "Update scheduled"})
            else:
                self.set_status(500)
                self.write({"status": "error", "message": "Bokeh document not ready"})

        except json.JSONDecodeError:
            self.set_status(400)
            self.write({"status": "error", "message": "Invalid JSON received"})
        except Exception as e:
            self.set_status(500)
            self.write({"status": "error", "message": str(e)})


app = Application(FunctionHandler(updater.initialize_document))

server = Server(
    {'/multi_runs': app},
    extra_patterns=[(r'/multi_runs/update-selected-files', UpdateHandler)],
    allow_websocket_origin=["*"],
    port=5006,
    num_procs=1
)

if __name__ == "__main__":
    server.start()
    server.io_loop.start()