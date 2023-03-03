#!/usr/bin/python3

# CSV format constants of your bank. Fill these in with your particular case
# DATE_COL = 0
# DESC_COL = 0
# CHARGED_COL = 0
# PAID_COL = 0

# DATE_STR_FMT = ""

skip_regex = list()

replace_regex = {
    "REPLACETHIS": "With This",
    "ANDTHIS": "With That",
}

weights = {
    "Person1": 1,
    "Person2": 1,
    "Person3": 2,
}


# return whether input description is included in the descriptions to skip
def check_skip(desc):
    for regex in skip_regex:
        if regex in desc:
            return True
    return False
