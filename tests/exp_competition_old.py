""" 
exp_competition.py: Run competitions with different AI players and compare their performance

Uses TrueSkill (https://trueskill.org/) ratings to rank the contestants
"""
import logging
from random import seed
from time import time

from trueskill import rate_1vs1
import matplotlib.pyplot as plt
import numpy as np
from math import ceil, log2

from hexai.players.alphabetaplayer import AlphaBetaPlayer
from hexai.players.mctsplayer import MctsPlayer
from hexai.hexgame import Hex
from hexai.hexboard import HexBoard

log = logging.getLogger(__name__.split('.')[-1])

seed(42)

MAX_TIME = 2


def plot_rating_hist(players):
    """Plot rating history for all players

    Args:
        players (list): List of Player objects
    """
    for player in players:
        means = np.array([rating.mu for rating in player.rating_history])
        dev = np.array([rating.sigma for rating in player.rating_history])
        x = range(0,len(means))
        plt.plot(x, means, label=player.name)
        plt.fill_between(x, means-dev, means+dev, alpha=0.2)
    
    plt.xlabel("Number of games")
    plt.ylabel("Rating")
    plt.legend()
    plt.show()


def update_rating(winner, loser):
    """Update player ratings after a game

    Args:
        winner (Player): Player that won the game
        loser (Player): Player that lost the game

    Returns:
        [type]: [description]
    """
    new_r1, new_r2 = rate_1vs1(winner.rating, loser.rating)
    winner.set_rating(new_r1)
    loser.set_rating(new_r2)


def get_players(option):
    if option == "base":
        players = [
            AlphaBetaPlayer("random", False, False, max_depth=3, name="player_3_random"),
            AlphaBetaPlayer("dijkstra", False, False, max_depth=3, name="player_3_dijkstra"),
            AlphaBetaPlayer("dijkstra", False, False, max_depth=4, name="player_4_dijkstra"),
        ]
    elif option == "idtt":
        players = [
            AlphaBetaPlayer("random", False, False, max_depth=3, name="player_3_random"),
            AlphaBetaPlayer("dijkstra", False, False, max_depth=4, name="player_4_dijkstra"),
            AlphaBetaPlayer("dijkstra", True, True, max_time=MAX_TIME, name="player_idtt"),
        ]
    elif option == "mcts":
        players = [
            AlphaBetaPlayer("random", False, False, max_depth=3, name="player_3_random"),
            AlphaBetaPlayer("dijkstra", True, True, max_time=MAX_TIME, name="player_idtt"),
            MctsPlayer(max_time=MAX_TIME, name="player_mcts"),
        ]
    else:
        raise ValueError("Unkown comp option")
    
    return players


def test(option, size, no_matches, use_start_moves):
    # Number of matches played per player pair. One match consists of two games, where each player starts once
    
    players = get_players(option)
    
    if no_matches is None:
        # Formula derived from https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf 
        # Subsection about convergence speed  the theoretical minimum of log(no_games) / log(no_players) is recommended as the amount of games needed per player
        no_matches = ceil(log2(len(players)))
        print("Number of matches set to {}".format(no_matches))
    
    
    start_moves = [None]
    if use_start_moves:
        start_moves = HexBoard(size).get_empty_cells()
    
    start_time = time()
    
    for match_no in range(no_matches):
        # for player_game in player_games:
        for move in start_moves:
            for player_one in range(len(players)-1):
                for player_two in range(player_one+1, len(players)):
                    player_game = [players[player_one], players[player_two]]

                    game = Hex(size, player_game)
                
                    for starter in range(2):
                        print("Playing match {} with players {} and {}".format(match_no+1, player_game[starter].name, player_game[(starter + 1) % 2].name))
                        print("Starter move {}".format(move))
                        
                        winner = game.play(starter, move, verbose=1)
                        loser = (winner + 1) % 2
                        update_rating(game.players[winner], game.players[loser])
    
    total_time = time() - start_time
    total_games = no_matches * len(players) * 2 * len(start_moves)
    
    print("\nRESULTS------------------------------")
    print("Played a total of {} games which took {:.2f} s ({:.2f} s avg.)".format(total_games, total_time, total_time / (total_games)))
           
    print("\nFinal rankings:")
    for player in players:
        print("{}: played {}, won {}: {} - Total turns: {} - Total evals: {} - Avg evals/turn: {} - Full Hits/Turn: {} - Half Hits/Turn: {}".format(player.name, player.games_played, player.games_won, player.rating, player.turn_count, player.eval_count, player.eval_count/(player.turn_count+0.0001), player.tt_hits_full/(player.turn_count+0.0001), player.tt_hits_half/(player.turn_count+0.0001)))
        
    print("-------------------------------------")
        
    plot_rating_hist(players)
    