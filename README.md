# NFLStatsAnalyzer
## Overview
NFLStatsAnalyzer is a Python-based tool designed to scrape and analyze weekly NFL player statistics for fantasy football or personal analysis. It features a GUI built with Tkinter for ease of use, enabling you to retrieve, view, and save player stats effortlessly.

## Features
### User-Friendly GUI:
React Web Application where you can view the rankings and player statistics.

### Comprehensive Data Retrieval:
Scrapes stats for all NFL positional players, including QBs, RBs, WRs, and more.

Includes metrics like yards, touchdowns, and interceptions.

Weekly Stats stored in the [position]_weekly_stats folder in this repository.

### Data Export:
Saves the retrieved data in CSV format for analysis in external tools.

## Prerequisites
Python Version: Python 3.8 or higher.

## Required Libraries:
requests
beautifulsoup4
pandas
react

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

|— requirements.txt  

|— data/

|— qb_weekly_stats

|— rb_weekly_stats

|— wr_weekly_stats

|— nfl_metadata

|— Scripts/

|— offensive_stats_parser.py

|— defensive_stats_parser.py  

|— GUI.py

# Data Pipelines
get_schedule.py

get_scores.py

get_defensive_stats.py

get_offensive_stats.py


## Per Season
getRosterPerTeam.py

getSkillPlayerData.py

get_nfl_schedule.py

get_career_data.py

get_weekly_data.py

## Analytics
offensive_stats_parser.py

chatbot.py

NLP model (In progress)



## Future Enhancements
Top 5 most likely to score

Add playoff predictions


## GUI DESIGN

Best positional matchups

Easiest defensive matchups

Wide receiver vs cb

