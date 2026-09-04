"""
GovLENS - Fraud Detection Engine
Deterministic, explainable rule-based scoring (85 pts) combined with an
unsupervised ML anomaly contribution (15 pts) from Isolation Forest.
No random.random() is used anywhere in scoring.
"""

import numpy as np
import pandas as pd

try:
    from sklearn.ensemble import IsolationForest
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False

MIN_SIMILAR_FOR_COST_CHECK = 5
MIN_PROJECTS_FOR_ML = 15


# --------------------------------------------------------------------
# A. Financial Anomaly (25 pts)
# --------------------------------------------------------------------
def financial_anomaly(row):
    reasons = []
    score = 0
    released_pct = row["released_pct"]
    exp_pct_of_released = row["expenditure_pct"]

    if row["expenditure"] > row["released_amount"] > 0:
        score += 10
        reasons.append("Expenditure exceeds funds released")

    if released_pct > 85 and exp_pct_of_released < 30:
        score += 10
        reasons.append(f"{released_pct:.0f}% funds released but only {exp_pct_of_released:.0f}% utilized")
    elif released_pct > 70 and exp_pct_of_released < 50:
        score += 6
        reasons.append(f"High release ({released_pct:.0f}%) with low utilization ({exp_pct_of_released:.0f}%)")

    if row["sanctioned_amount"] > 0 and row["released_amount"] > row["sanctioned_amount"]:
        score += 5
        reasons.append("Released amount exceeds sanctioned amount")

    score = min(25, score)
    return {"score": score, "flag": score > 0, "reason": "; ".join(reasons) if reasons else "No financial anomaly detected"}


# --------------------------------------------------------------------
# B. Cost Anomaly (20 pts) - median/IQR/z-score against similar projects
# --------------------------------------------------------------------
def cost_anomaly(row, df):
    similar = df[(df["project_type"] == row["project_type"]) & (df["state"] == row["state"])]
    if len(similar) < MIN_SIMILAR_FOR_COST_CHECK:
        similar = df[df["project_type"] == row["project_type"]]
    if len(similar) < MIN_SIMILAR_FOR_COST_CHECK:
        return {"score": 0, "flag": False, "reason": "Not enough comparable projects for cost benchmarking"}

    costs = similar["sanctioned_amount"]
    median = costs.median()
    q1, q3 = costs.quantile(0.25), costs.quantile(0.75)
    iqr = q3 - q1
    std = costs.std() if costs.std() > 0 else 1
    z = (row["sanctioned_amount"] - median) / std

    upper_fence = q3 + 1.5 * iqr
    is_outlier = row["sanctioned_amount"] > upper_fence
    ratio = row["sanctioned_amount"] / median if median > 0 else 1

    score = 0
    if is_outlier:
        score = min(20, int((ratio - 1) * 20))
    elif z > 1.5:
        score = min(12, int(z * 4))

    reason = f"Sanctioned amount is {ratio:.1f}x the median (₹{median/100000:.1f}L) for comparable projects"
    return {"score": score, "flag": score > 0, "reason": reason, "median": median, "ratio": ratio, "zscore": round(z, 2)}


# --------------------------------------------------------------------
# C. Timeline Anomaly (20 pts)
# --------------------------------------------------------------------
def timeline_anomaly(row):
    reasons = []
    score = 0

    if row["status"] == "Completed":
        return {"score": 0, "flag": False, "reason": "Project marked Completed"}

    delay_days = row["delay_days"] or 0
    if delay_days > 0:
        delay_months = delay_days / 30
        score += min(14, int(delay_months * 2))
        reasons.append(f"Overdue by {delay_days} days (~{delay_months:.1f} months) past expected completion")

    if row["elapsed_days"] and row["elapsed_days"] > 60 and row["est_completion_pct"] < 15:
        score += 6
        reasons.append("Very low estimated progress despite significant elapsed time")

    score = min(20, score)
    return {"score": score, "flag": score > 0, "reason": "; ".join(reasons) if reasons else "On track"}


# --------------------------------------------------------------------
# D. Ghost Project Risk Indicator (20 pts) - NOT real satellite verification
# --------------------------------------------------------------------
def ghost_project_risk(row):
    released_pct = row["released_pct"]
    completion = row["est_completion_pct"]

    is_ghost = released_pct > 80 and completion < 20
    partial = released_pct > 60 and completion < 40

    if is_ghost:
        score = 20
        reason = f"{released_pct:.0f}% funds released but only ~{completion:.0f}% estimated progress"
    elif partial:
        score = 10
        reason = f"High fund release ({released_pct:.0f}%) relative to estimated progress (~{completion:.0f}%)"
    else:
        score = 0
        reason = "Funds released proportionate to estimated progress"

    return {"score": score, "flag": score > 0, "reason": reason}


# --------------------------------------------------------------------
# E. Contractor Risk (15 pts)
# --------------------------------------------------------------------
def contractor_risk(row, df):
    cp = df[df["contractor"] == row["contractor"]]
    n = len(cp)
    if n < 3:
        return {"score": 3, "flag": False, "reason": f"Limited history ({n} project(s) on record)", "total_projects": n}

    avg_completion = cp["est_completion_pct"].mean()
    delayed = (cp["delay_days"] > 0).sum()
    delayed_pct = delayed / n * 100
    high_risk_count = 0  # filled in by caller after full scoring pass if desired

    score = 0
    reasons = []
    if avg_completion < 50:
        score += 8
        reasons.append(f"Low average estimated completion ({avg_completion:.0f}%) across {n} projects")
    if delayed_pct > 40:
        score += 7
        reasons.append(f"{delayed:.0f}/{n} projects ({delayed_pct:.0f}%) overdue")

    score = min(15, score)
    return {
        "score": score, "flag": score > 0,
        "reason": "; ".join(reasons) if reasons else f"Acceptable track record across {n} projects",
        "total_projects": n, "avg_completion": round(avg_completion, 1), "delayed_pct": round(delayed_pct, 1)
    }


