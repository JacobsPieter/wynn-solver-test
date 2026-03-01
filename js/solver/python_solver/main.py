"""
Main module for the Wynncraft build optimization algorithm using evolutionary principles.

This module implements a genetic algorithm to find optimal Wynncraft character builds by:
1. Generating random starting builds from available gear
2. Mutating builds over multiple generations
3. Evaluating fitness based on configured stats (e.g., effective HP)
4. Selecting and retaining the best builds each generation

The algorithm respects Wynncraft constraints like skill point requirements and legal
item combinations (no illegal item combinations like items from the same hive).

Key components:
- Build initialization from item pools
- Mutation strategies for gear replacement
- Evolutionary loop with fitness-based selection
- Output of top builds as Wynnbuilder URLs

Configuration is loaded from config.json and controls algorithm parameters,
required stats, and evaluation criteria.
"""

import parser
#import encoder
import evaluate_build as evaluate
#import progressbar
from classes import *



import random as rd
import json
import itertools




with open('python rewrite\\evolution_based\\config.json', 'r') as config_file:
    config = json.load(config_file)








def initialise_build(
        helmets: list[Armour], chestplates: list[Armour], leggings: list[Armour], boots: list[Armour],
        rings: list[Accessory], bracelets: list[Accessory], necklaces: list[Accessory],
        weapons: list[Weapon],
        armour_tomes: list[Tome], weapon_tomes: list[Tome], marathon_tomes: list[Tome], expertise_tomes: list[Tome],
        mysticism_tomes: list[Tome], lootrunning_tomes: list[Tome], guild_tomes: list[Tome]):
    """
    Create a single random build by selecting one item from each equipment category.

    Randomly chooses items from the provided pools to create a complete Wynncraft build
    consisting of armor pieces, accessories, a weapon, and tomes. This represents one
    individual in the population for the evolutionary algorithm.

    Args:
        helmets: List of available helmets
        chestplates: List of available chestplates
        leggings: List of available leggings
        boots: List of available boots
        rings: List of available rings (2 will be chosen)
        bracelets: List of available bracelets
        necklaces: List of available necklaces
        weapons: List of available weapons
        armour_tomes: List of available armour tomes (4 will be chosen)
        weapon_tomes: List of available weapon tomes (2 will be chosen)
        marathon_tomes: List of available marathon tomes (2 will be chosen)
        expertise_tomes: List of available expertise tomes (2 will be chosen)
        mysticism_tomes: List of available mysticism tomes (2 will be chosen)
        lootrunning_tomes: List of available lootrunning tomes (1 will be chosen)
        guild_tomes: List of available guild tomes (1 will be chosen)

    Returns:
        Build: A complete random build with all equipment slots filled
    """

    helmet = rd.choice(helmets)
    chestplate = rd.choice(chestplates)
    legging = rd.choice(leggings)
    boot = rd.choice(boots)
    
    ring1 = rd.choice(rings)
    ring2 = rd.choice(rings)
    bracelet = rd.choice(bracelets)
    necklace = rd.choice(necklaces)
    
    weapon = rd.choice(weapons)

    armour_tomes_list = [rd.choice(armour_tomes) for _ in range(4)]
    weapon_tomes_list = [rd.choice(weapon_tomes) for _ in range(2)]
    marathon_tomes_list = [rd.choice(marathon_tomes) for _ in range(2)]
    expertise_tomes_list = [rd.choice(expertise_tomes) for _ in range(2)]
    mysticism_tomes_list = [rd.choice(mysticism_tomes) for _ in range(2)]
    lootrunning_tomes_list = [rd.choice(lootrunning_tomes)]
    guild_tomes_list = [rd.choice(guild_tomes)]
    
    
    armour = [helmet, chestplate, legging, boot]
    accessories = [ring1, ring2, bracelet, necklace]
    tomes = [armour_tomes_list, weapon_tomes_list, marathon_tomes_list, expertise_tomes_list, mysticism_tomes_list, lootrunning_tomes_list, guild_tomes_list]
    starting_build = Build(armour, accessories, weapon, tomes)
    return starting_build


