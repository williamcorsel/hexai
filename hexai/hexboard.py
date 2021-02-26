""" 
hexboard.py: Gameboard class
"""
import numpy as np
from blessed import Terminal

t = Terminal()

class HexBoard:
    EMPTY = 0
    BLUE = 1
    RED = 2

    def __init__(self, board_size, board=None):
        """Initialises the board

        Args:
            board_size (int): Size of the board
            board (np.array, optional): Initial board data. Defaults to None
        """

        self.size = board_size
        
        if board is None:
            self.board = np.full((board_size, board_size), HexBoard.EMPTY)
        else:
            self.board = board


    def copy_state(self):
        """Returns a copy object of the current board state

        Returns:
            HexBoard: copy of current object
        """
        return HexBoard(self.size, self.board.copy())


    def border(self, color, move):
        """Checks if move is on the border of the board

        Args:
            color (int): Player to move
            move (tuple): Move (x, y) which is taken

        Returns:
            bool: True if the move is on the border and False if not
        """
        (nx, ny) = move
        return (color == HexBoard.BLUE and nx == self.size-1) or (color == HexBoard.RED and ny == self.size-1)


    def get_neighbors(self, coordinates):
        """Gets all the neighbouring cells of a given cell

        Args:
            coordinates (tuple): Cell (x, y) coordinates

        Returns:
            list: List of neighbouring cell coordinates tuples
        """
        (cx,cy) = coordinates
        neighbors = []
        if cx-1 >= 0: neighbors.append((cx-1,cy))
        if cx+1 < self.size: neighbors.append((cx+1,cy))
        if cx-1 >= 0 and cy+1 <= self.size-1: neighbors.append((cx-1,cy+1))
        if cx+1 < self.size and cy-1 >= 0: neighbors.append((cx+1,cy-1))
        if cy+1 < self.size: neighbors.append((cx,cy+1))
        if cy-1 >= 0: neighbors.append((cx,cy-1))

        return neighbors


    def traverse(self, color, move, visited):
        """Recursively moves the pieces of a single color and check if a border is reached

        Args:
            color (int): Player color
            move (tuple): (x, y) coordinates of move
            visited (dict): Dictionary containing the vistited coordinates

        Returns:
            bool: Whether the border is recursively reached
        """
        # If cell does not contain a correctly colored piece or the cell was already visited
        if not self.is_color(move, color) or (move in visited and visited[move]):
            return False

        # If the border is reached
        if self.border(color, move):
            return True

        # If not then this cell is visited
        visited[move] = True

        # And we go traverse the neighbouring cells
        for n in self.get_neighbors(move):
            if self.traverse(color, n, visited):
                return True

        return False


    def check_win(self, color):
        """Checks if a player won the game

        Args:
            color (int): Player color

        Returns:
            bool: Whether the player created a bridge accross the board
        """
        for i in range(self.size):
            if color == HexBoard.BLUE:
                move = (0,i)
            else:
                move = (i,0)

            if self.traverse(color, move, {}):
                #self.is_game_over = True
                return True

        return False
    
    
    def get_opposite_color(self, current_color):
        """Get opposite color of current one

        Args:
            current_color (int): Player color

        Returns:
            int: Opposite player color
        """
        if current_color == HexBoard.BLUE:
            return HexBoard.RED
        return HexBoard.BLUE
    
    
    def get_empty_cells(self):
        """Gets a list of empty cell coordinates

        Returns:
            list: List of coordinate tuples of empty cells
        """
        results = np.where(self.board == HexBoard.EMPTY)
        return list(zip(results[0], results[1]))
    
    
    def board_empty(self):
        """Checks if the board is empty

        Returns:
            bool: Whether board only contains zero
        """
        return not np.any(self.board)
    
    
    def take(self, coordinates):
        """Empty a given cell

        Args:
            coordinates (tuple): Cell (x, y) coordinates
        """
        self.board[coordinates] = HexBoard.EMPTY


    def place(self, coordinates, color):
        """Place a piece of a color on the board

        Args:
            coordinates (tuple): Cell (x, y) coordinates
            color (int): Player color
        """
        if not self.is_legal_move(coordinates) or self.board[coordinates] != HexBoard.EMPTY:
            return False 
        
        #if not self.game_over:
        self.board[coordinates] = color
        
        return True


    def tostring(self):
        """Converts board state to a string format

        Returns:
            str: String representation of the board datastructure
        """
        return np.array2string(self.board)


    def is_legal_move(self, move):
        """Checks if coordinate is within the board boundaries. Used for sanity checking

        Args:
            move (tuple): (x, y) coordinates of move

        Returns:
            bool: Whether the move is within the board bounds
        """
        return move[0] >= 0 and move[0] < self.size and move[1] >= 0 and move[1] < self.size


    def is_empty(self, coordinates):
        """Checks if cell is empty

        Args:
            coordinates (tuple): Cell (x, y) coordinates

        Returns:
            bool: Whether specified cell is empty
        """
        #assert self.is_legal_move(coordinates)
        return self.board[coordinates] == HexBoard.EMPTY


    def is_color(self, coordinates, color):
        """Checks if cell is filled with a certain color

        Args:
            coordinates (tuple): Cell (x, y) coordinates
            color (int): Player color

        Returns:
            bool: Whether specified cell contains the color
        """
        #assert self.is_legal_move(coordinates)
        return self.board[coordinates] == color
        
    
    def __str__(self):
        s = "   "
        for y in range(self.size):
            s += "{} ".format(chr(y+ord('a')))
        s += "\n  {}\n".format(t.red("-" * (self.size * 2 + 2)))
        
        for y in range(self.size):
            s += " " * (y - len(str(y))+1)
            s += str(y) + t.blue(" \\ ")

            for x in range(self.size):
                piece = self.board[x][y]

                if piece == HexBoard.BLUE: s += t.blue("B ")
                elif piece == HexBoard.RED: s += t.red("R ")
                else: s += "- "

            s += t.blue("\\ ") + str(y) + "\n"

        s += " " * (self.size + 2)
        s += t.red("-" * (self.size * 2 + 2)) + "\n"
        s += " " * (self.size + 4)

        for y in range(self.size):
            s += "{} ".format(chr(y+ord('a')))
        s += "\n"
        
        return s
        


    def print_dijkstra(self, scores):
        """Printout of the board in text
        """
        print("   ", end="")
        for y in range(self.size):
            print(chr(y+ord('a')),"",end="")
        print("")

        print(" ", t.red("-" * (self.size * 2 + 2)))

        for y in range(self.size):
            print(" " * (y - len(str(y))+1), end="")
            print(y, t.blue("\\ ") , end="")

            for x in range(self.size):
                piece = self.board[x][y]
                if scores[x][y] < 999: #TODO: this should be inf
                    if piece == HexBoard.BLUE: print(t.blue("{:d} ".format(scores[x][y])),end="")
                    elif piece == HexBoard.RED: print(t.red("{:d} ".format(scores[x][y])),end="")
                    else: print("{} ".format(scores[x][y]),end="")
                else: 
                    if piece == HexBoard.BLUE: print(t.blue("x "),end="")
                    elif piece == HexBoard.RED: print(t.red("x "),end="")
                    else: print("x ",end="")

            print(t.blue("\\ "), y)

        print(" " * (self.size + 2), end="")
        print(t.red("-" * (self.size * 2 + 2)))
        print(" " * (self.size + 3), end="")

        for y in range(self.size):
            print(chr(y+ord('a')), "", end="")
        print("")


