import requests
import random
import csv
from leaderboards import update_leaderboard, view_leaderboard, get_new_player_id, search_leaderboard

def login():
    """
    Prompts the user for username and password, then checks credentials
    against those stored in users.csv. Returns a dictionary with user details if valid.
    """
    username = input("Enter username: ").strip()
    password = input("Enter password: ").strip()
    
    try:
        with open('users.csv', mode='r', newline='') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                if row['username'] == username and row['password'] == password:
                    print("Login successful!\n")
                    player_id_str = row.get('PlayerID', '').strip()
                    if player_id_str == "":
                        player_id = get_new_player_id()
                    else:
                        player_id = int(player_id_str)
                    return {
                        'PlayerID': player_id,
                        'FirstName': row.get('FirstName', username),
                        'LastName': row.get('LastName', '')
                    }
    except FileNotFoundError:
        print("User file not found. Please ensure 'users.csv' exists.")
    print("Invalid credentials.")
    return None

def get_pokemon_info(identifier):
    url = f"https://pokeapi.co/api/v2/pokemon/{identifier.lower()}/"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    elif response.status_code == 404:
        print(f"[404] Pokémon '{identifier}' not found.")
        return None
    else:
        print(f"[{response.status_code}] An unexpected error occurred: {response.text}")
        return None

def display_card(pokemon_data, reveal=True):
    name = pokemon_data.get("name", "Unknown").capitalize()
    if reveal:
        print(f"\n=== {name} ===")
    else:
        print("\n=== [Hidden Card] ===")

    stats = {stat["stat"]["name"]: stat["base_stat"] for stat in pokemon_data["stats"]}
    if reveal:
        for stat_name, value in stats.items():
            print(f"{stat_name.capitalize()}: {value}")
    return stats

def top_trumps_game():
    user_wins = 0
    comp_wins = 0
    rounds = 5

    for round_num in range(1, rounds + 1):
        print(f"\n--- Round {round_num} ---")
        user_pokemon_id = random.randint(1, 150)
        comp_pokemon_id = random.randint(1, 150)
        
        user_pokemon = get_pokemon_info(str(user_pokemon_id))
        comp_pokemon = get_pokemon_info(str(comp_pokemon_id))
        
        if not user_pokemon or not comp_pokemon:
            print("Failed to retrieve Pokémon data. Skipping round.")
            continue
        
        print("Your card:")
        user_stats = display_card(user_pokemon, reveal=True)
        comp_stats = display_card(comp_pokemon, reveal=False)
        comp_reveal = comp_pokemon.get("name", "Unknown").capitalize()
        
        valid_stats = list(user_stats.keys())
        print("\nChoose a stat to compare from the following options:")
        print(", ".join(stat.capitalize() for stat in valid_stats))
        
        chosen_stat = input("Enter your chosen stat: ").strip().lower()
        while chosen_stat not in valid_stats:
            chosen_stat = input("Invalid stat. Please enter a valid stat: ").strip().lower()
        
        user_value = user_stats[chosen_stat]
        comp_value = comp_stats[chosen_stat]

        print(f"\nYour {chosen_stat.capitalize()}: {user_value}")
        print(f"Computer's {chosen_stat.capitalize()}: {comp_value}")
        
        if user_value > comp_value:
            print(f"You win this round! The Computer had {comp_reveal} and lost with {comp_value}")
            user_wins += 1
        elif user_value < comp_value:
            print(f"Computer wins this round! They had {comp_reveal} and won with {comp_value}")
            comp_wins += 1
        else:
            print("It's a draw!")
    
    print("\n--- Game Over ---")
    print(f"Your wins: {user_wins}")
    print(f"Computer wins: {comp_wins}")
    
    if user_wins > comp_wins:
        print("Overall, you win!")
    elif user_wins < comp_wins:
        print("Overall, the computer wins!")
    else:
        print("It’s a tie overall!")
    
    return user_wins, comp_wins, rounds

def main_menu(user_details):
    while True:
        print("\n1. Play Top Trumps")
        print("2. View Leaderboard")
        print("3. Search Leaderboard")
        print("4. Quit")

        choice = input("Select an option: ").strip()
        if choice == "1":
            wins, losses, total_rounds = top_trumps_game()
            update_leaderboard(
                player_id=user_details["PlayerID"],
                first_name=user_details["FirstName"],
                last_name=user_details["LastName"],
                score=wins,
                wins=wins,
                losses=losses,
                games_played=1
            )
        elif choice == "2":
            view_leaderboard()
        elif choice == "3":
            term = input("Enter a name or PlayerID to search for: ").strip()
            search_leaderboard(term)
        elif choice == "4":
            print("Thanks for playing!")
            break
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    user_details = login()
    if user_details:
        main_menu(user_details)
    else:
        print("Exiting the game due to login failure.")
