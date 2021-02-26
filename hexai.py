""" 
hexai.py: Main play file
"""
import argparse
import logging
from datetime import datetime
from os import path, mkdir

from hexai.hexgame import Hex
from hexai.players.humanplayer import HumanPlayer
from hexai.players.alphabetaplayer import AlphaBetaPlayer
from hexai.players.mctsplayer import MctsPlayer

# Parse arguments
parser = argparse.ArgumentParser(description='Play a Game of Hex!')
parser.add_argument("-p1", type=str, default='human', choices=['human', 'alphabeta', 'mcts'],
                    help='Player 1 type')
parser.add_argument("-p2", type=str, default='alphabeta', choices=['human', 'alphabeta', 'mcts'],
                    help='Player 2 type')
parser.add_argument("-s", "--size", type=int, default=5,
                    help="Size of board")
parser.add_argument("-t", "--use_tt", action="store_true",
                    help="Whether to use transposition table when using alphabeta player")
parser.add_argument("-b", "--begin", type=int, default=1,
                    help='Which player starts the game (1/2)')
args = parser.parse_args()


# Generate defaults directories
if not path.exists("logs/"):
    mkdir("logs/")


# Set logging
logging.basicConfig(filename="logs/game:{}.log".format(datetime.now().strftime("%Y_%m_%d:%H_%M_%S")), 
                    format='%(levelname)s:%(name)s: %(message)s',
                    level=logging.CRITICAL)


# Parse arguments
def generate_players(player_types):
    """Generates player objects based on input arguments

    Args:
        player_types (list): List of two strings containing the type for each player

    Returns:
        list: List of Player objects
    """
    players = []
    
    for player_mode in player_types:
        if player_mode == "human":
            players.append(HumanPlayer())
        elif player_mode == "alphabeta":
            players.append(AlphaBetaPlayer(evaluation="dijkstra",
                                           use_id=True, 
                                           use_tt=args.use_tt, 
                                           max_time=2))
        elif player_mode == "mcts":
            players.append(MctsPlayer(max_time=2))
    
    return players


board_size = int(args.size)
player_types = [args.p1, args.p2]
players = generate_players(player_types)

# Play the game!
game = Hex(board_size=board_size, players=players)
game.play(args.begin-1, verbose=2)