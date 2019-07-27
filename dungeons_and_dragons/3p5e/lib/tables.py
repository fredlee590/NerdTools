#!/usr/bin/python3

def get_lvl_entry(min_lvl, max_lvl, hd, narm, strdex, trks, spec):
    lvl_entry = {
        "class_boundaries": [min_lvl, max_lvl],
        "bonus":
        {
            "hit_dice": hd,
            "nat_armor": narm,
            "str_dex": strdex,
            "tricks": trks
        },
        "special": spec
    }

    return lvl_entry

def find_mods(druid_lvl):
    specials = list()
    target_lvl_entry = None
    for entry in upgrade_chart:
        min_lvl, max_lvl = entry["class_boundaries"]

        for spec in entry["special"]:
            specials.append(spec)

        if min_lvl <= druid_lvl and max_lvl >= druid_lvl:
            target_lvl_entry = entry
            break

    return target_lvl_entry, specials

def get_base_attack(hit_dice):
    # average
    return base_attacks[hit_dice - 1]

def get_save_mods(hit_dice):
    return save_mods[hit_dice - 1]

def find_hd_mods(hit_dice):
    base_attack = get_base_attack(hit_dice)
    save_mods = get_save_mods(hit_dice)

    return base_attack, save_mods

def get_size_mod(ac_attack, grapple, hide):
    return [ac_attack, grapple, hide]

def get_size_mods(size_str):
    return size_mods[size_str]

size_mods = {
    "fine": get_size_mod(8, -16, 16),
    "dimunitive": get_size_mod(4, -12, 12),
    "tiny": get_size_mod(2, -8, 8),
    "small": get_size_mod(1, -4, 4),
    "medium": get_size_mod(0, 0, 0),
    "large": get_size_mod(-1, 4, -4),
    "huge": get_size_mod(-2, 8, -8),
    "gargantuan": get_size_mod(-4, 12, -12),
    "colossal": get_size_mod(-8, 16, -16)
}

upgrade_chart = [
    get_lvl_entry(1, 2, 0, 0, 0, 1, ['Link', 'Share Spells']),
    get_lvl_entry(3, 5, 2, 2, 1, 2, ['Evasion']),
    get_lvl_entry(6, 8, 4, 4, 2, 3, ['Devotion']),
    get_lvl_entry(9, 11, 6, 6, 3, 4, ['Multiattack']),
    get_lvl_entry(12, 14, 8, 8, 4, 5, []),
    get_lvl_entry(15, 17, 10, 10, 5, 6, ['Improved Evasion']),
    get_lvl_entry(18, 20, 12, 12, 6, 7, [])
]

base_attacks = [
    [0],  # lvl 1
    [1],
    [2],
    [3],
    [4],
    [5],  # lvl 6
    [6, 1],
    [6, 1],
    [7, 2],
    [8, 3],
    [9, 4],  # lvl 11
    [9, 4],
    [10, 5],
    [11, 6, 1],
    [12, 7, 2],
    [12, 7, 2], # lvl 16
    [12, 7, 2],
    [13, 8, 3],
    [14, 9, 4],
    [15, 10, 5]  # lvl 20
]

save_mods = [
#   fort ref will
    [2,  2,  0],  # lvl 1
    [3,  3,  0],
    [3,  3,  1],
    [4,  4,  1],
    [4,  4,  1],
    [5,  5,  2],  # lvl 6
    [5,  5,  2],
    [6,  6,  2],
    [6,  6,  3],
    [7,  7,  3],
    [7,  7,  3],  # lvl 11
    [8,  8,  4],
    [8,  8,  4],
    [9,  9,  4],
    [9,  9,  5],
    [10, 10, 5],  # lvl 16
    [10, 10, 5],
    [11, 11, 6],
    [11, 11, 6],
    [12, 12, 6]   # lvl 20
]

skill_mods = {
    "Climb": "str",
    "Hide": "dex",
    "Listen": "wis",
    "Move Silently": "dex",
    "Spot": "wis",
    "Swim": "str"
}
