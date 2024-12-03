# Imports
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import Range1d, Div
from bokeh.layouts import Column
import numpy as np
from scipy.signal import find_peaks
from scipy.stats import linregress


# Text file data is retreived from
textFile = "TestRun1.TXT"

# Graph theme
curdoc().theme = "dark_minimal"

# Travel constants
FORK_TRAVEL = 170; SHOCK_TRAVEL = 170; BIT_RANGE = 1024 #Bitrange is range of measured values

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
            yShockValues.append(((float(accelerometerList[6])-initialShockDisplacement)/BIT_RANGE)*100)  # Rear shock
            yForkValues.append(((float(accelerometerList[7])-initialForkDisplacement)/BIT_RANGE)*100)  # Front fork
        else:
            if accelerometerInstance!='Run finished\n': # Footer with time of run value
                timeOfRun = int(accelerometerInstance)/1000

# Time values
sampleFrequency = lineCount/timeOfRun
samplePeriod = 1/sampleFrequency

# Populating x graph (time axis) into numpy array
xValues = np.arange(0, timeOfRun, samplePeriod)

# Convert lists to numpy arrays
yForkValues = np.array(yForkValues, dtype=float)
forkPeaks, _ = find_peaks(yForkValues)
forkTroughs, _ = find_peaks(-yForkValues)

forkPeakTimes = xValues[forkPeaks]
forkTroughTimes = xValues[forkTroughs]

# Initialize combined lists
fork_time_differences = []
fork_displacement_differences = []

# Loop through each peak
for peak, peak_time in zip(forkPeaks, forkPeakTimes):
    # Find the first trough that occurs after the peak time
    following_troughs = forkTroughTimes[(forkTroughTimes > peak_time)]

    if len(following_troughs) > 0:
        # Take the first following trough
        following_trough = following_troughs[0]

        # Calculate the time difference
        time_diff = following_trough - peak_time
        fork_time_differences.append(time_diff)

        # Calculate the displacement difference
        trough_value = yForkValues[forkTroughs[np.where(forkTroughTimes == following_trough)[0][0]]]
        displacement_diff = yForkValues[peak] - trough_value
        fork_displacement_differences.append((peak_time, displacement_diff, time_diff))
    else:
        # Handle case where there is no following trough
        fork_time_differences.append(np.nan)  # NaN for no following trough
        fork_displacement_differences.append((peak_time, np.nan, np.nan))  # NaN for no following trough

#Relevant fork index
relevantPeaksIndices = [
    forkPeaks[i]  # Use forkPeaks indices to map back to yForkValues
    for i, (_, displacement_diff, _) in enumerate(fork_displacement_differences)
    if displacement_diff > 3
]
relevantForkPeaksXaxis = [xValues[i] for i in relevantPeaksIndices]
relevantForkPeaksYaxis = [yForkValues[i] for i in relevantPeaksIndices]


# Relevant Trough Index
relevantForkTroughsIndices = []
# Iterate through the relevant peaks
for peak_index in relevantPeaksIndices:
    # Find the first trough index that occurs after the current peak
    following_troughs = forkTroughs[forkTroughs > peak_index]  # Trough indices after the current peak
    if len(following_troughs) > 0:
        relevantForkTroughsIndices.append(following_troughs[0])  # Take the first trough

# Get x and y points for the relevant troughs
relevantForkTroughsXaxis = [xValues[i] for i in relevantForkTroughsIndices]
relevantForkTroughsYaxis = [yForkValues[i] for i in relevantForkTroughsIndices]

formatted_fork_differences = [
    (xValues[peak_index],yForkValues[peak_index] - yForkValues[trough_index],(yForkValues[peak_index] - yForkValues[trough_index]) / (xValues[trough_index] - xValues[peak_index]))
    if trough_index is not None
    else f"{xValues[peak_index]:.3f}s: No trough found"
    for peak_index, trough_index in zip(relevantPeaksIndices, relevantForkTroughsIndices + [None] * (len(relevantPeaksIndices) - len(relevantForkTroughsIndices)))
]

# Calculating turning points
yShockValues = np.array(yShockValues, dtype=float)
shockPeaks, _ = find_peaks(yShockValues)
shockTroughs, _ = find_peaks(-yShockValues)

shockPeakTimes = xValues[shockPeaks]
shockTroughTimes = xValues[shockTroughs]

shock_time_differences = []
shock_displacement_differences = []

