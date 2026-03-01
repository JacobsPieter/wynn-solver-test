"""
Stat name mapping utilities for Wynncraft item statistics.

This module provides mappings between human-readable stat names and their
internal short forms used in the data files taken from wynnbuilder will get
changed very quickly as I'm working on compatability with the wynnapi.
It also provides
index mappings for efficient array-based stat storage and access.

The STAT_NAMES dictionary maps descriptive names to short codes, while
STAT_INDICES provides the reverse mapping with array positions for numpy arrays.

Functions in this module handle conversion between different stat name formats
and provide index lookups for the stat arrays used throughout the codebase.
"""


def get_stat_pos(stat_name: str):
    pos = WYNNAPI_STAT_NAMES.index(stat_name)
    return pos

def get_stats_pos_list(stat_names: list[str]) -> list[int]:
    return [get_stat_pos(stat_name) for stat_name in stat_names]



WYNNAPI_STAT_NAMES: list = [
    '1stSpellCost',
    '2ndSpellCost',
    '3rdSpellCost',
    '4thSpellCost',
    'agility',
    'airDamage',
    'airDefence',
    'airMainAttackDamage',
    'airSpellDamage',
    'averageDps',
    'baseAirDefence',
    'baseEarthDefence',
    'baseFireDefence',
    'baseHealth',
    'baseThunderDefence',
    'baseWaterDefence',
    'criticalDamageBonus',
    'damage',
    'damageFromMobs',
    'defence',
    'dexterity',
    'earthDamage',
    'earthDefence',
    'earthMainAttackDamage',
    'earthSpellDamage',
    'elementalDamage',
    'elementalDefence',
    'elementalMainAttackDamage',
    'elementalSpellDamage',
    'exploding',
    'fireDamage',
    'fireDefence',
    'fireMainAttackDamage',
    'fireSpellDamage',
    'healingEfficiency',
    'healthRegen',
    'healthRegenRaw',
    'intelligence',
    'jumpHeight',
    'knockback',
    'level',
    'lifeSteal',
    'lootBonus',
    'mainAttackDamage',
    'mainAttackRange',
    'manaRegen',
    'manaSteal',
    'neutralDamage',
    'neutralMainAttackDamage',
    'neutralSpellDamage',
    'poison',
    'powderSlots',
    'raw1stSpellCost',
    'raw2ndSpellCost',
    'raw3rdSpellCost',
    'raw4thSpellCost',
    'rawAgility',
    'rawAirDamage',
    'rawAirMainAttackDamage',
    'rawAirSpellDamage',
    'rawAttackSpeed',
    'rawDamage',
    'rawDefence',
    'rawDexterity',
    'rawEarthDamage',
    'rawEarthMainAttackDamage',
    'rawEarthSpellDamage',
    'rawElementalDamage',
    'rawElementalMainAttackDamage',
    'rawElementalSpellDamage',
    'rawFireDamage',
    'rawFireMainAttackDamage',
    'rawFireSpellDamage',
    'rawHealth',
    'rawIntelligence',
    'rawMainAttackDamage',
    'rawMaxMana',
    'rawNeutralDamage',
    'rawNeutralMainAttackDamage',
    'rawNeutralSpellDamage',
    'rawSpellDamage',
    'rawStrength',
    'rawThunderDamage',
    'rawThunderMainAttackDamage',
    'rawThunderSpellDamage',
    'rawWaterDamage',
    'rawWaterMainAttackDamage',
    'rawWaterSpellDamage',
    'reflection',
    'slowEnemy',
    'spellDamage',
    'sprint',
    'sprintRegen',
    'stealing',
    'strength',
    'thorns',
    'thunderDamage',
    'thunderDefence',
    'thunderMainAttackDamage',
    'thunderSpellDamage',
    'walkSpeed',
    'waterDamage',
    'waterDefence',
    'waterSpellDamage',
    'weakenEnemy',
    'xpBonus',
]









if __name__ == "__main__":
    for name in sorted(WYNNAPI_STAT_NAMES):
        print(f"'{name}',")
    """ stat_indices = get_stat_indices()
    for stat_name, index in stat_indices.items():
        print(f"'{stat_name}': {index},") """