def initialise_starting_builds(
        helmets: list[Armour], chestplates: list[Armour], leggings: list[Armour], boots: list[Armour],
        rings: list[Accessory], bracelets: list[Accessory], necklaces: list[Accessory],
        weapons: list[Weapon],
        armour_tomes: list[Tome], weapon_tomes: list[Tome], marathon_tomes: list[Tome], expertise_tomes: list[Tome],
        mysticism_tomes: list[Tome], lootrunning_tomes: list[Tome], guild_tomes: list[Tome],
        generate_per_iteration: int):
    """
    Generate a batch of random starting builds for the initial population.

    Creates multiple random builds by calling initialise_build repeatedly. This is used
    to create the initial population for the evolutionary algorithm before the first
    generation of mutations and selections.

    Args:
        helmets: List of available helmets
        chestplates: List of available chestplates
        leggings: List of available leggings
        boots: List of available boots
        rings: List of available rings
        bracelets: List of available bracelets
        necklaces: List of available necklaces
        weapons: List of available weapons
        armour_tomes: List of available armour tomes
        weapon_tomes: List of available weapon tomes
        marathon_tomes: List of available marathon tomes
        expertise_tomes: List of available expertise tomes
        mysticism_tomes: List of available mysticism tomes
        lootrunning_tomes: List of available lootrunning tomes
        guild_tomes: List of available guild tomes
        generate_per_iteration: Number of builds to generate in this batch

    Returns:
        list[Build]: List of randomly generated builds
    """
    starting_builds = [initialise_build(helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes,  mysticism_tomes, lootrunning_tomes, guild_tomes) for _ in range(generate_per_iteration)]
    return starting_builds


def gen_new_build_mutations(
        change_per_generation: int,
        existing_build: Build,
        helmets: list[Armour], chestplates: list[Armour], leggings: list[Armour], boots: list[Armour],
        rings: list[Accessory], bracelets: list[Accessory], necklaces: list[Accessory],
        weapons: list[Weapon],
        armour_tomes: list[Tome], weapon_tomes: list[Tome], marathon_tomes: list[Tome], expertise_tomes: list[Tome],
        mysticism_tomes: list[Tome], lootrunning_tomes: list[Tome], guild_tomes: list[Tome]):
    """
    Generate mutated versions of an existing build for evolutionary exploration.

    Creates multiple variations of a build by randomly replacing individual items.
    Each mutation replaces exactly one item with a random alternative from the
    same category. This implements the "mutation" step of the genetic algorithm.

    The mutation logic handles different item types:
    - Armor pieces: Replace one of 4 slots
    - Accessories (rings): Replace one of 2 slots
    - Accessories (bracelet/necklace): Replace single slot
    - Weapons: Replace single slot
    - Tomes: Handle based on tome type (armour tomes have 4 slots, others vary)

    Args:
        change_per_generation: Number of mutated builds to create
        existing_build: The parent build to mutate
        helmets: List of available helmets
        chestplates: List of available chestplates
        leggings: List of available leggings
        boots: List of available boots
        rings: List of available rings
        bracelets: List of available bracelets
        necklaces: List of available necklaces
        weapons: List of available weapons
        armour_tomes: List of available armour tomes
        weapon_tomes: List of available weapon tomes
        marathon_tomes: List of available marathon tomes
        expertise_tomes: List of available expertise tomes
        mysticism_tomes: List of available mysticism tomes
        lootrunning_tomes: List of available lootrunning tomes
        guild_tomes: List of available guild tomes

    Returns:
        list[Build]: List containing the original build plus change_per_generation mutations
    """
    changed_builds: list[Build] = [existing_build]
    for _ in range(change_per_generation):
        changed = Build(existing_build.armour, existing_build.accessories, existing_build.weapon, existing_build.tomes)
        list_to_choose_item_from = rd.choice([helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes,  mysticism_tomes, lootrunning_tomes, guild_tomes])
        if isinstance(list_to_choose_item_from[0], Tome):
            check_by_item = list_to_choose_item_from[0]
            match check_by_item.sub_type:
                case 'armour_tome':
                    changed.set_item(rd.choice(list_to_choose_item_from), rd.randint(0,3))
                case 'guild_tome':
                    changed.set_item(rd.choice(list_to_choose_item_from), 0)
                case 'lootrun_tome':
                    changed.set_item(rd.choice(list_to_choose_item_from), 0)
                case _:
                    changed.set_item(rd.choice(list_to_choose_item_from), rd.randint(0,1))
        elif list_to_choose_item_from[0].sub_type == 'ring':
            changed.set_item(rd.choice(list_to_choose_item_from), rd.randint(0,1))
        else:
            changed.set_item(rd.choice(list_to_choose_item_from))

        changed_builds.append(changed)
    return changed_builds



