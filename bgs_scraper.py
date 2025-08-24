'''
A simple Hearthstone Battlegrounds leaderboard scraper and GUI display using Tkinter. 
Scrapes player data based on predefined usernames and displays results in a styled window.

Made because I was tired of checking the leaderboard manually since it has no search function.
'''



import requests
import tkinter as tk
from tkinter import ttk

# --- CONFIGURATION ---
TARGETS = ["Pigduh", "SupriseIsPHI", "Keeban", "MysteryMan"]
#TARGETS = ["SupriseIsPHI"]
BASE_URL = "https://hearthstone.blizzard.com/api/community/leaderboardsData"
REGION = "US"
LEADERBOARD_ID = "battlegroundsduo"

# --- SCRAPER FUNCTION ---
def find_players(target_tags):
    found_players = []
    params = {
        "region": REGION,
        "leaderboardId": LEADERBOARD_ID,
        "page": 1
    }

    while True:
        response = requests.get(BASE_URL, params=params)
        if response.status_code != 200:
            break

        data = response.json()
        rows = data.get("leaderboard", {}).get("rows", [])
        if not rows or not target_tags:
            break

        for player in rows:
            name = player.get("accountid", "")
            for target in list(target_tags):
                if target.lower() in name.lower():
                    found_players.append({
                        "username": name,
                        "rank": player["rank"],
                        "rating": player["rating"]
                    })
                    target_tags.remove(target)
        params["page"] += 1
    return found_players

# --- GUI CARD CREATION ---
def create_gamer_card(parent, username, rank, rating):
    card = tk.Frame(parent, bg="#1e293b", bd=2, relief="solid", highlightbackground="#22c55e", highlightcolor="#22c55e", highlightthickness=2)
    card.pack(pady=8, padx=12, fill="x")

    top = tk.Frame(card, bg="#1e293b")
    top.pack(fill="x", padx=10, pady=(10, 5))

    user_icon = tk.Label(top, text="👤", bg="#22c55e", fg="black", width=3, height=1, font=("Segoe UI", 12, "bold"))
    user_icon.pack(side="left", padx=(0, 10))

    info = tk.Frame(top, bg="#1e293b")
    info.pack(side="left", fill="x", expand=True)

    name_label = tk.Label(info, text=username, font=("Courier", 12), fg="#22c55e", bg="#1e293b")
    name_label.pack(anchor="w")

    rank_rating_frame = tk.Frame(info, bg="#1e293b")
    rank_rating_frame.pack(anchor="w")

    rank_label = tk.Label(rank_rating_frame, text=f"Rank #{rank}", font=("Courier", 10), fg="#67e8f9", bg="#1e293b")
    rank_label.pack(side="left", padx=(0, 10))

    rating_label = tk.Label(rank_rating_frame, text=f"{rating} MMR", font=("Courier", 10), fg="#67e8f9", bg="#1e293b")
    rating_label.pack(side="left")

# --- MAIN TKINTER APP ---
def show_ui(players):
    root = tk.Tk()
    root.title("Hearthstone Leaderboard Lookup")
    root.configure(bg="#0f172a")

    header = tk.Label(root, text="Battlegrounds Duo Tracker", font=("Segoe UI", 16, "bold"), fg="#22c55e", bg="#0f172a", pady=10)
    header.pack()

    if players:
        for player in players:
            create_gamer_card(root, player['username'], player['rank'], player['rating'])
    else:
        no_result = tk.Label(root, text="❌ No matching players found.", fg="white", bg="#0f172a", font=("Segoe UI", 12))
        no_result.pack(pady=20)

    root.mainloop()

# --- ENTRY POINT ---
if __name__ == "__main__":
    matched_players = find_players(TARGETS.copy())
    show_ui(matched_players)
