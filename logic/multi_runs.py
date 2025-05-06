from bokeh.io import curdoc
from bokeh.plotting import figure
from bokeh.models import Range1d, Div
from bokeh.layouts import row, column
from data_processing import load_and_process_data, process_bike_data, displacement_values, regression_values
import json
from tornado import web, gen

# JSON in format from frontend
# Once linked JSON variable will be reading from frontend
testJSON = """
{
  "runs": {
    "test1/testrun1.txt": {
      "visible": true,
      "comments": false
    },
    "test1/testrun2.txt": {
      "visible": true,
      "comments": false
    },
    "test2/01.03.25 test day.md": {
      "visible": false,
      "comments": false
    },
    "test2/RUN5.TXT": {
      "visible": false,
      "comments": false
    },
    "test2/RUN6.TXT": {
      "visible": false,
      "comments": false
    },
    "test2/RUN7.TXT": {
      "visible": false,
      "comments": false
    },
    "test2/RUN8.TXT": {
      "visible": false,
      "comments": false
    },
    "test2/RUN9.TXT": {
      "visible": false,
      "comments": false
    },
    "RUN1.TXT": {
      "visible": false,
      "comments": false
    },
    "RUN2.TXT": {
      "visible": false,
      "comments": false
    },
    "RUN3.TXT": {
      "visible": false,
      "comments": false
    },
    "RUN4.TXT": {
      "visible": false,
      "comments": false
    },
    "uploaded_file.txt": {
      "visible": false,
      "comments": false
    },
    "uploaded_file1.txt": {
      "visible": false,
      "comments": false
    }
  },
  "riderFile": "full_range_values.txt"
}
"""

test_json1_data = json.loads(testJSON)

# Run and rider paths
run_path_prefix = "../data/run_data/"
rider_path_prefix = "../data/bike_profiles/"


def create_displacement_plot(data, component='fork'):
    # Create displacement plot for fork and shock

    # Generate list of dictionaries of key values for plot
    values = displacement_values(data, component=component)
    if not values or not values.get("files"):
        return Div(
            text=f"<p style='color:orange'>No data to display for {component} displacement. Check run visibility and data processing.</p>")

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

    # Ensure there's data before trying to find max displacement
    if values["files"] and any(file_data["y_values"] for file_data in values["files"]):
        max_displacement = max(
            max(file_data["y_values"]) if file_data["y_values"] else 0 for file_data in values["files"])
        plot.y_range = Range1d(start=0, end=max_displacement * 1.1 if max_displacement > 0 else 100,
                               bounds=(0, max_displacement * 1.1 if max_displacement > 0 else 100))
    else:
        plot.y_range = Range1d(start=0, end=100, bounds=(0, 100))  # Default if no y_values

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

        # Peaks
        if file_data["peak_times"] and file_data["peaks"]:
            plot.scatter(
                file_data["peak_times"],
                file_data["peaks"],
                color=file_data["color"],
                size=4,
                legend_label=file_data["peaks_name"],
                marker="circle"
            )

        # Troughs
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
    if not values or not values.get("files"):
        return Div(
            text=f"<p style='color:orange'>No data for {component} {movement_type}. Check run visibility and data processing.</p>")

    plot = figure(
        title=values["title"],
        sizing_mode="stretch_width",
        height=450,
        x_axis_label="Speed of displacement (%/s)",
        y_axis_label="Absolute change in displacement (%)",
        tools="pan,reset,wheel_zoom,xwheel_zoom,fullscreen,examine,crosshair",
    )

    all_speeds = [speed for file_data in values["files"] for speed in file_data["speed"]]
    all_displacements = [disp for file_data in values["files"] for disp in file_data["displacement"]]

    if all_speeds and all_displacements:
        valid_speeds = [s for s in all_speeds if isinstance(s, (int, float))]
        valid_displacements = [d for d in all_displacements if isinstance(d, (int, float))]

        if valid_speeds and valid_displacements:
            speed_r_index = int(len(valid_speeds) * 0.9)
            if speed_r_index < len(valid_speeds):
                speed_r = sorted(valid_speeds)[speed_r_index]
                plot.x_range = Range1d(start=0, end=speed_r * 1.1 if speed_r > 0 else 10)
            else:
                plot.x_range = Range1d(start=0, end=max(valid_speeds) * 1.1 if valid_speeds else 10)

            plot.y_range = Range1d(start=0, end=max(valid_displacements) * 1.1 if valid_displacements else 10)
        else:
            plot.x_range = Range1d(start=0, end=10)
            plot.y_range = Range1d(start=0, end=10)
    else:
        plot.x_range = Range1d(start=0, end=10)
        plot.y_range = Range1d(start=0, end=10)

    # Plot each file's data
    for file_data in values["files"]:
        if file_data["speed"] and file_data["displacement"]:  # Ensure there's data to plot
            plot.scatter(
                file_data["speed"],
                file_data["displacement"],
                color=file_data["color"],
                size=4,
                legend_label=file_data["name"],
                marker="circle"
            )

            if file_data["regress"] and file_data["displacement"]:  # Check displacement again for regression line
                plot.line(
                    x=file_data["regress"],
                    y=file_data["displacement"],  # Make sure displacement matches length of regress
                    color=file_data["color"],
                    legend_label=f"{file_data['name']} Regression",
                    line_width=2
                )

    plot.toolbar.logo = None
    plot.legend.click_policy = "hide"
    return plot


