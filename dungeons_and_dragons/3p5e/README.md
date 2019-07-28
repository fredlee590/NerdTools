# Dungeons and Dragons 3.5e Tools

# Overview

Sometimes, math is hard. Dungeons and Dragons doesn't have to be. Here are some
tools to handle some repetitive tasks.

# Tools

Here be da tools.

## Animal Companion Leveler

Codifies the algorithm for Druids' animal companions for 3.5 edition according
to [this wiki|http://archive.wizards.com/default.asp?x=dnd/rg/20070206a].

### Usage

The Animal Companion leveler requires at least two arguments: A base animal
template compiled from the Monster Manual and the druid's level. From there,
adding options can print out more detailed information. The full help is below:

```
usage: animal_companion_lvl_up.py [-h] [--name NAME] [--descriptions]
                                  [--changes CHANGES]
                                  base_json druid_lvl

positional arguments:
  base_json             Base animal profile. Basic information from Monster
                        Manual
  druid_lvl             Druid level to determine bonuses

optional arguments:
  -h, --help            show this help message and exit
  --name NAME, -n NAME  Name of your animal companion
  --descriptions, -d    Show ability descriptions
  --changes CHANGES, -c CHANGES
                        Changes for your animal companion. Feats, skills, and
                        the like
```

All data and inputs is (currently) handled in the JSON file format. All fields in the included base animal templates are required, so start there to create a new one. A sample change file, which represents the additional skills and feats for an animal companion is shown below:
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
    ]
}
```

Use these files to generate animal companion stats. Example usage is below:
```
./animal_companion_lvl_up.py templates/dire_rat.json 6 --name "Grog the Almighty" --changes grog.json
```
