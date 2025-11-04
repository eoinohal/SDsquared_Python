from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, DataTable, TableColumn, Range1d, Div, HTMLTemplateFormatter
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
import statistics

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
            run_comments = []  # To store comments for visible runs

            run_items = list(json_config.get("runs", {}).items())

            for json_index, (run_file, props) in enumerate(run_items):
                if props.get("visible"):
                    normalized_path = os.path.normpath(run_file).replace("\\", "/")
                    full_path = os.path.join(run_path_prefix, normalized_path)
                    visible_runs.append((json_index, full_path, props))  # Now includes props

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

            for json_index, run_path, props in visible_runs:
                data = load_and_process_data(run_path, bike_data)
                if data:
                    # Collect comments if enabled
                    if props.get("comments", True):
                        comment = data['comment']
                        if comment:
                            run_name = os.path.basename(run_path)
                            run_comments.append(f"<b>{run_name}:</b> {comment}")

                    data['path'] = run_path
                    data['color'] = self.run_colors[run_path]
                    processed_data[run_path] = data

            if not processed_data:
                self.doc.add_root(Div(text="<p style='color:red'>No valid data could be processed</p>"))
                return

            # Create comments section if there are any comments
            comments_section = None
            if run_comments:
                comments_html = "<h2 style='color:white; margin-bottom:10px;'>Comments:</h2>"
                comments_html += "<div style='color:white; font-size:15px; line-height:1.6; margin-bottom:20px; border-radius:5px;'>"
                comments_html += "<br>".join(run_comments)
                comments_html += "</div>"
                comments_section = Div(text=comments_html)

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

            # Create the main layout
            layout_components = []

            # Add the plots
            layout_components.extend([fork_plots, shock_plots])

            # Add comments section first if it exists
            if comments_section:
                layout_components.append(comments_section)

            # Add stats table
            layout_components.append(self.create_stats_table(processed_data))

            layout = column(
                *layout_components,
                sizing_mode="stretch_width"
            )

            self.doc.clear()
            self.doc.add_root(layout)

        except Exception as e:
            error_msg = f"Error updating visualization: {str(e)}"
            self.doc.add_root(Div(text=f"<p style='color:red'>{error_msg}</p>"))

    def create_stats_table(self, processed_data):
        """Create a table showing key statistics for each run with color coding"""
        if not processed_data:
            return Div(text="<p style='color:orange'>No data available for stats table</p>")

        # Prepare the data structure
        table_data = {
            'run_name': [],
            # Fork metrics
            'fork_compression': [], 'fork_compression_color': [],
            'fork_compression_speed': [], 'fork_compression_speed_color': [],
            'fork_rebound': [], 'fork_rebound_color': [],
            'fork_rebound_speed': [], 'fork_rebound_speed_color': [],
            'max_fork_disp': [], 'max_fork_disp_color': [],
            # Shock metrics
            'shock_compression': [], 'shock_compression_color': [],
            'shock_compression_speed': [], 'shock_compression_speed_color': [],
            'shock_rebound': [], 'shock_rebound_color': [],
            'shock_rebound_speed': [], 'shock_rebound_speed_color': [],
            'max_shock_disp': [], 'max_shock_disp_color': [],
            # Time
            'time_of_run': [], 'time_of_run_color': [],
        }

        # Lists to store numeric values for mean calculation
        numeric_data = {
            # Fork metrics
            'fork_compression': [],
            'fork_compression_speed': [],
            'fork_rebound': [],
            'fork_rebound_speed': [],
            'max_fork_disp': [],
            # Shock metrics
            'shock_compression': [],
            'shock_compression_speed': [],
            'shock_rebound': [],
            'shock_rebound_speed': [],
            'max_shock_disp': [],
            # Time
            'time_of_run': [],
        }

        def value_to_color(val, avg, scale=0.3):  # scale controls sensitivity (0.3 = 30% change)
            """Map value to RGB color: red (low), white (mean), green (high) using percentage change"""
            if val is None:
                return "#ffffff"  # white for invalid values

            # Calculate percentage change from mean
            if avg != 0:
                pct_change = (val - avg) / avg
            else:
                pct_change = 0

            # Normalize to [-scale, scale] range
            norm_pct = max(-1, min(1, pct_change / scale))

            # Convert to [0, 1] range
            norm = (norm_pct + 1) / 2

            r = int(255 * (1 - norm))
            g = int(255 * norm)
            b = int(50 * (1 - abs(norm - 0.5)))  # Very small blue component

            return f"rgb({r},{g},{b})"

        # First pass: collect all numeric values
        for run_path, data in processed_data.items():
            # Fork metrics
            if data.get('forkCompression_regress'):
                numeric_data['fork_compression'].append(statistics.median(data['forkCompression_regress']))
                numeric_data['fork_compression_speed'].append(statistics.median(data['forkCompressionSpeed']))

            if data.get('forkRebound_regress'):
                numeric_data['fork_rebound'].append(statistics.median(data['forkRebound_regress']))
                numeric_data['fork_rebound_speed'].append(statistics.median(data['forkReboundSpeed']))

            # Shock metrics
            if data.get('shockCompression_regress'):
                numeric_data['shock_compression'].append(statistics.median(data['shockCompression_regress']))
                numeric_data['shock_compression_speed'].append(statistics.median(data['shockCompressionSpeed']))

            if data.get('shockRebound_regress'):
                numeric_data['shock_rebound'].append(statistics.median(data['shockRebound_regress']))
                numeric_data['shock_rebound_speed'].append(statistics.median(data['shockReboundSpeed']))

            # Time and max values
            numeric_data['time_of_run'].append(data['timeOfRun'])
            numeric_data['max_fork_disp'].append(max(data['yForkValues']) if data.get('yForkValues') else 0)
            numeric_data['max_shock_disp'].append(max(data['yShockValues']) if data.get('yShockValues') else 0)

        # Calculate means for each metric
        stats = {}
        for key, values in numeric_data.items():
            stats[key] = {
                'mean': sum(values) / len(values) if values else 0
            }

        # Second pass: populate table data with color coding
        for run_path, data in processed_data.items():
            run_name = os.path.basename(run_path)
            table_data['run_name'].append(run_name)

            # Helper function to process each metric
            def process_metric(metric, value, default="N/A"):
                if value is not None and value != "N/A":
                    color = value_to_color(value, stats[metric]['mean'])
                    table_data[metric].append(f"{value:.2f}" if metric != 'time_of_run' else f"{value:.1f}s")
                    table_data[f"{metric}_color"].append(color)
                else:
                    table_data[metric].append(default)
                    table_data[f"{metric}_color"].append("#ffffff")

            # Process fork metrics
            process_metric('fork_compression',
                           data['forkCompression_regress'][0] if data.get('forkCompression_regress') else None)
            process_metric('fork_compression_speed',
                           data['forkCompressionSpeed'][0] if data.get('forkCompressionSpeed') else None)
            process_metric('fork_rebound', data['forkRebound_regress'][0] if data.get('forkRebound_regress') else None)
            process_metric('fork_rebound_speed', data['forkReboundSpeed'][0] if data.get('forkReboundSpeed') else None)
            max_fork = max(data['yForkValues']) if data.get('yForkValues') else 0
            process_metric('max_fork_disp', max_fork)

            # Process shock metrics
            process_metric('shock_compression',
                           data['shockCompression_regress'][0] if data.get('shockCompression_regress') else None)
            process_metric('shock_compression_speed',
                           data['shockCompressionSpeed'][0] if data.get('shockCompressionSpeed') else None)
            process_metric('shock_rebound',
                           data['shockRebound_regress'][0] if data.get('shockRebound_regress') else None)
            process_metric('shock_rebound_speed',
                           data['shockReboundSpeed'][0] if data.get('shockReboundSpeed') else None)
            max_shock = max(data['yShockValues']) if data.get('yShockValues') else 0
            process_metric('max_shock_disp', max_shock)

            # Process time
            process_metric('time_of_run', data['timeOfRun'])

        # Create DataTable columns with color formatters
        columns = [
            TableColumn(field="run_name", title="Run Name"),
        ]

        # Add fork metrics columns
        fork_columns = [
            ('fork_compression', 'Fork Compression'),
            ('fork_compression_speed', 'Fork Comp Speed'),
            ('fork_rebound', 'Fork Rebound'),
            ('fork_rebound_speed', 'Fork Reb Speed'),
            ('max_fork_disp', 'Max Fork Disp')
        ]

        # Add shock metrics columns
        shock_columns = [
            ('shock_compression', 'Shock Compression'),
            ('shock_compression_speed', 'Shock Comp Speed'),
            ('shock_rebound', 'Shock Rebound'),
            ('shock_rebound_speed', 'Shock Reb Speed'),
            ('max_shock_disp', 'Max Shock Disp')
        ]

        # Time column
        time_column = [('time_of_run', 'Duration')]

        # Combine all columns in desired order
        all_columns = fork_columns + shock_columns + time_column

        for metric, title in all_columns:
            columns.append(TableColumn(
                field=metric,
                title=title,
                formatter=HTMLTemplateFormatter(
                    template='<div style="background-color: <%= ' + f'{metric}_color' + ' %>;' +
                             'padding: 4px; margin: -4px; display: block;">' +
                             '<%= value %></div>'
                )
            ))

        # Custom CSS for the table
        table_style = """
        .slick-header-column {
            color: white !important;
            background-color: #333 !important;
            font-size:15px;
        }
        .slick-cell {
            color: black !important;
            font-size:12px;
            padding: 0 !important;
        }
        .slick-cell div {
            width: 100%;
            height: 100%;
        }
        .slick-row.last-row {
            background-color: #e6e6e6 !important;
            font-weight: bold;
        }
        """

        # Create the table
        source = ColumnDataSource(table_data)
        table = DataTable(
            source=source,
            columns=columns,
            sizing_mode='stretch_width',
            autosize_mode='force_fit',
            css_classes=["custom-table"]
        )

        # Add the CSS style
        table.stylesheets.append(table_style)

        stats_div = Div(text="<h2 style='color:white; margin-bottom:10px;'>Run Statistics</h2>")
        return column(stats_div, table, sizing_mode='stretch_width')


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
                plot.x_range = Range1d(start=0, end=sorted(all_speeds)[int(len(all_speeds) * 0.9)] * 1.75)
                plot.y_range = Range1d(start=0, end=sorted(all_disps)[int(len(all_disps) * 0.9)] * 1.75)

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