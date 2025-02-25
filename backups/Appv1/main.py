from player import Player
from game import TopTrumpsGame
from leaderboards import Leaderboard

def main_menu(player):
    while True:
        print("\n1. Play Top Trumps")
        print("2. View Leaderboard")
        print("3. Search Leaderboard")
        print("4. Quit")
        choice = input("Select an option: ").strip()
        if choice == "1":
            game = TopTrumpsGame(player)
            game.play_game()
        elif choice == "2":
            Leaderboard.view_leaderboard()
        elif choice == "3":
            term = input("Enter a name or PlayerID to search for: ").strip()
            Leaderboard.search_leaderboard(term)
        elif choice == "4":
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    player = Player.login()
    if player:
        main_menu(player)
    else:
        print("Exiting the game due to login failure.")
