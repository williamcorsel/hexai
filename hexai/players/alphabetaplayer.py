"""
Alpha-Beta Pruning player
"""
from random import seed, randint, choice
import numpy as np
# from players.baseplayer import BasePlayer
import logging
from time import time
from ctypes import c_int
from multiprocessing import Process, Value, Array
from random import randint

from hexai.players.baseplayer import BasePlayer
from hexai.transpositiontable import TranspositionTable

log = logging.getLogger(__name__.split('.')[-1])

INF = 9999 
LOSE = 1000 # Choose win value higher than possible score but lower than INF


class AlphaBetaPlayer(BasePlayer):

    def __init__(self, evaluation, use_id, use_tt, max_depth=3, max_time=0.5, color=None, name="AlphaBeta"):
        """Initialize Alpha-Beta player

        Args:
            evaluation (str): Type of evaluation to be used. Can be "random" or "dijkstra"
            use_id (bool): Whether to use iterative deepening
            use_tt (bool): Whether to use transposition tables
            max_depth (int, optional): Max search depth used when iterative deepening is not used. Defaults to 3.
            max_time (int, optional): Max search time in seconds used for iterative deepening. Defaults to 2.
            color (int, optional): Player color set when the game starts. Defaults to None.
            name (str, optional): Name id of the player for printing purposes. Defaults to "AlphaBeta".

        Raises:
            ValueError: When an unkown evaluation function is entered
        """
        super().__init__(name, color)
        
        self.max_depth = max_depth
        self.use_id = use_id
        self.use_tt = use_tt
        self.max_time = max_time
        
        if evaluation == "random":
            self.eval = self.eval_random
        elif evaluation == "dijkstra":
            self.eval = self.eval_dijkstra
        else:
            raise ValueError("Unkown evaluation function!")
        
        if self.use_tt:
            self.tt = TranspositionTable()
        
        self.turn_timer = None
        
       
    def reset(self):
        """Reset transposition table
        """
        self.tt = TranspositionTable() #Reset transposition table for every time a game is played
        
        
    def eval_random(self, color):
        """Evaluate board using a randomly generated number

        Returns:
            int: Assigned board score
        """
        self.eval_count += 1
        return self.local_random.randint(0, self.board.size*2) 
    
    
    def eval_dijkstra(self, color):
        """Evaluation based on distance to border. Score computed by taking difference of dijkstra score of opponent and current player

        Returns:
            int: Board evaluation score
        """
        self.eval_count += 1
        return self.get_dijkstra_score(self.board.get_opposite_color(color)) - self.get_dijkstra_score(color)

   
    def dijkstra_update(self, color, scores, updated):
        """Updates the given dijkstra scores array for given color

        Args:
            color (HexBoard.color): color to evaluate
            scores (int array): array of initial scores
            updated (bool array): array of which nodes are up-to-date (at least 1 should be false for update to do something)

        Returns:
            the updated scores
        """
        log.debug("Starting dijkstra algorithm")
        updating = True
        while updating: 
            updating = False
            for i, row in enumerate(scores): #go over rows
                for j, point in enumerate(row): #go over points 
                    if not updated[i][j]: 
                        neighborcoords = self.board.get_neighbors((i,j))
                        for neighborcoord in neighborcoords:
                            target_coord = tuple(neighborcoord)
                            path_cost = LOSE #1 for no color, 0 for same color, INF for other color 
                            if self.board.is_empty(target_coord):
                                path_cost = 1
                            elif self.board.is_color(target_coord, color):
                                path_cost = 0
                            
                            if scores[target_coord] > scores[i][j] + path_cost: #if new best path to this neighbor
                                scores[target_coord] = scores[i][j] + path_cost #update score
                                updated[target_coord] = False #This neighbor should be updated
                                updating = True #make sure next loop is started
        return scores
            
     
    def timed_turn_loop(self):
        """Search loop for Iterative Deepening search

        Returns:
            int: Evaluation score of the best move
            tuple: Best move
        """
        self.turn_timer = time()
        
        for depth in range(1, INF):
            result, move = self.alphabeta_nega(self.color, -INF, INF, depth)
            
            if result is not None and move is not None:
                if time() - self.turn_timer > self.max_time:
                    if result > best_score:
                        best_move = move
                        best_score = result
                else:
                    best_move = move
                    best_score = result
                
            # If position is winning or losing, stop searching deeper
            if best_score >= LOSE or best_score <= -LOSE:
                break
                       
        self.turn_timer = None       
            
        return best_score, best_move


    def do_turn(self, verbose=0):
        """Do a single turn

        Args:
            verbose (int, optional): How much to print. Defaults to 0.
        """
        assert self.board != None and self.color != None
        self.no_nodes_searched = 0
        self.no_cuts = 0
        self.turn_count += 1 #count amount of turns 
        
        if verbose > 0:
            print("Player {} AI is thinking...".format(self.color))
        
        start_time = time()
            
        if self.use_id:
            # Do Iterative Deepening using max_time
            best_score, best_move = self.timed_turn_loop()
        else:
            # Do base version using max_depth
            best_score, best_move = self.alphabeta_nega(self.color, -INF, INF, self.max_depth)
        
        turn_time = time() - start_time
        self.turn_time += turn_time
                
        self.board.place(best_move, self.color)
        
        if verbose > 0:
            print("AI took {:.4f} s to decide, visited {} states, and cut {} times".format(turn_time, self.no_nodes_searched, self.no_cuts))
            if self.use_tt:
                print("TT found {} full hits and {} half hits".format(self.tt_hits_full, self.tt_hits_half))
            print("Doing move: ", best_move, "With score:", best_score)
    
   
    def get_dijkstra_score(self, color): 
        """gets the dijkstra score for a certain color, differs from dijkstra eval in that it only considers the passed color

        Args:
            color (Hexboard.Color): What color to evaluate

        Returns:
            int: score of how many (shortest) path-steps remain to victory
        """
        scores = np.array([[LOSE for i in range(self.board.size)] for j in range(self.board.size)])
        updated = np.array([[True for i in range(self.board.size)] for j in range(self.board.size)]) #Start updating at one side of the board 

        #alignment of color (blue = left->right so (1,0))
        alignment = (0, 1) if color == self.board.BLUE else (1, 0)


        for i in range(self.board.size):
            newcoord = tuple([i * j for j in alignment]) #iterate over last row or column based on alignment of current color

            updated[newcoord] = False
            if self.board.is_color(newcoord, color): #if same color --> path starts at 0
                scores[newcoord] = 0
            elif self.board.is_empty(newcoord): #if empty --> costs 1 move to use this path 
                scores[newcoord] = 1
            else: #If other color --> can't use this path
                scores[newcoord] = LOSE

        scores = self.dijkstra_update(color, scores, updated)

        #self.board.print_dijkstra(scores)

        results = [scores[alignment[0] * i - 1 + alignment[0]][alignment[1]*i - 1 + alignment[1]] for i in range(self.board.size)] #take "other side" to get the list of distance from end-end on board
        best_result = min(results)
        
        # if best_result == 0:
        #     best_result = -500
        
        log.debug("Best score for color {}: {}".format(color, best_result))
        return best_result #return minimum distance to get current score
        
    
    def get_moves(self):
        """Gets all possible moves from board -> analogous to all empty cells

        Returns:
            list: list of move coordinate tuples
        """
        return self.board.get_empty_cells()
    
    
    def alphabeta_nega(self, color, alpha, beta, depth):
        """AlphaBeta in NegaMax form
        Inspired by: https://www.researchgate.net/figure/Enhanced-NegaMax-with-Alpha-Beta-Property-Pseudo-Code_fig4_262672371
                     https://en.wikipedia.org/wiki/Negamax

        Args:
            color (int): Player color to move
            alpha (int): Minimum score that max player is assured to reach
            beta (int): Maximum score that min player is assured to reach
            depth (int): Current search depth

        Returns:
            int: Value of the board
            tuple: Current best move
        """
        # If turn timer is exceeded quit the loop ASAP -> used for iterative deepening
        if self.turn_timer is not None and time() > self.turn_timer + self.max_time:
            return None, None
        

        best_move = None    
        best_value = -INF #reset best_value

        # If cache is used check that first
        if self.use_tt:
            hit, tt_move, tt_score = self.tt.lookup(depth, self.board.tostring()) 
            
            # If we find a hit return that score
            if hit == 1: #if not actual depth found, but somewhere shallower was found - try best found move first 
                self.tt_hits_half += 1 #This is handles in the for-loop

            elif hit == 2: #if actual best move at passed depth has been found
                self.tt_hits_full += 1
                log.debug("found move {} with score {}".format(tt_move, tt_score))
                return tt_score, tt_move
            
        
        
        # Check if we are at maxdepth or the game is over
        # TODO: stop if board is full or when previous move caused a win?
        if depth <= 0 or self.board.check_win(self.board.get_opposite_color(color)):
        #if depth <= 0 or len(self.board.get_empty_cells()) == 0:
            best_value = self.eval(color)
            best_move = None
            return best_value, best_move
        else:
            self.no_nodes_searched += 1
            moves = self.get_moves()
            
            # if cache is used, search the best move first
            if self.use_tt and tt_move is not None:
                moves = [tt_move] + moves
            
            for move in moves:
                self.board.place(move, color)
                
                log.debug("Trying move {}".format(move))
            
                new_value, _ = self.alphabeta_nega(self.board.get_opposite_color(color), -beta, -alpha, depth-1)
                log.debug("try {} for color {}\tGot value: {}".format(move, color, new_value))
                
                # This happens if the turn_timer expires for ID
                if new_value is None:
                    self.board.take(move)
                    return best_value, best_move
                
                new_value = -new_value
                    
                if new_value > best_value: 
                    best_move = move 
                    best_value = new_value
                
                self.board.take(move)
                
                alpha = max(alpha, best_value)
                if alpha >= beta:
                    self.no_cuts += 1
                    break

        # Store best move if cache is used    
        if self.use_tt:
            assert best_move is not None
            assert best_value is not None
            self.tt.store(depth, self.board.tostring(), best_move, best_value)    
            
        return best_value, best_move


    
