# NFLStatsAnalyzer
## Overview
NFLStatsAnalyzer is a Python-based tool designed to scrape and analyze weekly NFL player statistics for fantasy football or personal analysis. It features a GUI built with Tkinter for ease of use, enabling you to retrieve, view, and save player stats effortlessly.

## Features
### User-Friendly GUI:
Built with Tkinter for seamless interaction.
Options to filter data by team, position, and week.

### Comprehensive Data Retrieval:
Scrapes stats for all NFL positional players, including QBs, RBs, WRs, and more.

Includes metrics like yards, touchdowns, and interceptions.

### Weekly Stats stored in the [position]_weekly_stats folder in this repository.

### Data Export:
Saves the retrieved data in CSV format for analysis in external tools.

## Prerequisites
Python Version: Python 3.8 or higher.

## Required Libraries:
requests
beautifulsoup4
pandas
tkinter (pre-installed with Python)

## Install dependencies:
pip install -r requirements.txt  
python nfl_stats_analyzer.py  

## Use the GUI:
python GUI.py

## Select filters like team, position, and week.
Click "Scrape Data" to retrieve player stats.

## Export Data:
Use the "Save to CSV" option to save the data for further analysis.

## File Structure
NFLStatsAnalyzer/  
|— README.md  
|— nfl_stats_analyzer.py  
|— requirements.txt  
|— data/  

## Future Enhancements
Add historical data scraping.

Introduce data visualization in the GUI.

Move csv files to the cloud.

Implement advanced filters and error handling.

Add more (Going to create a project based on these)
