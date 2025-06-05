# NFLStatsAnalyzer

## Overview

**NFLStatsAnalyzer** is a high-performance NFL analytics platform built in Python that dynamically extracts player statistics from multiple NFL data sources, cleans and transforms them, and loads the results into a structured database for personal analysis or fantasy football insights.

Currently being refactored to use **Polars** for faster processing and scalable performance, the platform supports automated weekly and seasonal data collection through robust, modular pipelines. It connects to a **React** frontend and is being prepared for deployment to a public website.

The system emphasizes clean, composable data engineering practices—supporting easy extension, monitoring, and maintenance across seasons, formats, and data sources.

In addition, the collected statistics are being integrated into an **NLP-powered chatbot** that leverages the **OpenAI API** and **Langchain** to enable natural language querying and conversational analysis of NFL data, offering a seamless user experience for fans and analysts alike.


# Features

## React Frontend
- A React-based web interface displays rankings and player statistics in real-time.
- Built for user-friendly exploration, with live updates and filtering in future iterations.

## High-Performance Data Processing
- Refactored to use Polars (instead of pandas) for increased speed and efficiency.
- Handles data quality issues such as duplicate headers, malformed columns, and inconsistent rows.

## Comprehensive Scraping and Stats
- Supports all major positions: QB, RB, WR, TE, K, D/ST.
- Scrapes weekly and seasonal data from FantasyPros, NFL, and ESPN.
- Tracks fantasy-relevant metrics like yards, touchdowns, INTs, FPTS/G, and more.
- Weekly stats saved under folders like `qb_weekly_stats`, `rb_weekly_stats`, etc.

## Export and Storage
- Outputs cleaned and ranked player data as CSV files for easy integration with external tools.
- Stores datasets in **Google Wrangler**, enabling seamless analysis and querying.
- Files are systematically organized by position, season, and week for efficient retrieval and historical comparisons.

## Modular Data Pipelines
- Designed for composability and reliability.
- Weekly and seasonal scraping functions separated by module.
- Integrated with Google Composer to incorporate pipline orchestration

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
├── data/
│   ├── qb_weekly_stats/
│   ├── rb_weekly_stats/
│   ├── wr_weekly_stats/
│   ├── te_weekly_stats/
│   ├── official_stats/
│   |   ├── official_qb_stats.csv/
│   |   ├── official_rb_stats.csv/
│   |   ├── official_te_stats.csv/
│   |   ├── official_wr_stats.csv/
│   |   ├── official_k_stats.csv/
│   ├── nfl_metadata/
├── pipelines/
│   ├── get_nfl_schedule.py
│   ├── get_weekly_stats.py
│   ├── get_offensive_rankings.py
│   ├── get_defensive_rankings.py
├── frontend/
│   ├── src/
│   |    ├── App.jsx
│   |    ├── App.css
│   ├── public/
│   |    ├── package.json
├── season_scripts/
│   ├── get_adp_stats.py
│   ├── get_career_stats.py
│   ├── get_roster_per_team.py
├── analytics/
│   ├── chatbot.py
│   ├── draft_calculator.py
│   ├── nlp_model.py (in progress)
├── README.md
├── requirements.txt
```

