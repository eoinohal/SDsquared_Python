# Imports
from bokeh.io import curdoc
from bokeh.plotting import figure, show
import numpy as np
from bokeh.models import Range1d
from scipy.signal import find_peaks

# Graph theme
curdoc().theme = "dark_minimal"

# Lists used
xValues = [] # use np array to fill
yForkValues = []
yShockValues = []

# Reading length for x values
with open("exampleTestRun.TXT", "r") as file:
    lineCount = len(file.readlines())

# Reading raw accelerometer values
with open("exampleTestRun.TXT", "r") as file:
    # Skip header (first 2 lines)
    file.readline()
    file.readline()
    for accelerometerInstance in file :
        accelerometerList = accelerometerInstance.split(",")
        if len(accelerometerList)!=1:
            # Axis measured - Update values ##------------------------------------------------------------------------------------------##
            yShockValues.append(accelerometerList[0])
            yForkValues.append(accelerometerList[1])

# Populating x graph (time axis) into numpy array
sampleFrequency = 1000; samplePeriod = (1/sampleFrequency); timeLength = lineCount*samplePeriod
xValues = array = np.arange(0, timeLength, samplePeriod)

# Convert lists to numpy arrays
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



#---- Data analysis
print("Shock values:")
print("Max: ", yShockValues.max(), " Min: ", yShockValues.min(), " Mean: ", yShockValues.mean())
print("Fork values:")
print("Max: ", yForkValues.max(), " Min: ", yForkValues.min(), " Mean: ", yForkValues.mean())
maxYValue = max(yShockValues.max(),yForkValues.max())
minYValue = min(yShockValues.min(),yForkValues.min())
#----



# Limit axis movement
p.x_range = Range1d(start=0, end=timeLength, bounds=(0, timeLength))
p.y_range = Range1d(start=minYValue*1.2, end=maxYValue*1.2, bounds=(minYValue*1.2, maxYValue*1.2))

# Rendering Fork line + Points
p.line(xValues, yForkValues, legend_label="Front Fork", color="grey", line_width=0.5)
p.scatter(xValues[forkPeaks], yForkValues[forkPeaks], color="red", size=2, legend_label="Fork Peaks", marker="circle")
p.scatter(xValues[forkTroughs], yForkValues[forkTroughs], color="blue", size=2, legend_label="Fork Troughs", marker="circle")

# Rendering Shock line + Points
p.line(xValues, yShockValues, legend_label="Rear Shock", color="orange", line_width=0.5)
p.scatter(xValues[shockPeaks], yShockValues[shockPeaks], color="red", size=2, legend_label="Shock Peaks", marker="circle")
p.scatter(xValues[shockTroughs], yShockValues[shockTroughs], color="blue", size=2, legend_label="Shock Troughs", marker="circle")

# Call function to display plot
p.legend.click_policy = "hide"
show(p)

