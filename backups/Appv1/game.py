import random
from pokemon import Pokemon
from leaderboards import Leaderboard

class TopTrumpsGame:
    def __init__(self, player):
        self.player = player
        self.rounds = 5

    def play_round(self, round_num):
        print(f"\n--- Round {round_num} ---")
        user_pokemon = Pokemon(random.randint(1, 150))
        comp_pokemon = Pokemon(random.randint(1, 150))
        
        if not user_pokemon.data or not comp_pokemon.data:
            print("Failed to retrieve Pokémon data. Skipping round.")
            return
        
        print("Your card:")
        user_pokemon.display_card(reveal=True)
        print("Computer's card:")
        comp_pokemon.display_card(reveal=False)
        comp_name = comp_pokemon.name
        
        valid_stats = user_pokemon.available_stats()
        print("\nChoose a stat to compare from the following options:")
        print(", ".join(stat.capitalize() for stat in valid_stats))
        chosen_stat = input("Enter your chosen stat: ").strip().lower()
        while chosen_stat not in valid_stats:
            chosen_stat = input("Invalid stat. Please enter a valid stat: ").strip().lower()
        
        user_value = user_pokemon.get_stat(chosen_stat)
        comp_value = comp_pokemon.get_stat(chosen_stat)
        print(f"\nYour {chosen_stat.capitalize()}: {user_value}")
        print(f"Computer's {chosen_stat.capitalize()}: {comp_value}")
        
        if user_value > comp_value:
            print(f"You win this round! The Computer had {comp_name} and lost with {comp_value}")
            self.player.wins += 1
        elif user_value < comp_value:
            print(f"Computer wins this round! They had {comp_name} and won with {comp_value}")
            self.player.losses += 1
        else:
            print("It's a draw!")
    
    def play_game(self):
        for round_num in range(1, self.rounds + 1):
            self.play_round(round_num)
        print("\n--- Game Over ---")
        print(f"Wins: {self.player.wins}")
        print(f"Losses: {self.player.losses}")
        self.player.games_played += 1
        self.player.score = self.player.wins  # Adjust score logic as needed.
        if self.player.wins > self.player.losses:
            print("Overall, you win!")
        elif self.player.wins < self.player.losses:
            print("Overall, the computer wins!")
        else:
            print("It’s a tie overall!")
        # Update the leaderboard after the game.
        Leaderboard.update_leaderboard(
            self.player.player_id,
            self.player.first_name,
            self.player.last_name,
            self.player.score,
            self.player.wins,
            self.player.losses,
            1  # Each complete match counts as one game played.
        )
