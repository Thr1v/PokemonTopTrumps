import tkinter as tk
from tkinter import messagebox, simpledialog, Toplevel, scrolledtext
from tkinter import ttk
import os
import csv
import random
import datetime
from PIL import Image, ImageTk

from player import Player
from pokemon import Pokemon
from leaderboards import Leaderboard
from helper import get_next_unique_id

TOTAL_ROUNDS = 5

def format_datetime(dt_value):
    """
    Convert a datetime or string to a nicer format like 'DD/MM/YYYY'.
    Adjust if you also want time: '%d/%m/%Y %H:%M:%S'.
    """
    if not dt_value:
        return ""
    if hasattr(dt_value, 'strftime'):
        return dt_value.strftime("%d/%m/%Y")
    try:
        parsed = datetime.datetime.fromisoformat(str(dt_value))
        return parsed.strftime("%d/%m/%Y")
    except ValueError:
        return str(dt_value)

# -----------------------------------------------------------------------------
# AnimatedGIFLabel Class
# -----------------------------------------------------------------------------
class AnimatedGIFLabel(tk.Label):
    """
    A Label that animates a GIF using PIL to cycle through frames
    at the GIF's original resolution.
    """
    def __init__(self, parent, gif_path, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.frames = []
        try:
            self.gif = Image.open(gif_path)
        except Exception as e:
            print(f"Error opening GIF '{gif_path}': {e}")
            return

        self.delay = self.gif.info.get('duration', 100)
        try:
            while True:
                frame = ImageTk.PhotoImage(self.gif.copy())
                self.frames.append(frame)
                self.gif.seek(self.gif.tell() + 1)
        except EOFError:
            pass

        self.frame_index = 0
        if self.frames:
            self.config(image=self.frames[self.frame_index])
            self.after(self.delay, self.next_frame)

    def next_frame(self):
        self.frame_index = (self.frame_index + 1) % len(self.frames)
        self.config(image=self.frames[self.frame_index])
        self.after(self.delay, self.next_frame)

# -----------------------------------------------------------------------------
# Main Application Class
# -----------------------------------------------------------------------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Top Trumps Pokémon Game")
        self.geometry("900x700")
        self.player = None  # Set after login

        container = tk.Frame(self)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}
        for F in (LoginFrame, MainMenuFrame, GameFrame):
            frame = F(container, self)
            self.frames[F] = frame
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(LoginFrame)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()
        if cont == MainMenuFrame and self.player is not None:
            frame.refresh()
        elif cont == GameFrame and self.player is not None:
            frame.start_game()

