"""
humanplayer.py: Human controlled player using terminal input
"""
from hexai.players.baseplayer import BasePlayer
from blessed import Terminal

t = Terminal()

class HumanPlayer(BasePlayer):

    def __init__(self, name="Human", color=None):
        """Initialize human player
        """
        super().__init__(name, color)
    
    
    def parse_move(self, move):
        """Parses human move input to a coordinate

        Args:
            move (string): input string of the move, should consist of a letter followed by a number

        Returns:
            tuple: Move coordinates (x, y) that were parsed. (-1, -1) if parsing failed
        """
        # Check the move format
        move = move.strip()
        if len(move) < 2 or len(move) > 3:
            return (-1, -1)
        
        if not move[0].isalpha() or not move[1:].isdigit():
            return (-1, -1)
        
        # Convert character to number
        char_number = ord(move[0].lower()) - ord('a') 
        return (char_number, int(move[1:]))
        
        
    def do_turn(self, verbose=0):
        """Perform a turn by asking the human for input
        """
        assert self.board != None and self.color != None
        
        input_msg = "Do your move "
        
        if self.color == self.board.BLUE:
            input_msg += t.blue("Player 1: ")
        elif self.color == self.board.RED:
            input_msg += t.red("Player 2: ")
        
        input_move = input(input_msg)
        move = self.parse_move(input_move)
        print("Doing move: ", move)
        while not self.board.place(move, self.color):
            input_move = input("Incorrect move! Try again: ")
            move = self.parse_move(input_move)
            print("Doing move: ", move)
            