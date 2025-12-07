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
import random  # for monster respawn positions

SAVE_FILE = "savefile.json"


def create_default_map_state():
    # default map data: single monster on the map
    return {
        "player_pos": [0, 0],
        "town_pos": [0, 0],
        "monster_pos": [5, 5],
        "monster_alive": True,
    }


def xp_for_next_level(level):
    # simple increasing XP curve
    return 10 + (level - 1) * 5


def save_game(money, hp, inventory, map_state, xp, level):
    # save player data to a JSON file
    with open(SAVE_FILE, "w") as f:
        json.dump(
            {
                "money": money,
                "hp": hp,
                "inventory": inventory,
                "map_state": map_state,
                "xp": xp,
                "level": level,
            },
            f,
        )
    print("\nGame saved.\n")


def load_game():
    # load player data from JSON if it exists
    if not os.path.exists(SAVE_FILE):
        print("\nNo saved game found.\n")
        return None
    with open(SAVE_FILE, "r") as f:
        data = json.load(f)
    print("\nGame loaded.\n")
    return data


def main():
    # intro
    print("=" * 50)
    print(" WELCOME TO MY COOL AWESOME GAME ".center(50, "="))
    print("=" * 50 + "\n")

    # Load or start new
    print("1) Start New Game")
    print("2) Load Saved Game")
    print("Use the numbers on your keyboard to make a selection.")
    choice = read_menu_choice({"1", "2"})

    if choice == "2":
        data = load_game()
        if data:
            money = data.get("money", 0.0)
            hp = data.get("hp", 30)
            inventory = data.get("inventory", [])
            map_state = data.get("map_state") or create_default_map_state()
            xp = data.get("xp", 0)
            level = data.get("level", 1)
        else:
            money = 0.0
            hp = 30
            inventory = []
            map_state = create_default_map_state()
            xp = 0
            level = 1
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
        xp = 0
        level = 1

    # item prices
    health_price = 12.00
    sword_price = 20.00
    greatsword_price = 45.00
    stone_price = 30.00

    # shop item list used for display and purchase
    shop_items_for_display = [
        {
            "name": "Health Potion",
            "price": health_price,
            "min_level": 1,
            "template": {"name": "health potion", "type": "usable"},
        },
        {
            "name": "Sword",
            "price": sword_price,
            "min_level": 1,
            "template": {
                "name": "sword",
                "type": "weapon",
                "maxDurability": 10,
                "currentDurability": 10,
                "damage_bonus": 2,
            },
        },
        {
            "name": "Magic Stone",
            "price": stone_price,
            "min_level": 2,
            "template": {
                "name": "magic stone",
                "type": "consumable",
                "note": "Defeats monster instantly",
            },
        },
        {
            "name": "Greatsword",
            "price": greatsword_price,
            "min_level": 3,
            "template": {
                "name": "greatsword",
                "type": "weapon",
                "maxDurability": 8,
                "currentDurability": 8,
                "damage_bonus": 4,
            },
        },
    ]

    # initial preview of shop inventory with level locks
    print_full_shop_menu(shop_items_for_display, level)

    def shop():
        nonlocal money
        # number-based shop; one purchase per selection
        while True:
            print("\n" + "=" * 50)
            print(" SHOP ".center(50, "="))
            print("=" * 50)
            print(f"Level {level} | Gold: {money:.2f}")
            print("SHOP (sorted by lowest to highest gold price)\n")

            sorted_items = sorted(
                shop_items_for_display, key=lambda item: item["price"]
            )
            for idx, item in enumerate(sorted_items, start=1):
                lock_text = ""
                if level < item["min_level"]:
                    lock_text = f" [LOCKED: Lv {item['min_level']}]"
                print(
                    f"{idx}. {item['name']} - {item['price']:.2f} Gold{lock_text}"
                )
            print("0. Exit shop")
            print("\nUse the numbers on your keyboard to make a selection.")

            choice_str = input("> ").strip()
            if not choice_str.isdigit():
                print("Please enter a number.\n")
                continue

            choice_num = int(choice_str)
            if choice_num == 0:
                print("You leave the shop.\n")
                break
            if not (1 <= choice_num <= len(sorted_items)):
                print("Invalid selection.\n")
                continue

            selected = sorted_items[choice_num - 1]
            if level < selected["min_level"]:
                print(
                    f"You must be at least level {selected['min_level']} "
                    f"to buy {selected['name']}.\n"
                )
                continue
            if money < selected["price"]:
                print("You do not have enough gold for that.\n")
                continue

            money -= selected["price"]
            inventory.append(selected["template"].copy())
            print(
                f"You purchased 1 {selected['name']}. "
                f"Remaining gold: {money:.2f}\n"
            )

    # open the shop once at game start
    shop()

    # main game loop
    max_hp = 30
    equipped_weapon = None

    while True:
        print("\n" + "=" * 50)
        print(" TOWN ".center(50, "="))
        print("=" * 50)
        print(
            f"Level: {level} | XP: {xp}/{xp_for_next_level(level)} | "
            f"HP: {hp}/{max_hp} | Gold: {money:.0f}"
        )
        print("-" * 50)
        print("1) Leave town (Explore Map)")
        print("2) Sleep at the inn (Restore HP for 5 Gold)")
        print("3) Visit the shop")
        print("4) Save and Quit")
        print("Use the numbers on your keyboard to make a selection.")
        choice = read_menu_choice({"1", "2", "3", "4"})

        if choice == "1":
            equipped_weapon = choose_equipped_weapon(inventory)
            while True:
                # launch overworld map (pygame window)
                action, map_state = run_map(map_state)

                # if we collided with the monster
                if action == "monster" and map_state.get("monster_alive", True):
                    monster = new_random_monster(level)

                    # run a combat encounter (text-based)
                    hp, money, outcome = fight_monster(
                        hp,
                        money,
                        monster,
                        inventory,
                        equipped_weapon,
                    )

                    if outcome == "won":
                        # award XP for defeating monster
                        xp_gain = int(monster.get("xp", 0))
                        if xp_gain > 0:
                            print(f"You gained {xp_gain} XP!")
                            xp += xp_gain

                            # handle level-ups
                            leveled_up = False
                            while xp >= xp_for_next_level(level):
                                xp -= xp_for_next_level(level)
                                level += 1
                                leveled_up = True
                                print(f"*** You reached Level {level}! ***")
                            if leveled_up:
                                print(
                                    "Monsters feel more dangerous... "
                                    "they will now be stronger.\n"
                                )

                        # monster defeated, spawn a new one elsewhere
                        print(
                            "The monster was defeated! A new one appears elsewhere."
                        )
                        map_state["monster_alive"] = True
                        map_state["monster_pos"] = [
                            random.randint(0, 9),
                            random.randint(0, 9),
                        ]
                        # stay in explore loop, go back to map again
                        continue

                    if outcome in ("fled", "died"):
                        # return player to town tile
                        town_pos = map_state.get("town_pos", [0, 0])
                        map_state["player_pos"] = town_pos
                        # hp already set by fight_monster (1 HP if died)
                        break

                    # fallback
                    continue

                else:
                    # action was "town" or window closed
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
            save_game(money, hp, inventory, map_state, xp, level)
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
