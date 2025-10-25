# game.py – main game loop driver
from gamefunctions import (
    print_welcome,
    print_shop_menu,
    purchase_item,
    new_random_monster,
    read_menu_choice,
    fight_monster,
)


def main():
    # intro
    print("Welcome to my cool awesome game.\n")
    name = input("What is your name? ")
    print()
    print_welcome(name, 30)
    print()

    item1, price1 = "Health Potion", 12.00
    item2, price2 = "Mana Potion", 10.00
    print_shop_menu(item1, price1, item2, price2)
    print()

    # gold and quantity inputs
    try:
        money = float(input("How much gold do you have? "))
    except ValueError:
        money = 0.0
    try:
        qty = int(input(f"How many {item1}s would you like to buy? "))
    except ValueError:
        qty = 0
    bought, money = purchase_item(price1, money, qty)
    print(f"You bought {bought} {item1}(s). Gold left: {money:.2f}\n")

    # main game loop
    hp, max_hp = 30, 30
    while True:
        print("You are in town.")
        print(f"Current HP: {hp}, Current Gold: {money:.0f}")
        print("What would you like to do?")
        print(
            "  1) Leave town (Fight Monster)\n  2) Sleep (Restore HP for 5 Gold)\n  3) Quit")
        choice = read_menu_choice({"1", "2", "3"})

        if choice == "1":
            hp, money = fight_monster(hp, money, new_random_monster())
        elif choice == "2":
            if money >= 5:
                money -= 5
                hp = max_hp
                print("You feel well rested. (+Full HP, -5 Gold)\n")
            else:
                print("Not enough gold to sleep.\n")
        else:  # "3"
            print("Thanks for playing!")
            break


if __name__ == "__main__":
    main()
