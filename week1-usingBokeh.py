# Imports
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import Range1d
from scipy.signal import find_peaks
import numpy as np

# Graph theme
curdoc().theme = "dark_minimal"

# Lists which populate graph
xValues = []
yForkValues = []
yShockValues = []

# Reading length for x values
with open("exampleTestRun.TXT", "r") as file:
    lineCount = len(file.readlines()) - 4 # Skip headers

# Reading raw accelerometer values
with open("exampleTestRun.TXT", "r") as file:
    file.readline();file.readline() # Skip header
    for accelerometerInstance in file:
        accelerometerList = accelerometerInstance.split(",")
        if len(accelerometerList)!=1:
            # Axis measured - Update values ##------------------------------------------------------------------------------------------##
            yShockValues.append(accelerometerList[6]) # 6 is the rear shock
            yForkValues.append((accelerometerList[7])) # 7 is the front fork

# Populating x graph (time axis) into numpy array
sampleFrequency = 1000; samplePeriod = (1/sampleFrequency); timeLength = lineCount*samplePeriod
xValues = array = np.arange(0, timeLength, samplePeriod)

# Convert lists to numpy arrays
yForkValues = np.array(yForkValues, dtype=float)
forkPeaks, _ = find_peaks(yForkValues)
forkTroughs, _ = find_peaks(-yForkValues)

yShockValues = np.array(yShockValues, dtype=float)
shockPeaks, _ = find_peaks(yShockValues)
shockTroughs, _ = find_peaks(-yShockValues)

# Create a new graph plot with a title and axis labels
forkGraph = figure(
    title="Compression Plot",
    sizing_mode="stretch_width",
    height=450,
    x_range=(0, 10),
    y_range=(-7, 7),
    x_axis_label='Time (s)',
    y_axis_label='Compression (mm)',
    tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair"
)
shockGraph = figure(
    title="Compression Plot",
    sizing_mode="stretch_width",
    height=450,
    x_range=(0, 10),
    y_range=(-7, 7),
    x_axis_label='Time (s)',
    y_axis_label='Compression (mm)',
    tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair"
)
forkGraph.toolbar.logo = None; shockGraph.toolbar.logo = None


#---- Data analysis ---# Move to function or method
# Range of graph in y-axis
maxYValue = max(yShockValues.max(),yForkValues.max()); minYValue = min(yShockValues.min(),yForkValues.min())

# Calculating gradients
xForkTurningPoints = [val for pair in zip(forkPeaks, forkTroughs) for val in pair]; xForkTurningPoints.insert(0, 0); xShockTurningPoints = [val for pair in zip(shockPeaks, forkPeaks) for val in pair]
gradientsFork = []; gradientsShock = []
for value in xForkTurningPoints:
    if value == 0: lastValue = value;pass
    gradientsFork.append((yForkValues[value]-yForkValues[lastValue])/(value-lastValue))
    lastValue = value

for value in xShockTurningPoints:
    if value == 0: lastValue = value;pass
    gradientsShock.append((yShockValues[value]-yShockValues[lastValue])/(value-lastValue))
    lastValue = value
#----


# Rendering Fork line + Points
forkGraph.line(xValues, yForkValues, legend_label="Front Fork", color="grey", line_width=1)
forkGraph.scatter(xValues[forkPeaks], yForkValues[forkPeaks], color="red", size=2, legend_label="Fork Peaks", marker="circle")
forkGraph.scatter(xValues[forkTroughs], yForkValues[forkTroughs], color="blue", size=2, legend_label="Fork Troughs", marker="circle")

# Plotting gradients
forkGraph.line(xValues[xForkTurningPoints], gradientsFork, legend_label="Fork Gradient", color="white", line_width=1)


# Rendering Shock line + Points
shockGraph.line(xValues, yShockValues, legend_label="Rear Shock", color="orange", line_width=0.5)
shockGraph.scatter(xValues[shockPeaks], yShockValues[shockPeaks], color="red", size=2, legend_label="Shock Peaks", marker="circle")
shockGraph.scatter(xValues[shockTroughs], yShockValues[shockTroughs], color="blue", size=2, legend_label="Shock Troughs", marker="circle")

# Plotting gradients
shockGraph.line(xValues[xShockTurningPoints], gradientsShock, legend_label="Shock Gradient", color="Brown", line_width=1)


# Limit axis movement and display plots
forkGraph.x_range = Range1d(start=0, end=timeLength, bounds=(0, timeLength)); shockGraph.x_range = Range1d(start=0, end=timeLength, bounds=(0, timeLength))
forkGraph.y_range = Range1d(start=minYValue*1.2, end=maxYValue*1.2, bounds=(minYValue*1.2, maxYValue*1.2)); shockGraph.y_range = Range1d(start=minYValue*1.2, end=maxYValue*1.2, bounds=(minYValue*1.2, maxYValue*1.2))
forkGraph.legend.click_policy = "hide"; shockGraph.legend.click_policy = "hide"
show(forkGraph)
