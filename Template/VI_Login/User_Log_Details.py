import sys
import os
import csv
from datetime import datetime

def log_user(username):
    file_name = "Log_History.csv"
    file_exists = os.path.isfile(file_name)

    now = datetime.now()
    date_str = now.strftime("%d-%m-%Y")
    time_str = now.strftime("%H-%M-%S")

    with open(file_name, mode='a', newline='') as csvfile:
        writer = csv.writer(csvfile)

        # Write header if file is new
        if not file_exists:
            writer.writerow(["OPERATOR", "DATE", "TIME"])

        # Write log row
        writer.writerow([username, date_str, time_str])

    # print("Log updated successfully")

def main():
    if len(sys.argv) != 3:
        print("Usage: script.py <username> <password>")
        sys.exit(1)

    username = sys.argv[1]
    password = sys.argv[2]

    # Password is accepted as input but not stored/logged (security)
    log_user(username)

if __name__ == "__main__":
    main()
