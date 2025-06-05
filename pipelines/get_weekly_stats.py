import os
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import logging

# Helper Functions
def _handle_duplicate_headers(headers):
    seen = {}
    result = []
    for h in headers:
        if h not in seen:
            seen[h] = 1
            result.append(h)
        else:
            seen[h] += 1
            result.append(f"{h}.{seen[h]}")
    return result

def _convert_numeric(df, cols):
    for col in cols:
        df[col] = pd.to_numeric(df.get(col, 0).replace(",", "", regex=True), errors="coerce").fillna(0)
    return df

def _rename_duplicate_stats(df, stat_map):
    for base_col, new_col in stat_map.items():
        matches = [col for col in df.columns if base_col in col]
        if len(matches) > 1:
            df.rename(columns={matches[1]: new_col}, inplace=True)
    return df

def _clean_name(name):
    """Remove content in parentheses and extra whitespace from a player name."""
    if not isinstance(name, str):
        return name
    name = re.sub(r"\s*\(.*?\)", "", name)  # Remove parentheses and their content
    return name.strip()

# Position Configurations
POSITION_CONFIG = {
    "qb": {
        "numeric_cols": ["CMP", "YDS", "TD", "Y/A", "INT", "FPTS/G", "FPTS", "R_YDS", "R_TD", "R_ATT"],
        "score_func": lambda df: (
            df["YDS"] * 0.4 + df["R_YDS"] * 0.1 + df["TD"] * 0.3 +
            df["Y/A"] * 0.2 - df["INT"] * 0.1 + df["FPTS/G"] * 0.4 +
            df["FPTS"] * 0.3 + df["CMP"] * 0.1 + df["R_TD"] * 0.2
        ),
        "top_n": 32,
        "handle_duplicates": True,
        "stat_renames": {"YDS": "R_YDS", "TD": "R_TD", "ATT": "R_ATT"}
    },
    "rb": {
        "numeric_cols": ["ATT", "YDS", "TD", "REC_YDS", "REC_TD", "Y/A", "FPTS/G", "FPTS", "FL", "REC"],
        "score_func": lambda df: (
            df["YDS"] * 0.45 + df["TD"] * 0.4 + df["Y/A"] * 0.15 +
            df["FPTS/G"] * 0.3 + df["FPTS"] * 0.2 + df["ATT"] * 0.1 -
            df["FL"] * 0.1 + df["REC"] * 0.1 + df.get("REC_YDS", 0) * 0.1 +
            df.get("REC_TD", 0) * 0.1
        ),
        "top_n": 32,
        "handle_duplicates": True,
        "stat_renames": {"YDS": "REC_YDS", "TD": "REC_TD"}
    },
    "wr": {
        "numeric_cols": ["REC", "YDS", "TD", "Y/R", "LG", "20+"],
        "score_func": lambda df: (
            df["REC"] * 0.35 + df["YDS"] * 0.25 + df["TD"] * 0.5 +
            df["Y/R"] * 0.15 + df["LG"] * 0.1 + df["20+"] * 0.1
        ),
        "top_n": 50,
        "handle_duplicates": False
    },
    "te": {
        "numeric_cols": ["REC", "YDS", "TD", "Y/R", "LG", "20+", "FPTS/G", "FPTS"],
        "score_func": lambda df: (
            df["REC"] * 0.35 + df["YDS"] * 0.25 + df["TD"] * 0.5 +
            df["Y/R"] * 0.15 + df["LG"] * 0.1 + df["20+"] * 0.1 +
            df["FPTS/G"] * 0.4 + df["FPTS"] * 0.3
        ),
        "top_n": 50,
        "handle_duplicates": False
    },
    "k": {
        "numeric_cols": ["FG", "FGA", "PCT", "1-19", "20-29", "30-39", "40-49", "50+", "FPTS/G", "FPTS"],
        "score_func": lambda df: (
            df["FG"] * 0.4 + df["FGA"] * 0.2 + df["PCT"] * 0.2 + df["1-19"] * 0.1 +
            df["20-29"] * 0.2 + df["30-39"] * 0.1 + df["40-49"] * 0.1 + df["50+"] * 0.1 +
            df["FPTS/G"] * 0.4 + df["FPTS"] * 0.3
        ),
        "top_n": 32,
        "handle_duplicates": False
    },
}

# Main Function
def find_best_players(position, year=None, week=None):
    if position not in POSITION_CONFIG:
        print(f"Position '{position}' not supported.")
        return None

    c = POSITION_CONFIG[position]
    folder = "career" if week is None else "weekly"
    os.makedirs(f"data/official_rankings/{folder}", exist_ok=True)

    base_url = f"https://www.fantasypros.com/nfl/stats/{position}.php?scoring=PPR"
    if week:
        base_url += f"&range=week&week={week}"
    else:
        base_url += f"&range=full"

    try:
        response = requests.get(base_url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")
        table = soup.find("table", {"class": "table"})
        if not table:
            print(f"No table found for {position} year {year} week {week}.")
            return None

        headers = [th.text.strip() for th in table.find("thead").find_all("th")]
        if c.get("handle_duplicates"):
            headers = _handle_duplicate_headers(headers)

        rows = [[td.text.strip() for td in tr.find_all("td")] for tr in table.find("tbody").find_all("tr")]
        if not rows:
            print(f"No player data found for {position} year {year} week {week}.")
            return None

        df = pd.DataFrame(rows, columns=headers)
        
        # Clean player names
        if "Player" in df.columns:
            df["Player"] = df["Player"].apply(_clean_name)
            
        if "stat_renames" in c:
            df = _rename_duplicate_stats(df, c["stat_renames"])

        if df.columns.tolist().count("YDS") > 1:
            df = df.loc[:, ~df.columns.duplicated()]
        if "YDS" in df.columns:
            df["YDS"] = df["YDS"].str.replace(",", "", regex=True)

        df = _convert_numeric(df, c["numeric_cols"])

        df["Score"] = c["score_func"](df)
        df["Rank"] = df["Score"].rank(ascending=False, method="min").astype(int)

        df = df.sort_values("Score", ascending=False).head(c["top_n"]).reset_index(drop=True)

        suffix = f"{position}_{year}_week{week}.csv" if week else f"{position}_{year}.csv"
        filename = f"data/official_rankings/{folder}/official_{suffix}"
        df.to_csv(filename, index=False)
        print(f"Saved {position.upper()} rankings to {filename}")

        return df

    except Exception as e:
        print(f"Error processing {position} year {year} week {week}: {e}")
        return None

if __name__ == "__main__":
    positions = ["qb", "rb", "wr", "te", "k"]
    year = 2025
    for pos in positions:
        find_best_players(pos, year)
        for week in range(1, 19):
            best_players = find_best_players(pos, year, week=week)
            print(f"Processed {pos.upper()} for year {year} week {week}")
            print(best_players.head(5) if best_players is not None else "No data found.")
