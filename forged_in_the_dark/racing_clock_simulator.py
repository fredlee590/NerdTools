#!/usr/bin/env python3

import argparse, logging, random, sys

logger = logging.getLogger(__name__)


B_CLOCK_SIZE = 10
D_CLOCK_SIZE = 10 # tier 0 / 2d6 - about matched
#D_CLOCK_SIZE = 7 # tier 1 / 3d6 - about matched
#D_CLOCK_SIZE = 5 # tier 2 / 4d6 - about matched
#D_CLOCK_SIZE = 4 # tier 3 / 5d6 - about matched
#D_CLOCK_SIZE = 3 # tier 4 / 5d6 - out-matched, evenly matched with pushing
#D_CLOCK_SIZE = 2 # tier 5 / 5d6 - even more out-matched, regular out-matched with pushing

def two_of(roll_list, n):
    n_of = 0
    for roll in roll_list:
        if roll == n:
            n_of += 1
    return n_of >= 2

def two_sixes(roll_list):
    return two_of(roll_list, 6)

def two_ones(roll_list):
    return two_of(roll_list, 1)

RESULTS = {
    "attack": {
        "crit_succ": {
            "range_func": two_sixes,
            "b_ticks": 3,  # beneficial ticks
            "d_ticks": 0,  # detrimental ticks
        },
        "success": {
            "range_func": lambda x: any([i == 6 for i in x]),
            "b_ticks": 2,  # beneficial ticks
            "d_ticks": 0,  # detrimental ticks
        },
        "partial": {
            "range_func": lambda x: any([i in (4,5) for i in x]),
            "b_ticks": 2,  # beneficial ticks
            "d_ticks": 2,  # detrimental ticks
        },
        "fail": {
            "range_func": lambda x: any([i in (1,2,3) for i in x]),
            "b_ticks": 0,  # beneficial ticks
            "d_ticks": 2,  # detrimental ticks
        },
    },
    "defense": {
        "crit_succ": {
            "range_func": two_sixes,
            "b_ticks": 2,  # beneficial ticks
            "d_ticks": 0,  # detrimental ticks
        },
        "success": {
            "range_func": lambda x: any([i == 6 for i in x]),
            "b_ticks": 1,  # beneficial ticks
            "d_ticks": 0,  # detrimental ticks
        },
        "partial": {
            "range_func": lambda x: any([i in (4,5) for i in x]),
            "b_ticks": 1,  # beneficial ticks
            "d_ticks": 1,  # detrimental ticks
        },
        "fail": {
            "range_func": lambda x: any([i in (1,2,3) for i in x]),
            "b_ticks": 0,  # beneficial ticks
            "d_ticks": 2,  # detrimental ticks
        },
    }
}
def parse_args():
    parser = argparse.ArgumentParser(description='Template')

    parser.add_argument("--rounds", "-r", default=10, type=int,
                        help="Number of iterations to simulate")
    parser.add_argument("--pc-clock-size", "-p", default=B_CLOCK_SIZE, type=int,
                        help="Number of segments for 'PC wins' clock")
    parser.add_argument("--npc-clock-size", "-n", default=D_CLOCK_SIZE, type=int,
                        help="Number of segments for 'NPC wins' clock")
    parser.add_argument("--dice", "-d", default=2, type=int,
                        help="Number of d6s to use per action roll")
    parser.add_argument("--sims", "-s", default=1, type=int,
                        help="Number of times to simulate a fight")
    parser.add_argument("--log-level", "-l", default="INFO",
                        choices=logging._nameToLevel.keys(),
                        help='Set log level')

    return parser.parse_args()

def simulate_fight(rounds, dice, pc_clock_size, npc_clock_size):
    def update_ticks(current, add, max_val):
        updated_val = current + add
        if updated_val > max_val:
            return max_val
        return updated_val

    b_tick_num = 0
    d_tick_num = 0
    winner_str = None
    for i in range(rounds):
        logger.info(f"ROUND {i + 1}")
        for k in ("attack", "defense"):
            rolls = list()
            for r in range(dice):
                rolls.append(random.randint(1, 6))
            logger.debug(rolls)

            for choice, values in RESULTS[k].items():
                range_func, b_tick, d_tick = values.values()

                if range_func(rolls):
                    b_tick_num = update_ticks(b_tick_num, b_tick, pc_clock_size)
                    d_tick_num = update_ticks(d_tick_num, d_tick, npc_clock_size)

                    logger.debug(f'\t{choice} - {k}: {rolls} -> b: {b_tick_num} d: {d_tick_num}')

                    if b_tick_num == pc_clock_size:
                        if d_tick_num == npc_clock_size:
                            winner_str = "TIE"
                        else:
                            winner_str = "PC WINS"
                    elif d_tick_num == npc_clock_size:
                        winner_str = "NPC WINS"
                    if winner_str:
                        logger.info(f"FIGHT OVER! {winner_str}! {b_tick_num} {d_tick_num}")
                        return winner_str 

                    break

    return None

def main():
    args = parse_args()

    logging.basicConfig(format='[%(asctime)-15s] %(levelname)-8s %(message)s',
                        datefmt='%H:%M:%S',
                        level=args.log_level)

    logger.debug(args)

    pc_win_count = 0
    npc_win_count = 0
    tie_count = 0

    for sim in range(args.sims):
        logger.info(f"SIM #{sim + 1}")
        winner_str = simulate_fight(args.rounds, args.dice, args.pc_clock_size, args.npc_clock_size)
        if winner_str == "PC WINS":
            pc_win_count += 1
        elif winner_str == "NPC WINS":
            npc_win_count += 1
        elif winner_str == "TIE":
            tie_count += 1
    
    total = pc_win_count + npc_win_count + tie_count
    logger.info(f"PC Win: {pc_win_count} ({pc_win_count/total})")
    logger.info(f"NPC Win: {npc_win_count} ({npc_win_count/total})")
    logger.info(f"Tie: {tie_count} ({tie_count/total})")

if __name__ == "__main__":
    main()
