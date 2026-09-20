import pandas as pd
from src.db import get_connection

KEEP_COLUMNS = [
    "SEASON_YEAR", "PLAYER_ID", "PLAYER_NAME", "TEAM_ID", "TEAM_ABBREVIATION",
    "GAME_ID", "GAME_DATE", "MATCHUP", "WL", "MIN",
    "FGM", "FGA", "FG3M", "FG3A", "FTM", "FTA",
    "OREB", "DREB", "REB", "AST", "TOV", "STL", "BLK", "PF", "PTS", "PLUS_MINUS",
]


def parse_matchup(matchup):
    """'LAL vs. BOS' -> ('BOS', 1);  'LAL @ BOS' -> ('BOS', 0)."""
    if " vs. " in matchup:
        return matchup.split(" vs. ")[1].strip(), 1
    if " @ " in matchup:
        return matchup.split(" @ ")[1].strip(), 0
    return None, None


def clean_game_logs(df):
    df = df[KEEP_COLUMNS].copy()

    df["GAME_DATE"] = pd.to_datetime(df["GAME_DATE"]).dt.date.astype(str)

    parsed = df["MATCHUP"].apply(parse_matchup)
    df["OPPONENT"] = [p[0] for p in parsed]
    df["IS_HOME"] = [p[1] for p in parsed]

    df["WIN"] = (df["WL"] == "W").astype(int)
    df = df.drop(columns=["MATCHUP", "WL"])

    df = df.sort_values(["PLAYER_ID", "GAME_DATE"]).reset_index(drop=True)
    return df


def build_clean_table():
    with get_connection() as conn:
        raw = pd.read_sql("SELECT * FROM raw_player_game_logs", conn)
        clean = clean_game_logs(raw)
        clean.to_sql("clean_player_game_logs", conn,
                     if_exists="replace", index=False)
    return len(clean)