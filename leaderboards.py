import pyodbc
import csv

class Leaderboard:
    CONN_STR = (
        "DRIVER={SQL Server};"
        "SERVER=DESKTOP-6S0DBV7;"  # or "SERVER=localhost;"
        "DATABASE=PokemonDB;"
        "Trusted_Connection=yes;"
    )
    
    @classmethod
    def ensure_table_exists(cls):
        conn = pyodbc.connect(cls.CONN_STR)
        cursor = conn.cursor()
        cursor.execute("""
            IF NOT EXISTS (
                SELECT * FROM INFORMATION_SCHEMA.TABLES 
                WHERE TABLE_NAME = 'Leaderboards'
            )
            BEGIN
                CREATE TABLE Leaderboards (
                    PlayerID INT PRIMARY KEY,
                    FirstName VARCHAR(50),
                    LastName VARCHAR(50),
                    Score INT,
                    Wins INT,
                    Losses INT,
                    GamesPlayed INT,
                    LastUpdated DATETIME DEFAULT GETDATE()
                );
            END
        """)
        conn.commit()
        conn.close()
    
    @classmethod
    def get_new_player_id(cls):
        cls.ensure_table_exists()
        conn = pyodbc.connect(cls.CONN_STR)
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(PlayerID) FROM Leaderboards")
        row = cursor.fetchone()
        conn.close()
        return 1 if row[0] is None else row[0] + 1
    
    @classmethod
    def update_leaderboard(cls, player_id, first_name, last_name, score, wins, losses, games_played):
        cls.ensure_table_exists()
        conn = pyodbc.connect(cls.CONN_STR)
        cursor = conn.cursor()
        cursor.execute("""
        MERGE Leaderboards AS target
        USING (VALUES (?, ?, ?, ?, ?, ?, ?)) AS source 
            (PlayerID, FirstName, LastName, Score, Wins, Losses, GamesPlayed)
        ON target.PlayerID = source.PlayerID
        WHEN MATCHED THEN 
            UPDATE SET 
                Score = source.Score,
                Wins = target.Wins + source.Wins,
                Losses = target.Losses + source.Losses,
                GamesPlayed = target.GamesPlayed + source.GamesPlayed,
                LastUpdated = GETDATE()
        WHEN NOT MATCHED THEN
            INSERT (PlayerID, FirstName, LastName, Score, Wins, Losses, GamesPlayed, LastUpdated)
            VALUES (source.PlayerID, source.FirstName, source.LastName, source.Score, source.Wins, source.Losses, source.GamesPlayed, GETDATE());
        """, (player_id, first_name, last_name, score, wins, losses, games_played))
        conn.commit()
        conn.close()
    
    @classmethod
    def view_leaderboard(cls):
        cls.ensure_table_exists()
        conn = pyodbc.connect(cls.CONN_STR)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT PlayerID, FirstName, LastName, Score, Wins, Losses, GamesPlayed, LastUpdated
            FROM Leaderboards
            ORDER BY Score DESC
        """)
        rows = cursor.fetchall()
        if rows:
            print("\n=== Leaderboard ===")
            for row in rows:
                print(
                    f"PlayerID: {row.PlayerID}, "
                    f"Name: {row.FirstName} {row.LastName}, "
                    f"Score: {row.Score}, "
                    f"Wins: {row.Wins}, "
                    f"Losses: {row.Losses}, "
                    f"Games Played: {row.GamesPlayed}, "
                    f"Last Updated: {row.LastUpdated}"
                )
        else:
            print("\nLeaderboard is empty.")
        conn.close()

    @classmethod
    def get_player_record(cls, player_id):
        cls.ensure_table_exists()
        conn = pyodbc.connect(cls.CONN_STR)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT PlayerID, FirstName, LastName, Score, Wins, Losses, GamesPlayed, LastUpdated
            FROM Leaderboards
            WHERE PlayerID = ?
        """, (player_id,))
        row = cursor.fetchone()
        conn.close()
        return row
    
    @classmethod
    def search_leaderboard(cls, search_term):
        cls.ensure_table_exists()
        conn = pyodbc.connect(cls.CONN_STR)
        cursor = conn.cursor()
        wildcard_term = f"%{search_term}%"
        cursor.execute("""
            SELECT PlayerID, FirstName, LastName, Score, Wins, Losses, GamesPlayed, LastUpdated
            FROM Leaderboards
            WHERE FirstName LIKE ? OR LastName LIKE ? OR CAST(PlayerID AS VARCHAR) LIKE ?
            ORDER BY Score DESC
        """, (wildcard_term, wildcard_term, wildcard_term))
        rows = cursor.fetchall()
        if rows:
            print("\n=== Search Results ===")
            for row in rows:
                print(
                    f"PlayerID: {row.PlayerID}, "
                    f"Name: {row.FirstName} {row.LastName}, "
                    f"Score: {row.Score}, "
                    f"Wins: {row.Wins}, "
                    f"Losses: {row.Losses}, "
                    f"Games Played: {row.GamesPlayed}, "
                    f"Last Updated: {row.LastUpdated}"
                )
        else:
            print("\nNo matching records found.")
        conn.close()

    @classmethod
    def get_all_records(cls):
        cls.ensure_table_exists()
        conn = pyodbc.connect(cls.CONN_STR)
        cursor = conn.cursor()
        cursor.execute("""
            SELECT PlayerID, FirstName, LastName, Score, Wins, Losses, GamesPlayed, LastUpdated
            FROM Leaderboards
            ORDER BY Score DESC
        """)
        rows = cursor.fetchall()
        conn.close()
        return rows

    @classmethod
    def search_leaderboard_records(cls, search_term):
        cls.ensure_table_exists()
        conn = pyodbc.connect(cls.CONN_STR)
        cursor = conn.cursor()
        wildcard_term = f"%{search_term}%"
        cursor.execute("""
            SELECT PlayerID, FirstName, LastName, Score, Wins, Losses, GamesPlayed, LastUpdated
            FROM Leaderboards
            WHERE FirstName LIKE ? OR LastName LIKE ? OR CAST(PlayerID AS VARCHAR) LIKE ?
            ORDER BY Score DESC
        """, (wildcard_term, wildcard_term, wildcard_term))
        rows = cursor.fetchall()
        conn.close()
        return rows
