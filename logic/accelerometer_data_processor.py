# accelerometer_data_processor.py
# Processes  accelerometer data, calculating key metrics like displacement, speed, and turning points then outputs formatted results for analysis

import os.path

def find_displacement_speed(arr1, arr2, arr1_times, arr2_times):
    # Uses gradient between turning points to find time, total displacement and speed of compression/rebound
    # compression = (peaks, troughs) and rebound = (troughs, peaks)
    times, speeds, displacements = [], [], []

    # Determine starting point in second array
    for i, value in enumerate(arr2_times):
        if value > arr1_times[0]:
            startIndex = i
            break

    itterations = min(len(arr1), len(arr2) - startIndex)

    for i in range(itterations):
        val1 = arr1[i]
        time1 = arr1_times[i]
        val2 = arr2[i + startIndex]
        time2 = arr2_times[i + startIndex]
        displacement = abs(val2 - val1)
        if displacement > 1:  # Filter out small displacements (vibrations)
            times.append(time1)
            speeds.append(abs(displacement / (time2 - time1)))
            displacements.append(displacement)

    return times, speeds, displacements


def turning_points(array, acceptance):
    # Returns all indexes of turning points in 1D array. Acceptance is the minimum change for turning point to be not considered vibration
    idx_max, idx_min = [], []

    NEUTRAL, RISING, FALLING = range(3)

    def get_state(a, b):
        if a > b and (a - b) > acceptance:
            return RISING
        if a < b and (b - a) > acceptance:
            return FALLING
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


def process_accelerometer_file(file, bike_data):
    # Main function to process file into dict of key values
    shock_min_value = bike_data[0]
    shock_max_value = bike_data[1]
    fork_min_value = bike_data[2]
    fork_max_value = bike_data[3]

    if not os.path.exists(file):
        print(f"File '{file}' not found")
        return None

    with open(file, "r") as f:
        lineCount = len(f.readlines()) - 4  # Discount header and footer

    with open(file, "r") as f:
        yShockValues, yForkValues = [], []
        f.readline()  # Skip header
        initialValues = f.readline().split(',')
        for accelerometerInstance in f:
            accelerometerList = accelerometerInstance.split(",")
            if len(accelerometerList) != 1:
                shock_value = float(accelerometerList[6])
                fork_value = float(accelerometerList[7])
                if shock_value >= 1024:
                    shock_value = 0
                if fork_value >= 1024:
                    fork_value = 0
                yShockValues.append(
                    ((shock_value - shock_min_value) / (shock_max_value - shock_min_value)) * 100
                )
                yForkValues.append(
                    ((fork_value - fork_min_value) / (fork_max_value - fork_min_value)) * 100
                )
            elif accelerometerInstance != 'Run finished\n':
                timeOfRun = int(accelerometerInstance) / 1000
    # Generate xValues without numpy
    xValues = [i * (timeOfRun / lineCount) for i in range(lineCount)]
    shock = get_line_data(xValues, yShockValues)
    fork = get_line_data(xValues, yForkValues)
    textData = format_data(shock[0], fork[0])

    return {
        "textData": ensure_non_empty(textData),
        "timeOfRun": ensure_non_empty(timeOfRun),
        "xValues": ensure_non_empty(xValues),
        "yForkValues": ensure_non_empty(yForkValues),
        "yShockValues": ensure_non_empty(yShockValues),
        "forkPeakTimes": ensure_non_empty(fork[1][0]),
        "forkPeaks": ensure_non_empty(fork[1][1]),
        "forkTroughTimes": ensure_non_empty(fork[1][2]),
        "forkTroughs": ensure_non_empty(fork[1][3]),
        "forkCompressionSpeed": ensure_non_empty(fork[2][0]),
        "forkCompressionDisplacement": ensure_non_empty(fork[2][1]),
        "forkCompression_regress": ensure_non_empty(fork[2][2]),
        "forkReboundSpeed": ensure_non_empty(fork[3][0]),
        "forkReboundDisplacement": ensure_non_empty(fork[3][1]),
        "forkRebound_regress": ensure_non_empty(fork[3][2]),
        "shockPeakTimes": ensure_non_empty(shock[1][0]),
        "shockPeaks": ensure_non_empty(shock[1][1]),
        "shockTroughTimes": ensure_non_empty(shock[1][2]),
        "shockTroughs": ensure_non_empty(shock[1][3]),
        "shockCompressionSpeed": ensure_non_empty(shock[2][0]),
        "shockCompressionDisplacement": ensure_non_empty(shock[2][1]),
        "shockCompression_regress": ensure_non_empty(shock[2][2]),
        "shockReboundSpeed": ensure_non_empty(shock[3][0]),
        "shockReboundDisplacement": ensure_non_empty(shock[3][1]),
        "shockRebound_regress": ensure_non_empty(shock[3][2]),
    }

