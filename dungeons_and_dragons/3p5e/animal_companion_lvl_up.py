#!/usr/bin/python3

import argparse, json, sys

from lib.tables import  get_lvl_entry, find_mods, get_base_attack, \
                    get_save_mods, find_hd_mods, get_size_mod, \
                    get_size_mods, save_mods, size_mods, \
                    base_attacks, upgrade_chart, skill_mods

from lib.dnd_math import get_mod_from_score, mod_int_to_str, \
                     get_avg_roll
from lib.dnd_desc import descriptions

def update(base, mods, changes):

    new = base
    new["hit_dice"] += mods["bonus"]["hit_dice"]
    new["nat_armor"] += mods["bonus"]["nat_armor"]
    new["ability_scores"]["str"] += mods["bonus"]["str_dex"]
    new["ability_scores"]["dex"] += mods["bonus"]["str_dex"]

    new_base_attack, hd_mods = find_hd_mods(new["hit_dice"])

    new["bonus_hp"] += mods["bonus"]["hit_dice"]
    new["base_attack"] = new_base_attack
    new["saves"]["fort"] += hd_mods[0]
    new["saves"]["ref"] += hd_mods[1]
    new["saves"]["will"] += hd_mods[2]

    num_allowed_feats = int(new["hit_dice"] / 3 + 1)
    if "new_feats" in changes.keys():
        new["feats"] += changes["new_feats"]
    len_feats = len(new["feats"])
    assert len_feats == num_allowed_feats, \
           f'Unexpected feats ({len_feats} vs {num_allowed_feats} allowed)'

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
            if tsp > masp:
                print(f"Max allowed skill points exceeded ({tsp} > {masp})")
                sys.exit(1)

    else:
        masp = tsp = 0

    new["max_allowed_tricks"] = mods["bonus"]["tricks"]
    if "new_tricks" in changes.keys():
        new["tricks"] = changes["new_tricks"]
    else:
        new["tricks"] = list()

    return new, masp - tsp

def print_char_sheet(args, stats, specs):
    print("=" * len(args.name))
    print(args.name)
    print("=" * len(args.name))
    species = stats["species"]
    size_str = stats["size"]
    hd = stats["hit_dice"]
    bhp = stats["bonus_hp"]
    hd_type = stats["hd_type"]
    hp = int(hd * get_avg_roll(hd_type)) + bhp

    feat_hp = 3 if "Toughness" in stats["feats"] else 0

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
        assert atk_range == 'melee' or 'ft' in atk_range
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

    print("----- Special Attacks -----")
    for spec_attack in stats["special_attacks"]:
        print(spec_attack)
        if args.descriptions:
            print(descriptions["special_attacks"][spec_attack])
            print()
    print()

    print("----- Specials -----")
    for spec in specs:
        print(spec)
        if args.descriptions:
            print(descriptions["specials"][spec])
            print()
    for spec_qual in stats["special_qualities"]:
        print(spec_qual)
        if args.descriptions:
            print(descriptions["special_qualities"][spec_qual])
            print()
    
    print()

    print("----- Feats -----")
    for feat in stats["feats"]:
        print(feat)
        if args.descriptions:
            print(descriptions["feats"][feat])
            print()
    print()

    print("----- Skills -----")
    for skill_name, skill_val in stats["skills"].items():
        ab = skill_mods[skill_name]
        skill_mod = get_mod_from_score(stats["ability_scores"][ab])
        new_skill_val = skill_val + skill_mod
        if skill_name == "Hide":
            new_skill_val += hide_size_mod

        print(f"{skill_name}: {new_skill_val}")
    print()

    print("----- Bonus Tricks -----")
    tricks = stats["tricks"]
    for trick in tricks:
        print(trick)

    max_allowed_tricks = new["max_allowed_tricks"]
    num_tricks = len(tricks)
    trick_diff = max_allowed_tricks - num_tricks
    if num_tricks < max_allowed_tricks:
        print(f"WARNING: You still have {trick_diff} bonus tricks to choose")
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

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    with open(args.base_json) as f:
        base = json.load(f)

    mods, specs = find_mods(args.druid_lvl)

    # TODO: do this in a more organized way
    # skill points remaining
    if args.changes:
        with open(args.changes) as f:
            changes = json.load(f)
    else:
        changes = dict()

    new, spr = update(base, mods, changes)
    print_char_sheet(args, new, specs)

    if spr != 0:
        print(f"WARNING: You still have {spr} skill points available for allocation")
