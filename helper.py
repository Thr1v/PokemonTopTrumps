import csv
from leaderboards import Leaderboard

def update_csv_with_player_id(username, new_id, csv_filename="users.csv"):
    rows = []
    updated = False

    import os
    print(f"[DEBUG] update_csv_with_player_id called for username={username}, new_id={new_id}")
    print(f"[DEBUG] Using CSV path: {os.path.abspath(csv_filename)}")

    with open(csv_filename, mode="r", newline="") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        print("[DEBUG] CSV fieldnames are:", fieldnames)

        for row in reader:
            print("[DEBUG] Checking row:", row)
            if (row.get("username") == username 
                and (not row.get("PlayerID") or not row["PlayerID"].strip())):
                row["PlayerID"] = str(new_id)
                updated = True
                print(f"[DEBUG] Updated row with new ID: {new_id}")
            rows.append(row)

    if updated:
        with open(csv_filename, mode="w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print("[DEBUG] Wrote updated rows to CSV.")
    else:
        print("[DEBUG] No row updated; either PlayerID wasn't blank or user not found.")

    return updated

def get_max_player_id_from_csv(csv_filename="users.csv"):
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

def get_next_unique_id(csv_filename="users.csv"):
    csv_max = get_max_player_id_from_csv(csv_filename)
    sql_max = Leaderboard.get_new_player_id() - 1  # get_new_player_id returns (max+1)
    return max(csv_max, sql_max) + 1
