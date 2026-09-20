import sqlite3
import pandas as pd
from src import config

def get_connection():
    return sqlite3.connect(config.DB_PATH)

def insert_dataframe(df, table_name, conn):
    columns = ", ".join(df.columns)
    placeholders = ", ".join("?" for _ in df.columns)
    sql = f"INSERT OR IGNORE INTO {table_name} ({columns}) VALUES ({placeholders})"
    rows = df.astype(object).where(pd.notnull(df), None).values.tolist()
    cursor = conn.executemany(sql, rows)
    return cursor.rowcount