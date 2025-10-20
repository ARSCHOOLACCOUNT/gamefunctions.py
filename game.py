# game.py - tiny driver program for gamefunctions.py

from gamefunctions import (
    print_welcome,
    print_shop_menu,
    purchase_item,
    new_random_monster,
)


def main():
    print("Welcome to my cool awesome game.\n")
    name = input("What is your name? ")
    print()
    print_welcome(name, 30)
    print()

    # Simple shop
    item1, price1 = "Health Potion", 12.00
    item2, price2 = "Mana Potion", 10.00
    print_shop_menu(item1, price1, item2, price2)
    print()

    try:
        money = float(input("How much gold do you have? "))
    except ValueError:
        money = 0.0
    try:
        qty = int(input(f"How many {item1}s would you like to buy? "))
    except ValueError:
        qty = 0

    bought, remaining = purchase_item(price1, money, qty)
    print(f"You bought {bought} {item1}(s). Gold left: {remaining:.2f}")

    # Meet a monster
    print("\nA monster approaches!")
    m = new_random_monster()
    print(f"{m['name']}: {m['description']}")
    print(
        f"Stats -> Health: {m['health']}, "
        f"Power: {m['power']}, Money: {m['money']}"
    )


if __name__ == "__main__":
    main()
