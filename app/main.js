const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');
const { spawn } = require('child_process');

let pythonProcess;

app.whenReady().then(() => {
    // Start the Python script
    const projectRoot = path.resolve(__dirname, '..');
    const scriptPath = path.join(projectRoot, 'logic', 'telemetry', 'multi_runs.py');
    pythonProcess = spawn('python', [scriptPath], { stdio: 'inherit' });

    // Create the Electron BrowserWindow
    let win = new BrowserWindow({
        width: 1200,
        height: 700,
        autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: true,
            contextIsolation: false
        }
    });
    win.loadFile(path.join(__dirname, 'dashboard.html'));

    // Loading data into dashboard from data dir
    win.webContents.on('did-finish-load', () => {
        const runDataPath = path.join(projectRoot, 'data', 'run_data');
        const bikeProfilesPath = path.join(projectRoot, 'data', 'bike_profiles');

        console.log('Attempting to auto-load Run Path:', runDataPath);
        console.log('Attempting to auto-load Rider Path:', bikeProfilesPath);

        win.webContents.send('auto-load-paths', {
            runPath: runDataPath,
            riderPath: bikeProfilesPath
        });
    });
});

// Shutdown app
app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') {
        if (pythonProcess) {
            pythonProcess.kill();
        }
        app.quit();
    }
});
