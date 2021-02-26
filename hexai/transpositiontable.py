""" 
transpositiontable.py: Tranposition Table cache for alpha-beta players
TODO: look into improvements -> https://github.com/duilio/c4/blob/master/c4/cache.py
"""
import numpy as np

class TranspositionTable():
    
    def __init__(self):
        """Init Transposition Table

            Movelist will contain a dict for each dept h containing
            a move and score for a given board state
        """
        self.move_list = {}
      
        
    def store(self, depth, state, move, score):
        """Store record in the table

        Args:
            depth (int): Search depth
            state (HexBoard): Board state
            move (tuple): Best move for the board state
            score (int): Score assigned to that state
        """
        if not state in self.move_list:
            self.move_list[state] = {}
        

        self.move_list[state][depth] = (move, score)
      
        
    def lookup(self, depth, state):
        """Checks if TT contains a record for the given state

        Args:
            depth (int): Search depth
            state (HexBoard): Board state

        Returns:
            int: 0: no entry found, 1: state found but lower than desired depth, 2:state found at desired depth 
            tuple: Best move for the state
            int: Assigned score of the state
        """
        
        if state in self.move_list:
            # State was already stored
            if depth in self.move_list[state]:
                # State of current depth was found so return move of that one
                return 2, self.move_list[state][depth][0], self.move_list[state][depth][1]
            else:
                # State was not found on this depth -> return False but still give best move found. 
                depths = [d for d in self.move_list[state]]

                if len(depths) == 0:
                    return 0, None, None #if No entries found at all
               
                maxdepth = np.max(depths)#take only max depth
             
                return 1, self.move_list[state][maxdepth][0], self.move_list[state][maxdepth][1] #Return the best move for the max depth
            
        return 0, None, None
        