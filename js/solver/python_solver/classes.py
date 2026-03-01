"""
Classes module defining the data structures for Wynncraft items and builds.

This module provides the core object model for representing Wynncraft game items
and character builds. It handles item statistics, skill point requirements, and
build composition.

Key classes:
- Item: Base class for all equippable items with stats and requirements
- Gear hierarchy: Armour, Accessory, Weapon classes with specific properties
- Tome: Special items that provide some stat bonuses
- Build: Complete character equipment set with combined statistics

All item stats are stored as numpy arrays for efficient computation, indexed
according to the stat names defined in human_readable_stat_names_and_indices.
"""

import human_readable_stat_names_and_indices as stat_indices

import itertools
import numpy as np


class Item:
    """
    Base class representing any equippable item in Wynncraft.

    Items contain statistics, skill point requirements, and other properties.
    Statistics are stored as a numpy array for efficient computation and
    indexed according to the stat names defined in stat_indices.

    Attributes:
        name: Item name
        id: Item ID
        type: Item type (weapon, helmet, etc.)
        category: Item category (optional)
        base_health: Base health value (optional)
        raw_health: Raw health identification (optional)
    
    TODO: make sure the classes work with the new item file, provided by the wynncraft api itself
    base_health and raw_health still don't work, and the old implementation with the np arrays messed up
    by using the new itemfile
    """

    def __init__(self, item: dict) -> None:
        self.name = item['name']
        self.id = item['id']
        self.type = item['type']
        match item['type']:
            case 'weapon':
                self.sub_type = item['weaponType']
            case 'armour':
                self.sub_type = item['armourType']
            case 'accessory':
                self.sub_type = item['accessoryType']
            case 'tome':
                self.sub_type = item['tomeType']
            case _:
                print('forgot to implement the correct subtype for this item, create an issue')
        if not item.get('category', None) == None:
            self.category = item['category']
        
        
        self.__stats = self.__get_item_stats_from_dict(item)
        self.__skillpoints_requirements = tuple(self.get_stats_list(['strength', 'dexterity', 'intelligence', 'defence', 'agility']))
        self.__skillpoints = tuple(self.get_stats_list(['rawStrength', 'rawDexterity', 'rawIntelligence', 'rawDefence', 'rawAgility']))
    
    def __str__(self):
        return f'{self.name}, {self.__stats}'
    
    def __get_item_stats_from_dict(self, item: dict) -> np.ndarray:
        flattened_item = self.__get_flattened_stat_dict(item)
        stats_list = [flattened_item.get(stat_key, 0) for stat_key in stat_indices.WYNNAPI_STAT_NAMES]
        stats = np.array(stats_list, int)
        return stats

    def __get_flattened_stat_dict(self, item: dict) -> dict:
        return_dict: dict = {}
        for key, value in item.items():
            match key:
                case 'requirements':
                    for sub_key, sub_value in value.items():
                        return_dict[sub_key] = sub_value
                case 'identifications':
                    for sub_key, sub_value in value.items():
                        return_dict[sub_key] = sub_value.get('max') if isinstance(sub_value, dict) else sub_value
                case 'base':
                    for sub_key, sub_value in value.items():
                        #TODO: make it so the base damage of a weapon gets imported correctly (maybe by making it a weapon only attribute... don't know yet) i'll fix when implementing the actual damage calculations
                        return_dict[sub_key] = sub_value.get('max') if isinstance(sub_value, dict) else sub_value
                case _:
                    return_dict[key] = value
        return return_dict
    
    def get_skillpoints_requirements(self) -> tuple:
        return self.__skillpoints_requirements

    def get_skillpoints(self) -> tuple:
        return self.__skillpoints
    
    def get_all_stats(self):
        return self.__stats

    def get_stat(self, stat: str):
        value = self.__stats[stat_indices.get_stat_pos(stat)]
        return value
    
    def get_stats_list(self, stats: list[str]):
        values: list[int] = [self.__stats[stat_indices.get_stat_pos(stat)] for stat in stats]
        return values


class Gear(Item):
    def __init__(self, item: dict) -> None:
        super().__init__(item)
        self.majorid = item.get('majorid', '')

    def get_majorid(self):
        return self.majorid


class Powderable(Gear):
    def __init__(self, item: dict) -> None:
        super().__init__(item)
        self.powderslots = self.get_stat('powderSlots')


class Armour(Powderable):
    def __init__(self, item: dict) -> None:
        super().__init__(item)
        self.subtype = item['armourType']


class Accessory(Gear):
    def __init__(self, item: dict) -> None:
        super().__init__(item)
        self.subtype = item['accessoryType']


