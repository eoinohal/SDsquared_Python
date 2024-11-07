from bokeh.io import curdoc
from bokeh.plotting import figure, show
import numpy as np
from bokeh.models import Range1d
from scipy.signal import find_peaks

# apply theme to current document
curdoc().theme = "dark_minimal"

# prepare some data
xValues = []
yForkValues = []
yShockValues = []

# reading files
with open("exampleTestRun.TXT", "r") as file:
    # Skip the first two lines
    file.readline()
    file.readline()

    for i in range(0, 5000):
        xValues.append(i * 0.01)
        temp = file.readline().split(",")
        yForkValues.append(temp[1])
        yShockValues.append(temp[0])

# Convert lists to numpy arrays
xValues = np.array(xValues, dtype=float)

yForkValues = np.array(yForkValues, dtype=float)
forkPeaks, _ = find_peaks(yForkValues)
forkTroughs, _ =find_peaks(-yForkValues)

yShockValues = np.array(yShockValues, dtype=float)
shockPeaks, _ = find_peaks(yShockValues)
shockTroughs, _ =find_peaks(-yShockValues)

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
p.y_range = Range1d(start=-100, end=100, bounds=(-100, 100))

# Rendering Fork line + Points
p.line(xValues, yForkValues, legend_label="Front Fork", color="grey", line_width=0.5)
p.circle(xValues[forkPeaks], yForkValues[forkPeaks], color="red", size=2, legend_label="Fork Peaks")
p.circle(xValues[forkTroughs], yForkValues[forkTroughs], color="blue", size=2, legend_label="Fork Troughs")


p.line(xValues, yShockValues, legend_label="Rear Shock", color="orange", line_width=0.5)
p.circle(xValues[shockPeaks], yShockValues[shockPeaks], color="red", size=2, legend_label="Shock Peaks")
p.circle(xValues[shockTroughs], yShockValues[shockTroughs], color="blue", size=2, legend_label="Shock Troughs")

# Call function to display plot
p.legend.click_policy = "hide"
show(p)

print("Shock values:")
print("Max: ", yShockValues.max(), " Min: ", yShockValues.min(), " Mean: ", yShockValues.mean())
print("Fork values:")
print("Max: ", yForkValues.max(), " Min: ", yForkValues.min(), " Mean: ", yForkValues.mean())
