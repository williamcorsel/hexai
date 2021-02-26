""" 
exp_mcts.py: MCTS hyperparameter comparison

Uses TrueSkill (https://trueskill.org/) ratings to rank the contestants
"""
import logging
import pickle
from random import seed, Random, randint
from math import sqrt, ceil, log2
from time import time
from copy import deepcopy

from trueskill import rate_1vs1
import matplotlib.pyplot as plt
import numpy as np

from hexai.players.alphabetaplayer import AlphaBetaPlayer
from hexai.players.mctsplayer import MctsPlayer
from hexai.hexgame import Hex

from multiprocessing import Pool

log = logging.getLogger(__name__.split('.')[-1])

seed(42)

def plot_rating_hist(players):
    """Plot rating history for all players

    Args:
        players (dict): Dict of unique Player objects containing the results
    """
    for key in players.keys():
        player = players[key]
        means = np.array([rating.mu for rating in player.rating_history])
        
        x = range(0,len(means))
        plt.plot(x, means, label=player.name)
    
    plt.xlabel("Number of games")
    plt.ylabel("Rating")
    plt.legend(loc='upper left')
    plt.show()
    

def update_rating(winner, loser):
    """Update player ratings after a game

    Args:
        winner (Player): Player that won the game
        loser (Player): Player that lost the game
    """
    new_r1, new_r2 = rate_1vs1(winner.rating, loser.rating)
    winner.set_rating(new_r1)
    loser.set_rating(new_r2)
    
    
def play_game(players, size):
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
        winner = game.play(starter, verbose=1)
        
        for player in players:
            times[player.name] = player.turn_time / player.turn_count
        
        winners.append(winner)
     
    return [winners, times]


def test(size, no_matches):
    ########################################################
    # Define experiment options
    n_options = [10000, 1000, 100]
    cp_options = [0.0, 0.5, 1.0, sqrt(2),1.8, 2.0]
    ########################################################
    
    # Generate unique players dict and option combination list
    players = {}
    options = []
    for n in n_options:
        for cp in cp_options:
            player_name = "mcts_{}_{:.2f}".format(n, cp)
            players[player_name] = MctsPlayer(no_simulations=n, exploration_factor=cp, name=player_name)
            options.append([n, cp])
    
    if no_matches == None:
        # Formula derived from https://www.microsoft.com/en-us/research/wp-content/uploads/2007/01/NIPS2006_0688.pdf 
        # Subsection about convergence speed  the theoretical minimum of log(no_games) / log(no_players) is recommended as the amount of games needed per player
        no_matches = ceil(log2(len(players)))
        print("Number of matches set to {}".format(no_matches))
   
    # Generate games from options list
    games = []
    for x in range(len(options)-1):
        for y in range(x+1, len(options)):
            for _ in range(no_matches):
                games.append([
                    [MctsPlayer(no_simulations=options[x][0], exploration_factor=options[x][1], seed=randint(0, 10000), name="mcts_{}_{:.2f}".format(options[x][0], options[x][1])), 
                    MctsPlayer(no_simulations=options[y][0], exploration_factor=options[y][1], seed=randint(0, 10000), name="mcts_{}_{:.2f}".format(options[y][0], options[y][1]))], size])
    
    
    # Create a multithreaded pool and allocate the games
    start_time = time()
    with Pool() as p:
        results = p.starmap(play_game, games)
    
    total_time = time() - start_time
    
    # Setup turn time dict
    avg_turn_times = {}
    for player_name in players.keys():
        avg_turn_times[player_name] = []
    
    print(results[0])
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
    
    print(avg_turn_times)
    
    rating_hists = {}
    
    # Print results
    print("\nRESULTS------------------------------")
    print("Played a total of {} games which took {:.2f} s ({:.2f} s avg.)".format(len(games), total_time, total_time / (len(games))))
           
    print("\nFinal rankings:")
    for key in players.keys():
        player = players[key]
        rating_hists[player.name] = player.rating_history
        print("{}: played {}, won {}: {}".format(player.name, player.games_played, player.games_won, player.rating))
        
    print("-------------------------------------")
    
    hist_file = open("logs/results.pkl", "wb")
    pickle.dump(rating_hists, hist_file)
    hist_file.close()
    
    
    # Plot rating history
    plot_rating_hist(players)