# -----------------------------------------------------------------------------
# Login Frame
# -----------------------------------------------------------------------------
class LoginFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        # Animated background
        self.bg_label = AnimatedGIFLabel(self, "background.gif")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        tk.Label(self, text="Top Trumps Pokémon Login", font=("Andy", 24), bg="#ffffff").pack(pady=20)
        tk.Label(self, text="Username:", font=("Andy", 14), bg="#ffffff").pack(pady=5)
        self.username_entry = tk.Entry(self, font=("Andy", 14))
        self.username_entry.pack(pady=5)
        tk.Label(self, text="Password:", font=("Andy", 14), bg="#ffffff").pack(pady=5)
        self.password_entry = tk.Entry(self, show="*", font=("Andy", 14))
        self.password_entry.pack(pady=5)

        self.username_entry.bind("<Return>", lambda e: self.attempt_login())
        self.password_entry.bind("<Return>", lambda e: self.attempt_login())

        tk.Button(self, text="Login", font=("Andy", 16), command=self.attempt_login).pack(pady=10)
        tk.Button(self, text="New User", font=("Andy", 12), command=self.create_new_user).pack(pady=5)

    def attempt_login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        try:
            with open("users.csv", mode="r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    if row.get("username") == username and row.get("password") == password:
                        messagebox.showinfo("Login", "Login successful!")
                        player_id_str = row.get("PlayerID", "").strip()
                        if player_id_str.isdigit():
                            player_id = int(player_id_str)
                        else:
                            player_id = 0
                        self.controller.player = Player(
                            player_id,
                            username,
                            row.get("FirstName", username),
                            row.get("LastName", "")
                        )
                        self.controller.show_frame(MainMenuFrame)
                        return
                messagebox.showerror("Login Failed", "Invalid credentials.")
        except FileNotFoundError:
            messagebox.showerror("Error", "Could not find 'users.csv'.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def create_new_user(self):
        from helper import get_next_unique_id
        new_username = simpledialog.askstring("New User", "Enter a new username:")
        if not new_username:
            return
        new_password = simpledialog.askstring("New User", "Enter a new password:", show="*")
        if not new_password:
            return

        user_exists = False
        rows = []
        try:
            with open("users.csv", mode="r", newline="") as csvfile:
                reader = csv.DictReader(csvfile)
                fieldnames = reader.fieldnames
                for row in reader:
                    rows.append(row)
                    if row.get("username") == new_username:
                        user_exists = True
        except FileNotFoundError:
            fieldnames = ["username", "password", "PlayerID", "FirstName", "LastName"]

        if user_exists:
            messagebox.showerror("Error", "That username already exists. Please choose another.")
            return

        # Generate a new unique ID before saving
        new_id = get_next_unique_id("users.csv")
        print(f"[DEBUG] Generated new unique ID for new user: {new_id}")
        # Reserve this ID in the database with initial zero values
        Leaderboard.update_leaderboard(new_id, new_username, "", 0, 0, 0, 0)

        new_row = {
            "username": new_username,
            "password": new_password,
            "PlayerID": str(new_id),
            "FirstName": new_username,
            "LastName": ""
        }
        rows.append(new_row)

        with open("users.csv", mode="w", newline="") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=["username", "password", "PlayerID", "FirstName", "LastName"])
            writer.writeheader()
            writer.writerows(rows)

        messagebox.showinfo("New User", f"User '{new_username}' created successfully with ID {new_id}!")

# -----------------------------------------------------------------------------
# Main Menu Frame
# -----------------------------------------------------------------------------
class MainMenuFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_label = AnimatedGIFLabel(self, "background.gif")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.score_label = tk.Label(self, text="", font=("Andy", 18), bg="#ffffff")

        tk.Label(self, text="Main Menu", font=("Andy", 24), bg="#ffffff").pack(pady=20)
        self.score_label.pack(pady=5)

        tk.Button(self, text="Start New Game", font=("Andy", 16),
                  command=lambda: controller.show_frame(GameFrame)).pack(pady=10)
        tk.Button(self, text="View Leaderboard", font=("Andy", 16),
                  command=self.view_leaderboard_treeview).pack(pady=10)
        tk.Button(self, text="Search Leaderboard", font=("Andy", 16),
                  command=self.search_leaderboard_treeview).pack(pady=10)
        tk.Button(self, text="Quit", font=("Andy", 16),
                  command=self.quit_app).pack(pady=20)

    def refresh(self):
        player_id = self.controller.player.player_id
        row = Leaderboard.get_player_record(player_id)
        if row:
            db_score = row[3]
            self.score_label.config(text=f"Welcome, {row[1]}! Your current score: {db_score}")
        else:
            self.score_label.config(text=f"Welcome, {self.controller.player.first_name}! No score yet.")

    def view_leaderboard_treeview(self):
        data_rows = Leaderboard.get_all_records()
        if not data_rows:
            messagebox.showinfo("Leaderboard", "Leaderboard is empty.")
            return

        top = Toplevel(self)
        top.title("Leaderboard")
        top.geometry("800x400")

        # Add a "Rank" column
        columns = ("Rank", "PlayerID", "FirstName", "Score", "Wins", "Losses", "GamesPlayed", "LastUpdated")
        tree = ttk.Treeview(top, columns=columns, show="headings", height=15)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("Rank", text="Rank")
        tree.heading("PlayerID", text="ID")
        tree.heading("FirstName", text="FirstName")
        tree.heading("Score", text="Score")
        tree.heading("Wins", text="Wins")
        tree.heading("Losses", text="Losses")
        tree.heading("GamesPlayed", text="Games")
        tree.heading("LastUpdated", text="LastUpdated")

        tree.column("Rank", width=50, anchor="center")
        tree.column("PlayerID", width=50, anchor="center")
        tree.column("FirstName", width=120, anchor="center")
        tree.column("Score", width=60, anchor="center")
        tree.column("Wins", width=50, anchor="center")
        tree.column("Losses", width=60, anchor="center")
        tree.column("GamesPlayed", width=70, anchor="center")
        tree.column("LastUpdated", width=100, anchor="center")

        # Enumerate rows to create a rank
        for i, row in enumerate(data_rows, start=1):
            # row => (PlayerID, FirstName, LastName, Score, Wins, Losses, GamesPlayed, LastUpdated)
            rank = i
            rank_values = (
                rank,           # Rank
                row[0],         # PlayerID
                row[1] or "",   # FirstName
                row[3],         # Score
                row[4],         # Wins
                row[5],         # Losses
                row[6],         # GamesPlayed
                format_datetime(row[7])
            )
            tree.insert("", tk.END, values=rank_values)

    def search_leaderboard_treeview(self):
        term = simpledialog.askstring("Search Leaderboard", "Enter a name or PlayerID:")
        if term is None:
            return
        data_rows = Leaderboard.search_leaderboard_records(term)
        if not data_rows:
            messagebox.showinfo("Search Results", "No matching records found.")
            return

        top = Toplevel(self)
        top.title("Search Results")
        top.geometry("800x400")

        columns = ("Rank", "PlayerID", "FirstName", "Score", "Wins", "Losses", "GamesPlayed", "LastUpdated")
        tree = ttk.Treeview(top, columns=columns, show="headings", height=15)
        tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(top, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        tree.heading("Rank", text="Rank")
        tree.heading("PlayerID", text="ID")
        tree.heading("FirstName", text="FirstName")
        tree.heading("Score", text="Score")
        tree.heading("Wins", text="Wins")
        tree.heading("Losses", text="Losses")
        tree.heading("GamesPlayed", text="Games")
        tree.heading("LastUpdated", text="LastUpdated")

        tree.column("Rank", width=50, anchor="center")
        tree.column("PlayerID", width=50, anchor="center")
        tree.column("FirstName", width=120, anchor="center")
        tree.column("Score", width=60, anchor="center")
        tree.column("Wins", width=50, anchor="center")
        tree.column("Losses", width=60, anchor="center")
        tree.column("GamesPlayed", width=70, anchor="center")
        tree.column("LastUpdated", width=100, anchor="center")

        for i, row in enumerate(data_rows, start=1):
            rank = i
            rank_values = (
                rank,
                row[0],
                row[1] or "",
                row[3],
                row[4],
                row[5],
                row[6],
                format_datetime(row[7])
            )
            tree.insert("", tk.END, values=rank_values)

    def quit_app(self):
        self.controller.destroy()

# -----------------------------------------------------------------------------
# Game Frame
# -----------------------------------------------------------------------------
class GameFrame(tk.Frame):
    def __init__(self, parent, controller):
        super().__init__(parent)
        self.controller = controller

        self.bg_label = AnimatedGIFLabel(self, "background.gif")
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        self.current_round = 0
        self.player_pokemon = None
        self.computer_pokemon = None
        self.selected_stat = tk.StringVar()

        self.info_label = tk.Label(self, text="", font=("Andy", 16), bg="#ffffff")
        self.info_label.pack(pady=10)

        # Player card frame
        self.player_frame = tk.Frame(self, bg="#ffffff")
        self.player_frame.pack(side="left", padx=20, pady=20)
        tk.Label(self.player_frame, text="Your Card", font=("Andy", 18), bg="#ffffff").pack(pady=5)
        self.player_image_label = tk.Label(self.player_frame, bg="#ffffff")
        self.player_image_label.pack()
        self.player_stats_label = tk.Label(self.player_frame, font=("Andy", 14), justify="left", bg="#ffffff")
        self.player_stats_label.pack(pady=5)

        # Computer card frame
        self.computer_frame = tk.Frame(self, bg="#ffffff")
        self.computer_frame.pack(side="right", padx=20, pady=20)
        tk.Label(self.computer_frame, text="Computer's Card", font=("Andy", 18), bg="#ffffff").pack(pady=5)
        self.computer_image_label = tk.Label(self.computer_frame, bg="#ffffff")
        self.computer_image_label.pack()
        self.computer_stats_label = tk.Label(self.computer_frame, font=("Andy", 14), justify="left", bg="#ffffff")
        self.computer_stats_label.pack(pady=5)

        # Control panel
        control_frame = tk.Frame(self, bg="#ffffff")
        control_frame.pack(pady=20)
        tk.Label(control_frame, text="Choose a stat:", font=("Andy", 16), bg="#ffffff").grid(row=0, column=0, padx=5)
        self.stat_menu = tk.OptionMenu(control_frame, self.selected_stat, "")
        self.stat_menu.config(font=("Andy", 14))
        self.selected_stat.set("Select Stat")
        self.stat_menu.grid(row=0, column=1, padx=5)

        self.submit_button = tk.Button(control_frame, text="Submit Stat", font=("Andy", 16),
                                       command=self.submit_stat)
        self.submit_button.grid(row=0, column=2, padx=10)
        self.next_round_button = tk.Button(control_frame, text="Next Round", font=("Andy", 16),
                                           command=self.next_round, state="disabled")
        self.next_round_button.grid(row=0, column=3, padx=10)

        self.result_label = tk.Label(self, text="", font=("Andy", 16), bg="#ffffff")
        self.result_label.pack(pady=10)

        # Finish button repurposed to always allow returning to Main Menu.
        self.finish_button = tk.Button(self, text="Finish Game", font=("Andy", 16),
                                       command=self.return_to_menu, state="normal")
        self.finish_button.pack(pady=10)

    def start_game(self):
        self.current_round = 0
        self.controller.player.wins = 0
        self.controller.player.losses = 0
        self.controller.player.games_played = 0
        self.controller.player.score = 0

        self.result_label.config(text="")
        self.finish_button.config(text="Finish Game", state="normal")
        self.next_round_button.config(state="disabled")
        self.submit_button.config(state="normal")
        self.start_round()

    def start_round(self):
        self.current_round += 1
        if self.current_round > TOTAL_ROUNDS:
            self.finish_game()
            return

        self.info_label.config(text=(
            f"Round {self.current_round} / {TOTAL_ROUNDS} | "
            f"Wins: {self.controller.player.wins} | "
            f"Losses: {self.controller.player.losses}"
        ))
        self.result_label.config(text="")
        self.player_pokemon = Pokemon(random.randint(1, 150))
        self.computer_pokemon = Pokemon(random.randint(1, 150))

        self.display_pokemon(self.player_pokemon, self.player_image_label, self.player_stats_label, reveal=True)

        # Hide computer's card initially
        self.computer_image_label.config(image="", text="Hidden")
        self.computer_image_label.image = None
        self.computer_stats_label.config(text="")

        # Populate dropdown with player's stats
        stats = self.player_pokemon.available_stats()
        menu = self.stat_menu["menu"]
        menu.delete(0, "end")
        for stat in stats:
            menu.add_command(label=stat.capitalize(), command=lambda s=stat: self.selected_stat.set(s))
        self.selected_stat.set("Select Stat")

        self.submit_button.config(state="normal")
        self.next_round_button.config(state="disabled")

    def display_pokemon(self, pokemon_obj, image_label, stats_label, reveal=True):
        pokemon_name = pokemon_obj.name.lower()
        image_path = os.path.join("images", f"{pokemon_name}.png")
        print(f"[DEBUG] Attempting to load image for: {pokemon_name} at path: {image_path}")
        if not os.path.exists(image_path):
            fallback_path = os.path.join("images", "invalid.png")
            print(f"[DEBUG] {image_path} not found. Trying fallback: {fallback_path}")
            if os.path.exists(fallback_path):
                image_path = fallback_path
            else:
                print("[DEBUG] invalid.png also not found. No image will be displayed.")
                image_path = None

        if image_path:
            try:
                img = Image.open(image_path)
                img = img.resize((200, 200), Image.Resampling.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                image_label.configure(image=photo, text="")
                image_label.image = photo
                print(f"[DEBUG] Successfully loaded: {image_path}")
            except Exception as e:
                print(f"[DEBUG] Error loading image {image_path}: {e}")
                image_label.configure(image="", text="No Image")
                image_label.image = None
        else:
            image_label.configure(image="", text="No Image")
            image_label.image = None

        if reveal:
            stats_text = f"Name: {pokemon_obj.name}\n"
            for stat, value in pokemon_obj.stats.items():
                stats_text += f"{stat.capitalize()}: {value}\n"
            stats_label.config(text=stats_text)
        else:
            stats_label.config(text="")

    def submit_stat(self):
        chosen = self.selected_stat.get()
        if chosen == "Select Stat":
            messagebox.showerror("Error", "Please select a stat.")
            return

        self.display_pokemon(self.computer_pokemon, self.computer_image_label, self.computer_stats_label, reveal=True)

        player_value = self.player_pokemon.get_stat(chosen.lower())
        computer_value = self.computer_pokemon.get_stat(chosen.lower())

        if player_value > computer_value:
            self.controller.player.wins += 1
            result = f"You win this round! {chosen.capitalize()} {player_value} vs {computer_value}"
        elif player_value < computer_value:
            self.controller.player.losses += 1
            result = f"Computer wins this round! {chosen.capitalize()} {computer_value} vs {player_value}"
        else:
            result = "This round is a draw!"

        self.result_label.config(text=result)
        self.submit_button.config(state="disabled")
        self.next_round_button.config(state="normal")
        self.info_label.config(text=(
            f"Round {self.current_round} / {TOTAL_ROUNDS} | "
            f"Wins: {self.controller.player.wins} | "
            f"Losses: {self.controller.player.losses}"
        ))

    def next_round(self):
        self.start_round()

    def finish_game(self):
        self.submit_button.config(state="disabled")
        self.next_round_button.config(state="disabled")

        final_text = (
            f"Game Over!\n"
            f"Final Score - Wins: {self.controller.player.wins}, Losses: {self.controller.player.losses}\n"
        )
        if self.controller.player.wins > self.controller.player.losses:
            final_text += "Overall, you win!"
        elif self.controller.player.wins < self.controller.player.losses:
            final_text += "Overall, the computer wins!"
        else:
            final_text += "It’s a tie overall!"

        self.result_label.config(text=final_text)
        self.controller.player.games_played += 1
        self.controller.player.score = self.controller.player.wins
        Leaderboard.update_leaderboard(
            self.controller.player.player_id,
            self.controller.player.first_name,
            self.controller.player.last_name,
            self.controller.player.score,
            self.controller.player.wins,
            self.controller.player.losses,
            1
        )
        messagebox.showinfo("Game Finished", final_text)
        self.finish_button.config(text="Return to Menu", command=self.return_to_menu)

    def return_to_menu(self):
        self.controller.show_frame(MainMenuFrame)

def main():
    app = App()
    app.mainloop()

if __name__ == "__main__":
    main()
