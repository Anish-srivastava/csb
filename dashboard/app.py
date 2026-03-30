"""
Flask dashboard for ransomware simulation monitoring.
"""

from pathlib import Path
import json
from flask import Flask, render_template

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_FILE = BASE_DIR / "logs" / "activity_log.txt"
STATS_FILE = BASE_DIR / "logs" / "stats.json"

app = Flask(__name__, template_folder="templates")


def load_stats():
    if STATS_FILE.exists():
        try:
            return json.loads(STATS_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            pass
    return {"total_files_scanned": 0, "suspicious_activity_count": 0}


def load_logs():
    if not LOG_FILE.exists():
        return []

    rows = []
    lines = LOG_FILE.read_text(encoding="utf-8").splitlines()
    for line in lines[1:]:
        if not line.strip():
            continue
        parts = line.split("|", maxsplit=4)
        if len(parts) != 5:
            continue
        rows.append(
            {
                "timestamp": parts[0],
                "event": parts[1],
                "path": parts[2],
                "classification": parts[3],
                "message": parts[4],
            }
        )
    return rows


@app.route("/")
def index():
    stats = load_stats()
    logs = load_logs()

    normal_count = sum(1 for row in logs if row["classification"] == "Normal")
    ransomware_count = sum(1 for row in logs if row["classification"] == "Ransomware")

    return render_template(
        "index.html",
        total_files_scanned=stats.get("total_files_scanned", 0),
        suspicious_activity_count=stats.get("suspicious_activity_count", 0),
        logs=logs,
        chart_labels=["Normal", "Ransomware"],
        chart_values=[normal_count, ransomware_count],
    )


if __name__ == "__main__":
    app.run(debug=True)
