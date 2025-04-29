from flask import Flask, request, jsonify
import subprocess
import sys
import psutil
import signal
import time

app = Flask(__name__)

bokeh_process = None


def kill_bokeh_server():
    """Kill any running Bokeh server processes."""
    global bokeh_process

    if bokeh_process is not None:
        try:
            print(f"Attempting to terminate tracked process {bokeh_process.pid}")
            bokeh_process.terminate()

        except Exception as e:
            print(f"Error terminating tracked process: {e}")
            try:
                print(f"Attempting to kill tracked process {bokeh_process.pid}")
                bokeh_process.kill()
            except Exception as e_kill:
                print(f"Error killing tracked process: {e_kill}")

        finally:
            bokeh_process = None
            print("Tracked process reference cleared.")


    print("Checking for other Bokeh processes...")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            cmdline = proc.info.get('cmdline')
            if cmdline and any('bokeh' in part.lower() for part in cmdline):
                 if proc.pid != app.pid and (bokeh_process is None or proc.pid != bokeh_process.pid): # Check against tracked pid if still exists
                    print(f"Found potential Bokeh process {proc.pid} ({proc.info.get('name')}), attempting terminate...")
                    proc.terminate()
                    print(f"Process {proc.pid} terminated.")

        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
        except Exception as e:
            print(f"Error processing process {proc.pid}: {e}")

    print("Bokeh process cleanup finished.")


@app.route('/update-selected-files', methods=['POST'])
def update_selected_files():
    global bokeh_process

    data = request.get_json()
    kill_bokeh_server()

    selected_files = data.get('selectedFiles', [])

    if len(selected_files) == 0:  # no files
        print('No files selected')
        return jsonify({
            "status": "success",
            "message": "No files selected, no Bokeh server started.",
            "bokeh_url": None
        })

    elif len(selected_files) == 1:  # single file
        selected_file = selected_files[0].get('fileName')
        if not selected_file:
            return jsonify({"status": "error", "message": "Invalid file data received"}), 400

        print('1 file selected:', selected_file)
        try:
            bokeh_process = subprocess.Popen(
                [sys.executable, "-m", "bokeh", "serve", "single_run.py", "--args", selected_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"Single file Bokeh server started with PID: {bokeh_process.pid}")
            time.sleep(1)
            return jsonify({
                "status": "success",
                "message": f"Bokeh server started for single file: {selected_file}",
                "bokeh_url": f"http://localhost:5006/single_run?_t={int(time.time())}"
            })
        except Exception as e:
            print(f"Error starting single file Bokeh server: {e}")
            return jsonify({"status": "error", "message": f"Failed to start Bokeh server: {e}"}), 500

    else:  # multi file
        file_names = ','.join(f.get('fileName') for f in selected_files if f.get('fileName'))
        if not file_names:
            return jsonify({"status": "error", "message": "No valid file names received for multiple files"}), 400

        print('Multiple files selected:', file_names)
        try:
            bokeh_process = subprocess.Popen(
                [sys.executable, "-m", "bokeh", "serve", "multi_runs.py", "--args", file_names],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print(f"Multi file Bokeh server started with PID: {bokeh_process.pid}")
            time.sleep(1)
            return jsonify({
                "status": "success",
                "message": f"Bokeh server started for multiple files: {file_names}",
                "bokeh_url": f"http://localhost:5006/multi_runs?_t={int(time.time())}"
            })
        except Exception as e:
            print(f"Error starting multi file Bokeh server: {e}")
            return jsonify({"status": "error", "message": f"Failed to start Bokeh server: {e}"}), 500

@app.route('/shutdown', methods=['POST'])
def shutdown():
    print("Shutdown requested.")
    kill_bokeh_server()
    return jsonify({"status": "success", "message": "Bokeh server shutdown attempted."})


if __name__ == '__main__':
    print("Starting Flask server on port 5000...")
    kill_bokeh_server()
    try:
        app.run(port=5000, debug=True)
    finally:
        print("Flask server shutting down, killing Bokeh server...")
        kill_bokeh_server()
