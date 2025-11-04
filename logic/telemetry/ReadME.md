# Backend

## Use: 

### Command to start the single run system:
python -m bokeh serve --show single_run.py

### Command to start the multi run system:
python -m bokeh serve --show multi_runs.py

### Command to stop servers
CTRL+C


## Documentation:
Data is taken from data folder, either run data or bike profiles\
Selected JSON is passed to backend using POST
JSON: {rider_profile_name, (list_of_runs, boolean_comment_value)}
### Run data:
Run data is csv format containing samples taken from an accelerometer recorded by microcontroller.

#### Header:
Line 1: Comment \
Line 2: Shorthand name: Sampling frequency: Longhand name \
Line 3: Shock starting displacement, Fork starting displacement, Rear brake starting value (unused), Front 2 starting value (unused) 

#### Footer:
Length of run in ms \
Message: Run finished

#### Data:
Lines 1-5: Accelerometer axis measurements - Forces in other axis \
Line 6: Shock accelerometer recording \
Line 7: Fork accelerometer recording \
Lines 8-9: Unused braking measurements.

#### Interpreting the data:
The accelerometer records a value at the sample frequency in the range 0(fully extended)-1024(fully compressed)\
This is based on the displacement measured by the accelerometer\
This value can be converted to a % displacement measurement using data from bike profile \
As shock and fork lengths vary and the accelerometer measurement length is constant,\
the measured value must be set against the range of values that can be measured by the fork/shock
e.g. (For a 160mm shock, accelerometer might go to only 800, therefore for true % displacement, max value used needs to be changed.)

### Scripts explained:

#### run_processing 
Data is read and processed. Returning a dictionary of values along (key - name).
process_accelerometer_file: reads file
get_line_data: Uses turning_points to find all turning points in data,\ then generates a list of the compression and rebound zones, and overall regression of these groups using get_compression_and_rebound.

#### graph_dictionaries 
Data has to be organised from the dictionary into a format ready to be plotted\
This is done to keep graph parameter setup and graph generation separate\
load_and_process_data and process_bike_data takes data from run_processing\
displacement_values assigns parameters in a dictionary for the displacement graph\
regression_values assigns parameters in a dictionary for the regression graph

#### multi_runs
Runs a bokeh server serving bokeh graphs on a page using WebSocket to update graphs\
UpdateHandler receives frontend POST request (JSON of runs, comment boolean value and rider profile)\
safe_update takes JSON, loads and processes data and creates plots and layout\
Uses scripts to generate dict from graph_dictionaries filling in values for each graph\
create_stats_table generates a table from dict of values, to show changes in data between runs\
value_to_color is used for color highlighting to show data spread\

#### single_run
A simpler version of generate_dashboard as it just displays 1 run,\
therefore does not include updates or multi run plots\
Uses data from graph_dictionaries and plots using bokeh (skips using dict layout at graphs are not repeated)\
Not used in the Telemetry Dashboard\
Test plotting a run by changing current_data_file and current_bike_file.
