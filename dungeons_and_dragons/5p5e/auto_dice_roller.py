#!/usr/bin/env python3

import argparse, logging, random

logger = logging.getLogger(__name__)


def parse_args():
    parser = argparse.ArgumentParser(description="Auto/mass dice roller for 5.5e Dungeons and Dragons")

    parser.add_argument("--log-level", "-l", default="INFO",
                        choices=logging._nameToLevel.keys(),
                        help='Set log level')
    parser.add_argument("--advantage", "-a", action='store_true',
                        help='Advantage')
    parser.add_argument("--disadvantage", "-d", action='store_true',
                        help='Disadvantage')
    parser.add_argument("--size", "-s", type=int, default=20, help='dice size')
    parser.add_argument("--plus", "-p", default=None, help='bonus')
    parser.add_argument("--minus", "-m", default=None, help='anti-bonus')
    parser.add_argument("--threshold", "-t", type=int, default=None, help='threshold to beat')
    parser.add_argument("num_npcs", type=int, help='number of npcs')

    return parser.parse_args()

def main():
    args = parse_args()

    logging.basicConfig(format='[%(asctime)-15s] %(levelname)-8s %(message)s',
                        level=args.log_level,
                        datefmt='%Y-%m-%d %H:%M:%S')

    logger.debug(args)

    if args.plus and args.minus:
        raise AssertionError("Only plus or minus, you dummy!")

    mod = 0
    if args.plus:
        mod += int(args.plus)

    if args.minus:
        mod -= int(args.minus)

    position = 0

    # advantage + disadvantage cancel out
    if args.advantage:
        position += 1

    if args.disadvantage:
        position -= 1

    total = 0
    num_over_threshold = 0
    for npc_id in range(1, args.num_npcs + 1):
        if not position:
            logger.debug("single")
            roll = random.randint(1, args.size)
        else:
            rolls = list()
            for i in range(2):
                rolls.append(random.randint(1, args.size))

            if position > 0:
                logger.debug(f"advantage: {rolls}")
                roll = max(rolls)
            else:
                logger.debug(f"disadvantage: {rolls}")
                roll = min(rolls)

        crit = roll == args.size
        roll += mod

        if not args.threshold or roll >= args.threshold:
            if args.threshold:
                num_over_threshold += 1

            total += roll

            npc_str = f"{npc_id}: {roll}"

            if crit:
                npc_str += " CRIT"

            print(npc_str)

    if args.num_npcs > 1 and args.size != 20:
        print(f"total: {total}")

    if args.threshold:
        print(f"over threshold: {num_over_threshold}")


if __name__ == "__main__":
    main()
