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
