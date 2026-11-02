import json
import csv
import os

VALID_LEVELS = ("INFO", "WARNING", "ERROR")


def parse_line(line):
    line = line.strip()
    if not line:
        return None

    parts = line.split(" ", 3)
    if len(parts) < 4:
        return None

    date, time, level, message = parts
    if level not in VALID_LEVELS:
        return None

    return {"date": date, "time": time, "level": level, "message": message}


def load_log_file(filepath):
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Plik nie istnieje: {filepath}")

    entries = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            entry = parse_line(line)
            if entry:
                entries.append(entry)

    return entries


def get_statistics(entries):
    total = len(entries)
    info = sum(1 for e in entries if e["level"] == "INFO")
    warning = sum(1 for e in entries if e["level"] == "WARNING")
    error = sum(1 for e in entries if e["level"] == "ERROR")

    error_counts = {}
    for e in entries:
        if e["level"] == "ERROR":
            error_counts[e["message"]] = error_counts.get(e["message"], 0) + 1

    if error_counts:
        most_common_error = max(error_counts, key=error_counts.get)
        most_common_count = error_counts[most_common_error]
    else:
        most_common_error = None
        most_common_count = 0

    return {
        "total_entries": total,
        "info": info,
        "warning": warning,
        "error": error,
        "most_common_error": most_common_error,
        "most_common_error_count": most_common_count,
    }


def get_errors(entries):
    return [e for e in entries if e["level"] == "ERROR"]


def search_logs(entries, text, level=None):
    text = text.lower()
    results = []
    for e in entries:
        if level and e["level"] != level:
            continue
        if text in e["message"].lower():
            results.append(e)
    return results


def export_json(stats, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=4, ensure_ascii=False)


def export_csv(stats, filepath):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["metric", "value"])
        for key, value in stats.items():
            writer.writerow([key, value])
