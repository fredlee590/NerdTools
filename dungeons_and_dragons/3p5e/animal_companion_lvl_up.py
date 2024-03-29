#!/usr/bin/python3

import argparse, json, sys, logging

from lib.tables import find_mods, find_hd_mods, get_size_mods, \
                       skill_mods

from lib.dnd_math import get_mod_from_score, mod_int_to_str, \
                         get_avg_roll
from lib.dnd_desc import descriptions

logger = logging.getLogger(__name__)


def update(base, mods, specials, changes):

    new = base
    logger.debug(f'init: {new}')
    new["hit_dice"] += mods["bonus"]["hit_dice"]
    new["nat_armor"] += mods["bonus"]["nat_armor"]
    new["ability_scores"]["str"] += mods["bonus"]["str_dex"]
    new["ability_scores"]["dex"] += mods["bonus"]["str_dex"]

    new_base_attack, hd_mods = find_hd_mods(new["hit_dice"])

    new["base_attack"] = new_base_attack
    new["saves"]["fort"] += hd_mods[0]
    new["saves"]["ref"] += hd_mods[1]
    new["saves"]["will"] += hd_mods[2]
    new["specials"] = specials

    logger.debug(f'pre-changes: {new}')

    num_allowed_feats = int(new["hit_dice"] / 3 + 1)
    if "new_feats" in changes.keys():
        new["feats"] += changes["new_feats"]
    len_feats = len(new["feats"])
    assert len_feats == num_allowed_feats, \
           f'Expected {num_allowed_feats} feats. {len_feats} detected.'

    logger.debug(f'post-feats: {new}')

    if "new_skills" in changes.keys():
        cand_int_mod = new["ability_scores"]["int"]
        int_mod = 1 if cand_int_mod < 0 else cand_int_mod
        tsp = 0
        masp = 2 + (new["hit_dice"] * int_mod)
        for i, v in changes["new_skills"].items():
            try:
                new["skills"][i] += v
            except KeyError:
                new["skills"][i] = v
            tsp += v
        assert masp == tsp, \
               f"Expected {masp} skill points allocated. {tsp} allocated."

    logger.debug(f'post-skills: {new}')

    if "new_tricks" in changes.keys():
        exp_num_tricks = mods["bonus"]["tricks"]
        obs_num_tricks = len(changes["new_tricks"])
        assert exp_num_tricks == obs_num_tricks, \
               f"Expected {exp_num_tricks} tricks. Detected {obs_num_tricks}."
        new["tricks"] = changes["new_tricks"]
    else:
        new["tricks"] = list()

    logger.debug(f'post-tricks: {new}')

    return new