# Loop through each peak
for peak, peak_time in zip(shockPeaks, shockPeakTimes):
    # Find the first trough that occurs after the peak time
    following_troughs = shockTroughTimes[(shockTroughTimes > peak_time)]

    if len(following_troughs) > 0:
        # Take the first following trough
        following_trough = following_troughs[0]

        # Calculate the time difference
        time_diff = following_trough - peak_time
        shock_time_differences.append(time_diff)

        # Calculate the displacement difference
        trough_value = yShockValues[shockTroughs[np.where(shockTroughTimes == following_trough)[0][0]]]
        displacement_diff = yShockValues[peak] - trough_value
        shock_displacement_differences.append((peak_time, displacement_diff, time_diff))
    else:
        # Handle case where there is no following trough
        shock_time_differences.append(np.nan)  # NaN for no following trough
        shock_displacement_differences.append((peak_time, np.nan, np.nan))  # NaN for no following trough

#Relevant shock index
relevantShockPeaksIndices = [
    shockPeaks[i]
    for i, (_, displacement_diff, _) in enumerate(shock_displacement_differences)
    if displacement_diff > 3
]
relevantShockPeaksXaxis = [xValues[i] for i in relevantShockPeaksIndices]
relevantShockPeaksYaxis = [yShockValues[i] for i in relevantShockPeaksIndices]


# Relevant Trough Index
relevantShockTroughsIndices = []
# Iterate through the relevant peaks
for peak_index in relevantPeaksIndices:
    # Find the first trough index that occurs after the current peak
    following_troughs = shockTroughs[shockTroughs > peak_index]  # Trough indices after the current peak
    if len(following_troughs) > 0:
        relevantShockTroughsIndices.append(following_troughs[0])  # Take the first trough

# Get x and y points for the relevant troughs
relevantShockTroughsXaxis = [xValues[i] for i in relevantShockTroughsIndices]
relevantShockTroughsYaxis = [yShockValues[i] for i in relevantShockTroughsIndices]

formatted_shock_differences = [
    (xValues[peak_index],yShockValues[peak_index] - yShockValues[trough_index],(yShockValues[peak_index] - yShockValues[trough_index]) / (xValues[trough_index] - xValues[peak_index]))
    if trough_index is not None
    else f"{xValues[peak_index]:.3f}s: No trough found"
    for peak_index, trough_index in zip(relevantPeaksIndices, relevantShockTroughsIndices + [None] * (len(relevantPeaksIndices) - len(relevantShockTroughsIndices)))
]

##--- Displacement plot graph ---##
displacementGraph = figure(
    title="Percentage Displacement Plot: " + textFile,
    sizing_mode="stretch_width",
    height=450,
    x_axis_label="Time (s)",
    y_axis_label="Percentage displacement (%)",
    tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
)
displacementGraph.toolbar.logo = None

# Data analysis
shockMax, shockMin, shockMean = yShockValues.max(), yShockValues.min(), yShockValues.mean()
forkMax, forkMin, forkMean = yForkValues.max(), yForkValues.min(), yForkValues.mean()

# Limit axis movement
displacementGraph.x_range = Range1d(start=0, end=timeOfRun, bounds=(0, timeOfRun)) # Display whole time range
displacementGraph.y_range = Range1d(start=0, end=100, bounds=(0, 100))

# Rendering Fork line + Points
displacementGraph.line(xValues, yForkValues, legend_label="Front Fork", color="#00FFFF", line_width=0.5)
displacementGraph.scatter(
    relevantForkPeaksXaxis,
    relevantForkPeaksYaxis,
    color="red",
    size=2,  # Slightly larger for clarity
    legend_label="Fork Peaks",
    marker="circle",
)

displacementGraph.scatter(
    relevantForkTroughsXaxis,
    relevantForkTroughsYaxis,
    color="orange",
    size=2,
    legend_label="Fork Troughs",
    marker="circle",
)

# Rendering Shock line + Points
displacementGraph.line(xValues, yShockValues, legend_label="Rear Shock", color="#FF9500", line_width=0.5)
displacementGraph.scatter(
    relevantShockPeaksXaxis,
    relevantShockPeaksYaxis,
    color="red",
    size=2,
    legend_label="Shock Peaks",
    marker="circle",
)
displacementGraph.scatter(
    relevantShockTroughsXaxis,
    relevantShockTroughsYaxis,
    color="orange",
    size=2,
    legend_label="Shock Troughs",
    marker="circle",
)


