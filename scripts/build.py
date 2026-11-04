"""Clean the sleep dataset, run the SQL analysis and the model checks, and write the dashboard data.

Run from the repository root:
    python scripts/build.py

Outputs: sql/results/*.csv, reports/model_validation.json, dashboard/dashboard_data.js
"""
import csv
import json
import sqlite3
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import GroupKFold, StratifiedKFold, cross_val_score, train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.tree import DecisionTreeClassifier

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "Sleep_health_and_lifestyle_dataset.csv"
SQL_DIR = ROOT / "sql"
RESULTS = SQL_DIR / "results"
REPORTS = ROOT / "reports"
DB = ROOT / "sleep.db"
MODEL = dict(random_state=0, max_depth=4, min_samples_leaf=1, min_samples_split=2, class_weight="balanced")


def load_clean():
    """Same cleaning as the notebook: split blood pressure, merge 'Normal Weight' into 'Normal'."""
    df = pd.read_csv(DATA, keep_default_na=False)            # keep "None" as a label
    df[["BP Systolic", "BP Diastolic"]] = df["Blood Pressure"].str.split("/", expand=True).astype(int)
    df = df.drop(columns="Blood Pressure")
    df["BMI Category"] = df["BMI Category"].replace("Normal Weight", "Normal")
    return df


def run_sql(df):
    if DB.exists():
        DB.unlink()
    con = sqlite3.connect(DB)
    files = sorted(SQL_DIR.glob("*.sql"))
    con.executescript(files[0].read_text())
    cols = {"Person ID": "person_id", "Gender": "gender", "Age": "age", "Occupation": "occupation",
            "Sleep Duration": "sleep_hours", "Quality of Sleep": "sleep_quality",
            "Physical Activity Level": "activity_minutes", "Stress Level": "stress_level",
            "BMI Category": "bmi_category", "BP Systolic": "bp_systolic", "BP Diastolic": "bp_diastolic",
            "Heart Rate": "heart_rate", "Daily Steps": "daily_steps", "Sleep Disorder": "sleep_disorder"}
    t = df.rename(columns=cols)[list(cols.values())].copy()
    t["profile_key"] = t.drop(columns="person_id").astype(str).agg("|".join, axis=1)
    t.to_sql("people", con, if_exists="append", index=False)
    out = {}
    RESULTS.mkdir(parents=True, exist_ok=True)
    for f in files[1:]:
        cur = con.execute(f.read_text())
        header = [d[0] for d in cur.description]
        rows = cur.fetchall()
        with open(RESULTS / f"{f.stem}.csv", "w", newline="") as fh:
            w = csv.writer(fh)
            w.writerow(header)
            w.writerows(rows)
        out[f.stem] = [dict(zip(header, r)) for r in rows]
    con.close()
    DB.unlink()
    return out


def model_checks(df):
    """Reproduce the notebook's 88% and test it against duplicate rows."""
    d = df.drop(columns="Person ID").copy()
    encoders = {}
    for col in ["Gender", "Occupation", "BMI Category", "Sleep Disorder"]:
        encoders[col] = LabelEncoder().fit(d[col])
        d[col] = encoders[col].transform(d[col])
    X, y = d.drop(columns="Sleep Disorder"), d["Sleep Disorder"]
    classes = list(encoders["Sleep Disorder"].classes_)

    # 1. The original evaluation: random 80/20 split, heart-rate outliers removed from training
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=0)
    z = np.abs(stats.zscore(X_tr[["Heart Rate"]]))
    drop = np.where(z > 3)[0]
    X_tr, y_tr = X_tr.drop(X_tr.index[drop]), y_tr.drop(y_tr.index[drop])
    m = DecisionTreeClassifier(**MODEL).fit(X_tr, y_tr)
    pred = m.predict(X_te)
    key = lambda a: a.astype(str).agg("|".join, axis=1)  # noqa: E731
    in_train = int(key(X_te).isin(set(key(X_tr))).sum())

    # 2. Leak-free: identical profiles never appear in both training and test folds
    groups = pd.factorize(key(X))[0]
    group_acc = [accuracy_score(y.iloc[te], DecisionTreeClassifier(**MODEL).fit(X.iloc[tr], y.iloc[tr]).predict(X.iloc[te]))
                 for tr, te in GroupKFold(n_splits=5).split(X, y, groups)]

    # 3. Each unique profile counted once
    u = d.drop_duplicates()
    dedup_acc = cross_val_score(DecisionTreeClassifier(**MODEL), u.drop(columns="Sleep Disorder"), u["Sleep Disorder"],
                                cv=StratifiedKFold(5, shuffle=True, random_state=0))

    imp = sorted(zip(X.columns, m.feature_importances_), key=lambda t: -t[1])
    return {
        "classes": classes,
        "original_split": {"test_rows": int(len(X_te)), "accuracy": round(accuracy_score(y_te, pred), 4),
                           "test_rows_also_in_training": in_train,
                           "confusion_matrix": confusion_matrix(y_te, pred).tolist()},
        "group_kfold": {"folds": [round(a, 4) for a in group_acc], "mean_accuracy": round(float(np.mean(group_acc)), 4)},
        "unique_profiles_cv": {"rows": int(len(u)), "mean_accuracy": round(float(dedup_acc.mean()), 4)},
        "majority_baseline": round(float((y == y.mode()[0]).mean()), 4),
        "unique_profiles_baseline": round(float((u["Sleep Disorder"] == u["Sleep Disorder"].mode()[0]).mean()), 4),
        "feature_importance": [{"feature": f, "importance": round(float(v), 4)} for f, v in imp if v > 0],
    }


def main():
    df = load_clean()
    sql = run_sql(df)
    model = model_checks(df)
    REPORTS.mkdir(exist_ok=True)
    (REPORTS / "model_validation.json").write_text(json.dumps(model, indent=2) + "\n")

    rows = df[["Gender", "Age", "Occupation", "Sleep Duration", "Quality of Sleep", "Physical Activity Level",
               "Stress Level", "BMI Category", "BP Systolic", "Heart Rate", "Daily Steps", "Sleep Disorder"]]
    data = {"columns": list(rows.columns), "rows": rows.values.tolist(), "model": model}
    (ROOT / "dashboard" / "dashboard_data.js").write_text(
        "// Generated by scripts/build.py. Do not edit by hand.\nwindow.SLEEP = "
        + json.dumps(data, separators=(",", ":"), default=lambda v: v.item()) + ";\n")

    q = {r["item"]: r["value"] for r in sql["02_data_quality"]}
    print(f"{q['people']} people, {q['unique profiles']} unique profiles")
    print(f"Original split accuracy {model['original_split']['accuracy']:.1%} "
          f"({model['original_split']['test_rows_also_in_training']} of {model['original_split']['test_rows']} test rows also in training)")
    print(f"Leak-free (GroupKFold) {model['group_kfold']['mean_accuracy']:.1%}; "
          f"unique profiles {model['unique_profiles_cv']['mean_accuracy']:.1%} vs baseline {model['unique_profiles_baseline']:.1%}")


if __name__ == "__main__":
    main()