if __name__ == "__main__":
    from hexai.hexboard import HexBoard
    
    # Set logging
    logging.basicConfig(format='%(levelname)s:%(name)s: %(message)s',
                        level=logging.INFO)
    
    seed(42)
    
    board = HexBoard(5)
    player = AlphaBetaPlayer("dijkstra", use_id=False, use_tt=False, max_depth=1, color=HexBoard.BLUE)
    player.board = board
    
    board.place((0,3), HexBoard.BLUE)
    board.place((2,1), HexBoard.BLUE)
    board.place((1,2), HexBoard.BLUE)
    
    board.place((2,3), HexBoard.RED)
    board.place((2,4), HexBoard.RED)
    board.place((2,2), HexBoard.RED)
    board.place((3,0), HexBoard.RED)
    
    
    print(board)
    player.get_dijkstra_score(HexBoard.BLUE)
    
    # board = HexBoard(3)
    # player = AlphaBetaPlayer("dijkstra", use_id=False, use_tt=False, max_depth=1, color=HexBoard.BLUE)
    # player.board = board
    
    # board.place((0,0), HexBoard.BLUE)
    # print(board)
    
    # assert player.get_dijkstra_score(HexBoard.BLUE) == 2
    # assert player.get_dijkstra_score(HexBoard.RED) == 3
    
    # board.place((1,0), HexBoard.BLUE)
    # print(board)
    
    # assert player.get_dijkstra_score(HexBoard.BLUE) == 1
    # assert player.get_dijkstra_score(HexBoard.RED) == 3
  
    # board.place((2,0), HexBoard.BLUE)
    # print(board)
    
    # assert player.get_dijkstra_score(HexBoard.BLUE) == 0
    # assert player.get_dijkstra_score(HexBoard.RED) == LOSE
    # print("Dijkstra score", player.eval_dijkstra(HexBoard.BLUE))
    
    # board.take((2,0))
    
    # player.do_turn()
    # print(board)
    
    # board.place((1,1), HexBoard.RED)
    # board.place((1,2), HexBoard.RED)
    # print("Dijkstra score", player.eval_dijkstra(HexBoard.BLUE))
    # print(board)
    # player.do_turn()
    # print(board)
    
    # print("\n----------------------------------------\n")
    
    
 
    