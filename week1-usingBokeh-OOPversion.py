from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import Range1d

class DataFile:
    def __init__(self, filepath, x_factor=0.01, y_columns=(0, 1)):
        self.filepath = filepath
        self.x_factor = x_factor
        self.y_columns = y_columns
        self.x_values = []
        self.y_values = [[] for _ in y_columns]
        self._load_data()

    def _load_data(self):
        with open(self.filepath, "r") as file:
            file.readline()  # Skip header lines
            file.readline()
            for i in range(5000):
                self.x_values.append(i * self.x_factor)
                data = file.readline().split(",")
                for j, col in enumerate(self.y_columns):
                    self.y_values[j].append(float(data[col]))
                    

class Line:
    def __init__(self, x_values, y_values, label, color, line_width=0.5):
        self.x_values = x_values
        self.y_values = y_values
        self.label = label
        self.color = color
        self.line_width = line_width


class Graph:
    def __init__(self, title, x_label, y_label, width=450, height=450, theme="dark_minimal"):
        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.width = width
        self.height = height
        self.theme = theme
        self.lines = []
        
        curdoc().theme = self.theme
        self.figure = figure(
            title=self.title,
            sizing_mode="stretch_width",
            height=self.height,
            x_range=(0, 10),
            y_range=(-7, 7),
            x_axis_label=self.x_label,
            y_axis_label=self.y_label,
            tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair"
        )
        self.figure.toolbar.logo = None
        self.figure.x_range = Range1d(start=0, end=5, bounds=(0, 25))
        self.figure.y_range = Range1d(start=-100, end=100, bounds=(-100, 100))

    def add_line(self, line):
        self.lines.append(line)

    def add_file(self, data_file, labels, colors):
        for y_values, label, color in zip(data_file.y_values, labels, colors):
            line = Line(data_file.x_values, y_values, label, color)
            self.add_line(line)

    def display(self):
        for line in self.lines:
            self.figure.line(
                line.x_values, 
                line.y_values, 
                legend_label=line.label, 
                color=line.color, 
                line_width=line.line_width
            )
        show(self.figure)
        

# Load files
data_file_1 = DataFile("exampleTestRun.TXT")

# Instantiate a Graph
compressionLinePlot = Graph(
    title="Compression Plot",
    x_label="Time (s)",
    y_label="Compression (mm)"
)

# Add data from files
compressionLinePlot.add_file(data_file_1, labels=["Front Fork", "Rear Shock"], colors=["grey", "orange"])

# Display the graph
compressionLinePlot.display()