def evolution_step(
        keep_per_step: int,
        change_per_generation: int,
        current_builds: list[Build],
        helmets: list[Armour], chestplates: list[Armour], leggings: list[Armour], boots: list[Armour],
        rings: list[Accessory], bracelets: list[Accessory], necklaces: list[Accessory],
        weapons: list[Weapon],
        armour_tomes: list[Tome], weapon_tomes: list[Tome], marathon_tomes: list[Tome], expertise_tomes: list[Tome],
        mysticism_tomes: list[Tome], lootrunning_tomes: list[Tome], guild_tomes: list[Tome]):
    """
    Perform one generation of the evolutionary algorithm.

    Takes the current population of builds and creates the next generation by:
    1. Generating mutations for each build in the current population
    2. Evaluating all builds (original + mutations) for fitness
    3. Selecting the top builds to survive to the next generation

    This implements the core evolutionary loop: mutation + selection.

    Args:
        keep_per_step: Number of builds to keep for the next generation
        change_per_generation: Number of mutations to create per parent build
        current_builds: Current population of builds
        helmets: List of available helmets
        chestplates: List of available chestplates
        leggings: List of available leggings
        boots: List of available boots
        rings: List of available rings
        bracelets: List of available bracelets
        necklaces: List of available necklaces
        weapons: List of available weapons
        armour_tomes: List of available armour tomes
        weapon_tomes: List of available weapon tomes
        marathon_tomes: List of available marathon tomes
        expertise_tomes: List of available expertise tomes
        mysticism_tomes: List of available mysticism tomes
        lootrunning_tomes: List of available lootrunning tomes
        guild_tomes: List of available guild tomes

    Returns:
        list[Build]: The next generation of builds (top keep_per_step builds)
    """
    new_build_mutations = list(itertools.chain.from_iterable([gen_new_build_mutations(change_per_generation, build, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes,  mysticism_tomes, lootrunning_tomes, guild_tomes) for build in current_builds]))

    next_builds: list[Build] = evaluate.evaluate_builds(keep_per_step, new_build_mutations, config)

    return next_builds









def main():
    """
    Main entry point for the Wynncraft build optimization algorithm.

    Orchestrates the complete evolutionary algorithm process:
    1. Loads and parses item data from items.json
    2. Filters weapons (currently hardcoded to "Guardian" only)
    3. Generates initial population of random builds
    4. Runs evolutionary algorithm for configured number of generations
    5. Outputs top builds as Wynnbuilder URLs

    The algorithm uses parameters from config.json to control:
    - Population size (subjects)
    - Number of generations
    - Mutations per generation
    - Fitness evaluation criteria

    Progress is displayed via console progress bars during execution.
    """
    items = parser.parse_items('data\\items.json')

    helmets, chestplates, leggings, boots, rings, bracelets, necklaces, spears, bows, daggers, wands, reliks, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes, mysticism_tomes, lootrunning_tomes, guild_tomes = items
    weapons = list(itertools.chain(spears, bows, daggers, wands, reliks))

    # TODO: Make weapon filtering configurable instead of hardcoded
    #weapons = [item for item in weapons if item.name == "Guardian"]

    generations = config["algorithm"]["generations"]
    max_best_length = config["algorithm"]["subjects"]
    change_per_generation = config["algorithm"]["change_per_generation"]
    return_amount = config["return_length"]

    # Generate initial population
    starting_builds: list[Build] = []
    #progressbar.printProgressBar(0, max_best_length, prefix='Generating starting builds: ', suffix='Complete')
    while len(starting_builds) < max_best_length:
        starting_builds.extend(initialise_starting_builds(helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes,  mysticism_tomes, lootrunning_tomes, guild_tomes, 10))
        starting_builds = evaluate.evaluate_builds(max_best_length, starting_builds, config)
        #progressbar.printProgressBar(len(starting_builds), max_best_length, prefix='Generating starting builds: ', suffix='Complete')
    starting_builds = starting_builds[:max_best_length]

    # Run evolutionary algorithm
    #progressbar.printProgressBar(0, generations, prefix='Generating progress: ', suffix='Complete')
    current_builds = starting_builds
    resulting_builds = current_builds
    for i in range(generations):
        resulting_builds = evolution_step(max_best_length, change_per_generation, current_builds, helmets, chestplates, leggings, boots, rings, bracelets, necklaces, weapons, armour_tomes, weapon_tomes, marathon_tomes, expertise_tomes,  mysticism_tomes, lootrunning_tomes, guild_tomes)
        current_builds = resulting_builds
        #progressbar.printProgressBar(i+1, generations, prefix='Generating progress: ', suffix='Complete')

    # Output results
    for i, build in enumerate(resulting_builds):
        #print(f'{i+1}) https://wynnbuilder.github.io/builder/#{encoder.encode_build(build)}')
        if i >= return_amount-1:
            break
    input()





if __name__ == "__main__":
    main()
