## Frontend

Run <b>electron main.js</b> to generate electron application

For frontend only, run <b>dashboard.html</b>

# Backend

## Use: 

### Command to start the single run system:
python -m bokeh serve --show single_run.py

### Command to start the multi run system:
python -m bokeh serve --show multi_runs.py

### Command to stop servers
CTRL+C


## Documentation:
main.js runs electron app, starting backend and frontend up to generate app\
dashboard and styles make up the interface to select riders\
Select runs, comment toggle, Select rider\
Generates and sends JSON to backend using POST

### Frontend Components

**File Manager Panel**
- Run selection with hierarchical file tree
- Rider profile selection section
- Toggle visibility and comments for individual runs
- Resizable panel interface

**Visualization Area**
- Bokeh server integration for data visualization
- Real-time updates based on selections
- Fallback messaging system

### Key Functions

**updateVisualization**
- Sends selected run files and rider profile to Bokeh server
- Displays fallback text if no runs or rider are selected
- Handles server communication errors

**getDirectoryEntriesFromPathAsync**
- Reads folders and files using Node.js fs (Electron environments)
- Supports auto-upload of run and rider files

**loadRunDirectoryFromPath**
- Loads root run directory and populates file tree
- Handles directory structure parsing

**loadRiderProfilesFromPath**
- Scans folder for .txt rider profiles
- Enables single selection of rider profiles

**buildFileTreeFromEntries / buildFileTreeWithHandle**
- Recursively creates folder and file tree structure in DOM
- Supports file selection and comment toggling
- Handles both Electron and browser file systems

**loadDirectory**
- Loads folders using browser's directory picker API
- Fallback for manual directory selection

**Panel Resizing**
- Drag divider to adjust file manager and dashboard areas
- Maintains minimum width constraints

**Electron Integration**
- Autoloads preset paths from main process via ipcRenderer (run and rider)
- Loads backend and frontend into application