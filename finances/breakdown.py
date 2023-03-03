#!/usr/bin/python3

import csv
import argparse
import logging

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("csv_file", help="File to categorize")
    parser.add_argument("--log-level", "-l", default='INFO', help="Level of extra messages")
    parser.add_argument("--config", "-c", default=None, help="Config library to import")
    parser.add_argument("--group", "-g", action="store_true", help="Group common expenses together")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(format='[%(asctime)-15s] %(levelname)-8s %(message)s',
                        level=args.log_level.upper())

    if args.config:
        import importlib
        cfg = importlib.import_module(args.config)
    else:
        import config as cfg

    logger.debug(args.csv_file)

    breakdown = dict()
    total_charged = 0.0
    total_paid = 0.0

    with open(args.csv_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            desc = row[cfg.DESC_COL]
            charged = row[cfg.CHARGED_COL]
            paid = row[cfg.PAID_COL]

            if cfg.check_skip(desc):
                logger.debug("{} is on the list. Skipping.".format(desc))
                continue

            if args.group:
                for k, v in cfg.replace_regex.items():
                    if k in desc:
                        old_len = len(desc)
                        new_len = len(v)
                        assert new_len < old_len
                        desc = v + " " * (old_len - new_len)

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
