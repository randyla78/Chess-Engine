import chess
import random

class Engine:

    def __init__(self, board, max_depth, bot_color):
        self.board=board
        self.bot_color=bot_color
        self.max_depth=max_depth
    
    def get_best_move(self):
        return self.engine(None, 1)

    def get_evaluation(self):
        eval = 0
        #get evaluation by returning total piece values
        eval+=self.get_piece_values()
        eval+=self.check_checkmate() + self.opening() + 0.001*random.random()
        return eval

    def engine(self, node_value, depth):
        #end recursion if max depth reached or if no more legal moves
        if ( depth == self.max_depth or self.board.legal_moves.count() == 0):
            return self.get_evaluation()
        else:
            move_list = list(self.board.legal_moves)
            new_node_value = None
            #uneven depth implies engine's turn
            if(depth % 2 != 0):
                new_node_value = float("-inf")
            else:
                new_node_value = float("inf")
            for i in move_list:
                #temporarily play move to get the value of that move
                self.board.push(i)
                value = self.engine(new_node_value, depth + 1) 
                if(value > new_node_value and depth % 2 != 0):
                    if (depth == 1):
                        move=i
                    new_node_value = value
                #minimizing during player's turn
                elif(value < new_node_value and depth % 2 == 0):
                    new_node_value = value
                #alpha-beta prunning 
                if (node_value != None and value < node_value and depth % 2 == 0):
                    self.board.pop()
                    break
                elif (node_value != None and value > node_value and depth % 2 != 0):
                    self.board.pop()
                    break
                self.board.pop()
            if (depth>1):
                return new_node_value
            else:
                return move

    def get_piece_values(self):
        total = 0
        for i in range(64):
            piece_value = 0
            if(self.board.piece_type_at(i) == chess.PAWN):
                piece_value += 1
            elif (self.board.piece_type_at(i) == chess.ROOK):
                piece_value += 5.1
            elif (self.board.piece_type_at(i) == chess.BISHOP):
                piece_value += 3.33
            elif (self.board.piece_type_at(i) == chess.KNIGHT):
                piece_value += 3.2
            elif (self.board.piece_type_at(i) == chess.QUEEN):
                piece_value += 8.8
            if (self.board.color_at(i)!=self.bot_color):
                total -=piece_value
            else:
                total +=piece_value
        return total

    def check_checkmate(self):
        if (self.board.legal_moves.count()==0):
            if (self.board.turn == self.bot_color):
                return -999
            else:
                return 999
        else:
            return 0
        
    def opening(self):
        if (self.board.fullmove_number<10):
            if (self.board.turn == self.bot_color):
                return 1/30 * self.board.legal_moves.count()
            else:
                return -1/30 * self.board.legal_moves.count()
        else:
            return 0