def main(run_files, bike_file):
    curdoc().clear()
    curdoc().theme = "dark_minimal"

    nullFile = False
    processing_error_file = None
    bike_data = process_bike_data(bike_file)

    data = {}
    if not run_files:
        print("No runs configured to be visible.")
    else:
        for run_file_path in run_files:
            processed_data = load_and_process_data(run_file_path, bike_data)
            if processed_data is None:
                print(f"Error processing file: {run_file_path}")
                nullFile = True
                processing_error_file = run_file_path
                break
            data[run_file_path] = processed_data

    if nullFile:
        error_text = f"<p style='color:red; font-size:18px;'>Error processing data file: {processing_error_file}. Please check the file or configuration.</p>"
        content_area = Div(text=error_text)
    elif not data:
        message_text = "<p style='color:orange; font-size:18px;'>No data to display. This could be due to no runs being marked as 'visible' in the current configuration, or all visible runs had issues.</p>"
        content_area = Div(text=message_text)
    else:
        fork_displacement = create_displacement_plot(data, component='fork')
        fork_compression = create_regression_plot(data, component='fork', movement_type='compression')
        fork_rebound = create_regression_plot(data, component='fork', movement_type='rebound')

        shock_displacement = create_displacement_plot(data, component='shock')
        shock_compression = create_regression_plot(data, component='shock', movement_type='compression')
        shock_rebound = create_regression_plot(data, component='shock', movement_type='rebound')

        content_area = column(
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
            sizing_mode="stretch_width"  # Changed from stretch_both for the content column
        )

    final_layout = column(content_area, sizing_mode="stretch_width")
    curdoc().add_root(final_layout)


def setup_and_render(json_config_data):
    # Parses the JSON, determines visible runs and bike file
    visible_runs_list = []
    for run_filename, run_properties in json_config_data.get("runs", {}).items():
        if run_properties.get("visible") is True:
            visible_runs_list.append(run_path_prefix + run_filename)

    bike_file_name = str(json_config_data["riderFile"])
    current_bike_file_path = rider_path_prefix + bike_file_name

    main(visible_runs_list, current_bike_file_path)


# Using to try sync with the frontend * I need to fix this to make it work
class UpdateSelectedFilesHandler(web.RequestHandler):
    def set_default_headers(self):
        # Enable CORS
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "Content-Type")
        self.set_header("Access-Control-Allow-Methods", "POST, OPTIONS")
        self.set_header("Content-Type", "application/json")

    def options(self):
        # Handle preflight requests (CORS)
        self.set_status(204)  # No content
        self.finish()

    @gen.coroutine
    def post(self):
        try:
            json_data = json.loads(self.request.body)
            print(f"Received data: {json.dumps(json_data, indent=2)}")
            doc = curdoc()
            doc.add_next_tick_callback(lambda: setup_and_render(json_data))

            self.write(json.dumps({"status": "success", "message": "Visualization updated"}))
        except Exception as e:
            print(f"Error processing update request: {str(e)}")
            self.set_status(500)
            self.write(json.dumps({"status": "error", "message": str(e)}))


def add_handlers(doc):
    if hasattr(doc, 'session_context') and doc.session_context:
        try:
            from bokeh.server.contexts import BokehServerContext
            if isinstance(doc.session_context.server_context, BokehServerContext):
                app = doc.session_context.server_context.tornado_app
                if app:
                    app.add_handlers(
                        r".*",
                        [
                            (r"/multi_runs/update-selected-files", UpdateSelectedFilesHandler),
                        ]
                    )
                    print("Handlers added successfully")
                else:
                    print("No Tornado application available")
            else:
                print("Not running in BokehServerContext")
        except Exception as e:
            print(f"Failed to add handlers: {str(e)}")
    else:
        print("No session context available")


def on_server_loaded(server_context):
    """Function that runs when the server is loaded."""
    app = server_context.tornado_app
    app.add_handlers(
        r".*",
        [
            (r"/multi_runs/update-selected-files", UpdateSelectedFilesHandler),
        ]
    )
    print("Handlers added via on_server_loaded")


def on_document_loaded(event):
    """Function that runs when a document is loaded."""
    doc = event.document
    print("Document loaded")


setup_and_render(test_json1_data)