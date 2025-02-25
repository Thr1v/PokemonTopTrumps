import csv
import getpass
from leaderboards import Leaderboard
from helper import update_csv_with_player_id, get_max_player_id_from_csv, get_next_unique_id

class Player:
    def __init__(self, player_id, username, first_name="", last_name=""):
        self.player_id = player_id
        self.username = username
        self.first_name = first_name if first_name else username
        self.last_name = last_name
        self.wins = 0
        self.losses = 0
        self.games_played = 0
        self.score = 0  # Score can be defined as needed.
    
    @classmethod
    def login(cls, csv_filename="users.csv"):
        username = input("Enter username: ").strip()
        password = getpass.getpass("Enter password: ").strip()
        try:
            with open(csv_filename, mode='r', newline='') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get('username') == username and row.get('password') == password:
                        print("Login successful!\n")
                        player_id_str = row.get('PlayerID', '').strip()
                        if not player_id_str:
                            # Generate new ID using the centralized helper function.
                            new_id = get_next_unique_id(csv_filename)
                            print(f"[DEBUG] Generated new ID: {new_id}")
                            # Insert a placeholder record into SQL so that the ID is reserved.
                            # Here we assume zero scores; adjust as needed.
                            Leaderboard.update_leaderboard(new_id, username, "", 0, 0, 0, 0)
                            update_csv_with_player_id(username, new_id, csv_filename)
                            player_id = new_id
                        else:
                            player_id = int(player_id_str)
                        return cls(player_id, username, row.get('FirstName', username), row.get('LastName', ''))
        except FileNotFoundError:
            print("User file not found. Please ensure 'users.csv' exists.")
        print("Invalid credentials.")
        return None
