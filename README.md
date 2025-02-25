Requirements will be: PIL

"pip install pillow" to install dependencies.

This is the Top Trumps Pokemon card game! I was inspired to make this game based off being shown the databases module with QA for the coding fundamentals. We learnt how to interact with using the 'requests' module which can parse json data from webpages. Using a site that housed information on pokemon, I built this game to by parsing this json data and defining pokemon attributes. It now also connects to my local database and creates leaderboards based off how many wins you have etc.


Overview
The game uses the PokéAPI to fetch Pokémon data in JSON format. Each card displays key stats like HP, Attack, Defense, and more. Players compete against the computer in a best-of-5 rounds match, selecting a stat from their card to compare with the computer's. Based on wins and losses, the game updates a leaderboard stored in a local SQL Server database.

API Integration:
Uses the requests module to retrieve and parse Pokémon data from the PokéAPI. Pokémon attributes are dynamically extracted from the JSON response. Pokemon.py helps define API pulling and attributes.

Database & Leaderboard:
Connects to a local SQL Server database using pyodbc. The game creates a leaderboard table (if it doesn’t already exist) and updates it based on each game’s wins, losses, and overall score. I would update this later to not be a local DB but instead a server that can receive requests.
The leaderboard can be viewed and searched via a Tkinter Treeview display.

User Management:
User credentials are maintained in a CSV file. Players can log in or create a new account via the GUI. When a new user is created, their details are appended to the CSV file.

Graphical User Interface:
Built with Tkinter and styled with "Andy" font for a Pokémon-like feel.

Login Screen: Features a Login or New User buttons and supports "Enter" key login.
Main Menu: Displays the current player’s score and options to start a new game, view the leaderboard, search the leaderboard, or quit.
Game Screen: Displays Pokémon cards for both the player and the computer, the user must select their chosen attribute to pit against the computer. After each round, the computer’s card is revealed, and round results are shown. Best of 5 and your stats are uploaded at the end of 5 rounds. Welcome to quit anytime by pressing the "Finish Game" button.
Leaderboard Display: Uses a Tkinter Treeview to present leaderboard data in clean, aligned columns with dates formatted as DD/MM/YYYY.

Requirements
Python
Python Modules:

requests
random
pyodbc
csv
tkinter (included with Python)
Pillow (install via pip install pillow)
Database:
A local SQL Server database named PokemonDB (ensure it exists or is created by the script).

Files & Folders:

An images folder containing Pokémon images, a fallback image named invalid.png, and an animated background GIF named background.gif.
A CSV file (users.csv) for user credentials.
Usage
Run the application with:
python gui.py
Log in with your username and password, or create a new user.
From the Main Menu, start a new game, view/search the leaderboard, or quit.
Play a 5-round match by selecting stats to compare on your Pokémon card.
At game’s end, your results are updated in the leaderboard and displayed.
Enjoy the game and good luck!

Please also see other versions for a different approach. Version 1 runs off "main.py"