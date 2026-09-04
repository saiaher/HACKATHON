"""
GovLENS - Database Layer
SQLite persistence for the real MPLAD dataset, investigation workflow,
and computed-risk cache. No random/fake data is ever written here.
"""

import os
import sqlite3
import pandas as pd
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mplad.db")
SEED_SQL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "seed_data.sql")

VALID_STATUSES = [
    "Detected",
    "Under Review",
    "Field Verification Required",
    "Resolved",
    "False Positive",
    "Escalated",
]


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(force_reseed: bool = False):
    """Create tables if they don't exist and seed projects from the real dataset.
    Investigation history is NEVER wiped on normal startup."""
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS raw_projects (
            Project_ID TEXT PRIMARY KEY,
            Member_of_Parliament TEXT,
            State_District TEXT,
            Project_Type TEXT,
            Sanctioned_Amount REAL,
            Released_Amount REAL,
            Expenditure REAL,
            Start_Date TEXT,
            Completion_Date TEXT,
            Contractor TEXT,
            GPS_Location TEXT,
            Project_Status TEXT,
            Project_Images TEXT
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS investigations (
            project_id TEXT PRIMARY KEY,
            status TEXT DEFAULT 'Detected',
            notes TEXT DEFAULT '',
            updated_at TEXT
        )
    """)

    conn.commit()

    cur.execute("SELECT COUNT(*) AS c FROM raw_projects")
    count = cur.fetchone()["c"]

    if count == 0 or force_reseed:
        if force_reseed:
            cur.execute("DELETE FROM raw_projects")
        with open(SEED_SQL_PATH, "r", encoding="utf-8") as f:
            seed_sql = f.read()
        cur.executescript(seed_sql)
        conn.commit()

    conn.close()


def reload_from_dataset():
    """Used by the 'Refresh Data' button. Reloads the real dataset from
    seed_data.sql into SQLite. Does NOT generate any random data and does
    NOT touch investigation history."""
    init_db(force_reseed=True)


def _safe_float(v, default=0.0):
    try:
        if v is None or v == "":
            return default
        return float(v)
    except (ValueError, TypeError):
        return default


def _parse_gps(gps_str):
    try:
        lat_str, lon_str = str(gps_str).split(",")
        return float(lat_str.strip()), float(lon_str.strip())
    except (ValueError, AttributeError):
        return None, None


def _parse_date(date_str):
    try:
        return pd.to_datetime(date_str)
    except (ValueError, TypeError):
        return pd.NaT


def load_projects_df() -> pd.DataFrame:
    """Load and normalize the dataset from SQLite into a DataFrame the
    rest of the app can use. Missing/invalid fields are handled safely
    and never fabricated."""
    conn = get_connection()
    raw = pd.read_sql_query("SELECT * FROM raw_projects ORDER BY Project_ID", conn)
    conn.close()

    if raw.empty:
        return pd.DataFrame()

    rows = []
    for _, r in raw.iterrows():
        district, _, state = (r["State_District"] or "Data not available, Data not available").partition(",")
        district = district.strip() or "Data not available"
        state = state.strip() or "Data not available"

        sanctioned = _safe_float(r["Sanctioned_Amount"])
        released = _safe_float(r["Released_Amount"])
        expenditure = _safe_float(r["Expenditure"])

        start_date = _parse_date(r["Start_Date"])
        completion_date = _parse_date(r["Completion_Date"])

        lat, lon = _parse_gps(r["GPS_Location"])

        status = (r["Project_Status"] or "Data not available").strip() or "Data not available"

        image_url = (r["Project_Images"] or "").strip()
        if not image_url.lower().startswith("http"):
            image_url = ""

        released_pct = round((released / sanctioned * 100), 1) if sanctioned > 0 else 0.0
        expenditure_pct = round((expenditure / released * 100), 1) if released > 0 else 0.0
        expenditure_pct_of_sanctioned = round((expenditure / sanctioned * 100), 1) if sanctioned > 0 else 0.0

        now = pd.Timestamp.now()
        total_duration_days = (completion_date - start_date).days if pd.notna(start_date) and pd.notna(completion_date) else None
        elapsed_days = (now - start_date).days if pd.notna(start_date) else None

        # Physical completion % is NOT present in the dataset. We derive a
        # transparent, deterministic TIME-BASED ESTIMATE (elapsed / total
        # duration), clearly labeled as an estimate everywhere it's shown.
        if status == "Completed":
            est_completion = 100.0
        elif total_duration_days and total_duration_days > 0 and elapsed_days is not None:
            est_completion = round(max(0.0, min(100.0, (elapsed_days / total_duration_days) * 100)), 1)
        else:
            est_completion = 0.0

        delay_days = max(0, (elapsed_days - total_duration_days)) if (
            elapsed_days is not None and total_duration_days is not None and status != "Completed"
        ) else 0

        rows.append({
            "project_id": r["Project_ID"],
            "mp_name": r["Member_of_Parliament"] or "Data not available",
            "district": district,
            "state": state,
            "project_type": r["Project_Type"] or "Data not available",
            "sanctioned_amount": sanctioned,
            "released_amount": released,
            "expenditure": expenditure,
            "released_pct": released_pct,
            "expenditure_pct": expenditure_pct,
            "expenditure_pct_of_sanctioned": expenditure_pct_of_sanctioned,
            "start_date": start_date,
            "completion_date": completion_date,
            "contractor": r["Contractor"] or "Data not available",
            "gps_lat": lat,
            "gps_lon": lon,
            "status": status,
            "image_url": image_url,
            "est_completion_pct": est_completion,
            "total_duration_days": total_duration_days,
            "elapsed_days": elapsed_days,
            "delay_days": delay_days,
        })

    return pd.DataFrame(rows)


def get_investigation_status(project_id: str) -> dict:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT status, notes, updated_at FROM investigations WHERE project_id = ?", (project_id,))
    row = cur.fetchone()
    conn.close()
    if row:
        return {"status": row["status"], "notes": row["notes"], "updated_at": row["updated_at"]}
    return {"status": "Detected", "notes": "", "updated_at": None}


def get_all_investigation_status() -> dict:
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT project_id, status, notes, updated_at FROM investigations")
    rows = cur.fetchall()
    conn.close()
    return {r["project_id"]: {"status": r["status"], "notes": r["notes"], "updated_at": r["updated_at"]} for r in rows}


def set_investigation_status(project_id: str, status: str, notes: str = ""):
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO investigations (project_id, status, notes, updated_at)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(project_id) DO UPDATE SET
            status=excluded.status, notes=excluded.notes, updated_at=excluded.updated_at
    """, (project_id, status, notes, datetime.now().isoformat(timespec="seconds")))
    conn.commit()
    conn.close()