# --------------------------------------------------------------------
# ML Anomaly (Isolation Forest) - contributes up to 15 pts
# --------------------------------------------------------------------
def compute_ml_scores(df: pd.DataFrame) -> pd.Series:
    """Returns a 0-15 ML anomaly contribution per row, index-aligned to df."""
    if not SKLEARN_AVAILABLE or len(df) < MIN_PROJECTS_FOR_ML:
        return pd.Series([0.0] * len(df), index=df.index)

    features = df[[
        "sanctioned_amount", "released_amount", "expenditure",
        "released_pct", "expenditure_pct", "est_completion_pct",
    ]].fillna(0)

    # duration/delay as extra signal where available
    dur = df["total_duration_days"].fillna(df["total_duration_days"].median() if df["total_duration_days"].notna().any() else 0)
    delay = df["delay_days"].fillna(0)
    features = features.assign(duration=dur, delay=delay)

    model = IsolationForest(n_estimators=200, contamination="auto", random_state=42)
    model.fit(features)
    raw_scores = model.decision_function(features)  # higher = more normal

    # normalize: more negative (more anomalous) -> higher contribution 0-15
    min_s, max_s = raw_scores.min(), raw_scores.max()
    if max_s - min_s < 1e-9:
        return pd.Series([0.0] * len(df), index=df.index)

    normalized_anomaly = (max_s - raw_scores) / (max_s - min_s)  # 0..1, 1 = most anomalous
    contribution = (normalized_anomaly * 15).round(1)
    return pd.Series(contribution, index=df.index)


# --------------------------------------------------------------------
# Combine everything into one explainable risk record
# --------------------------------------------------------------------
def classify(score):
    if score >= 60:
        return "HIGH", "🔴", "#EF4444"
    elif score >= 30:
        return "MEDIUM", "🟡", "#F59E0B"
    else:
        return "LOW", "🟢", "#10B981"


def compute_all_risks(df: pd.DataFrame) -> pd.DataFrame:
    """Calculate risk once for the whole dataset and return an augmented
    DataFrame plus a parallel dict of full explainable breakdowns keyed
    by project_id. Call this once per data version and reuse everywhere
    (dashboard, list, alerts, analytics, detail) instead of recomputing."""
    if df.empty:
        return df, {}

    ml_scores = compute_ml_scores(df)

    breakdowns = {}
    rule_scores = []
    for idx, row in df.iterrows():
        fin = financial_anomaly(row)
        cost = cost_anomaly(row, df)
        tl = timeline_anomaly(row)
        ghost = ghost_project_risk(row)
        contractor = contractor_risk(row, df)

        rule_total = fin["score"] + cost["score"] + tl["score"] + ghost["score"] + contractor["score"]
        ml_contribution = float(ml_scores.loc[idx])
        total = min(100, round(rule_total + ml_contribution))
        level, color, hexcolor = classify(total)

        breakdowns[row["project_id"]] = {
            "total_score": total,
            "rule_score": rule_total,
            "ml_contribution": round(ml_contribution, 1),
            "risk_level": level,
            "color": color,
            "hexcolor": hexcolor,
            "financial": fin,
            "cost": cost,
            "timeline": tl,
            "ghost": ghost,
            "contractor": contractor,
        }
        rule_scores.append(total)

    df = df.copy()
    df["risk_score"] = rule_scores
    df["risk_level"] = df["project_id"].map(lambda pid: breakdowns[pid]["risk_level"])
    return df, breakdowns


def top_reasons(breakdown, n=3):
    """Flatten the breakdown into a sorted list of (label, score, reason) for
    display, biggest contributor first."""
    parts = [
        ("Financial", breakdown["financial"]["score"], breakdown["financial"]["reason"]),
        ("Cost", breakdown["cost"]["score"], breakdown["cost"]["reason"]),
        ("Timeline", breakdown["timeline"]["score"], breakdown["timeline"]["reason"]),
        ("Ghost Project Risk Indicator", breakdown["ghost"]["score"], breakdown["ghost"]["reason"]),
        ("Contractor", breakdown["contractor"]["score"], breakdown["contractor"]["reason"]),
        ("ML Anomaly Detection", breakdown["ml_contribution"], "Isolation Forest flagged unusual feature combination" if breakdown["ml_contribution"] > 5 else "Within normal ML-modeled range"),
    ]
    parts.sort(key=lambda p: p[1], reverse=True)
    return [p for p in parts if p[1] > 0][:n]


def recommended_action(breakdown):
    if breakdown["risk_level"] != "HIGH" and breakdown["risk_level"] != "MEDIUM":
        return "No action required"
    actions = []
    if breakdown["ghost"]["flag"]:
        actions.append("Field Verification Required")
    if breakdown["financial"]["flag"] or breakdown["cost"]["flag"]:
        actions.append("Financial Review Required")
    if breakdown["contractor"]["flag"]:
        actions.append("Contractor Review Required")
    if not actions:
        actions.append("Document Verification Required")
    return "; ".join(dict.fromkeys(actions))
