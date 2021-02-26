import argparse
import logging
from datetime import datetime
from os import path, mkdir


# Parse arguments
parser = argparse.ArgumentParser(description='Hex experiments')
parser.add_argument("test", type=str, default='comp', choices=['comp', 'comp_old', 'mcts'],
                    help='What experiments to run')
parser.add_argument("-o", "--option", type=str, default="base", choices=['base', 'idtt', 'mcts'],
                    help="What competition config to use")
parser.add_argument("-s", "--size", type=int, default=5,
                    help="Size of board")
parser.add_argument("-n", "--no_matches", type=int, default=None,
                    help="Number of matches to be played")
parser.add_argument("-m", "--start_moves", action="store_true",
                    help="Whether to use fixed start moves")
args = parser.parse_args()


# Generate defaults directories
if not path.exists("logs/"):
    mkdir("logs/")


# Set logging
logging.basicConfig(filename="logs/game:{}.log".format(datetime.now().strftime("%Y_%m_%d:%H_%M_%S")), 
                    format='%(levelname)s:%(name)s: %(message)s',
                    level=logging.CRITICAL)

if args.test == "comp":
    from tests.exp_competition import test
    test(args.option, args.size, args.no_matches, args.start_moves)
elif args.test == "comp_old":
    from tests.exp_competition_old import test
    test(args.option, args.size, args.no_matches, args.start_moves)
elif args.test == "mcts":
    from tests.exp_mcts import test
    test(args.size, args.no_matches)