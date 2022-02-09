#!/usr/bin/python3

import csv, logging, argparse
from datetime import datetime
from os.path import splitext
from config import DESC_COL, DATE_COL, CHARGED_COL, PAID_COL, \
                   DATE_STR_FMT, check_skip

logger = logging.getLogger(__name__)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("first_total", type=float,
                        help="First total from which to total deltas")
    parser.add_argument("csv_file", help="File of money transfers to apply")
    parser.add_argument("--log-level", "-l", default='INFO', help="Level of extra messages")

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    logging.basicConfig(format='[%(asctime)-15s] %(levelname)-8s %(message)s',
                        level=args.log_level.upper())

    total = args.first_total
    new_csv = list()
    with open(args.csv_file) as csvfile:
        reader = csv.reader(csvfile, delimiter=',')

        for row in reader:
            date_str = row[DATE_COL]
            desc = row[DESC_COL]
            if check_skip(desc):
                continue
            lost = row[CHARGED_COL]
            gained = row[PAID_COL]

            if not lost and gained:
                delta_str = gained
            elif lost and not gained:
                delta_str = lost
            else:
                logger.error('Both paid and gained columns are empty')

            new_csv.append([date_str, delta_str])

    new_csv.sort(key=lambda x: datetime.strptime(x[0], DATE_STR_FMT))
    first = True
    for row in new_csv:
        delta = float(row[1])
        if not first:
            total += delta
        else:
            first = False
        logger.debug(row)
        row.append(round(total, 2))
        logger.debug(row)

    file_name, _ = splitext(args.csv_file)
    out_file = f'{file_name}-out.csv'
    logger.info(f'Attempting to write new CSV with totals to {out_file}')
    with open(out_file, 'w') as f:
        writer = csv.writer(f, delimiter=',')
        for new_row in new_csv:
            logger.debug(new_row)
            writer.writerow(new_row)

