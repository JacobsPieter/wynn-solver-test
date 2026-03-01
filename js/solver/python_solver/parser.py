"""
Data parsing module for Wynncraft item data.

This module handles loading and parsing of item data from JSON files, converting
raw item dictionaries into appropriate class instances (Armour, Weapon, Accessory, Tome).
It also provides utilities for loading skill point data and ID mappings.

The parser expects item data in a specific format from the Wynncraft API or
exported data files, and categorizes items by type and subtype for use by
the evolutionary algorithm.
"""

from classes import *

import json
import csv

def get_skillpoints_data(data_file: str):
    with open(data_file, mode ='r') as file:    
        csvFile = list(csv.reader(file))
        return csvFile







def get_bad_data(file_path):
    with open(file_path, 'rb') as file:
        file.seek(6137317)
        problematic_bytes = file.read(100)
        print(f"Bytes at position 6137317: {problematic_bytes}")

def get_data(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return data



def get_data_keys(item: dict, lookup=False) -> dict:
    if not lookup:
        valid_keys = [key for key in item.keys() if isinstance(item[key], (int, float))]
        return dict(zip(valid_keys, [int(item[key]) for key in valid_keys]))
    else:
        return dict(zip([key for key in item.keys() if key != 'name'], [value for (key, value) in item.items() if key != 'name']))


def make_numpy_arrays_stat_keys(category: dict[str, dict[str, int]]):
    all_keys = set()
    for stats in category.values():
        all_keys |= set(stats.keys())
    return all_keys


def get_item_id_mappings(map_file = 'data\\idmap.json'):
    with open(map_file, 'r') as file:
        data = json.load(file)
        return data

def get_tome_id_mappings(map_file = 'data\\tome_id_map.json'):
    with open(map_file, 'r') as file:
        data = json.load(file)
        return data


def get_items_and_sets(data_file) -> dict[str, dict]:
    data = get_data(data_file)
    """ items: list[dict] = data['items']
    sets: dict[str, dict] = data['sets'] """
    return data


def parse_items(data_file):
    """
    Parse item data from JSON file and categorize into appropriate collections.

    Loads item data from the specified file, maps internal names to IDs, and creates
    instances of appropriate item classes (Armour, Accessory, Weapon, Tome) organized
    by type and subtype.

    The function returns 19 separate lists, one for each combination of item type
    and subtype that's relevant for build optimization.

    Args:
        data_file: Path to the JSON file containing item data

    Returns:
        tuple: 19 lists containing categorized items:
            (helmets, chestplates, leggings, boots, rings, bracelets, necklaces,
             spears, bows, daggers, wands, reliks, armour_tomes, weapon_tomes,
             marathon_tomes, expertise_tomes, mysticism_tomes, lootrunning_tomes, guild_tomes)
    """
    items = get_items_and_sets(data_file)
    item_ids = get_item_id_mappings()
    tome_ids = get_tome_id_mappings()
    helmets: list[Armour] = []
    chestplates: list[Armour] = []
    leggings: list[Armour] = []
    boots: list[Armour] = []
    rings: list[Accessory] = []
    bracelets: list[Accessory] = []
    necklaces: list[Accessory] = []
    spears: list[Weapon] = []
    bows: list[Weapon] = []
    daggers: list[Weapon] = []
    wands: list[Weapon] = []
    reliks: list[Weapon] = []
    armour: list[Tome] = []
    weapon: list[Tome] = []
    marathon: list[Tome] = []
    expertise: list[Tome] = []
    mysticism: list[Tome] = []
    lootrunning: list[Tome] = []
    guild: list[Tome] = []
    for item_name, item_data in items.items():
        item_data['name'] = item_name
        item = item_data
        match item['type']:
            case 'armour':
                item['id'] = item_ids[item['internalName']]
                match item['armourType']:
                    case 'helmet':
                        helmets.append(Armour(item))
                    case 'chestplate':
                        chestplates.append(Armour(item))
                    case 'leggings':
                        leggings.append(Armour(item))
                    case 'boots':
                        boots.append(Armour(item))
                    case _:
                        print(f"Unknown armour type: {item['armourType']}")
            case 'accessory':
                item['id'] = item_ids[item['internalName']]
                match item['accessoryType']:
                    case 'ring':
                        rings.append(Accessory(item))
                    case 'bracelet':
                        bracelets.append(Accessory(item))
                    case 'necklace':
                        necklaces.append(Accessory(item))
                    case _:
                        print(f"Unknown accessory type: {item['accessoryType']}")
            case 'weapon':
                item['id'] = item_ids[item['internalName']]
                match item['weaponType']:
                    case 'spear':
                        spears.append(Weapon(item))
                    case 'bow':
                        bows.append(Weapon(item))
                    case 'dagger':
                        daggers.append(Weapon(item))
                    case 'wand':
                        wands.append(Weapon(item))
                    case 'relik':
                        reliks.append(Weapon(item))
                    case _:
                        print(f"Unknown weapon type: {item['weaponType']}")
            case 'tome':
                item['id'] = tome_ids[item['internalName']]
                match item['tomeType']:
                    case 'armour_tome':
                        armour.append(Tome(item))
                    case 'weapon_tome':
                        weapon.append(Tome(item))
                    case 'marathon_tome':
                        marathon.append(Tome(item))
                    case 'expertise_tome':
                        expertise.append(Tome(item))
                    case 'mysticism_tome':
                        mysticism.append(Tome(item))
                    case 'lootrun_tome':
                        lootrunning.append(Tome(item))
                    case 'guild_tome':
                        guild.append(Tome(item))
                    case _:
                        print(f"Unknown tome type: {item['tomeType']}")
            case 'ingredient':
                pass
            case 'material':
                pass
            case 'tool':
                pass
            case 'charm':
                pass
            case _:
                print(f"Unknown item type: {item['type']}")
    return helmets, chestplates, leggings, boots, rings, bracelets, necklaces, spears, bows, daggers, wands, reliks, armour, weapon, marathon, expertise, mysticism, lootrunning, guild





if __name__ == "__main__":
    get_bad_data('data\\items.json')
    parse_items("data\\items.json")
