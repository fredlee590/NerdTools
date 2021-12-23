Dungeons and Dragons 3.5e Python Tools
======================================

# The Tools

## Animal Companion Leveler

Codifies the algorithm for Druids' animal companions for 3.5 edition according
to the Dungeons and Dragons 3.5 Edition Player Handbook.

### Usage

The Animal Companion leveler requires at least two arguments: A base animal
template compiled from the Monster Manual and the druid's level. From there,
adding options can print out more detailed information. The full help is below:

```
$ ./animal_companion_lvl_up.py --help
usage: animal_companion_lvl_up.py [-h] [--name NAME] [--descriptions] [--changes CHANGES]
                                  [--log-level {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}]
                                  base_json druid_lvl

positional arguments:
  base_json             Base animal profile from Monster Manual. JSON file format.
  druid_lvl             Druid level to determine bonuses

optional arguments:
  -h, --help            show this help message and exit
  --name NAME, -n NAME  Name of your animal companion
  --descriptions, -d    Show ability descriptions
  --changes CHANGES, -c CHANGES
                        Changes for your animal companion. JSON file format.
  --log-level {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}, -l {CRITICAL,FATAL,ERROR,WARN,WARNING,INFO,DEBUG,NOTSET}
                        Log levels, pulled from standard log level enums.

```

All data and inputs is (currently) handled in the JSON file format. All fields in the included base animal templates are required, so start there to create a new one. See examples of such animal template JSONs in the `templates/` directory. Reference the Dungeons and Dragons 3.5 edition Monster Manual when creating a new one.

A sample change file, which represents the additional skills and feats for an animal companion is shown below:
```
{
    "new_skills": {
        "Climb": 2,
        "Hide": 1,
        "Listen": 1,
        "Move Silently": 2,
        "Spot": 1,
        "Swim": 0
    },
    "new_tricks": [
        "Attack",
        "Guard",
        "Fetch"
    ],
    "new_feats": [
    ]
}
```

Use these files to generate animal companion stats. Example usage is below:
```
$ ./animal_companion_lvl_up.py templates/dire_rat.json 6 --name "Grog the Almighty" --changes grog.json
=================
Grog The Almighty
=================
Species: Dire Rat (small - HD: 5) Hit Points: 28
nominal speed: 40 climb speed: 20
str: 12 (+1) dex: 19 (+4) con: 12 (+1) int: 1 (-5) wis: 12 (+1) chr: 4 (-3)
fort save: +7 ref save: +6 will save: +7
Natural Armor: 5  Size AC Mod: 1
Armor Class: 20  Touch AC: 15  Flat-Footed AC: 16
Base Attack: +4  Grapple: +1  Initiative: +4

----- Attacks -----
Bite:
  Attack: +9
  Range: melee
  Damage: 1d4 + 1 (x2)
  Type: piercing
  Effects: disease

----- Special Attacks -----
DISEASE

----- Special Abilities (Animal Companion) -----
LINK
SHARE SPELLS
EVASION
DEVOTION

----- Special Abilities (Species) -----
LOW-LIGHT VISION
SCENT

----- Feats -----
ALERTNESS
WEAPON FINESSE

----- Bonus Tricks -----
ATTACK
GUARD
FETCH

----- Skills -----
Climb: 14
Hide: 10
Listen: 5
Move Silently: 7
Spot: 5
Swim: 12
```
