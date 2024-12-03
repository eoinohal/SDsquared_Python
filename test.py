import numpy as np
from scipy.signal import find_peaks
from scipy.stats import linregress

#Returns arr1/arr2 as speed arr1 - arr2 as displacement
#compression(peaks,troughs)
#rebound(troughs,peaks)
def find_displacement_speed(arr1, arr2, arr1_times, arr2_times):
    arr_speeds = []
    arr_displacements = []

    for i in range(len(arr1)):
        displacement = abs(arr2[i] - arr1[i])
        if displacement > 0.25: # Remove vibrations
            speed = abs(displacement / (arr2_times[i] - arr1_times[i]))
            arr_speeds.append(speed); arr_displacements.append(displacement)
    return arr_speeds, arr_displacements

textFile = "TestRun1.TXT"

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

# np array for fork peak and trough
yForkValues = np.array(yForkValues, dtype=float)
forkPeaks, _ = find_peaks(yForkValues)
forkTroughs, _ = find_peaks(-yForkValues)
forkPeakTimes = xValues[forkPeaks]
forkTroughTimes = xValues[forkTroughs]

a = find_displacement_speed(forkPeaks,forkTroughs,forkPeakTimes,forkTroughTimes)
print(a[0])
print(a[1])

