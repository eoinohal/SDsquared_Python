const { app, BrowserWindow } = require('electron');

app.whenReady().then(() => {
    let win = new BrowserWindow({
        width: 1200,
        height: 700,
        autoHideMenuBar: true,
        webPreferences: {
            nodeIntegration: true
        }
    });
    win.loadFile('dashboard.html');
});

app.on('window-all-closed', () => {
    if (process.platform !== 'darwin') app.quit();
});
