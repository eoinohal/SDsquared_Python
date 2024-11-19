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
time_differences = []
displacement_differences = []

# Loop through each peak
for peak, peak_time in zip(forkPeaks, forkPeakTimes):
    # Find the first trough that occurs after the peak time
    following_troughs = forkTroughTimes[(forkTroughTimes > peak_time)]

    if len(following_troughs) > 0:
        # Take the first following trough
        following_trough = following_troughs[0]

        # Calculate the time difference
        time_diff = following_trough - peak_time
        time_differences.append(time_diff)

        # Calculate the displacement difference
        trough_value = yForkValues[forkTroughs[np.where(forkTroughTimes == following_trough)[0][0]]]
        displacement_diff = yForkValues[peak] - trough_value
        displacement_differences.append((peak_time, displacement_diff, time_diff))
    else:
        # Handle case where there is no following trough
        time_differences.append(np.nan)  # NaN for no following trough
        displacement_differences.append((peak_time, np.nan, np.nan))  # NaN for no following trough

# Convert results to formatted strings
formatted_differences = [
    f"{time:.3f}: {time_diff:.3f}: {displacement_diff:.2f}: {displacement_diff / time_diff:}"
    if not (np.isnan(displacement_diff) or np.isnan(time_diff))
    else f"{time:.3f}s: No trough"
    for time, displacement_diff, time_diff in displacement_differences
]

# Calculating turning points
yShockValues = np.array(yShockValues, dtype=float)
shockPeaks, _ = find_peaks(yShockValues)
shockTroughs, _ = find_peaks(-yShockValues)

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
    xValues[forkPeaks],
    yForkValues[forkPeaks],
    color="red",
    size=2,
    legend_label="Fork Peaks",
    marker="circle",
)
displacementGraph.scatter(
    xValues[forkTroughs],
    yForkValues[forkTroughs],
    color="orange",
    size=2,
    legend_label="Fork Troughs",
    marker="circle",
)

# Rendering Shock line + Points
displacementGraph.line(xValues, yShockValues, legend_label="Rear Shock", color="#FF9500", line_width=0.5)
displacementGraph.scatter(
    xValues[shockPeaks],
    yShockValues[shockPeaks],
    color="red",
    size=2,
    legend_label="Shock Peaks",
    marker="circle",
)
displacementGraph.scatter(
    xValues[shockTroughs],
    yShockValues[shockTroughs],
    color="orange",
    size=2,
    legend_label="Shock Troughs",
    marker="circle",
)


####------------------------- Scatter Plot -------------------------####

# Determine Shock Compression
displacementTimeList = []
displacementSpeedList = []
for item in formatted_differences:
    split = item.split(': ')
    if split[-1]!='No trough': #skipping over empty cases
        displacementTimeList.append(split[1])
        displacementSpeedList.append(split[3])

# Convert lists to numpy arrays
displacementTimeList = np.array(displacementTimeList, dtype=float)
displacementSpeedList = np.array(displacementSpeedList, dtype=float)

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
compGraph.x_range = Range1d(start=0, end=max(displacementTimeList)*1.2, bounds=(0, max(displacementTimeList)*1.1))
compGraph.y_range = Range1d(start=0, end=max(displacementSpeedList)*1.2, bounds=(0, max(displacementSpeedList)*1.1))

# shock compression scatter
compGraph.scatter(
    displacementTimeList,
    displacementSpeedList,
    color="orange",
    size=4,
    legend_label="shock compression",
    marker="circle",
)

# Line of best fit for shock compression
shockCompression = linregress(displacementTimeList, displacementSpeedList)
y_regress = shockCompression.slope * displacementTimeList + shockCompression.intercept
compGraph.line(x=displacementTimeList, y=y_regress, color='red', legend_label="shock regression", line_width=2)

####------------------------- HTML Readings -------------------------####

# Display stats as HTML below the plot - Useful for debugging
stats_div = Div(
    text=f"""
    <h3>Shock Values:</h3>
    <p><b>Max:</b> {shockMax:.2f} mm<br><b>Min:</b> {shockMin:.2f} mm<br><b>Mean:</b> {shockMean:.2f} mm</p>
    <h3>Fork Values:</h3>
    <p><b>Max:</b> {forkMax:.2f} mm<br><b>Min:</b> {forkMin:.2f} mm<br><b>Mean:</b> {forkMean:.2f} mm</p>
    <h3>Fork Displacement Differences:</h3>
    <ul>
    {''.join(f'<li>{item}</li>' for item in formatted_differences)}
    </ul>
    """,
    sizing_mode="stretch_width",
)

####------------------------- Rendering -------------------------####

# Combine graphs into a dashboard layout
displacementGraph.legend.click_policy = "hide"; compGraph.legend.click_policy = "hide"
layout = Column(displacementGraph, compGraph, stats_div, sizing_mode="stretch_both")

# Show the plot with stats
show(layout)
