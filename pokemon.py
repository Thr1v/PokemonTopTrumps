import requests

class Pokemon:
    def __init__(self, identifier):
        self.identifier = str(identifier).lower()
        self.data = None
        self.name = "Unknown"
        self.stats = {}
        self.fetch_data()
    
    def fetch_data(self):
        url = f"https://pokeapi.co/api/v2/pokemon/{self.identifier}/"
        response = requests.get(url)
        if response.status_code == 200:
            self.data = response.json()
            self.name = self.data.get("name", "Unknown").capitalize()
            self.stats = { stat["stat"]["name"]: stat["base_stat"] for stat in self.data.get("stats", []) }
        elif response.status_code == 404:
            print(f"[404] Pokémon '{self.identifier}' not found.")
        else:
            print(f"[{response.status_code}] Error: {response.text}")
    
    def display_card(self, reveal=True):
        if reveal:
            print(f"\n=== {self.name} ===")
            for stat_name, value in self.stats.items():
                print(f"{stat_name.capitalize()}: {value}")
        else:
            print("\n=== [Hidden Card] ===")
    
    def get_stat(self, stat_name):
        return self.stats.get(stat_name)
    
    def available_stats(self):
        return list(self.stats.keys())
