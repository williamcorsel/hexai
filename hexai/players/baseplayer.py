from trueskill import Rating
from random import Random

class BasePlayer(object):

    def __init__(self, name, seed=None, color=None):
        """Initialise base player values

        Args:
            name (str): Name of the player
            seed (int, optional): Set manual seed of player if random components are used. Defaults to None.
            color (int, optional): Player color. Defaults to None.
        """
        self.name = name
        self.color = color
        self.board = None
        self.rating = Rating()
        self.rating_history = [self.rating]
        self.games_played = 0
        self.games_won = 0
        
        self.local_random = Random(seed)

        self.eval_count= 0 #for total amount of evaluations
        self.turn_count = 0  #for total amount of turns
        self.turn_time = 0

        self.tt_hits_full = 0 #for transition table evaluation
        self.tt_hits_half = 0 #for transition table evaluation
    
    
    def reset(self):
        pass
    
    def set_seed(self, seed):
        """Set seed of player

        Args:
            seed (int): Seed to set
        """
        self.local_random = Random(seed)


    def set_board_and_color(self, board, color):
        """Set board and color for the player

        Args:
            board (HexBoard): Board to be used
            color (int): Color assigned to player
        """
        self.board = board
        self.color = color
        
        
    def set_rating(self, rating):
        """Set rating

        Args:
            rating (trueskill.Rating): Rating assigned to player
        """
        self.rating_history.append(rating)
        self.rating = rating
        
        
        
    def do_turn(self, verbose=0):
        """Do a single turn

        Args:
            verbose (int, optional): How much to print. Defaults to 0.
        """
        raise NotImplementedError("Abstract method, please subclass")