class Weapon(Powderable):
    def __init__(self, item: dict) -> None:
        super().__init__(item)
        match item['weaponType']:
            case 'bow':
                self.sub_type = 'bow'
                self.character_class = 'Archer'
            case 'spear':
                self.sub_type = 'spear'
                self.character_class = 'Warrior'
            case 'wand':
                self.sub_type = 'wand'
                self.character_class = 'Mage'
            case 'dagger':
                self.sub_type = 'dagger'
                self.character_class = 'Assassin'
            case 'relik':
                self.sub_type = 'relik'
                self.character_class = 'Shaman'
            case _:
                raise ValueError
        
        self.damages = self.__get_damages(item)
        self.attackspeed = self.__get_attackspeed(item)

        self.powderslots = self.get_stat('powderSlots')

    def __get_damages(self, item: dict) -> np.ndarray:
        damages = np.array([[0, 0] for _ in range(6)])
        damage_types: list[str] = ['neutral', 'earth', 'thunder', 'water', 'fire', 'air']
        if not item.get('base', None) == None:
            for i, damage in enumerate(damage_types):
                if damage == 'neutral':
                    if not item['base'].get(f'baseDamage', None) == None:
                        damages[i] = [item['base']['baseDamage']['min'], item['base']['baseDamage']['max']]
                        continue
                if not item['base'].get(f'base{damage.capitalize()}Damage', None) == None:
                    damages[i] = item['base'][f'base{damage.capitalize()}Damage']['min'], item['base'][f'base{damage.capitalize()}Damage']['max']
        return damages
    
    def __get_attackspeed(self, item: dict) -> float:
        speed = 0.0
        match item['attackSpeed']:
            case 'superSlow':
                speed = 0.51
            case 'verySlow':
                speed = 0.83
            case 'slow':
                speed = 1.5
            case 'normal':
                speed = 2.05
            case 'fast':
                speed = 2.5
            case 'veryFast':
                speed = 3.1
            case 'superFast':
                speed = 4.3
            case _:
                print(f'unknown attackspeed: {item['attackSpeed']}')
        return speed



class Tome(Item):
    def __init__(self, item: dict) -> None:
        super().__init__(item)