def print_char_sheet(args, stats):
    def print_space_if_desc():
        if not args.descriptions:
            print()

    def print_list_and_descs(label, list_id):
        print(f"----- {label} -----")
        for i in stats[list_id]:
            print(f'{i.upper()}')
            if args.descriptions:
                print(descriptions[list_id][i])
                print()
        print_space_if_desc()

    print("=" * len(args.name))
    print(args.name)
    print("=" * len(args.name))
    species = stats["species"]
    size_str = stats["size"]
    hd = stats["hit_dice"]
    bhp = stats["bonus_hp"]
    hd_type = stats["hd_type"]
    con_mod = get_mod_from_score(stats["ability_scores"]["con"])
    hp = int(hd * (get_avg_roll(hd_type) + con_mod)) + bhp

    feat_hp = 3 if "Toughness" in stats["feats"] else 0

    logger.debug(f'{hd}x({get_avg_roll(hd_type)}+{con_mod})+{bhp}+{feat_hp}')
    print(f"Species: {species} ({size_str} - HD: {hd}) Hit Points: {hp + feat_hp}")

    speeds = stats["speeds"]

    speed_str = ""
    for speed_type, speed in speeds.items():
        new_speed_str = f"{speed_type} speed: {speed}"
        if speed_str:
            speed_str += f" {new_speed_str}"
        else:
            speed_str = new_speed_str
    print(speed_str)

    abilities_str = str()
    for i, v in stats["ability_scores"].items():
        mod_val = get_mod_from_score(v)
        abilities_str += f"{i}: {v} ({mod_int_to_str(mod_val)}) "
    print(abilities_str)

    saves_str = str()
    for i, v in stats["saves"].items():
        saves_str += f"{i} save: {mod_int_to_str(v)} "
    print(saves_str)

    str_mod = get_mod_from_score(stats["ability_scores"]["str"])
    dex_mod = get_mod_from_score(stats["ability_scores"]["dex"])
    nat_armor = stats["nat_armor"]
    ac_size_mod, grap_size_mod, hide_size_mod = get_size_mods(size_str)
    print(f"Natural Armor: {nat_armor}  Size AC Mod: {ac_size_mod}")
    ac = 10 + dex_mod + nat_armor + ac_size_mod
    tac = ac - nat_armor
    ffac = ac - dex_mod
    print(f"Armor Class: {ac}  Touch AC: {tac}  Flat-Footed AC: {ffac}")

    init_str = mod_int_to_str(dex_mod)
    base_atks = stats["base_attack"]
    base_prim_atk = base_atks[0]

    grapples_str = [mod_int_to_str(x + str_mod + grap_size_mod) \
                    for x in base_atks]
    base_attack_str = '/'.join([mod_int_to_str(x) \
                                for x in base_atks])
    grapple_str = mod_int_to_str(base_prim_atk + str_mod + \
                                 grap_size_mod)
    print(f"Base Attack: {base_attack_str}  Grapple: {grapple_str}  Initiative: {init_str}")

    print()
    print("----- Attacks -----")
    for attack in stats["attacks"]:
        effects_str = None
        for effect in attack["effects"]:
            if effects_str:
                effects_str += f",{effect}"
            else:
                effects_str = effect

        atk_range = attack['range']
        assert atk_range == 'melee' or 'ft' in atk_range, \
               "Invalid attack information. Need melee or range in feet."
        attr_mod = str_mod if atk_range == 'melee' else dex_mod

        dmg_mod = attack['add_damage'] + str_mod
        atk_mod = attack['add_attack'] + attr_mod + base_prim_atk
        atk_mod_str = mod_int_to_str(atk_mod)

        print(f"{attack['name']}:")
        print(f"  Attack: {atk_mod_str}")
        print(f"  Range: {attack['range']}")
        print(f"  Damage: {attack['damage']} + {dmg_mod} ({attack['critical']})")
        print(f"  Type: {attack['type']}")
        print(f"  Effects: {effects_str}")
        print()

    print_list_and_descs("Special Attacks", "special_attacks")
    print_list_and_descs("Special Abilities (Animal Companion)", "specials")
    print_list_and_descs("Special Abilities (Species)", "special_qualities")
    print_list_and_descs("Feats", "feats")
    print_list_and_descs("Bonus Tricks", "tricks")

    print("----- Skills -----")
    for skill_name, skill_val in stats["skills"].items():
        ab = skill_mods[skill_name]
        skill_mod = get_mod_from_score(stats["ability_scores"][ab])
        new_skill_val = skill_val + skill_mod
        if skill_name == "Hide":
            new_skill_val += hide_size_mod

        print(f"{skill_name}: {new_skill_val}")
    print()

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("base_json",
                        help="Base animal profile from Monster Manual. JSON file format.")
    parser.add_argument("druid_lvl", type=int, help="Druid level to determine bonuses")
    parser.add_argument("--name", "-n", default="(Unnamed)",
                        help="Name of your animal companion")
    parser.add_argument("--descriptions", "-d", action='store_true',
                        help="Show ability descriptions")
    parser.add_argument("--changes", "-c",
                        help="Changes for your animal companion. JSON file format.")
    parser.add_argument("--log-level", "-l", choices=logging._nameToLevel.keys(),
                        help="Log levels, pulled from standard log level enums.")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(format='[%(asctime)-15s] %(levelname)-8s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S',
                        level=args.log_level)

    with open(args.base_json) as f:
        base = json.load(f)

    mods, specs = find_mods(args.druid_lvl)

    if args.changes:
        with open(args.changes) as f:
            changes = json.load(f)
    else:
        changes = dict()

    new = update(base, mods, specs, changes)
    print_char_sheet(args, new)

