import tkinter as tk
from tkinter import ttk
import pandas as pd


NFL_Teams = ["Patriots","Bills","Dolphins","Jets""Steelers", "Ravens", "Bengals", "Browns","Texans", "Colts", "Jaguars","Titans","Cheifs", "Chargers", "Broncos", "Raiders","Eagles", "Commanders", "Cowboys", "Giants","Lions", "Vikings","Packers","Bears","Buccaneers", "Falcons","Saints","Panthers","Rams", "Seahawks", "Cardinals","49ers"]
AFC_East = ["Patriots","Bills","Dolphins","Jets"]
AFC_North = ["Steelers", "Ravens", "Bengals", "Browns"]
AFC_South = ["Texans", "Colts", "Jaguars","Titans"]
AFC_West = ["Cheifs", "Chargers", "Broncos", "Raiders"]
NFC_East = ["Eagles", "Commanders", "Cowboys", "Giants"]
NFC_North = ["Lions", "Vikings","Packers","Bears"]
NFC_South = ["Buccaneers", "Falcons","Saints","Panthers"]
NFC_West = ["Rams", "Seahawks", "Cardinals","49ers"]


#display_data("official_qb_stats.csv", qb_frame)  # Replace with actual file paths
#display_data("official_rb_stats.csv", rb_frame)  # Replace with actual file paths
#display_data("official_wr_stats.csv", wr_frame)  # Replace with actual file paths
#display_data("official_kicker_stats.csv", kicker_frame)  # Replace with actual file paths

# Function to create a Treeview for displaying CSV data
def display_data(csv_file, parent_frame):
    # Load the CSV file into a pandas DataFrame
    df = pd.read_csv(csv_file)

    # Create a Treeview widget to display the DataFrame
    tree = ttk.Treeview(parent_frame)

    # Define the columns of the Treeview based on the DataFrame columns
    tree["columns"] = list(df.columns)

    # Format the columns
    tree.column("#0", width=0, stretch=tk.NO)  # Hide the default column
    for col in df.columns:
        tree.heading(col, text=col)  # Set column headers
        tree.column(col, width=100)  # Set column width

    # Insert data into the Treeview
    for index, row in df.iterrows():
        tree.insert("", "end", values=list(row))

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

# Create the main window
window = tk.Tk()
window.title("NFL Player Stats")

# Set the dimensions of the window
window.geometry("800x600")

# Create a Notebook widget for tabs
notebook = ttk.Notebook(window)

# Create frames for each position
qb_frame = ttk.Frame(notebook)
rb_frame = ttk.Frame(notebook)
wr_frame = ttk.Frame(notebook)
kicker_frame = ttk.Frame(notebook)
defense_frame = ttk.Frame(notebook)

# Add tabs to the Notebook
notebook.add(qb_frame, text="Quarterbacks")
notebook.add(rb_frame, text="Running Backs")
notebook.add(wr_frame, text="Wide Receivers")
notebook.add(kicker_frame, text="Kickers")
notebook.add(defense_frame, text="Defense")

# Display data in each tab
display_data("official_qb_stats.csv", qb_frame)  # Replace with actual file paths
display_data("official_rb_stats.csv", rb_frame)  # Replace with actual file paths
display_data("official_wr_stats.csv", wr_frame)  # Replace with actual file paths
display_data("official_kicker_stats.csv", kicker_frame)  # Replace with actual file paths
display_data("official_defense_stats.csv", defense_frame)  # Replace with actual file paths

# Pack the Notebook widget to expand and fill the window
notebook.pack(expand=True, fill=tk.BOTH)

# Start the Tkinter event loop
window.mainloop()
