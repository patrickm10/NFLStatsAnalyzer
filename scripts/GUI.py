import tkinter as tk
from tkinter import ttk
import pandas as pd

# NFL Teams and Divisions
NFL_Teams = ["Patriots", "Bills", "Dolphins", "Jets", "Steelers", "Ravens", "Bengals", "Browns",
             "Texans", "Colts", "Jaguars", "Titans", "Chiefs", "Chargers", "Broncos", "Raiders",
             "Eagles", "Commanders", "Cowboys", "Giants", "Lions", "Vikings", "Packers", "Bears",
             "Buccaneers", "Falcons", "Saints", "Panthers", "Rams", "Seahawks", "Cardinals", "49ers"]

AFC_East = ["Patriots", "Bills", "Dolphins", "Jets"]
AFC_North = ["Steelers", "Ravens", "Bengals", "Browns"]
AFC_South = ["Texans", "Colts", "Jaguars", "Titans"]
AFC_West = ["Chiefs", "Chargers", "Broncos", "Raiders"]
NFC_East = ["Eagles", "Commanders", "Cowboys", "Giants"]
NFC_North = ["Lions", "Vikings", "Packers", "Bears"]
NFC_South = ["Buccaneers", "Falcons", "Saints", "Panthers"]
NFC_West = ["Rams", "Seahawks", "Cardinals", "49ers"]


# Function to calculate a color based on value
def calculate_color(value, min_value, max_value):
    if pd.isna(value) or max_value == min_value:
        return "#FFFFFF"  # Default to white for invalid or uniform values

    normalized = (value - min_value) / (max_value - min_value)
    red = int(255 * (1 - normalized))
    green = int(255 * normalized)
    blue = 0
    return f"#{red:02x}{green:02x}{blue:02x}"

# Function to create a Treeview for displaying CSV data with sortable columns and color scaling
def display_data(csv_file, parent_frame, colorscalevar):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)
    original_df = df.copy()  # Save the original order for resetting

    # Create a Treeview widget to display the DataFrame
    tree = ttk.Treeview(parent_frame)

    # Define the columns of the Treeview based on the DataFrame columns
    tree["columns"] = list(df.columns)

    # Track the sorting state of each column
    sort_states = {col: None for col in df.columns}  # None, "asc", "desc"

    # Function to apply color scale
    def apply_color_scale():
        if colorscalevar.get():  # Check if color scale is enabled
            for col in df.columns:
                if pd.api.types.is_numeric_dtype(df[col]):
                    col_min, col_max = df[col].min(), df[col].max()
                    col_range = col_max - col_min if col_max != col_min else 1  # Avoid division by zero

                    for iid, row in zip(tree.get_children(), df.itertuples(index=False, name=None)):
                        # Use column index to fetch the value
                        value = row[df.columns.get_loc(col)]
                        if pd.notna(value):
                            # Calculate green-to-red scale (0 is red, 1 is green)
                            scale = (value - col_min) / col_range
                            red = int((1 - scale) * 255)
                            green = int(scale * 255)
                            color = f"#{red:02x}{green:02x}00"
                            tree.tag_configure(f"{col}_{iid}", background=color)
                            tree.item(iid, tags=(f"{col}_{iid}",))
        else:
            # Remove color scale if toggle is off
            for iid in tree.get_children():
                tree.tag_configure(iid, background="white")
                tree.item(iid, tags="")  # Remove any tags

    # Function to handle column sorting
    def sort_column(col):
        nonlocal df
        if sort_states[col] is None or sort_states[col] == "desc":
            # Sort ascending
            df = df.sort_values(by=col, ascending=True)
            sort_states[col] = "asc"
        elif sort_states[col] == "asc":
            # Sort descending
            df = df.sort_values(by=col, ascending=False)
            sort_states[col] = "desc"
        else:
            # Reset to original order
            df = original_df.copy()
            sort_states[col] = None

        # Clear and repopulate the Treeview
        tree.delete(*tree.get_children())
        for index, row in df.iterrows():
            tree.insert("", "end", values=list(row))

        # Reapply color scale after sorting
        apply_color_scale()

    # Format the columns
    tree.column("#0", width=0, stretch=tk.NO)  # Hide the default column
    for col in df.columns:
        tree.heading(col, text=col, command=lambda c=col: sort_column(c))  # Bind header click
        tree.column(col, width=100)  # Set column width

    # Insert data into the Treeview
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

    # Apply the color scale initially
    apply_color_scale()

    # Add vertical scrollbar
    vsb = ttk.Scrollbar(parent_frame, orient="vertical", command=tree.yview)
    vsb.pack(side="right", fill="y")
    tree.configure(yscrollcommand=vsb.set)

    # Add horizontal scrollbar
    hsb = ttk.Scrollbar(parent_frame, orient="horizontal", command=tree.xview)
    hsb.pack(side="bottom", fill="x")
    tree.configure(xscrollcommand=hsb.set)

    # Pack the Treeview widget
    tree.pack(expand=True, fill=tk.BOTH)

    # Return the Treeview widget and the apply_color_scale function for future updates
    return tree, apply_color_scale

