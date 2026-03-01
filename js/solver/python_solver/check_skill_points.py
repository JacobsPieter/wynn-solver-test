"""
Skill point validation module for Wynncraft builds.

This module contains the complex logic for checking whether a build's skill point
requirements can be satisfied. It handles the Wynncraft skill point system where
equipment must be equipped in a specific order to meet requirements, and skill
points can only be invested up to certain limits.

Key challenges addressed:
- Equipment ordering matters for skill point requirements
- Maximum 100 SP per stat, 200 SP total from equipment
- Some items provide skill points, others only have requirements
- Guild tomes always contribute their skill points

TODO: Make it work more like the new proposed solution from wynnbuilder as this
one is influenced by it, but it seems like they found a better version I would
like to draw some inspiration from as in more recent testing I've found it to
not always produce correct results.
"""

import itertools

import human_readable_stat_names_and_indices as stat_indices
from classes import *



def check_skillpoints(build: Build):
    """
    Check if a build's skill point requirements can be satisfied.

    This is the core skill point validation logic for Wynncraft builds. It determines
    whether it's possible to equip all items in the build by finding a valid equipment
    order and skill point investment strategy.

    The algorithm categorizes equipment into:
    - Fixed: Items that always contribute (guild tome, items with no requirements)
    - Consider: Items with both requirements and bonuses (tried in all permutations)
    - Noboost: Items with requirements but no bonuses (no skill points provided)
    - Weapon: Always equipped last

    It tries all possible orderings of equipment that need consideration, calculating
    the minimum skill points needed to meet requirements while respecting Wynncraft's
    limits (100 SP max per stat invested yourself, 200 SP total to invest, items can go
    over these limits).

    Args:
        build: The Build object to validate

    Returns:
        bool: True if the build can be equipped with valid skill point investment,
              False otherwise. Also sets build.skill_points and build.skill_points_applied
              to the optimal skill point allocation if possible.
    """
    weapon_item = build.weapon
    equipment_items = build.get_all_gear()[:-1]
    tome = build.guild_tome
    
    weapon_item_sp = (weapon_item.name, (weapon_item.get_skillpoints(), weapon_item.get_skillpoints_requirements()))
    equipment_items_sp = [(item.name, (item.get_skillpoints(), item.get_skillpoints_requirements())) for item in equipment_items]
    tome_sp = (tome.name, (tome.get_skillpoints(), tome.get_skillpoints_requirements()))

    fixed = [tome_sp]
    consider = []
    noboost = []
    for name, (skillpoints, reqs) in equipment_items_sp:
        if all(x==0 for x in reqs):
            fixed.append((name, (skillpoints, reqs)))
        elif all(x <= 0 for x in skillpoints):
            noboost.append((name, (skillpoints, reqs)))
        else:
            consider.append((name, (skillpoints, reqs)))
    
    sp_base = [0, 0, 0, 0, 0]
    for name, (skillpoints, reqs) in fixed:
        for i in range(5):
            sp_base[i] += skillpoints[i]
    

    least_applied = [0, 0, 0, 0, 0]
    least_applied_total = 0
    possible = False

    permutations = itertools.permutations(consider)
    for perm in permutations:
        current_sp = sp_base.copy()
        feasible = True
        applied_sp = [0, 0, 0, 0, 0]
        total_applied = 0
        for name, (skillpoints, reqs) in perm:
            needed_sp = [0, 0, 0, 0, 0]
            for i in range(5):
                if current_sp[i] < reqs[i] and reqs[i] > 0:
                    needed_sp[i] += reqs[i] - current_sp[i]
                    total_applied += needed_sp[i]
                    current_sp[i] += needed_sp[i]
                    applied_sp[i] += needed_sp[i]
            if not all(sp_applied <= 100 for sp_applied in applied_sp) or total_applied > 200:
                feasible = False
                break
            else:
                for i in range(5):
                    current_sp[i] += skillpoints[i]
        if not feasible:
            continue
        for name, (skillpoints, reqs) in noboost + [weapon_item_sp]:
            needed_sp = [0, 0, 0, 0, 0]
            for i in range(5):
                if current_sp[i] < reqs[i]:
                    needed_sp[i] += reqs[i] - current_sp[i]
                    total_applied += needed_sp[i]
                    current_sp[i] += needed_sp[i]
                    applied_sp[i] += needed_sp[i]
            if not all(sp_applied <= 100 for sp_applied in applied_sp) or total_applied > 200:
                feasible = False
                break
            else:
                for i in range(5):
                    current_sp[i] += skillpoints[i]
        if not feasible:
            continue
        total_reqs = build.get_combined_skill_point_requirements()
        needed_extra_sp = [0, 0, 0, 0, 0]
        for i, sp in enumerate(current_sp):
            if sp < total_reqs[i] and total_reqs[i] > 0:
                needed_extra_sp[i] += total_reqs[i] - current_sp[i]
                total_applied += needed_extra_sp[i]
                current_sp[i] += needed_extra_sp[i]
                applied_sp[i] += needed_extra_sp[i]
        if not all(sp_applied <= 100 for sp_applied in applied_sp) or sum(sp_applied for sp_applied in applied_sp) > 200:
            continue
        possible = True
        if least_applied_total < total_applied:
            least_applied_total = total_applied
            least_applied = applied_sp
            build.skill_points = current_sp
            build.skill_points_applied = least_applied
    return possible