class Build:
    """
    Represents a complete Wynncraft character build with all equipment.

    A build consists of armor pieces, accessories, a weapon, and various tomes.
    Provides methods for calculating combined statistics, fitness evaluation,
    and item management.

    Attributes:
        armour: List of 4 armor pieces [helmet, chestplate, leggings, boots]
        accessories: List of 4 accessories [ring1, ring2, bracelet, necklace]
        weapon: Single weapon item
        tomes: Nested list of tome collections by type
        validated: Whether build passes skill point and item combination checks
        skill_points: Current skill point allocation (used for eg. ehp calculation)
    """

    def __init__(self, armour: list[Armour], accessories: list[Accessory], weapon: Weapon, tomes: list[list[Tome]]):
        self.armour = armour
        self.helmet, self.chestplate, self.leggings, self.boots = tuple(self.armour)
        self.accessories = accessories
        self.ring1, self.ring2, self.bracelet, self.necklace = tuple(self.accessories)
        self.weapon = weapon

        self.tomes = tomes
        self.armour_tomes: list[Tome] = self.tomes[0]
        self.weapon_tomes: list[Tome] = self.tomes[1]
        self.marathon_tomes: list[Tome] = self.tomes[2]
        self.expertise_tomes: list[Tome] = self.tomes[3]
        self.mysticism_tomes: list[Tome] = self.tomes[4]
        self.lootrunning_tome: Tome = self.tomes[5][0]
        self.guild_tome: Tome = self.tomes[6][0]

        self.skill_points = [0, 0, 0, 0, 0]
        self.skill_points_applied = [0, 0, 0, 0, 0]

        self.validated = False
        self.__fitness = 0
        self.__calculated_build_stats = False
        self.__calculated_skill_point_requirements = False
    
    def set_item(self, item: Armour | Accessory | Weapon | Tome, position=0):
        """
        Replace an item in the build with a new one.

        Handles the complex logic of updating different equipment slots based on item type.
        For items with multiple slots (armor pieces, rings, tomes), uses position parameter
        to determine which slot to replace.

        Args:
            item: The new item to equip
            position: Slot index for items that have multiple positions (leave to zero if
            there is only one slot for that itemtype, use as a listindex to choose a different
            slot if there are more slots for that item. (example: tomes)
        """
        match item.type:
            case 'weapon':
                if isinstance(item, Weapon):
                    self.weapon = item
            case 'armour':
                match item.sub_type:
                    case 'helmet':
                        if isinstance(item, Armour):
                            self.helmet = item
                    case 'chestplate':
                        if isinstance(item, Armour):
                            self.chestplate = item
                    case 'leggings':
                        if isinstance(item, Armour):
                            self.leggings = item
                    case 'boots':
                        if isinstance(item, Armour):
                            self.boots = item
            case 'accessory':
                match item.sub_type:
                    case 'ring':
                        if isinstance(item, Accessory):
                            if position == 0:
                                self.ring1 = item
                            else:
                                self.ring2 = item
                    case 'bracelet':
                        if isinstance(item, Accessory):
                            self.bracelet = item
                    case 'necklace':
                        if isinstance(item, Accessory):
                            self.necklace = item
            case 'tome':
                match item.sub_type:
                    case 'armour_tome':
                        if isinstance(item, Tome):
                            self.armour_tomes[position] = item
                    case 'marathon_tome':
                        if isinstance(item, Tome):
                            self.marathon_tomes[position] = item
                    case 'expertise_tome':
                        if isinstance(item, Tome):
                            self.expertise_tomes[position] = item
                    case 'mysticism_tome':
                        if isinstance(item, Tome):
                            self.mysticism_tomes[position] = item
                    case 'weapon_tome':
                        if isinstance(item, Tome):
                            self.weapon_tomes[position] = item
                    case 'lootrun_tome':
                        if isinstance(item, Tome):
                            self.lootrunning_tome = item
                    case 'guild_tome':
                        if isinstance(item, Tome):
                            self.guild_tome = item
                        
            case _:
                print('wrong typing in the code, create an issue')
        self.armour = [self.helmet, self.chestplate, self.leggings, self.boots]
        self.accessories = [self.ring1, self.ring2, self.bracelet, self.necklace]
        self.tomes = [self.armour_tomes, self.weapon_tomes, self.marathon_tomes, self.expertise_tomes, self.mysticism_tomes, [self.lootrunning_tome], [self.guild_tome]]
        

    def __str__(self):
        return f'{self.get_all_items()}'
    
    def get_name(self):
        return f'{self.get_all_items()}'
    
    def get_all_gear(self):
        return list(itertools.chain(self.armour, self.accessories, [self.weapon]))
    
    def get_all_tomes(self):
        return list(itertools.chain(self.tomes))
    
    def get_all_tomes_flattened(self):
        return list(itertools.chain.from_iterable(self.tomes))

    def get_all_items(self):
        return list(itertools.chain(self.armour, self.accessories, [self.weapon], self.get_all_tomes_flattened()))
    
    def get_combined_build_stats(self) -> np.ndarray:
        if self.__calculated_build_stats:
            return self.__combined_build_stats
        
        self.__calculated_build_stats = True
        self.__combined_build_stats = self.__combine_build_stats()
        return self.__combined_build_stats
    
    def get_stat_from_combined_stats(self, stat: str):
        value = self.get_combined_build_stats()[stat_indices.get_stat_pos(stat)]
        return value
    
    def get_stats_from_combined_stats(self, stats: list[str]):
        values = [self.get_combined_build_stats()[stat_indices.get_stat_pos(stat)] for stat in stats]
        return values
    
    def __combine_build_stats(self) -> np.ndarray:
        combined_stats = np.zeros_like(self.helmet.get_all_stats())
        for item in list(itertools.chain(self.armour, self.accessories, [self.weapon], itertools.chain.from_iterable(self.tomes))):
            combined_stats = np.add(combined_stats, item.get_all_stats())
        return combined_stats
    
    def get_fitness(self):
        return self.__fitness

    def set_fitness(self, new_fitness):
        self.__fitness = new_fitness
    
    def get_combined_skill_point_requirements(self):
        if self.__calculated_skill_point_requirements:
            return self.__combined_skill_point_requirements
        self.__combined_skill_point_requirements = self.__combine_skill_point_requirements()
        return self.__combined_skill_point_requirements
        
    def __combine_skill_point_requirements(self) -> tuple:
        str_req, dex_req, int_req, def_req, agi_req = 0, 0, 0, 0, 0
        for item in self.get_all_gear():
            str_req = max([item.get_skillpoints_requirements()[0], str_req])
            dex_req = max([item.get_skillpoints_requirements()[1], dex_req])
            int_req = max([item.get_skillpoints_requirements()[2], int_req])
            def_req = max([item.get_skillpoints_requirements()[3], def_req])
            agi_req = max([item.get_skillpoints_requirements()[4], agi_req])
        self.__calculated_skill_point_requirements = True
        return (str_req, dex_req, int_req, def_req, agi_req)

    def set_build_validated(self, value: bool):
        self.validated = value