# Create the main window
window = tk.Tk()
window.title("NFL Player Stats")

# Set the dimensions of the window
window.geometry("800x600")

# Create a BooleanVar for the color scale toggle
colorscalevar = tk.BooleanVar(value=True)  # Default to True (color scale on)

# Create a toggle button for the color scale
color_scale_toggle = ttk.Checkbutton(window, text="Toggle Dynamic Ratings", variable=colorscalevar)
color_scale_toggle.pack()

# Create a Notebook widget for tabs
notebook = ttk.Notebook(window)

# Create frames for each position
qb_frame = ttk.Frame(notebook)
rb_frame = ttk.Frame(notebook)
wr_frame = ttk.Frame(notebook)
kicker_frame = ttk.Frame(notebook)
defense_frame = ttk.Frame(notebook)
schedule_frame = ttk.Frame(notebook)

# Add tabs to the Notebook
notebook.add(qb_frame, text="Quarterbacks")
notebook.add(rb_frame, text="Running Backs")
notebook.add(wr_frame, text="Wide Receivers")
notebook.add(kicker_frame, text="Kickers")
notebook.add(defense_frame, text="Defense")
notebook.add(schedule_frame, text="Schedule")

# Display data in each frame and get the apply_color_scale function
tree_qb, apply_color_scale_qb = display_data("official_qb_stats.csv", qb_frame, colorscalevar)  # Replace with actual file paths
tree_rb, apply_color_scale_rb = display_data("official_rb_stats.csv", rb_frame, colorscalevar)  # Replace with actual file paths
tree_wr, apply_color_scale_wr = display_data("official_wr_stats.csv", wr_frame, colorscalevar)  # Replace with actual file paths
tree_kicker, apply_color_scale_kicker = display_data("official_kicker_stats.csv", kicker_frame, colorscalevar)  # Replace with actual file paths
tree_defense, apply_color_scale_defense = display_data("official_defense_stats.csv", defense_frame, colorscalevar)  # Replace with actual file paths
tree_defense, apply_color_scale_defense = display_data("schedule.csv", schedule_frame, colorscalevar)  # Replace with actual file paths

# Add trace to colorscalevar to update the color scale when the toggle is changed
def update_color_scale(*args):
    # Reapply the color scale whenever the toggle is changed
    if colorscalevar.get():
        apply_color_scale_qb()
        apply_color_scale_rb()
        apply_color_scale_wr()
        apply_color_scale_kicker()
        apply_color_scale_defense()
    else:
        # Remove color scale if toggle is off
        apply_color_scale_qb()
        apply_color_scale_rb()
        apply_color_scale_wr()
        apply_color_scale_kicker()
        apply_color_scale_defense()

colorscalevar.trace_add("write", update_color_scale)

# Pack the Notebook widget to expand and fill the window
notebook.pack(expand=True, fill=tk.BOTH)

# Start the Tkinter event loop
window.mainloop()
