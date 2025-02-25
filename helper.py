import csv
from leaderboards import Leaderboard

def update_csv_with_player_id(username, new_id, csv_filename="users.csv"):
    """
    Reads the CSV, updates the row matching 'username' with new_id in 'PlayerID',
    and rewrites the file. Only updates if PlayerID is blank.
    """
    rows = []
    updated = False

    with open(csv_filename, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames

        for row in reader:
            # Check if this is the correct user row AND no existing ID
            if (row.get("username") == username 
                and (not row.get("PlayerID") or not row["PlayerID"].strip())):
                row["PlayerID"] = str(new_id)
                updated = True
            rows.append(row)

    if updated:
        # Overwrite the CSV with updated rows
        with open(csv_filename, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)

    return updated

def get_max_player_id_from_csv(csv_filename="users.csv"):
    """
    Reads the CSV file and returns the maximum PlayerID found.
    If no valid PlayerID exists, returns 0.
    """
    max_id = 0
    with open(csv_filename, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            pid_str = row.get("PlayerID", "").strip()
            if pid_str.isdigit():
                pid = int(pid_str)
                if pid > max_id:
                    max_id = pid
    return max_id
