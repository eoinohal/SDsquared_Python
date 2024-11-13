# Imports
from bokeh.io import curdoc
from bokeh.plotting import figure, show
from bokeh.models import Range1d, Div
from bokeh.layouts import Column
import numpy as np
from scipy.signal import find_peaks

# Defining which text file to user
textFile = "TestRun1.TXT"

# Graph theme
curdoc().theme = "dark_minimal"

# Lists which populate graph
xValues = []
yForkValues = []
yShockValues = []

# Reading length for x values
with open(textFile, "r") as file:
    lineCount = len(file.readlines()) - 4  # Skip headers

# Reading raw accelerometer values
with open(textFile, "r") as file:
    file.readline()
    file.readline()  # Skip header
    for accelerometerInstance in file:
        accelerometerList = accelerometerInstance.split(",")
        if len(accelerometerList) != 1:
            # Axis measured - Update values
            yShockValues.append(float(accelerometerList[6]) - 5)  # Rear shock
            yForkValues.append(float(accelerometerList[7]) - 157)  # Front fork

# Populating x graph (time axis) into numpy array
sampleFrequency = 1000
samplePeriod = 1 / sampleFrequency
timeLength = lineCount * samplePeriod
xValues = np.arange(0, timeLength, samplePeriod)

# Convert lists to numpy arrays
yForkValues = np.array(yForkValues, dtype=float)
forkPeaks, _ = find_peaks(yForkValues)
forkTroughs, _ = find_peaks(-yForkValues)

forkPeakTimes = xValues[forkPeaks]
forkTroughTimes = xValues[forkTroughs]

# Initialize combined lists
time_differences = []
compression_differences = []

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

        # Calculate the compression difference
        trough_value = yForkValues[forkTroughs[np.where(forkTroughTimes == following_trough)[0][0]]]
        compression_diff = yForkValues[peak] - trough_value
        compression_differences.append((peak_time, compression_diff, time_diff))
    else:
        # Handle case where there is no following trough
        time_differences.append(np.nan)  # NaN for no following trough
        compression_differences.append((peak_time, np.nan, np.nan))  # NaN for no following trough

# Convert results to formatted strings
formatted_differences = [
    f"{time:.3f}s: {time_diff:.3f}s: {compression_diff:.2f} mm: {compression_diff / time_diff:} mm/s"
    if not (np.isnan(compression_diff) or np.isnan(time_diff))
    else f"{time:.3f}s: No trough"
    for time, compression_diff, time_diff in compression_differences
]



yShockValues = np.array(yShockValues, dtype=float)
shockPeaks, _ = find_peaks(yShockValues)
shockTroughs, _ = find_peaks(-yShockValues)

# Create a new graph plot with a title and axis labels
p = figure(
    title="Compression Plot: " + textFile,
    sizing_mode="stretch_width",
    height=450,
    x_axis_label="Time (s)",
    y_axis_label="Compression (mm)",
    tools="pan, reset, wheel_zoom, xwheel_zoom, fullscreen, examine, crosshair",
)
p.toolbar.logo = None

# Data analysis
shockMax, shockMin, shockMean = yShockValues.max(), yShockValues.min(), yShockValues.mean()
forkMax, forkMin, forkMean = yForkValues.max(), yForkValues.min(), yForkValues.mean()

# Limit axis movement
p.x_range = Range1d(start=0, end=timeLength, bounds=(0, timeLength))
p.y_range = Range1d(start=min(yShockValues.min(), yForkValues.min()) * 1.2,
                    end=max(yShockValues.max(), yForkValues.max()) * 1.2)

# Rendering Fork line + Points
p.line(xValues, yForkValues, legend_label="Front Fork", color="#00FFFF", line_width=0.5)
p.scatter(
    xValues[forkPeaks],
    yForkValues[forkPeaks],
    color="red",
    size=2,
    legend_label="Fork Peaks",
    marker="circle",
)
p.scatter(
    xValues[forkTroughs],
    yForkValues[forkTroughs],
    color="orange",
    size=2,
    legend_label="Fork Troughs",
    marker="circle",
)

# Rendering Shock line + Points
p.line(xValues, yShockValues, legend_label="Rear Shock", color="#FF9500", line_width=0.5)
p.scatter(
    xValues[shockPeaks],
    yShockValues[shockPeaks],
    color="red",
    size=2,
    legend_label="Shock Peaks",
    marker="circle",
)
p.scatter(
    xValues[shockTroughs],
    yShockValues[shockTroughs],
    color="orange",
    size=2,
    legend_label="Shock Troughs",
    marker="circle",
)

# Display stats as HTML below the plot
stats_div = Div(
    text=f"""
    <h3>Shock Values:</h3>
    <p><b>Max:</b> {shockMax:.2f} mm<br><b>Min:</b> {shockMin:.2f} mm<br><b>Mean:</b> {shockMean:.2f} mm</p>
    <h3>Fork Values:</h3>
    <p><b>Max:</b> {forkMax:.2f} mm<br><b>Min:</b> {forkMin:.2f} mm<br><b>Mean:</b> {forkMean:.2f} mm</p>
    <h3>Fork Compression Differences:</h3>
    <ul>
    {''.join(f'<li>{item}</li>' for item in formatted_differences)}
    </ul>
    """,
    sizing_mode="stretch_width",
)

p.legend.click_policy = "hide"
# Combine plot and stats into a layout
layout = Column(p, stats_div, sizing_mode="stretch_both")

# Show the plot with stats
show(layout)
