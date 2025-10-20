# gamefunctions.py by Antonio Rojo

"""
Adventure module utilities.

Provides small helper functions for a simple text adventure:
- print_welcome
- print_shop_menu
- purchase_item
- new_random_monster

Intended to be imported by game.py; when run directly it executes
simple self-tests.

Dependencies:
    random (standard library)
"""

import random


def print_welcome(name, width):
    """Print a centered welcome message.

    Args:
        name (str): Player's name to greet.
        width (int): Total width used to center the message.

    Returns:
        None
    """
    message = f"Hello, {name}!"
    print(message.center(width))


def print_shop_menu(item1Name, item1Price, item2Name, item2Price):
    """Display a simple two-item shop menu with prices.

    Args:
        item1Name (str): Name of the first item.
        item1Price (float): Price of the first item.
        item2Name (str): Name of the second item.
        item2Price (float): Price of the second item.

    Returns:
        None
    """
    print("/----------------------\\")
    price1_str = f"${item1Price:.2f}"
    padding1 = 20 - len(item1Name) - len(price1_str)
    print(f"| {item1Name}{' ' * padding1}{price1_str} |")

    price2_str = f"${item2Price:.2f}"
    padding2 = 20 - len(item2Name) - len(price2_str)
    print(f"| {item2Name}{' ' * padding2}{price2_str} |")

    print("\\----------------------/")


def purchase_item(itemPrice, startingMoney, quantityToPurchase=1):
    """Calculate how many items can be bought and money left over.

    Args:
        itemPrice (float): Cost of a single item. Must be > 0 to buy.
        startingMoney (float): Amount of money available.
        quantityToPurchase (int, optional): Desired quantity.
            Defaults to 1.

    Returns:
        tuple[int, float]: Number purchased, and remaining money.
    """
    if itemPrice <= 0:
        num_purchased = 0
    else:
        max_affordable = int(startingMoney / itemPrice)
        num_purchased = min(quantityToPurchase, max_affordable)

    cost = num_purchased * itemPrice
    money_remaining = startingMoney - cost

    return num_purchased, money_remaining


def new_random_monster():
    """Create a random monster with simple stats.

    Returns:
        dict: Monster data with keys:
            - 'name' (str)
            - 'description' (str)
            - 'health' (int)
            - 'power' (int)
            - 'money' (int)
    """
    monster_types = [
        {
            "name": "Goblin",
            "description": "A lone, stupid goblin. It rushes you with a tiny dagger.",
            "health_range": (15, 30),
            "power_range": (5, 10),
            "money_range": (10, 50),
        },
        {
            "name": "Orc",
            "description": "A hulking hunk of mass with a notched axe and a temper.",
            "health_range": (50, 80),
            "power_range": (12, 20),
            "money_range": (40, 120),
        },
        {
            "name": "Vulture",
            "description": "You discover a vulture eating the remains of two orcs.",
            "health_range": (10, 20),
            "power_range": (8, 15),
            "money_range": (5, 25),
        },
    ]

    template = random.choice(monster_types)

    monster = {
        "name": template["name"],
        "description": template["description"],
        "health": random.randint(
            template["health_range"][0], template["health_range"][1]
        ),
        "power": random.randint(
            template["power_range"][0], template["power_range"][1]
        ),
        "money": random.randint(
            template["money_range"][0], template["money_range"][1]
        ),
    }

    return monster


def test_functions():
    """Run simple tests for all module functions."""
    print("--- Testing print_welcome() ---")
    print_welcome("Peter", 20)
    print_welcome("Brian", 30)
    print_welcome("Lois", 40)
    print("\n")

    print("--- Testing print_shop_menu() ---")
    print_shop_menu("Apple", 31, "Pear", 1.234)
    print()
    print_shop_menu("Egg", 0.23, "Bag of Oats", 12.34)
    print()
    print_shop_menu("Health Potion", 50, "Mana Potion", 49.95)
    print("\n")

    print("--- Testing purchase_item() ---")
    num_bought, cash_left = purchase_item(123, 1000, 3)
    print("Attempting to buy 3 items for 123 each with 1000:")
    print(f"Items purchased: {num_bought}, Money remaining: {cash_left}\n")

    num_bought, cash_left = purchase_item(123, 201, 3)
    print("Attempting to buy 3 items for 123 each with 201:")
    print(f"Items purchased: {num_bought}, Money remaining: {cash_left}\n")

    num_bought, cash_left = purchase_item(123, 1000)
    print("Attempting to buy a default of 1 item for 123 with 1000:")
    print(f"Items purchased: {num_bought}, Money remaining: {cash_left}\n")

    print("--- Testing new_random_monster() ---")
    monster_1 = new_random_monster()
    print(f"A wild {monster_1['name']} appears!")
    print(f"{monster_1['description']}")
    print(
        f"Stats -> Health: {monster_1['health']}, "
        f"Power: {monster_1['power']}, Money: {monster_1['money']}\n"
    )

    monster_2 = new_random_monster()
    print(f"A wild {monster_2['name']} appears!")
    print(f"{monster_2['description']} ")
    print(
        f"Stats -> Health: {monster_2['health']}, "
        f"Power: {monster_2['power']}, Money: {monster_2['money']}\n"
    )

    monster_3 = new_random_monster()
    print(f"A wild {monster_3['name']} appears!")
    print(f"{monster_3['description']}")
    print(
        f"Stats -> Health: {monster_3['health']}, "
        f"Power: {monster_3['power']}, Money: {monster_3['money']}\n"
    )


if __name__ == "__main__":
    # Run tests only when executed directly, not when imported.
    test_functions()
