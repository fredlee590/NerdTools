#!/usr/bin/python3

import csv
import argparse
import logging

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("csv_file", help="File for which to calculate equalization payments")
    parser.add_argument("--log-level", "-l", default='INFO', help="Level of extra messages")
    parser.add_argument("--config", "-c", default=None, help="Config library to import")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(format='[%(asctime)-15s] %(levelname)-8s %(message)s',
                        level=args.log_level.upper())

    logger.debug(args.csv_file)

    if args.config:
        import importlib
        cfg = importlib.import_module(args.config)
        weights = cfg.weights
    else:
        from config import weights

    total = 0.0
    paid = dict()
    for user in weights.keys():
        paid[user] = 0.0

    heading_row_counted = False
    with open(args.csv_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            if len(row) != 4:
                logger.debug("Invalidly formatted length. Skipping")

            logger.debug(row)
            # 2021-01-01,Person 1,1.23,food from today
            date, user, cost, note = row
            if date == "Date" and user == "Contributor" and note == "Notes":
                if not heading_row_counted:
                    heading_row_counted = True
                    logger.debug("Heading row detected! Skipping")
                else:
                    logger.debug("Heading row detected again! That's weird")

                continue

            cost = float(cost)

            total += cost

            assert user in weights.keys(), f"Contributor {user} weight unspecified in config!"
            if user not in paid.keys():
                paid[user] = cost
            else:
                paid[user] += cost

    print(f'total: {total}')
    shares = 0
    for weight in weights.values():
        shares += weight

    share_price = total / shares
    print(f'share price: {round(share_price, 2)}')
    print()
    for user, weight in weights.items():
        print(f"{user} pays {weight} shares out of {shares} total")
    print()
    logger.debug(paid)
    for k, v in paid.items():
        paid[k] = v - share_price * weights[k]

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
