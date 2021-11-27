#!/usr/bin/python3

import csv
import argparse
import logging
from config import DESC_COL, CHARGED_COL, PAID_COL, skip_regex

logger = logging.getLogger(__name__)

# helper function: skip those above
def check_skip(desc):
    for regex in skip_regex:
        if regex in desc:
            return True
    return False

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("csv_file", help="File to categorize")
    parser.add_argument("--log-level", "-l", default='INFO', help="Level of extra messages")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(format='[%(asctime)-15s] %(levelname)-8s %(message)s',
                        level=args.log_level.upper())

    logger.debug(args.csv_file)

    breakdown = dict()
    total_charged = 0.0
    total_paid = 0.0

    with open(args.csv_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            desc = row[DESC_COL]
            charged = row[CHARGED_COL]
            paid = row[PAID_COL]

            if check_skip(desc):
                logger.debug("{} is on the list. Skipping.".format(desc))
                continue

            logger.debug("{}: charged ({}) paid ({})".format(desc, charged, paid))

            f_charged = float(charged) if charged else 0.0
            f_paid = float(paid) if paid else 0.0

            if not f_paid:
                try:
                    breakdown[desc] += f_charged
                except KeyError:
                    breakdown[desc] = f_charged

                total_charged += f_charged
            else:
                total_paid += f_paid

    print
    print("----- Breakdown -----")
    total_percentage = 0.0
    for desc in breakdown:
        f_charged = breakdown[desc]
        percentage = 100 * f_charged / total_charged
        print("{}: {:.2f} ({:.2f}%)".format(desc, f_charged, percentage))

        total_percentage += percentage

    print
    print("----- Summary -----")
    print("Total charged: {:.2f}".format(total_charged))
    print("Total paid: {:.2f}".format(-1 * total_paid))
    print("Net: {:.2f}".format(total_charged + total_paid))

    logger.debug("Total percentage sanity check (this should be 100%): {:.2f}%".format(total_percentage))
