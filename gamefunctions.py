# gamefunctions.py by Antonio Rojo

"""
Adventure module utilities.

Provides small helper functions for a simple text adventure:
- print_welcome
- print_shop_menu
- print_full_shop_menu
- purchase_item
- new_random_monster
- run_map

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
    # print a centered welcome message
    message = f"Hello, {name}!"
    print(message.center(width))


def print_shop_menu(itemName, itemPrice, item2Name, item2Price):
    # legacy item menu that i decided to keep for compatibility, not being used in the main game
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


def print_full_shop_menu(items, player_level=1):
    # small helper for quickly listing shop items with level locks
    print("Shop Items:")
    for item in items:
        min_level = item.get("min_level", 1)
        lock_note = ""
        if player_level < min_level:
            lock_note = f" (Requires level {min_level})"
        print(f"{item['name']} - {item['price']:.2f} Gold{lock_note}")
    print()


def purchase_item(itemPrice, startingMoney, quantityToPurchase=1):
    # Calculate how many items can be bought and money left over
    if itemPrice <= 0:
        return 0, startingMoney
    max_affordable = int(startingMoney / itemPrice)
    num_purchased = min(quantityToPurchase, max_affordable)
    cost = num_purchased * itemPrice
    return num_purchased, startingMoney - cost


def new_random_monster(player_level=1):
    # create a random monster with stats that scale with player level
    monster_types = [
        {
            "name": "Goblin",
            "description": "A lone, stupid goblin. It rushes you with a tiny dagger.",
            "health_range": (15, 30),
            "power_range": (5, 10),
            "money_range": (10, 50),
            "base_xp": 5,
        },
        {
            "name": "Orc",
            "description": "A hulking hunk of mass with a notched axe and a temper.",
            "health_range": (50, 80),
            "power_range": (10, 20),
            "money_range": (40, 120),
            "base_xp": 10,
        },
        {
            "name": "Vulture",
            "description": "You discover a vulture eating the remains of two orcs.",
            "health_range": (10, 20),
            "power_range": (5, 15),
            "money_range": (5, 25),
            "base_xp": 7,
        },
    ]
    template = random.choice(monster_types)

    # scale stats with player level
    level_multiplier = 1.0 + 0.25 * (player_level - 1)
    level_multiplier = max(1.0, min(level_multiplier, 3.0))

    health = int(random.randint(*template["health_range"]) * level_multiplier)
    power = int(random.randint(*template["power_range"]) * level_multiplier)
    money = int(
        random.randint(*template["money_range"])
        * (1.0 + 0.10 * (player_level - 1))
    )
    xp_reward = int(template["base_xp"] * level_multiplier)

    return {
        "name": template["name"],
        "description": template["description"],
        "health": max(1, health),
        "power": max(1, power),
        "money": max(0, money),
        "xp": max(1, xp_reward),
    }


def read_menu_choice(valid_choices):
    # prompt until the user enters one of the provided valid choices
    while True:
        choice = input("> ").strip()
        if choice in valid_choices:
            return choice
        print(f"Please choose one of: {', '.join(sorted(valid_choices))}")


def display_fight_stats(player_hp, monster):
    # player/monster combat state with a simple banner
    width = 40
    name = monster.get("name", "Monster")
    print("\n" + "=" * width)
    print(f" ENCOUNTER: {name} ".center(width, "="))
    print("=" * width)
    print(f"Your HP: {player_hp}")
    print(f"{name} HP: {monster.get('health', 0)}")
    print(f"{name} Power: {monster.get('power', 0)}")
    print("-" * width)


def choose_equipped_weapon(inventory):
    # Allow  player to choose a weapon from their inventory
    weapons = [item for item in inventory if item.get("type") == "weapon"]
    if not weapons:
        print("No weapons to equip.")
        return None
    print("\nEquip a weapon:")
    for idx, item in enumerate(weapons, 1):
        print(
            f"{idx}) {item['name']} (Durability: {item['currentDurability']}/{item['maxDurability']})"
        )
    print(f"{len(weapons)+1}) None")
    choice = input("Choose weapon number: ").strip()
    if choice.isdigit():
        choice = int(choice)
        if 1 <= choice <= len(weapons):
            return weapons[choice - 1]
    return None


def fight_monster(player_hp, player_gold, monster, inventory=None, equipped_weapon=None):
    """Run a combat encounter between the player and one monster.

    Returns player_hp, player_gold, outcome
    outcome is one of: "won", "fled", "died"
    """
    if inventory is None:
        inventory = []

    # ensure health is an int on the monster dict
    monster["health"] = int(monster.get("health", 1))
    m_pow = int(monster.get("power", 1))
    m_name = monster.get("name", "Monster")
    m_money = int(monster.get("money", 0))

    print(f"\nA monster approaches!\n\n{monster.get('description', '')}")
    while player_hp > 0 and monster["health"] > 0:
        display_fight_stats(player_hp, monster)

        print("Actions:")
        print("  1) Attack")
        print("  2) Use Health Potion")
        print("  3) Use Weapon")
        print("  4) Use Magic Stone")
        print("  5) Run")
        print("Use the numbers on your keyboard to make a selection.")
        choice = read_menu_choice({"1", "2", "3", "4", "5"})

        if choice == "5":
            print("You flee back to town!\n")
            return player_hp, player_gold, "fled"

        elif choice == "2":
            # use a potion if available
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
            # use a weapon if available and not broken
            for item in inventory:
                if item.get("type") == "weapon" and item["currentDurability"] > 0:
                    item["currentDurability"] -= 1
                    damage_bonus = int(item.get("damage_bonus", 2))
                    print(
                        f"You swing your {item['name']}! (+"
                        f"{damage_bonus} damage, Durability: "
                        f"{item['currentDurability']}/{item['maxDurability']})"
                    )
                    player_damage = random.randint(4, 8) + damage_bonus
                    break
            else:
                print("You have no working weapon! Default attack used.")
                player_damage = random.randint(4, 8)

        elif choice == "4":
            # use a magic stone for instant victory
            for item in inventory:
                if item.get("name") == "magic stone":
                    print(
                        "You used a Magic Stone! The monster is instantly defeated.\n"
                    )
                    inventory.remove(item)
                    return player_hp, player_gold + m_money, "won"
            else:
                print("No Magic Stones in inventory!\n")
            continue

        else:
            # Regular attack
            player_damage = random.randint(4, 8)

        # Exchange of damage
        monster["health"] = max(0, monster["health"] - player_damage)
        print(f"You strike the {m_name} for {player_damage} damage.")
        if monster["health"] <= 0:
            print(f"\nThe {m_name} is defeated! You loot {m_money} gold.\n")
            return player_hp, player_gold + m_money, "won"

        monster_damage = random.randint(1, max(1, m_pow))
        player_hp -= monster_damage
        print(f"The {m_name} hits you for {monster_damage} damage.\n")
        if player_hp <= 0:
            print("You collapse... You wake up in town with 1 HP and no new gold.\n")
            return 1, player_gold, "died"

    # fallback
    outcome = "won" if monster["health"] <= 0 else "fled"
    return player_hp, player_gold, outcome


def run_map(map_state):
    # show the world map and move the player around.
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("World Map")
    clock = pygame.time.Clock()

    # player, keep a right facing and left facing version
    player_image_right = None
    player_image_left = None
    try:
        img = pygame.image.load("images/player.png").convert_alpha()
        img = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
        player_image_right = img
        player_image_left = pygame.transform.flip(img, True, False)
    except (pygame.error, FileNotFoundError):
        print("Warning: could not load images/player.png, using blue rectangle.")

    # monster image
    monster_image = None
    try:
        img = pygame.image.load("images/monster.png").convert_alpha()
        monster_image = pygame.transform.scale(img, (CELL_SIZE, CELL_SIZE))
    except (pygame.error, FileNotFoundError):
        print("Warning: could not load images/monster.png, using red circle.")

    # current player image, start facing right
    current_player_image = player_image_right

    # map state setup
    player_x, player_y = map_state.get("player_pos", [0, 0])
    town_x, town_y = map_state.get("town_pos", [0, 0])
    monster_x, monster_y = map_state.get("monster_pos", [5, 5])
    monster_alive = map_state.get("monster_alive", True)

    # 2D list of tile "grass", "tree", "mountain", "town"
    terrain = map_state.get("terrain")
    if terrain is None:
        terrain = []
        for y in range(GRID_SIZE):
            row = []
            for x in range(GRID_SIZE):
                if [x, y] == [town_x, town_y]:
                    tile = "town"
                elif [x, y] == [monster_x, monster_y]:
                    # ensure starting monster tile is walkable
                    tile = "grass"
                else:
                    r = random.random()
                    if r < 0.10:
                        tile = "mountain"
                    elif r < 0.25:
                        tile = "tree"
                    else:
                        tile = "grass"
                row.append(tile)
            terrain.append(row)
        map_state["terrain"] = terrain

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
                    if player_image_left is not None:
                        current_player_image = player_image_left
                elif event.key == pygame.K_RIGHT:
                    dx = 1
                    if player_image_right is not None:
                        current_player_image = player_image_right

                # movement logic
                if dx or dy:
                    # Move Player
                    new_x = player_x + dx
                    new_y = player_y + dy
                    if 0 <= new_x < GRID_SIZE and 0 <= new_y < GRID_SIZE:
                        # cannot walk onto mountains
                        if terrain[new_y][new_x] != "mountain":
                            player_x, player_y = new_x, new_y

                            if [player_x, player_y] == [town_x, town_y]:
                                result = "town"
                                running = False
                            elif (
                                monster_alive
                                and [player_x, player_y] == [monster_x, monster_y]
                            ):
                                result = "monster"
                                running = False

                    # move Monster
                    if running and monster_alive:
                        step_dx, step_dy = random.choice(
                            [(0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)]
                        )
                        new_mx = monster_x + step_dx
                        new_my = monster_y + step_dy

                        if 0 <= new_mx < GRID_SIZE and 0 <= new_my < GRID_SIZE:
                            # monster cannot enter town or mountains
                            if (
                                [new_mx, new_my] != [town_x, town_y]
                                and terrain[new_my][new_mx] != "mountain"
                            ):
                                monster_x, monster_y = new_mx, new_my

                        # check collision AGAIN if monster walked into player
                        if [player_x, player_y] == [monster_x, monster_y]:
                            result = "monster"
                            running = False

        # draw everything
        screen.fill((0, 0, 0))

        for y in range(GRID_SIZE):
            for x in range(GRID_SIZE):
                rect = pygame.Rect(
                    x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                tile = terrain[y][x]

                # base terrain color
                if tile in ("grass", "town"):
                    pygame.draw.rect(screen, (16, 90, 16), rect)
                elif tile == "tree":
                    pygame.draw.rect(screen, (10, 60, 10), rect)
                elif tile == "mountain":
                    pygame.draw.rect(screen, (70, 70, 70), rect)

                # extra detail for trees
                if tile == "tree":
                    trunk = pygame.Rect(
                        rect.centerx - CELL_SIZE // 12,
                        rect.bottom - CELL_SIZE // 3,
                        CELL_SIZE // 6,
                        CELL_SIZE // 3,
                    )
                    pygame.draw.rect(screen, (80, 40, 10), trunk)
                    pygame.draw.circle(
                        screen,
                        (20, 120, 20),
                        (rect.centerx, rect.centery - CELL_SIZE // 6),
                        CELL_SIZE // 3,
                    )

                # extra detail for mountains
                if tile == "mountain":
                    peak = [
                        (rect.centerx, rect.top + CELL_SIZE // 6),
                        (rect.left + CELL_SIZE // 6, rect.bottom - CELL_SIZE // 6),
                        (rect.right - CELL_SIZE // 6,
                         rect.bottom - CELL_SIZE // 6),
                    ]
                    pygame.draw.polygon(screen, (120, 120, 120), peak)

                # grid lines
                pygame.draw.rect(screen, (40, 40, 40), rect, 1)

        # town marker
        town_rect = pygame.Rect(
            town_x * CELL_SIZE, town_y * CELL_SIZE, CELL_SIZE, CELL_SIZE
        )
        pygame.draw.circle(screen, (0, 255, 0),
                           town_rect.center, CELL_SIZE // 3)

        # monster
        if monster_alive:
            if monster_image is not None:
                screen.blit(
                    monster_image, (monster_x * CELL_SIZE,
                                    monster_y * CELL_SIZE)
                )
            else:
                monster_rect = pygame.Rect(
                    monster_x * CELL_SIZE, monster_y * CELL_SIZE, CELL_SIZE, CELL_SIZE
                )
                pygame.draw.circle(
                    screen, (255, 0, 0), monster_rect.center, CELL_SIZE // 3
                )

        # player
        if current_player_image is not None:
            screen.blit(current_player_image, (player_x *
                        CELL_SIZE, player_y * CELL_SIZE))
        else:
            player_rect = pygame.Rect(
                player_x * CELL_SIZE, player_y * CELL_SIZE, CELL_SIZE, CELL_SIZE
            )
            pygame.draw.rect(screen, (0, 0, 255), player_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

    # update map state before returning
    map_state["player_pos"] = [player_x, player_y]
    map_state["town_pos"] = [town_x, town_y]
    map_state["monster_pos"] = [monster_x, monster_y]
    map_state["monster_alive"] = monster_alive
    map_state["terrain"] = terrain

    return result, map_state