def ensure_non_empty(value):
    """Returns value if it's non-empty; otherwise, returns [0]."""
    return value if value else [0]


def get_line_data(x, y):
    # Function processes individual line (fork and shock split)
    peakIndexes, _ = turning_points(y, 0.1)
    troughIndexes, _ = turning_points([-val for val in y], 0.1)
    peaks = [y[i] for i in peakIndexes]
    troughs = [y[i] for i in troughIndexes]
    peakTimes = [x[i] for i in peakIndexes]
    troughTimes = [x[i] for i in troughIndexes]

    compression = get_compression_and_rebound(troughs, peaks, troughTimes, peakTimes)
    rebound = get_compression_and_rebound(peaks, troughs, peakTimes, troughTimes)

    # Data for text, peaks and troughs, compression, rebound
    return [max(y), min(y), sum(y) / len(y), compression[0], rebound[0]], [peakTimes, peaks, troughTimes, troughs], \
    compression[1], rebound[1]


def get_compression_and_rebound(a, b, c, d):
    # Determines regression of turning points (once split into compression and rebound). Returns model for plot and variables for processing
    data = find_displacement_speed(a, b, c, d)
    times = data[0]
    speed = data[1]
    displacement = data[2]
    regressionModel = linear_regression(displacement, speed)
    regressionResult = [regressionModel[0] * x + regressionModel[1] for x in displacement]

    return regressionModel[0], [speed, displacement, regressionResult]


def linear_regression(x, y):
    # Determines linear regression of scatter
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_xx = sum(xi * xi for xi in x)

    try:
        denominator = (n * sum_xx - sum_x * sum_x)
        if denominator == 0:
            raise ZeroDivisionError("Denominator for slope calculation is zero. Check input values.")

        slope = (n * sum_xy - sum_x * sum_y) / denominator
        intercept = (sum_y - slope * sum_x) / n if n != 0 else float('nan')  # Avoid division by zero

    except ZeroDivisionError as e:
        print(f"Error: {e}")
        slope = float('nan')  # Assign NaN or a default value
        intercept = float('nan')
    except Exception as e:
        print(f"Unexpected error: {e}")
        slope = float('nan')
        intercept = float('nan')

    return slope, intercept


def format_data(shock, fork):
    # Formats key variables in clean way for text output
    text = "\n\t\t\tSHOCK:\t\tFORK:\n"
    names = ['Max:\t\t', 'Min:\t\t', 'Mean:\t\t', 'Comp:\t\t', 'Rebound:\t']

    for i in range(5):
        text += f"{names[i]}\t{round(shock[i], 2)}\t\t{round(fork[i], 2)}\n"

    text += f"\nCOMP DIFF:\t\t{round(fork[3] - shock[3], 2)}\nREBO DIFF:\t\t{round(fork[4] - shock[4], 2)}"

    return text


def main(file_name):
    result = process_accelerometer_file(file_name)
    print(result["textData"])


if __name__ == "__main__":
    main("data/run_data/testrun1.txt", "bike_profiles/full_range_values.txt")
