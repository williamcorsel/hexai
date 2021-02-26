""" 
exp_competition.py: Run competitions with different AI players and compare their performance

Uses TrueSkill (https://trueskill.org/) ratings to rank the contestants
"""
import logging
from random import seed, randint
from time import time

from trueskill import rate_1vs1
import matplotlib.pyplot as plt
import numpy as np
from math import ceil, log2
from multiprocessing import Pool
from copy import deepcopy

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
        players (dict): Dict of unique Player objects containing the results
    """
    plt.figure(figsize=(8,6))
    for key in players.keys():
        player = players[key]
        means = np.array([rating.mu for rating in player.rating_history])
        dev = np.array([rating.sigma for rating in player.rating_history])
        x = range(0,len(means))
        plt.plot(x, means, label=player.name)
        plt.fill_between(x, means-dev, means+dev, alpha=0.2)
    
    plt.xlabel("Number of games")
    plt.ylabel("Rating")
    plt.legend(loc='upper left')
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
        players = {
            "player_3_random": AlphaBetaPlayer("random", False, False, max_depth=3, name="player_3_random"),
            "player_3_dijkstra": AlphaBetaPlayer("dijkstra", False, False, max_depth=3, name="player_3_dijkstra"),
            "player_4_dijkstra": AlphaBetaPlayer("dijkstra", False, False, max_depth=4, name="player_4_dijkstra"),
        }
    elif option == "idtt":
        players = {
            "player_3_random": AlphaBetaPlayer("random", False, False, max_depth=3, name="player_3_random"),
            "player_3_dijkstra": AlphaBetaPlayer("dijkstra", False, False, max_depth=3, name="player_3_dijkstra"),
            "player_4_dijkstra": AlphaBetaPlayer("dijkstra", False, False, max_depth=4, name="player_4_dijkstra"),
            "player_idtt": AlphaBetaPlayer("dijkstra", True, True, max_time=MAX_TIME, name="player_idtt"),
        }
    elif option == "mcts":
        players = {
            "player_3_random": AlphaBetaPlayer("random", False, False, max_depth=3, name="player_3_random"),
            "player_idtt": AlphaBetaPlayer("dijkstra", True, True, max_time=MAX_TIME, name="player_idtt"),
            "player_mcts": MctsPlayer(max_time=MAX_TIME, name="player_mcts"),
        }
    else:
        raise ValueError("Unkown comp option")
    
    return players


def play_game(players, size, start_move):
    """Play a single game

    Args:
        players (list): List of two players
        size (int): Size of the board

    Returns:
        list: List with winner results
    """
    times = {}
    winners = []
    game = Hex(size, players)
    for starter in range(2):
        print("Playing with players {} and {}".format(players[starter].name, players[(starter + 1) % 2].name))
        winner = game.play(starter, start_move, verbose=1)
        
        for player in players:
            
            times[player.name] = player.turn_time / player.turn_count
        
        winners.append(winner)
     
    return [winners, times]


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
        no_matches = 1
    
    
    games = []
    keys = list(players.keys())
    for _ in range(no_matches):
        for move in start_moves:
            for player_one in range(0, len(players)-1):
                for player_two in range(player_one+1, len(players)):
                    player_game = [deepcopy(players[keys[player_one]]), deepcopy(players[keys[player_two]])]
                    player_game[0].set_seed(randint(0, 10000))
                    player_game[1].set_seed(randint(0, 10000))
                    games.append([player_game, size, move])
    
    
    start_time = time()
    
    with Pool() as p:
        results = p.starmap(play_game, games)
    
    total_time = time() - start_time
    
    # Setup turn time dict
    avg_turn_times = {}
    for player_name in players.keys():
        avg_turn_times[player_name] = []
    
    # Parse the game results by updating players dict
    for i, config in enumerate(games):
        game = config[0]
        
        # Parse winners
        for winner in results[i][0]:
            loser = (winner + 1) % 2
            win_player = players[game[winner].name]
            lose_player = players[game[loser].name]
            update_rating(win_player, lose_player)
            win_player.games_played += 1
            win_player.games_won += 1
            lose_player.games_played += 1

        # Parse turn times
        for player in results[i][1].keys():
            avg_turn_times[player].append(results[i][1][player])
     
    for player in avg_turn_times.keys():
        avg_turn_times[player] = np.mean(avg_turn_times[player]) 
       
    total_games = len(games) * 2
    
    print("\nRESULTS------------------------------")
    print("Played a total of {} games which took {:.2f} s ({:.2f} s avg.)".format(total_games, total_time, total_time / total_games))
           
    print("\nFinal rankings:")
    for key in players.keys():
        player = players[key]
        print("{}: played {}, won {}: {}. avg turn time: {}".format(player.name, player.games_played, player.games_won, player.rating, avg_turn_times[player.name]))
        
    print("-------------------------------------")
        
    plot_rating_hist(players)
    