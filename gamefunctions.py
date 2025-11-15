# gamefunctions.py by Antonio Rojo

"""
Adventure module utilities.

Provides small helper functions for a simple text adventure:
- print_welcome
- print_shop_menu
- purchase_item
- new_random_monster

Intended to be imported by game.py.
"""

import random
import pygame
import sys

# map constants
GRID_SIZE = 10
CELL_SIZE = 32
WINDOW_SIZE = (GRID_SIZE * CELL_SIZE, GRID_SIZE * CELL_SIZE)


def print_welcome(name, width):
    """Print a centered welcome message."""
    message = f"Hello, {name}!"
    print(message.center(width))


def print_shop_menu(itemName, itemPrice, item2Name, item2Price):
    """Display a simple two-item shop menu with prices."""
    print("/------------------------\\")
    if itemName:
        price1_str = f"{itemPrice:.2f}"
        padding1 = 20 - len(itemName) - len(price1_str)
        print(f"| {itemName}{' ' * padding1}{price1_str} |")
    if item2Name:
        price2_str = f"{item2Price:.2f}"
        padding2 = 20 - len(item2Name) - len(price2_str)
        print(f"| {item2Name}{' ' * padding2}{price2_str} |")
    print("\\------------------------/")


def print_full_shop_menu(items):
    """Print all available shop items with names and prices."""
    print("Shop Items:")
    for item in items:
        print(f"{item['name']} - {item['price']:.2f} Gold")
    print()


def purchase_item(itemPrice, startingMoney, quantityToPurchase=1):
    """Calculate how many items can be bought and money left over."""
    if itemPrice <= 0:
        return 0, startingMoney
    max_affordable = int(startingMoney / itemPrice)
    num_purchased = min(quantityToPurchase, max_affordable)
    cost = num_purchased * itemPrice
    return num_purchased, startingMoney - cost


def new_random_monster():
    """Create a random monster with simple stats."""
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
            "power_range": (10, 20),
            "money_range": (40, 120),
        },
        {
            "name": "Vulture",
            "description": "You discover a vulture eating the remains of two orcs.",
            "health_range": (10, 20),
            "power_range": (5, 15),
            "money_range": (5, 25),
        },
    ]
    template = random.choice(monster_types)
    return {
        "name": template["name"],
        "description": template["description"],
        "health": random.randint(*template["health_range"]),
        "power": random.randint(*template["power_range"]),
        "money": random.randint(*template["money_range"]),
    }


def read_menu_choice(valid_choices):
    """Prompt until the user enters one of the provided valid choices."""
    while True:
        choice = input("> ").strip()
        if choice in valid_choices:
            return choice
        print(f"Please choose one of: {', '.join(sorted(valid_choices))}")


def display_fight_stats(player_hp, monster):
    """Pretty-print player/monster combat state."""
    print("\n-- Combat --")
    print(f"Your HP: {player_hp}")
    print(f"{monster['name']} HP: {monster.get('health', 0)}")
    print(f"Power: {monster.get('power', 0)}")


def choose_equipped_weapon(inventory):
    """Allow the player to choose a weapon from their inventory."""
    weapons = [item for item in inventory if item.get("type") == "weapon"]
    if not weapons:
        print("No weapons to equip.")
        return None
    print("\nEquip a weapon:")
    for idx, item in enumerate(weapons, 1):
        print(
            f"{idx}) {item['name']} (Durability: {item['currentDurability']}/{item['maxDurability']})")
    print(f"{len(weapons)+1}) None")
    choice = input("Choose weapon number: ").strip()
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(weapons):
            return weapons[choice - 1]
    return None


