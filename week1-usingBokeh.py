from bokeh.io import curdoc
from bokeh.plotting import figure, show
#import numpy as np
from bokeh.models import Range1d


# apply theme to current document
curdoc().theme = "dark_minimal"


# prepare some data
xValues = []

# y values
yForkVaues = []
yShockValues = []

# reading files
file = open("RUN4.TXT", "r")

#pass over every line
file.readline()
file.readline()

for i in range(0,2500):
    xValues.append(i*0.01)
    temp = file.readline().split(",")
    yForkVaues.append(temp[3])
    yShockValues.append(temp[4])

      
# Create a new plot with a title and axis labels
p = figure(
    title="Compression Plot",
    sizing_mode="stretch_width",
    height=450,
    x_range=(0, 10),
    y_range=(-7, 7),
    x_axis_label='Time (s)',
    y_axis_label='Compression (mm)',
    tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair"
    
)

# Removing toolbar
p.toolbar.logo = None

# Limit axis movement
p.x_range = Range1d(start=0, end=5, bounds=(0, 25))
p.y_range = Range1d(start=-8, end=8, bounds=(-8, 8))

# Rendering line
p.line(xValues, yForkVaues, legend_label="Front Fork", color="grey", line_width=0.5)
p.line(xValues, yShockValues, legend_label="Rear Shock", color="orange", line_width=0.5)

# Call function to convert to HTML
show(p)
