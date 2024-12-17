#  python -m bokeh serve --show graphing.py to run the server, once in file tree


# Imports
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import Range1d, Div
from bokeh.layouts import column, grid
import numpy as np
from scipy.stats import linregress



# Functions arr1 (start-point) arr2 (end-point)
def find_displacement_speed(arr1, arr2, arr1_times, arr2_times, start):
    times = []
    speeds = []
    displacements = []
    for i in range(len(arr1)-2):
        val1 = arr1[i];time1 = arr1_times[i]
        if start: #start is boolean to ensure
            val2 = arr2[i];time2 = arr2_times[i]
        else:
            val2 = arr2[i+1];time2 = arr2_times[i+1]
        displacement = abs(val2 - val1)
        if displacement > 1:  # Remove
            times.append(time2)
            speeds.append(abs(displacement / (time2 - time1)))
            displacements.append(displacement)
    return times, speeds, displacements

def turning_points(array,acceptance): #Index of points of 1d array
    idx_max, idx_min = [], []

    NEUTRAL, RISING, FALLING = range(3)
    def get_state(a, b):
        if a > b and (a-b)>acceptance: return RISING
        if a < b and (b-a)>acceptance: return FALLING
        return NEUTRAL

    ps = get_state(array[0], array[1])
    begin = 1
    for i in range(2, len(array)):
        s = get_state(array[i - 1], array[i])
        if s != NEUTRAL:
            if ps != NEUTRAL and ps != s:
                if s == FALLING:
                    idx_max.append((begin + i - 1) // 2)
                else:
                    idx_min.append((begin + i - 1) // 2)
            begin = i
            ps = s

    return idx_min, idx_max


# Text file data is retrieved from
textFile = "TestRun1.TXT"

# Graph theme
curdoc().theme = "dark_minimal"

# Travel constants
FORK_TRAVEL = 170; SHOCK_TRAVEL = 160; BIT_RANGE = 1024 #Bitrange is range of measured values

# Lists which populate graph
xValues = []; yForkValues = []; yShockValues = []

# Defining number of entries
with open(textFile, "r") as file:lineCount = len(file.readlines()) - 4  # skipping header and footer

# Reading raw accelerometer values from file
with open(textFile, "r") as file:
    file.readline()  # Header in format {shorthand name: sampling frequency: longhand name}
    initialValues = file.readline().split(',') # Initial values in list [shock displacement, fork displacement,braking, braking]
    initialShockDisplacement = float(initialValues[0]); initialForkDisplacement = float(initialValues[1])
    for accelerometerInstance in file:
        accelerometerList = accelerometerInstance.split(",")
        if len(accelerometerList) != 1:
            # Calculating percentage from Bit range
            yShockValues.append(((float(accelerometerList[6])-initialShockDisplacement)/BIT_RANGE)*SHOCK_TRAVEL)  # Rear shock
            yForkValues.append(((float(accelerometerList[7])-initialForkDisplacement)/BIT_RANGE)*FORK_TRAVEL)  # Front fork
        else:
            if accelerometerInstance!='Run finished\n': # Footer with time of run value
                timeOfRun = int(accelerometerInstance)/1000

# Time values
sampleFrequency = lineCount/timeOfRun
samplePeriod = 1/sampleFrequency

# Populating x graph (time axis) into numpy array
xValues = np.arange(0, timeOfRun, samplePeriod)

####------------------------- Fork -------------------------####

# np array for fork peak and trough
yForkValues = np.array(yForkValues, dtype=float)
forkPeaksIndexes, _ = turning_points(yForkValues,0.1) #acceptance set to 0 for most accurate readings - vibrations factored out in find_displacement_speed function
forkTroughsIndexes, _ = turning_points(-yForkValues,0.1) #change to be higher for clearer graph
forkPeaks = [yForkValues[i] for i in forkPeaksIndexes]
forkTroughs = [yForkValues[i] for i in forkTroughsIndexes]
forkPeakTimes = xValues[forkPeaksIndexes]
forkTroughTimes = xValues[forkTroughsIndexes]

# Fork compression
forkCompressionData = find_displacement_speed(forkPeaks,forkTroughs,forkPeakTimes,forkTroughTimes,(forkPeaksIndexes[0]>forkTroughsIndexes[0]))
forkCompressionTimes  = np.array(forkCompressionData[0], dtype=float)
forkCompressionSpeed = np.array(forkCompressionData[1], dtype=float)
forkCompressionDisplacement = np.array(forkCompressionData[2], dtype=float)
# Fork rebound
forkReboundData = find_displacement_speed(forkTroughs, forkPeaks, forkTroughTimes, forkPeakTimes, (forkTroughsIndexes[0]>forkPeaksIndexes[0]))
forkReboundTimes = np.array(forkReboundData[0], dtype=float)
forkReboundSpeed = np.array(forkReboundData[1], dtype=float)
forkReboundDisplacement = np.array(forkReboundData[2], dtype=float)

####------------------------- Shock -------------------------####

# np array for shock peak and trough
yShockValues = np.array(yShockValues, dtype=float)
shockPeaksIndexes, _ = turning_points(yShockValues,0.1)
shockTroughsIndexes, _ = turning_points(-yShockValues,0.1)
shockPeaks = [yShockValues[i] for i in shockPeaksIndexes]
shockTroughs = [yShockValues[i] for i in shockTroughsIndexes]
shockPeakTimes = xValues[shockPeaksIndexes]
shockTroughTimes = xValues[shockTroughsIndexes]

# shock compression
shockCompressionData = find_displacement_speed(shockPeaks,shockTroughs,shockPeakTimes,shockTroughTimes, (shockPeaksIndexes[0]>shockTroughsIndexes[0]))
shockCompressionTimes = np.array(shockCompressionData[0], dtype=float)
shockCompressionSpeed = np.array(shockCompressionData[1], dtype=float)
shockCompressionDisplacement = np.array(shockCompressionData[2], dtype=float)
# shock rebound
shockReboundData = find_displacement_speed(shockPeaks,shockTroughs,shockPeakTimes,shockTroughTimes, (shockPeaksIndexes[0]>shockTroughsIndexes[0]))
shockReboundTimes = np.array(shockReboundData[0], dtype=float)
shockReboundSpeed = np.array(shockReboundData[1], dtype=float)
shockReboundDisplacement = np.array(shockReboundData[2], dtype=float)

# Data analysis
shockMax, shockMin, shockMean = yShockValues.max(), yShockValues.min(), yShockValues.mean()
forkMax, forkMin, forkMean = yForkValues.max(), yForkValues.min(), yForkValues.mean()

##--- Displacement plot graph ---##
displacementGraph = figure(
    title="Percentage Displacement Plot: " + textFile,
    sizing_mode="stretch_width",
    height=450,
    x_axis_label="Time (s)",
    y_axis_label="Percentage displacement (%)",
    tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
)

# Limit axis movement
displacementGraph.x_range = Range1d(start=0, end=timeOfRun, bounds=(0, timeOfRun)) # Display whole time range
displacementGraph.y_range = Range1d(start=0, end=100, bounds=(0, 100))

# Rendering Fork line + Points
displacementGraph.line(xValues, yForkValues, legend_label="Front Fork", color="#00FFFF", line_width=0.5)
# Fork peaks
displacementGraph.scatter(
    forkPeakTimes,
    forkPeaks,
    color="red",
    size=2,  # Slightly larger for clarity
    legend_label="Fork Peaks",
    marker="circle",
)

#Fork troughs
displacementGraph.scatter(
    forkTroughTimes,
    forkTroughs,
    color="orange",
    size=2,
    legend_label="Fork Troughs",
    marker="circle",
)

# Rendering Shock line + Points
displacementGraph.line(xValues, yShockValues, legend_label="Rear Shock", color="#FF9500", line_width=0.5)
#Shock peaks
displacementGraph.scatter(
    shockPeakTimes,
    shockPeaks,
    color="red",
    size=2,
    legend_label="Shock Peaks",
    marker="circle",
)
#Shock troughs
displacementGraph.scatter(
    shockTroughTimes,
    shockTroughs,
    color="orange",
    size=2,
    legend_label="Shock Troughs",
    marker="circle",
)


####------------------------- Scatter Plots -------------------------####

##--- Compression scatter graph ---##
compGraph = figure(
    title="Compression Scatter Plot: " + textFile,
    sizing_mode="stretch_width",
    height=450,
    x_axis_label="Speed of displacement (%/s)",
    y_axis_label="Absolute change in displacement (%)",
    tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
)

# Limit axis movement
compGraph.x_range = Range1d(start=0, end=max(max(forkCompressionSpeed),max(shockCompressionSpeed))*1.1, bounds=(0, max(max(forkCompressionSpeed),max(shockCompressionSpeed))*1.1))
compGraph.y_range = Range1d(start=0, end=max(max(forkCompressionDisplacement),max(shockCompressionDisplacement))*1.1, bounds=(0, max(max(forkCompressionDisplacement),max(shockCompressionDisplacement))*1.1))

# fork compression scatter
compGraph.scatter(
    forkCompressionSpeed,
    forkCompressionDisplacement,
    color="blue",
    size=4,
    legend_label="fork compression",
    marker="circle",
)

# fork compression regression
forkCompression = linregress(forkCompressionDisplacement, forkCompressionSpeed)
forkCompression_regress = forkCompression.slope * forkCompressionDisplacement + forkCompression.intercept
compGraph.line(x=forkCompression_regress, y=forkCompressionDisplacement, color='#00FFFF', legend_label="fork regression", line_width=2)

# shock compression scatter
compGraph.scatter(
    shockCompressionSpeed,
    shockCompressionDisplacement,
    color="orange",
    size=4,
    legend_label="shock compression",
    marker="circle",
)

# shock compression regression
shockCompression = linregress(shockCompressionDisplacement, shockCompressionSpeed)
shockCompression_regress = shockCompression.slope * shockCompressionDisplacement + shockCompression.intercept
compGraph.line(x=shockCompression_regress, y=shockCompressionDisplacement, color='red', legend_label="shock regression", line_width=2)


##--- Rebound scatter graph ---##
rebGraph = figure(
    title="Rebound Scatter Plot: " + textFile,
    sizing_mode="stretch_width",
    height=450,
    width=100,
    x_axis_label="Speed of displacement (%/s)",
    y_axis_label="Absolute change in displacement (%)",
    tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
)

# Limit axis movement
rebGraph.x_range = Range1d(start=0, end=max(max(forkReboundSpeed),max(shockReboundSpeed))*1.1, bounds=(0, max(max(forkReboundSpeed),max(shockReboundSpeed))*1.1))
rebGraph.y_range = Range1d(start=0, end=max(max(forkReboundDisplacement),max(shockReboundDisplacement))*1.1, bounds=(0, max(max(forkReboundDisplacement),max(shockReboundDisplacement))*1.1))

# fork Rebound scatter
rebGraph.scatter(
    forkReboundSpeed,
    forkReboundDisplacement,
    color="blue",
    size=4,
    legend_label="fork rebound",
    marker="circle",
)

# fork Rebound regression
forkRebound = linregress(forkReboundDisplacement, forkReboundSpeed)
forkRebound_regress = forkRebound.slope * forkReboundDisplacement + forkRebound.intercept
rebGraph.line(x=forkRebound_regress, y=forkReboundDisplacement, color='#00FFFF', legend_label="fork regression", line_width=2)

# shock Rebound scatter
rebGraph.scatter(
    shockReboundSpeed,
    shockReboundDisplacement,
    color="orange",
    size=4,
    legend_label="shock rebound",
    marker="circle",
)

# shock Rebound regression
shockRebound = linregress(shockReboundDisplacement, shockReboundSpeed)
shockRebound_regress = shockRebound.slope * shockReboundDisplacement + shockRebound.intercept
rebGraph.line(x=shockRebound_regress, y=shockReboundDisplacement, color='red', legend_label="shock regression", line_width=2)

####------------------------- HTML Readings -------------------------####

# Display stats as HTML below the plot - Useful for debugging
stats_div = Div(
    text=f"""
    <h3>Fork Values:</h3>
    <p><b>Max:</b> {forkMax:.2f} mm<br><b>Min:</b> {forkMin:.2f} mm<br><b>Mean:</b> {forkMean:.2f} mm 
    <h3>Shock Values:</h3>
    <p><b>Max:</b> {shockMax:.2f} mm<br><b>Min:</b> {shockMin:.2f} mm<br><b>Mean:</b> {shockMean:.2f} mm 
    """,
    sizing_mode="stretch_width",
)


####------------------------- Rendering -------------------------####

# Combine graphs into a dashboard layout
displacementGraph.toolbar.logo = None; rebGraph.toolbar.logo = None; compGraph.toolbar.logo = None
displacementGraph.legend.click_policy = "hide"; compGraph.legend.click_policy = "hide"; rebGraph.legend.click_policy = "hide"
dashboardLayout = grid([[displacementGraph], [compGraph, rebGraph], [stats_div]],sizing_mode='stretch_both')


curdoc().add_root(dashboardLayout)