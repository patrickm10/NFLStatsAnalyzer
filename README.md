# NFLStatsAnalyzer

# Overview
NFLStatsAnalyzer is a high-performance Python tool for scraping, analyzing, and ranking NFL player statistics for fantasy football insights or personal data analysis. It is currently being refactored to use **Polars** for faster processing and improved scalability. The backend connects to a React web application and will soon be deployed to a public website.

# Features

## React Frontend
- A React-based web interface displays rankings and player statistics in real-time.
- Built for user-friendly exploration, with live updates and filtering in future iterations.

## High-Performance Data Processing
- Refactored to use Polars (instead of pandas) for increased speed and efficiency.
- Handles data quality issues such as duplicate headers, malformed columns, and inconsistent rows.

## Comprehensive Scraping and Stats
- Supports all major positions: QB, RB, WR, TE, K.
- Scrapes weekly and seasonal data from FantasyPros.
- Tracks fantasy-relevant metrics like yards, touchdowns, INTs, FPTS/G, and more.
- Weekly stats saved under folders like `qb_weekly_stats`, `rb_weekly_stats`, etc.

## Export and Storage
- Saves cleaned and ranked data into CSV files.
- Organized by position, year, and week for easy access.

## Modular Data Pipeline
- Designed for composability and reliability.
- Weekly and seasonal scraping functions separated by module.
- Plans to integrate with orchestration tools like Dagster.

# Prerequisites
- Python 3.8 or higher
- Node.js for React frontend

# Required Libraries
- requests  
- beautifulsoup4  
- polars  
- react  
- npm  

# Installation
pip install -r requirements.txt
python nfl_stats_analyzer.py

# Launch React App
cd frontend
npm install
npm start

## File Structure

```text
NFLStatsAnalyzer/
├── README.md
├── requirements.txt
├── data/
│   ├── qb_weekly_stats/
│   ├── rb_weekly_stats/
│   ├── wr_weekly_stats/
│   ├── nfl_metadata/
├── Scripts/
│   ├── offensive_stats_parser.py
│   ├── defensive_stats_parser.py
│   ├── GUI.py
├── Pipelines/
│   ├── get_nfl_schedule.py
│   ├── get_weekly_stats.py
│   ├── get_offensive_rankings.py
│   ├── get_defensive_rankings.py
├── SeasonStats/
│   ├── getRosterPerTeam.py
│   ├── get_career_stats.py
├── Analytics/
│   ├── offensive_stats_parser.py
│   ├── chatbot.py
│   ├── nlp_model.py (in progress)
```

