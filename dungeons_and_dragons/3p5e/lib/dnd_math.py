#!/usr/bin/python3

def mod_int_to_str(val):
    if val >= 0:
        return f"+{val}"
    else:
        return f"{val}"

def get_mod_from_score(score):
    if score < 10:
        offset = 11
    else:
        offset = 10
    return int((score - offset) / 2)

def get_avg_roll(dice_sides):
    return (dice_sides + 1) / 2
