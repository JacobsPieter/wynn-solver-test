"""
Build evaluation module for the Wynncraft optimizer.

This module handles the core evaluation logic for determining build quality:
- Skill point requirement validation
- Legal item combination checking (no items that can't be used together like Qira hive items)
- Fitness calculation based on configured stats
- Build ranking and selection

Key functions implement Wynncraft-specific rules like effective HP calculation,
item combination restrictions (Hive items, Ornate Shadow, etc.), and weighted fitness scoring.
"""

import check_skill_points
from classes import *
from parser import get_skillpoints_data
#import damage_calculations

import heapq



ORNATE_SHADOW_ITEMS = {
    'Ornate Shadow Cowl',
    'Ornate Shadow Garb',
    'Ornate Shadow Cover',
    'Ornate Shadow Cloud'}
FIRE_HIVE_ITEMS = {
    "Sparkweaver",
    "Soulflare",
    "Cinderchain",
    "Mantlewalkers",
    "Clockwork",
    "Dupliblaze"}
WATER_HIVE_ITEMS = {
    "Whitecap Crown",
    "Stillwater Blue",
    "Trench Scourer",
    "Silt of the Seafloor",
    "Coral Ring",
    "Moon Pool Circlet"}
EARTH_HIVE_ITEMS = {
    "Ambertoise Shell",
    "Beetle Aegis",
    "Elder Oak Roots",
    "Humbark Moccasins",
    "Subur Clip",
    "Golemlus Core"}
THUNDER_HIVE_ITEMS = {
    "Sparkling Visor",
    "Insulated Plate Mail",
    "Static-Charged Leggings",
    "Thunderous Step",
    "Bottled Thunderstorm",
    "Lightning Flash"}
AIR_HIVE_ITEMS = {
    "Pride of the Aerie",
    "Gale's Freedom",
    "Turbine Greaves",
    "Flashstep",
    "Breezehands",
    "Vortex Bracer"}
MASTER_HIVE_ITEMS = {
    "Abyss-Imbued Leggings",
    "Boreal-Patterned Crown",
    "Anima-Infused Cuirass",
    "Chaos-Woven Greaves",
    "Elysium-Engraved Aegis",
    "Eden-Blessed Guards",
    "Gaea-Hewn Boots",
    "Hephaestus-Forged Sabatons",
    "Obsidian-Framed Helmet",
    "Twilight-Gilded Cloak",
    "Infused Hive Relik",
    "Infused Hive Wand",
    "Infused Hive Spear",
    "Infused Hive Dagger",
    "Infused Hive Bow",
    "Contrast",
    "Prowess",
    "Intensity"}
GROOKWARTS = {
    "Dragon's Eye Bracelet",
    "Draoi Fair",
    "Renda Langit"}


ATTACK_TYPES = {'melee', 'spell'}


MAX_SP_TO_INVEST = 200
MAX_SP_TO_ADD_WITH_TOMES = MAX_SP_TO_INVEST + 5
MAX_SP_TO_INVEST_PER_STAT = 100
MAX_SKILL_POINTS: int = 595
MAX_STRREQ: int = 320
MAX_DEXREQ: int = 317
MAX_INTREQ: int = 283
MAX_DEFREQ: int = 284
MAX_AGIREQ: int = 333


LARGE_NEG = -1000000000000
LARGE_POS = 1000000000000







def skill_point_fast_check(skill_points: tuple[int, int, int, int, int]) -> bool:
    str_req = skill_points[0]
    dex_req = skill_points[1]
    int_req = skill_points[2]
    def_req = skill_points[3]
    agi_req = skill_points[4]
    if str_req + dex_req + int_req + def_req + agi_req > MAX_SKILL_POINTS:
        return False
    if str_req > MAX_STRREQ:
        return False
    if dex_req > MAX_DEXREQ:
        return False
    if int_req > MAX_INTREQ:
        return False
    if def_req > MAX_DEFREQ:
        return False
    if agi_req > MAX_AGIREQ:
        return False
    return True





def legal_item_combinations(build: Build) -> bool:
    ornate_shadow = False
    master_hive = False
    fire_hive = False
    water_hive = False
    earth_hive = False
    thunder_hive = False
    air_hive = False
    grookwarts = False
    for item in build.get_all_gear():
        if item.name in ORNATE_SHADOW_ITEMS:
            if ornate_shadow:
                return False
            ornate_shadow = True
        elif item.name in MASTER_HIVE_ITEMS:
            if master_hive:
                return False
            master_hive = True
        elif item.name in FIRE_HIVE_ITEMS:
            if fire_hive:
                return False
            fire_hive = True
        elif item.name in WATER_HIVE_ITEMS:
            if water_hive:
                return False
            water_hive = True
        elif item.name in EARTH_HIVE_ITEMS:
            if earth_hive:
                return False
            earth_hive = True
        elif item.name in THUNDER_HIVE_ITEMS:
            if thunder_hive:
                return False
            thunder_hive = True
        elif item.name in AIR_HIVE_ITEMS:
            if air_hive:
                return False
            air_hive = True
        elif item.name in GROOKWARTS:
            if grookwarts:
                return False
            air_hive = True
    return True


