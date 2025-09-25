from datetime import datetime
from automation.services.attendance_reporter import make_attendance_report


def main():
    # date = datetime.now().strftime()
    date = "2025-09-19"

    make_attendance_report(date)

if __name__ == "__main__":
    main()