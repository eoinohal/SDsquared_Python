# single_run.py
# Generates fork/shock displacement graphs and speed displacement scatter plot with regression using bokeh

from bokeh.io import curdoc
from bokeh.layouts import grid, row, column
from bokeh.models import Div, FileInput, Dropdown, Paragraph
from plot_functions import decomposed_displacement_plot, decomposed_regression_plot
from data_processing import load_and_process_data, process_bike_data, displacement_values, compression_values, rebound_values
import base64
import os

# Default files
current_file1 = "../data/run_data/testrun1.txt"
current_file2 = "../data/run_data/testrun2.txt"
current_bike_file = "../data/bike_profiles/wills_megatower.txt"

# Main function
def main(text_file1, bike_file):
    global current_file1, current_file2
    current_file1 = text_file1
    curdoc().clear()

    bike_data = process_bike_data(bike_file)

    # Load and process data
    data1 = load_and_process_data(text_file1, bike_data)

    if data1 is not None:
        # Create plots
        displacement_graph = decomposed_displacement_plot(displacement_values(data1, text_file1, bike_file))
        comp_graph = decomposed_regression_plot(compression_values(data1, text_file1))
        reb_graph = decomposed_regression_plot(rebound_values(data1, text_file1))

        # Configure graphs
        for graph in [displacement_graph, comp_graph, reb_graph]:
            graph.toolbar.logo = None
            graph.legend.click_policy = "hide"

        # Create dashboard layout
        dashboard_layout = column(
            displacement_graph,
            row(comp_graph, reb_graph, sizing_mode='stretch_width'),
            sizing_mode="stretch_both"
        )

        layout = column(dashboard_layout, sizing_mode="stretch_both")
    else:
        layout = column(top_select_layout, sizing_mode="stretch_both")

    # Set theme and display
    curdoc().theme = "dark_minimal"
    curdoc().clear()
    curdoc().add_root(layout)

# File selection dropdown
folder_path = "../data/run_data"
if os.path.exists(folder_path):  # Check if folder exists
    txt_files = [(file, file) for file in os.listdir(folder_path) if file.lower().endswith(".txt")]
else:
    txt_files = []

bike_folder_path = "../data/bike_profiles"
if os.path.exists(bike_folder_path):  # Check if folder exists
    bike_txt_files = [(file, file) for file in os.listdir(bike_folder_path) if file.lower().endswith(".txt")]
else:
    bike_txt_files = []

bike_dropdown = Dropdown(label="Select a file", menu=bike_txt_files)

dropdown1 = Dropdown(label="Select file 1", menu=txt_files)

def file1_selected(event):
    global current_file1
    current_file1 = folder_path + "/" + event.item
    main(current_file1, current_bike_file)

def bike_selected(event):
    main(current_file1, bike_folder_path+"/"+event.item)

dropdown1.on_event("menu_item_click", file1_selected)
dropdown2.on_event("menu_item_click", file2_selected)

# File upload callbacks
def upload_callback1(attr, old, new):
    global current_file1
    decoded = base64.b64decode(new)
    file_content = decoded.decode("utf-8")
    temp_file_path = "run_data/uploaded_file1.txt"
    with open(temp_file_path, "w", newline="") as f:
        f.write(file_content)
    current_file1 = temp_file_path
    main(current_file1, current_bike_file)

file_input1 = FileInput(accept=".txt")
file_input1.on_change("value", upload_callback1)

file_input2 = FileInput(accept=".txt")
file_input2.on_change("value", upload_callback2)

bike_dropdown.on_event("menu_item_click", bike_selected)
bike_select_text = Paragraph(text="Select bike here: ")

# Layout
file1_select_text = Paragraph(text="Select file 1 here: ")
file2_select_text = Paragraph(text="Select file 2 here: ")

top_select_layout = row(file1_select_text, file_input1, dropdown1, file2_select_text, file_input2, dropdown2, bike_dropdown)

# Initialize the dashboard
main(current_file1, current_file2, current_bike_file)