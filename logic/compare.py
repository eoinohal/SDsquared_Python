# compare.py
# Compares fork and shock recordings separately from two runs using displacement graph and scatter plot from bokeh

from bokeh.io import curdoc
from bokeh.layouts import grid, row, column
from bokeh.models import Div, FileInput, Dropdown, Paragraph
from plot_functions import decomposed_displacement_plot, decomposed_regression_plot
from data_processing import load_and_process_data, process_bike_data, fork_displacement_values, shock_displacement_values, fork_compression_values, fork_rebound_values, shock_compression_values, shock_rebound_values
import base64
import os

# Default files
current_file1 = "../data/run_data/testrun1.txt"
current_file2 = "../data/run_data/testrun2.txt"
current_bike_file = "../data/bike_profiles/wills_megatower.txt"

# Main function
def main(text_file1, text_file2, bike_file):
    global current_file1, current_file2
    current_file1 = text_file1
    current_file2 = text_file2
    curdoc().clear()

    bike_data = process_bike_data(bike_file)

    # Load and process data for both files
    data1 = load_and_process_data(text_file1, bike_data)
    data2 = load_and_process_data(text_file2, bike_data)

    if data1 is not None and data2 is not None:
        # Create fork plots
        fork_displacement_graph = decomposed_displacement_plot(fork_displacement_values(data1, data2, text_file1, text_file2))
        fork_comp_graph = decomposed_regression_plot(fork_compression_values(data1, data2, text_file1, text_file2))
        fork_reb_graph = decomposed_regression_plot(fork_rebound_values(data1, data2, text_file1, text_file2))

        # Create shock plots
        shock_displacement_graph = decomposed_displacement_plot(shock_displacement_values(data1, data2, text_file1, text_file2))
        shock_comp_graph = decomposed_regression_plot(shock_compression_values(data1, data2, text_file1, text_file2))
        shock_reb_graph = decomposed_regression_plot(shock_rebound_values(data1, data2, text_file1, text_file2))

        # Configure graphs
        for graph in [fork_displacement_graph, fork_comp_graph, fork_reb_graph, shock_displacement_graph,
                      shock_comp_graph, shock_reb_graph]:
            graph.toolbar.logo = None
            graph.legend.click_policy = "hide"

        # Create headers and subheadings
        head = Div(text="<h1 style='font-size:40px;'>Comparison of Accelerometer Data</h1>")
        fork_subheading = Div(text="<h2 style='font-size:30px;'>Fork Values</h2>")
        shock_subheading = Div(text="<h2 style='font-size:30px;'>Shock Values</h2>")
        displacement_subsubheading1 = Div(text="<h3 style='font-size:25px;'>Displacement Plot</h3>")
        regression_subsubheading1 = Div(text="<h3 style='font-size:25px;'>Regression Lines</h3>")
        displacement_subsubheading2 = Div(text="<h3 style='font-size:25px;'>Displacement Plot</h3>")
        regression_subsubheading2 = Div(text="<h3 style='font-size:25px;'>Regression Lines</h3>")

        # Create dashboard layout
        dashboard_layout = column(
            head,
            top_select_layout,
            fork_subheading,
            displacement_subsubheading1,
            fork_displacement_graph,
            regression_subsubheading1,
            row(fork_comp_graph, fork_reb_graph, sizing_mode='stretch_width'),
            shock_subheading,
            displacement_subsubheading2,
            shock_displacement_graph,
            regression_subsubheading2,
            row(shock_comp_graph, shock_reb_graph, sizing_mode='stretch_width'),
            sizing_mode="stretch_both"
        )

        layout = column(dashboard_layout, sizing_mode="stretch_both")
    else:
        layout = column(top_select_layout, sizing_mode="stretch_both")

    # Set theme and display
    curdoc().theme = "dark_minimal"
    curdoc().clear()
    curdoc().add_root(layout)

# File selection dropdowns
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
dropdown2 = Dropdown(label="Select file 2", menu=txt_files)

def file1_selected(event):
    global current_file1
    current_file1 = folder_path + "/" + event.item
    main(current_file1, current_file2, current_bike_file)

def file2_selected(event):
    global current_file2
    current_file2 = folder_path + "/" + event.item
    main(current_file1, current_file2, current_bike_file)

def bike_selected(event):
    main(current_file1, current_file2, bike_folder_path+"/"+event.item)

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
    main(current_file1, current_file2, current_bike_file)

def upload_callback2(attr, old, new):
    global current_file2
    decoded = base64.b64decode(new)
    file_content = decoded.decode("utf-8")
    temp_file_path = "run_data/uploaded_file2.txt"
    with open(temp_file_path, "w", newline="") as f:
        f.write(file_content)
    current_file2 = temp_file_path
    main(current_file1, current_file2, current_bike_file)

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