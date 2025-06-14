from utils.file_loader import load_csv_data

def get_qb_top_rankings():
    try:
        df = load_csv_data("official_qb_stats.csv")
        df = df.sort("Score", descending=True)
        return df.to_dicts()
    except Exception as e:
        return {"error": str(e)}
