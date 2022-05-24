#!/usr/bin/python3

import csv
import argparse
import logging

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("csv_file", help="File for which to calculate equalization payments")
    parser.add_argument("--log-level", "-l", default='INFO', help="Level of extra messages")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(format='[%(asctime)-15s] %(levelname)-8s %(message)s',
                        level=args.log_level.upper())

    logger.debug(args.csv_file)

    total = 0.0
    paid = dict()
    with open(args.csv_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            if len(row) != 4:
                logger.debug("Invalidly formatted length. Skipping")

            logger.debug(row)
            # 2021-01-01,Person 1,1.23,food from today
            date, user, _, note = row
            cost = float(row[2])

            total += cost
            if user not in paid.keys():
                paid[user] = cost
            else:
                paid[user] += cost

    print(f'total: {total}')
    fair_share = total / len(paid.keys())
    print(f'fair share: {round(fair_share, 2)}')

    logger.debug(paid)
    for k, v in paid.items():
        paid[k] = v - fair_share

    logger.debug(f'current: {paid}')
    for k1 in paid.keys():
        for k2 in paid.keys():
            logger.debug(f'k1: {k1} k2: {k2}')
            if k1 == k2:
                continue

            v1 = paid[k1]
            v2 = paid[k2]

            if v1 < 0.0 and v2 > 0.0:
                deduct_amount = abs(v2) if abs(v1) > abs(v2) else abs(v1)
                paid[k1] += deduct_amount
                paid[k2] -= deduct_amount
                print(f'{k1} must pay {k2} ${round(deduct_amount, 2)}')
                logger.debug(paid)

    for k, v in paid.items():
        paid[k] = round(v, 2)

    logger.debug(f'corrected: {paid}')