def fight_monster(player_hp, player_gold, monster, inventory=None, equipped_weapon=None):
    """Run a combat encounter between the player and one monster."""
    if inventory is None:
        inventory = []

    m_hp = int(monster.get("health", 1))
    m_pow = int(monster.get("power", 1))
    m_name = monster.get("name", "Monster")
    m_money = int(monster.get("money", 0))

    print(f"\nA monster approaches!\n\n{monster.get('description', '')}")
    while player_hp > 0 and m_hp > 0:
        display_fight_stats(player_hp, monster)

        print("Choose an action:")
        print("  1) Attack")
        print("  2) Use Health Potion")
        print("  3) Use Sword")
        print("  4) Use Magic Stone")
        print("  5) Run")
        choice = read_menu_choice({"1", "2", "3", "4", "5"})

        if choice == "5":
            print("You flee back to town!\n")
            return player_hp, player_gold

        elif choice == "2":
            # Use a potion if available
            for item in inventory:
                if item["name"] == "health potion":
                    player_hp = min(player_hp + 15, 30)
                    inventory.remove(item)
                    print("You used a health potion and recovered 15 HP!\n")
                    break
            else:
                print("You have no health potions!\n")
            continue

        elif choice == "3":
            # Use a sword if available and not broken
            for item in inventory:
                if item.get("type") == "weapon" and item["currentDurability"] > 0:
                    item["currentDurability"] -= 1
                    print(
                        f"You swing your {item['name']}! (+2 damage, Durability: {item['currentDurability']}/{item['maxDurability']})"
                    )
                    player_damage = random.randint(4, 8) + 2
                    break
            else:
                print("You have no working sword! Default attack used.")
                player_damage = random.randint(4, 8)

        elif choice == "4":
            # Use a magic stone for instant victory
            for item in inventory:
                if item.get("name") == "magic stone":
                    print(
                        "You used a Magic Stone! The monster is instantly defeated.\n")
                    inventory.remove(item)
                    return player_hp, player_gold + m_money
            else:
                print("No Magic Stones in inventory!\n")
            continue

        else:
            # Regular attack
            player_damage = random.randint(4, 8)

        # Exchange of damage
        m_hp -= player_damage
        print(f"You strike the {m_name} for {player_damage} damage.")
        if m_hp <= 0:
            print(f"\nThe {m_name} is defeated! You loot {m_money} gold.\n")
            return player_hp, player_gold + m_money

        monster_damage = random.randint(1, max(1, m_pow))
        player_hp -= monster_damage
        print(f"The {m_name} hits you for {monster_damage} damage.\n")
        if player_hp <= 0:
            print("You collapse... You wake up in town with 1 HP and no new gold.\n")
            return 1, player_gold

    return player_hp, player_gold


def run_map(map_state):
    # pygame map loop
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("World Map")
    clock = pygame.time.Clock()

    player_x, player_y = map_state.get("player_pos", [0, 0])
    town_x, town_y = map_state.get("town_pos", [0, 0])
    monster_x, monster_y = map_state.get("monster_pos", [5, 5])
    monster_alive = map_state.get("monster_alive", True)

    result = None
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                dx, dy = 0, 0
                if event.key == pygame.K_UP:
                    dy = -1
                elif event.key == pygame.K_DOWN:
                    dy = 1
                elif event.key == pygame.K_LEFT:
                    dx = -1
                elif event.key == pygame.K_RIGHT:
                    dx = 1

                if dx or dy:
                    new_x = player_x + dx
                    new_y = player_y + dy
                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                        player_x, player_y = new_x, new_y
                        if [player_x, player_y] == [town_x, town_y]:
                            result = "town"
                            running = False
                        elif monster_alive and [player_x, player_y] == [monster_x, monster_y]:
                            result = "monster"
                            running = False

        # draw background
        screen.fill((0, 0, 0))

        # draw grid
        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE,
                                   CELL_SIZE, CELL_SIZE)
                pygame.draw.rect(screen, (50, 50, 50), rect, 1)

        # draw town
        town_rect = pygame.Rect(town_x * CELL_SIZE, town_y *
                                CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.circle(screen, (0, 255, 0),
                           town_rect.center, CELL_SIZE // 3)

        # draw monster if alive
        if monster_alive:
            monster_rect = pygame.Rect(monster_x * CELL_SIZE, monster_y *
                                       CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.circle(screen, (255, 0, 0),
                               monster_rect.center, CELL_SIZE // 3)

        # draw player
        player_rect = pygame.Rect(player_x * CELL_SIZE, player_y *
                                  CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (0, 0, 255), player_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

    map_state["player_pos"] = [player_x, player_y]
    map_state["town_pos"] = [town_x, town_y]
    map_state["monster_pos"] = [monster_x, monster_y]
    map_state["monster_alive"] = monster_alive

    return result, map_state