if __name__ == "__main__":
    board = HexBoard(5)
    
    board.place((0,0), HexBoard.BLUE)
    board.place((0,1), HexBoard.BLUE)
    board.place((0,2), HexBoard.BLUE)
    board.place((0,3), HexBoard.BLUE)
    board.place((0,4), HexBoard.BLUE)
    
    board.place((4,0), HexBoard.BLUE)
    board.place((4,1), HexBoard.BLUE)
    board.place((4,2), HexBoard.BLUE)
    board.place((4,3), HexBoard.BLUE)
    board.place((4,4), HexBoard.BLUE)
    
    board.place((1,2), HexBoard.BLUE)
    board.place((2,2), HexBoard.BLUE)
    board.place((3,2), HexBoard.BLUE)
    
    print(board)
    
    board = HexBoard(5)
    board.place((0,0), HexBoard.RED)
    board.place((0,1), HexBoard.RED)
    board.place((0,2), HexBoard.RED)
    board.place((0,3), HexBoard.RED)
    board.place((0,4), HexBoard.RED)
    
    board.place((1,2), HexBoard.RED)
    board.place((2,2), HexBoard.RED)
    board.place((3,2), HexBoard.RED)
    board.place((4,2), HexBoard.RED)
    
    board.place((1,0), HexBoard.RED)
    board.place((2,0), HexBoard.RED)
    board.place((3,0), HexBoard.RED)
    board.place((4,0), HexBoard.RED)
    
    board.place((1,4), HexBoard.RED)
    board.place((2,4), HexBoard.RED)
    board.place((3,4), HexBoard.RED)
    board.place((4,4), HexBoard.RED)
    
    print(board)
    
    board = HexBoard(5)
    board.place((0,0), HexBoard.BLUE)
    board.place((1,1), HexBoard.BLUE)
    board.place((2,2), HexBoard.BLUE)
    board.place((3,3), HexBoard.BLUE)
    board.place((4,4), HexBoard.BLUE)
    
    board.place((0,4), HexBoard.BLUE)
    board.place((1,3), HexBoard.BLUE)
    board.place((3,1), HexBoard.BLUE)
    board.place((4,0), HexBoard.BLUE)
    
    print(board)