def calculate_fitness_wrapper(build, config):
    stat_stuff = config["required_stats"]
    required_stats_names = stat_stuff["required_stats_names"]
    required_stats_minimums: dict = stat_stuff["required_stats_minimums"]
    required_stats_maximums: dict = stat_stuff["required_stats_maximums"]
    required_stats_weights: dict = stat_stuff["required_stats_weights"]
    required_stats_minimums_list = [required_stats_minimums.get(stat,LARGE_NEG) for stat in required_stats_names]
    required_stats_maximums_list = [required_stats_maximums.get(stat,LARGE_POS) for stat in required_stats_names]
    required_stats_weights_list = [required_stats_weights[stat] for stat in required_stats_names]
    fitness = calculate_fitness(build, required_stats_names, required_stats_minimums_list, required_stats_maximums_list, required_stats_weights_list)
    return fitness  

def calculate_total_hp(build: Build):
    return sum(build.get_stats_from_combined_stats(['baseHealth', 'rawHealth']))


def calculate_ehp(build: Build):
    def_mult, agi_mult = 0.867, 0.951
    _, _, _, defense, agility = build.skill_points
    sp_data = get_skillpoints_data('data\\skillpoints.csv')
    pre_effectiveness_def = float(sp_data[max(min(defense,150),0)+1][2])
    pre_effectiveness_agi = float(sp_data[max(min(agility,150),0)+1][2])
    effective_def = pre_effectiveness_def * def_mult
    effective_agi = pre_effectiveness_agi * agi_mult
    total_hp = calculate_total_hp(build)
    total_ehp = total_hp / (0.10*effective_agi + (1-effective_agi) * (1-effective_def))
    return total_ehp


""" def get_attack_damage(build: Build, attack_type: str):
    if attack_type not in ATTACK_TYPES:
        raise ValueError(f'attacktype must be in ATTACK_TYPES: {ATTACK_TYPES}')
    damage_calculations.calculate_attack_damage(build, attack_type) """






def calculate_fitness(build: Build, required_stats_names: list[str], required_stats_minimums: list[float], required_stats_maximums: list[float], required_stats_weights: list[int]) -> float:
    make_value_zero_no_more: float = 0.01
    fitness: float = 0
    new_minimums = required_stats_minimums
    new_maximums = required_stats_maximums
    for i, minimum in enumerate(required_stats_minimums):
        if minimum == 0:
            minimum += make_value_zero_no_more
            new_minimums[i] = minimum
    for i, maximum in enumerate(required_stats_maximums):
        if maximum == 0:
            maximum += make_value_zero_no_more
            new_maximums[i] = maximum

    total_weigth = sum(required_stats_weights)
    if total_weigth == 0:
        return 0
    stats_fitnesses: list[float] = []
    for stat, stat_name in enumerate(required_stats_names):

        stat_fitness: float = 0
        if stat_name == 'total_hp':
            value = calculate_total_hp(build)
        elif stat_name == 'effective_hp':
            value = calculate_ehp(build)
        else:
            value = build.get_stat_from_combined_stats(stat_name)
        
        weight: float = required_stats_weights[stat]
        minimum: float = required_stats_minimums[stat]
        maximum: float = required_stats_maximums[stat]

        if value < 0.1 and value > -0.1:
            value = value + make_value_zero_no_more

        if minimum > LARGE_NEG and maximum < LARGE_POS:
            if minimum > maximum:
                continue
            if minimum <= value and value <= maximum:
                stat_fitness = 1
            elif value > maximum:
                stat_fitness = maximum / value
            elif value < minimum:
                stat_fitness = value / minimum
            stats_fitnesses.append(stat_fitness * weight)
            continue
        if maximum < LARGE_POS and minimum <= LARGE_NEG:
            stat_fitness = maximum / value
            stats_fitnesses.append(stat_fitness * weight)
            continue
        if minimum > LARGE_NEG and maximum >= LARGE_POS:
            stat_fitness = value / minimum
            stats_fitnesses.append(stat_fitness * weight)
            continue
        if minimum <= LARGE_NEG and maximum >= LARGE_POS:
            stats_fitnesses.append(value * weight)
            continue
    
    fitness = sum(stats_fitnesses) / total_weigth
    return fitness







def evaluate_builds(max_builds_list_length: int, builds_to_evaluate: list[Build], config) -> list[Build]:
    valid_builds: list[Build] = []
    valid_build_set = set()
    for build in builds_to_evaluate:
        if not build.validated:
            if not check_skill_points.check_skillpoints(build):
                continue
            if not legal_item_combinations(build):
                continue
            build.set_fitness(calculate_fitness_wrapper(build, config))
            build.set_build_validated(True)
        if not build.get_name() in valid_build_set:
            valid_build_set.add(build.get_name())
            valid_builds.append(build)
    valid_builds = heapq.nlargest(max_builds_list_length, valid_builds, key=lambda build: build.get_fitness())
    return valid_builds
