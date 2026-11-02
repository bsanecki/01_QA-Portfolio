from log_analyzer import (
    load_log_file,
    get_statistics,
    get_errors,
    search_logs,
    export_json,
    export_csv,
)

entries = []


def print_menu():
    print("=" * 40)
    print("             LOG ANALYZER")
    print("=" * 40)
    print()
    print("[1] Analyze log file")
    print("[2] Show statistics")
    print("[3] Show errors")
    print("[4] Search logs")
    print("[5] Export report")
    print("[0] Exit")
    print()
    print("=" * 40)


def analyze_log_file():
    global entries
    filepath = input("Enter path to .log file: ").strip()

    try:
        entries = load_log_file(filepath)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return

    if not entries:
        print("No valid log entries found in this file.")
        return

    print(f"Loaded {len(entries)} log entries.")


def show_statistics():
    if not entries:
        print("No data available. Please analyze a log file first.")
        return

    stats = get_statistics(entries)

    print("=" * 40)
    print("             STATISTICS")
    print("=" * 40)
    print()
    print(f"Total log entries: {stats['total_entries']}")
    print()
    print(f"INFO:       {stats['info']}")
    print(f"WARNING:    {stats['warning']}")
    print(f"ERROR:      {stats['error']}")
    print()
    if stats["most_common_error"]:
        print("Most common error:")
        print(stats["most_common_error"])
        print()
        print(f"Occurrences: {stats['most_common_error_count']}")
    else:
        print("No errors found.")
    print()
    print("=" * 40)


def show_errors():
    if not entries:
        print("No data available. Please analyze a log file first.")
        return

    errors = get_errors(entries)
    if not errors:
        print("No errors found.")
        return

    print(f"Found {len(errors)} errors:\n")
    for e in errors:
        print(f"{e['date']} {e['time']} ERROR {e['message']}")


def search_logs_menu():
    if not entries:
        print("No data available. Please analyze a log file first.")
        return

    text = input("Enter search text: ").strip()
    if not text:
        print("Search text cannot be empty.")
        return

    level_input = input("Filter by level (INFO/WARNING/ERROR or leave empty): ").strip().upper()
    level = level_input if level_input in ("INFO", "WARNING", "ERROR") else None

    results = search_logs(entries, text, level)

    print(f"\nFound {len(results)} results:\n")
    for e in results:
        print(f"{e['date']} {e['time']} {e['level']} {e['message']}")


def export_report():
    if not entries:
        print("No data available. Please analyze a log file first.")
        return

    stats = get_statistics(entries)

    print("[1] JSON")
    print("[2] CSV")
    choice = input("Choose export format: ").strip()

    if choice == "1":
        export_json(stats, "reports/report.json")
        print("Report exported to reports/report.json")
    elif choice == "2":
        export_csv(stats, "reports/report.csv")
        print("Report exported to reports/report.csv")
    else:
        print("Invalid choice.")


def main():
    while True:
        print_menu()
        choice = input("Select an option: ").strip()

        if choice == "1":
            analyze_log_file()
        elif choice == "2":
            show_statistics()
        elif choice == "3":
            show_errors()
        elif choice == "4":
            search_logs_menu()
        elif choice == "5":
            export_report()
        elif choice == "0":
            print("Goodbye!")
            break
        else:
            print("Invalid option. Please try again.")

        print()


if __name__ == "__main__":
    main()
