# gamefunctions.py by Antonio Rojo

"""
Adventure module utilities.

Provides small helper functions for a simple text adventure:
- print_welcome
- print_shop_menu
- purchase_item
- new_random_monster
- run_map (now supports multiple persistent wandering monsters)
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
    """Create a random monster with simple stats (returns a simple dict)."""
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


# -------------------
# Wandering monster support
# -------------------
class WanderingMonster:
    """Simple class to represent a wandering monster on the grid."""

    TYPE_COLORS = {
        "Goblin": (0, 200, 0),
        "Orc": (180, 20, 20),
        "Vulture": (200, 200, 0),
    }

    def __init__(self, x, y, template=None):
        # template can be the dict returned by new_random_monster()
        if template is None:
            template = new_random_monster()
        self.name = template.get("name", "Monster")
        self.description = template.get("description", "")
        self.health = int(template.get("health", 10))
        self.power = int(template.get("power", 2))
        self.money = int(template.get("money", 0))
        self.x = x
        self.y = y
        self.alive = True
        self.color = self.TYPE_COLORS.get(self.name, (255, 255, 255))

    def to_dict(self):
        """Return a serializable dict for persistence in map_state."""
        return {
            "name": self.name,
            "description": self.description,
            "health": self.health,
            "power": self.power,
            "money": self.money,
            "pos": [self.x, self.y],
            "alive": self.alive,
            "color": list(self.color),
        }

    @classmethod
    def from_dict(cls, d):
        m = cls(0, 0, template={
            "name": d.get("name"),
            "description": d.get("description", ""),
            "health_range": (d.get("health", 1), d.get("health", 1)),
            "power_range": (d.get("power", 1), d.get("power", 1)),
            "money_range": (d.get("money", 0), d.get("money", 0)),
        })
        # overwrite fields to match the dict
        pos = d.get("pos", [0, 0])
        m.x, m.y = pos[0], pos[1]
        m.health = int(d.get("health", m.health))
        m.power = int(d.get("power", m.power))
        m.money = int(d.get("money", m.money))
        m.alive = bool(d.get("alive", True))
        m.color = tuple(d.get("color", list(m.color)))
        return m

    def move(self, grid_size, town_pos, occupied_positions=None):
        """Attempt to move the monster one cell in a random direction.
        Will not move into the town square. occupied_positions is a set of (x,y) tuples to avoid."""
        if not self.alive:
            return
        if occupied_positions is None:
            occupied_positions = set()

        directions = [(0, -1), (0, 1), (-1, 0), (1, 0),
                      (0, 0)]  # allow staying still
        random.shuffle(directions)
        for dx, dy in directions:
            nx = self.x + dx
            ny = self.y + dy
            # valid
            if 0 <= nx < grid_size and 0 <= ny < grid_size:
                if [nx, ny] == list(town_pos):
                    continue
                if (nx, ny) in occupied_positions:
                    continue
                # adopt new position
                self.x = nx
                self.y = ny
                return


def _spawn_two_monsters(player_pos, town_pos, existing_positions=None):
    """Helper to create two WanderingMonster instances in random positions not on player/town."""
    monsters = []
    existing_positions = existing_positions or set()
    attempts = 0
    while len(monsters) < 2 and attempts < 200:
        attempts += 1
        x = random.randrange(GRID_SIZE)
        y = random.randrange(GRID_SIZE)
        if [x, y] == list(player_pos) or [x, y] == list(town_pos):
            continue
        if (x, y) in existing_positions:
            continue
        # create monster
        wm = WanderingMonster(x, y)
        monsters.append(wm)
        existing_positions.add((x, y))
    # fallback: can't find distinct places, place deterministically
    while len(monsters) < 2:
        x = (player_pos[0] + len(monsters) + 2) % GRID_SIZE
        y = (player_pos[1] + len(monsters) + 2) % GRID_SIZE
        if [x, y] != list(town_pos):
            monsters.append(WanderingMonster(x, y))
    return monsters


def run_map(map_state):
    pygame.init()
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("World Map")
    clock = pygame.time.Clock()

    # load persisted state (or defaults)
    player_x, player_y = map_state.get("player_pos", [0, 0])
    town_x, town_y = map_state.get("town_pos", [0, 0])

    # load monsters list from map_state if present
    monsters_data = map_state.get("monsters")
    monsters = []
    if monsters_data:
        for d in monsters_data:
            monsters.append(WanderingMonster.from_dict(d))
    else:
        # spawn two monsters on first visit
        monsters = _spawn_two_monsters([player_x, player_y], [town_x, town_y])

    # track how many player moves have happened so we move monsters every other player move
    player_moves = 0

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

                        # if entered town
                        if [player_x, player_y] == [town_x, town_y]:
                            result = "town"
                            running = False
                            break

                        # check if player stepped onto any alive monster
                        stepped_monster = None
                        for m in monsters:
                            if m.alive and [m.x, m.y] == [player_x, player_y]:
                                stepped_monster = m
                                break
                        if stepped_monster:
                            # place the monster dict in map_state so game.py can fight the exact monster
                            map_state["pending_monster"] = stepped_monster.to_dict()
                            result = "monster"
                            running = False
                            break

                        # otherwise, player moved successfully, increment move counter and possibly move monsters
                        player_moves += 1
                        if player_moves % 2 == 0:
                            # collect occupied positions to avoid monsters stacking on each other or on town
                            occupied = set()
                            for m in monsters:
                                if m.alive:
                                    occupied.add((m.x, m.y))
                            # monsters attempt to move
                            new_positions = set()
                            for m in monsters:
                                # remove its own position to allow movement
                                if (m.x, m.y) in occupied:
                                    occupied.remove((m.x, m.y))
                                m.move(GRID_SIZE, [town_x, town_y],
                                       occupied_positions=occupied)
                                new_positions.add((m.x, m.y))
                                # re-add to occupied so others won't collide
                                occupied.add((m.x, m.y))

                            # if any monster moved onto the player, initiate combat next loop
                            for m in monsters:
                                if m.alive and [m.x, m.y] == [player_x, player_y]:
                                    map_state["pending_monster"] = m.to_dict()
                                    result = "monster"
                                    running = False
                                    break
                            if not running:
                                break

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

        # draw monsters if alive
        any_alive = False
        for m in monsters:
            if m.alive:
                any_alive = True
                monster_rect = pygame.Rect(m.x * CELL_SIZE, m.y *
                                           CELL_SIZE, CELL_SIZE, CELL_SIZE)
                # color stored as tuple
                pygame.draw.circle(screen, tuple(m.color),
                                   monster_rect.center, CELL_SIZE // 3)

        # respawn two monsters if none are alive
        if not any_alive:
            # spawn two new monsters
            monsters = _spawn_two_monsters(
                [player_x, player_y], [town_x, town_y])

        # draw player
        player_rect = pygame.Rect(player_x * CELL_SIZE, player_y *
                                  CELL_SIZE, CELL_SIZE, CELL_SIZE)
        pygame.draw.rect(screen, (0, 0, 255), player_rect)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

    # persist monster state back to map_state
    map_state["player_pos"] = [player_x, player_y]
    map_state["town_pos"] = [town_x, town_y]
    map_state["monsters"] = [m.to_dict() for m in monsters]
    # pending_monster may hold the one the player walked into
    # map_state["pending_monster"] is set earlier when stepping on a monster

    return result, map_state
