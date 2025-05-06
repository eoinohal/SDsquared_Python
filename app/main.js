// main.js
// Creates electron application and loads data into dashboard
const { app, BrowserWindow, ipcMain } = require('electron');
const path = require('path');

app.whenReady().then(() => {
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

        const projectRoot = path.resolve(__dirname, '..');

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
    if (process.platform !== 'darwin') app.quit();
});