####------------------------- Scatter Plot -------------------------####

# Determine Fork Compression
forkDisplacementTimeList = []
forkDisplacementSpeedList = []
for item in formatted_fork_differences:
    if isinstance(item, str):
        split = item.split(': ')
        if split[-1] != 'No trough':  # skipping over empty cases
            forkDisplacementTimeList.append(float(split[1]))
            forkDisplacementSpeedList.append(float(split[3]))
    else:
        # item is a tuple (expected format: (peak_time, displacement_diff, time_diff))
        _, displacement_diff, time_diff = item
        if displacement_diff is not None:
            forkDisplacementTimeList.append(time_diff)
            forkDisplacementSpeedList.append(displacement_diff)

# Convert lists to numpy arrays
forkDisplacementTimeList = np.array(forkDisplacementTimeList, dtype=float)
forkDisplacementSpeedList = np.array(forkDisplacementSpeedList, dtype=float)

# Determine Shock Compression
shockDisplacementTimeList = []
shockDisplacementSpeedList = []
for item in formatted_fork_differences:
    if isinstance(item, str):
        split = item.split(': ')
        if split[-1] != 'No trough':  # skipping over empty cases
            shockDisplacementTimeList.append(float(split[1]))
            shockDisplacementSpeedList.append(float(split[3]))
    else:
        # item is a tuple (expected format: (peak_time, displacement_diff, time_diff))
        _, displacement_diff, time_diff = item
        if displacement_diff is not None:
            shockDisplacementTimeList.append(time_diff)
            shockDisplacementSpeedList.append(displacement_diff)

# Convert lists to numpy arrays
shockDisplacementTimeList = np.array(shockDisplacementTimeList, dtype=float)
shockDisplacementSpeedList = np.array(shockDisplacementSpeedList, dtype=float)

##--- Compression scatter graph ---##
compGraph = figure(
    title="Compression Scatter Plot: " + textFile,
    sizing_mode="stretch_width",
    height=450,
    x_axis_label="Speed of displacement (%/s)",
    y_axis_label="Absolute change in displacement (%)",
    tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
)
compGraph.toolbar.logo = None

# Limit axis movement
compGraph.x_range = Range1d(start=0, end=max(forkDisplacementTimeList)*1.2, bounds=(0, max(forkDisplacementTimeList)*1.1))
compGraph.y_range = Range1d(start=0, end=max(forkDisplacementSpeedList)*1.2, bounds=(0, max(forkDisplacementSpeedList)*1.1))

# shock compression scatter
compGraph.scatter(
    forkDisplacementTimeList,
    forkDisplacementSpeedList,
    color="orange",
    size=4,
    legend_label="shock compression",
    marker="circle",
)

# Line of best fit for fork compression
forkCompression = linregress(forkDisplacementTimeList, forkDisplacementSpeedList)
fork_y_regress = forkCompression.slope * forkDisplacementTimeList + forkCompression.intercept
compGraph.line(x=forkDisplacementTimeList, y=fork_y_regress, color='red', legend_label="fork regression", line_width=2)

# Line of best fit for shock compression
shockCompression = linregress(shockDisplacementTimeList, shockDisplacementSpeedList)
shock_y_regress = shockCompression.slope * shockDisplacementTimeList + shockCompression.intercept
compGraph.line(x=shockDisplacementTimeList, y=shock_y_regress, color='red', legend_label="shock regression", line_width=2)
####------------------------- HTML Readings -------------------------####

# Display stats as HTML below the plot - Useful for debugging
stats_div = Div(
    text=f"""
    <h3>Shock Values:</h3>
    <p><b>Max:</b> {shockMax:.2f} mm<br><b>Min:</b> {shockMin:.2f} mm<br><b>Mean:</b> {shockMean:.2f} mm</p>
    <h3>Fork Values:</h3>
    <p><b>Max:</b> {forkMax:.2f} mm<br><b>Min:</b> {forkMin:.2f} mm<br><b>Mean:</b> {forkMean:.2f} mm</p>
    """,
    sizing_mode="stretch_width",
)

####------------------------- Rendering -------------------------####

# Combine graphs into a dashboard layout
displacementGraph.legend.click_policy = "hide"; compGraph.legend.click_policy = "hide"
layout = Column(displacementGraph, compGraph, stats_div, sizing_mode="stretch_both")

# Show the plot with stats
show(layout)
