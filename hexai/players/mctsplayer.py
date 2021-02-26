"""
Monte-Carlo Tree Search Algorithm

Inspired by pseudocode from the book and https://github.com/int8/monte-carlo-tree-search
"""
from time import time
from copy import deepcopy
import logging
from random import Random

import numpy as np

from hexai.players.baseplayer import BasePlayer


class MctsPlayer(BasePlayer):
    
    
    def __init__(self, name="Mcts", seed=None, color=None, max_time=120, no_simulations=100000, exploration_factor=1.41):
        """Initialises Mcts player

        Args:
            name (str, optional): Name id of the player for printing purposes. Defaults to "Mcts".
            seed (int, optional): Seed assigned to the player. Defaults to None.
            color (int, optional): Player number. Defaults to None. Is set when game starts in Hex.
            max_time (int, optional): Max time (in seconds) the player can think. Defaults to 2.
            no_simulations (int, optional): Max rollouts the player can do per turn. Defaults to 100000.
            exploration_factor (float, optional): C_p value. Defaults to 1.4.
        """
        super().__init__(name, seed, color)
        
        self.max_time = max_time
        self.no_simulations = no_simulations # n
        self.exploration_factor = exploration_factor # C_p
        self.turn_timer = None
  
        
        self.root = None # Search Tree, set in mcts. 
        
    
    def do_turn(self, verbose=0):
        """Do a single turn

        Args:
            verbose (int, optional): How much to print. Defaults to 0.
        """
        assert self.board != None and self.color != None
    
        self.turn_timer = time()
        
        best_child = self.mcts()
        best_move = best_child.move
        
        self.board.place(best_move, self.color)

        self.turn_count += 1
        self.turn_time += time() - self.turn_timer
        
    
    
        
    def mcts(self):
        """Perform Monte-Carlo Tree Search

        Returns:
            MctsNode: Root child node witht the best score / move
        """
        # Initialize search tree.
        self.root = MctsNode(self.board, self.color, self.color, self.local_random) 
        
        # Start main loop
        iter_count = 0
        while self.time_left() and iter_count < self.no_simulations:
            # Select a node from the tree to search for by using the UTC formula
            node = self.select()
            
            # Play a random MC game on that node
            winner = node.rollout()
            
            # Backpropagate the result up the tree (updating n_j and w_j values)
            node.backpropagate(winner)
            iter_count += 1
        
        self.eval_count += iter_count
        
        # When we run out of resources, select the best root child    
        return self.root.best_child(exploration_factor=0) #  just select child with best score and don't care about exploration
            
            
    
    def select(self):
        """Walk through the tree and select the next node

        Returns:
            MctsNode: Best child node to search
        """
        cur_node = self.root
        
        # Go through the tree until we hit the bottom
        while not cur_node.is_leaf():
            if not cur_node.fully_extended():
                # If there are still unplayed_moves, expand the node, continue with that child node
                return cur_node.expand()
            else:
                # Else select the best child from the current node and continue there
                cur_node = cur_node.best_child(self.exploration_factor)
        
        return cur_node
        
    
    def time_left(self):
        """Whether there is time left to search

        Returns:
            bool: Wether turn timer has been exceeded
        """
        return time() <= self.turn_timer + self.max_time


class MctsNode():
    
    def __init__(self, state, color_to_move, mcts_color, random, parent=None):
        """Initialises new node

        Args:
            state (HexBoard): HexBoard object representing current board state
            color_to_move (int): Player color that is to move in the current state
            mcts_color (int): Color of the MCTS player. Used to count wins.
            random (Random): local random object set by MctsPlayer seed.
            parent (MctsNode, optional): Parent node. Defaults to None.
        """
        self.state = state
        self.move = None # Saves the move that has been taken in this node.
        self.parent = parent
        self.color_to_move = color_to_move
        self.mcts_color = mcts_color
        self.children = [] # Child board states
        self.local_random = random

        self.turn_count = 0 #for evaluation purposes
        self.eval_count = 0

        self.no_visits = 0
        self.no_wins = 0
    
        self.untried_moves = self.state.get_empty_cells() # Moves that can still be tried
        
    
    def expand(self):
        """Expands the current node by creating a new child node

        Returns:
            MctsNode: Child node containing the board with a next move
        """
        # Get a new move from the untried_moves list
        move = self.untried_moves.pop()
        
        # Create a new board from current one and do the move
        next_board = self.state.copy_state()
        next_board.place(move, self.color_to_move)
        
        # Create new node for the tree using the created board and add that to the children list
        new_child = MctsNode(next_board, self.state.get_opposite_color(self.color_to_move), self.mcts_color, self.local_random, parent=self)
        new_child.move = move
        self.children.append(new_child)
        
        return new_child
    
    
    def best_child(self, exploration_factor):
        """Select best child using UCT function:
        
        UTC(j) = w_j / n_j + C_p * sqrt( ln(n) / n_j )

        Args:
            exploration_factor (float): C_p exploration factor

        Returns:
            MctsNode: Best child node to continue search
        """
        weights = [
            (child.no_wins / child.no_visits) + 
            exploration_factor * np.sqrt((np.log(self.no_visits) / child.no_visits))
            for child in self.children
        ]
        return self.children[np.argmax(weights)]
    
    
    def rollout(self):
        """Play out a random MC game

        Returns:
            bool: Wheter MCTS player won the game
        """
        cur_state = self.state.copy_state() # Don't edit real board
        cur_color = deepcopy(self.color_to_move)
        
        # Get random order of moves
        moves = cur_state.get_empty_cells()
    
        self.local_random.shuffle(moves)
        
        # Place all moves
        while len(moves) > 0:
            move, moves = moves[0], moves[1:]
            cur_state.place(move, cur_color)
            cur_color = self.state.get_opposite_color(cur_color)
            
        return cur_state.check_win(self.mcts_color)
    
    
    def backpropagate(self, winner):
        """Walks back to the root and update visit and win values

        Args:
            winner (bool): Whether MCTS player won the game
        """
        self.no_visits += 1
        #self.results[winner] += 1
        if winner:
            self.no_wins += 1
        
        if self.parent is not None:
            self.parent.backpropagate(winner)


    def is_leaf(self):
        """Checks if node is a leaf node -> end of a game

        Returns:
            bool: Whether previous player already won the game
        """
        return self.state.check_win(self.state.get_opposite_color(self.color_to_move))
    
    
    def fully_extended(self):
        """Whether there are moves left to try in this node

        Returns:
            bool: Whether untried_moves list is empty or not
        """
        return len(self.untried_moves) == 0
    
    
if __name__ == "__main__":
    from hexai.hexboard import HexBoard
    
    # Set logging
    logging.basicConfig(format='%(levelname)s:%(name)s: %(message)s',
                        level=logging.INFO)
    
    seed(42)
    
    board = HexBoard(3)
    player = MctsPlayer(max_time=0.5, color=HexBoard.BLUE)
    player.board = board
    
    player.do_turn()
    print(board)