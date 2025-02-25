import csv
import getpass
from leaderboards import Leaderboard
from helper import update_csv_with_player_id, get_max_player_id_from_csv

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
                            # Generate new ID by comparing CSV max and SQL max values.
                            csv_max = get_max_player_id_from_csv(csv_filename)
                            sql_max = Leaderboard.get_new_player_id() - 1  # get_new_player_id returns max+1
                            new_id = max(csv_max, sql_max) + 1
                            player_id = new_id
                            update_csv_with_player_id(username, player_id, csv_filename)
                        else:
                            player_id = int(player_id_str)
                        return cls(player_id, username, row.get('FirstName', username), row.get('LastName', ''))
        except FileNotFoundError:
            print("User file not found. Please ensure 'users.csv' exists.")
        print("Invalid credentials.")
        return None
