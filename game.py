# game.py – main game loop driver
from gamefunctions import (
    print_welcome,
    print_shop_menu,
    print_full_shop_menu,
    purchase_item,
    new_random_monster,
    read_menu_choice,
    fight_monster,
    choose_equipped_weapon,
    run_map,
)

import json
import os


SAVE_FILE = "savefile.json"


def create_default_map_state():
    # default map data
    return {
        "player_pos": [0, 0],
        "town_pos": [0, 0],
        "monster_pos": [5, 5],
        "monster_alive": True,
    }


def save_game(money, hp, inventory, map_state):
    """Save player data to a JSON file."""
    with open(SAVE_FILE, "w") as f:
        json.dump({
            "money": money,
            "hp": hp,
            "inventory": inventory,
            "map_state": map_state,
        }, f)
    print("\nGame saved.\n")


def load_game():
    """Load player data from JSON if it exists."""
    if not os.path.exists(SAVE_FILE):
        print("\nNo saved game found.\n")
        return None
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    print("\nGame loaded.\n")
    return data


def main():
    # intro
    print("Welcome to my cool awesome game.\n")

    # Load or start new
    print("1) Start New Game\n2) Load Saved Game")
    choice = input("> ").strip()

    if choice == "2":
        data = load_game()
        if data:
            money = data.get("money", 0.0)
            hp = data.get("hp", 30)
            inventory = data.get("inventory", [])
            map_state = data.get("map_state") or create_default_map_state()
        else:
            money = 0.0
            hp = 30
            inventory = []
            map_state = create_default_map_state()
    else:
        name = input("What is your name? ")
        print()
        print_welcome(name, 30)
        print()
        try:
            money = float(input("How much gold do you have? "))
        except ValueError:
            money = 0.0
        inventory = []
        hp = 30
        map_state = create_default_map_state()

    # item prices
    health_price = 12.00
    sword_price = 20.00
    stone_price = 30.00

    # show shop items
    print_full_shop_menu([
        {"name": "Health Potion", "price": health_price},
        {"name": "Sword", "price": sword_price},
        {"name": "Magic Stone", "price": stone_price},
    ])

    def buy_item(name, price, item_data_template):
        # helper for purchasing items
        nonlocal money
        try:
            qty = int(input(f"How many {name}s do you want to buy? "))
        except ValueError:
            qty = 0
        bought, money = purchase_item(price, money, qty)
        for _ in range(bought):
            inventory.append(item_data_template.copy())

    def shop():
        # display shop and handle buying
        print(f"\nCurrent Gold: {money:.2f}")
        buy_item("Health Potion", health_price, {
                 "name": "health potion", "type": "usable"})
        buy_item("Sword", sword_price, {
                 "name": "sword", "type": "weapon", "maxDurability": 10, "currentDurability": 10})
        buy_item("Magic Stone", stone_price, {
                 "name": "magic stone", "type": "consumable", "note": "Defeats monster instantly"})
        print(f"\nGold left: {money:.2f}\n")

    shop()

    # main game loop
    max_hp = 30
    equipped_weapon = None

    while True:
        print("You are in town.")
        print(f"Current HP: {hp}, Current Gold: {money:.0f}")
        print("What would you like to do?")
        print("  1) Leave town (Explore Map)\n  2) Sleep (Restore HP for 5 Gold)\n  3) Shop\n  4) Save and Quit")
        choice = read_menu_choice({"1", "2", "3", "4"})

        if choice == "1":
            equipped_weapon = choose_equipped_weapon(inventory)
            while True:
                action, map_state = run_map(map_state)

                if action == "monster" and map_state.get("monster_alive", True):
                    before_gold = money
                    hp, money = fight_monster(
                        hp, money, new_random_monster(), inventory, equipped_weapon
                    )
                    if money > before_gold:
                        map_state["monster_alive"] = False
                    # after combat return to same place on map
                    if hp <= 0:
                        return
                    continue
                else:
                    # returned to town or just closed map
                    break

        elif choice == "2":
            # restore HP at cost of gold
            if money >= 5:
                money -= 5
                hp = max_hp
                print("You feel well rested. (+Full HP, -5 Gold)\n")
            else:
                print("Not enough gold to sleep.\n")

        elif choice == "3":
            shop()
        else:
            save_game(money, hp, inventory, map_state)
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
