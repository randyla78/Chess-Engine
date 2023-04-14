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
        bot = 0
        #Sums up the material values
        bot+=self.get_piece_values()
        bot+=self.check_checkmate() + self.opening() + 0.001*random.random()
        return bot

    def check_checkmate(self):
        if (self.board.legal_moves.count()==0):
            if (self.board.turn == self.bot_color):
                return -999
            else:
                return 999
        else:
            return 0

    #to make the engine developp in the first moves
    def opening(self):
        if (self.board.fullmove_number<10):
            if (self.board.turn == self.bot_color):
                return 1/30 * self.board.legal_moves.count()
            else:
                return -1/30 * self.board.legal_moves.count()
        else:
            return 0

    #Takes a square as input and 
    #returns the corresponding Hans Berliner's
    #system value of it's resident
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

        
    def engine(self, node_value, depth):
        
        #reached max depth of search or no possible moves
        if ( depth == self.max_depth or self.board.legal_moves.count() == 0):
            return self.get_evaluation()
        
        else:
            #get list of legal moves of the current position
            move_list = list(self.board.legal_moves)
            
            #initialise newCandidate
            new_node_value = None
            #(uneven depth means engine's turn)
            if(depth % 2 != 0):
                new_node_value = float("-inf")
            else:
                new_node_value = float("inf")
            
            #analyse board after deeper moves
            for i in move_list:

                #Play move i
                self.board.push(i)

                #Get value of move i (by exploring the repercussions)
                value = self.engine(new_node_value, depth + 1) 

                #Basic minmax algorithm:
                #if maximizing (engine's turn)
                if(value > new_node_value and depth % 2 != 0):
                    #need to save move played by the engine
                    if (depth == 1):
                        move=i
                    new_node_value = value
                #if minimizing (human player's turn)
                elif(value < new_node_value and depth % 2 == 0):
                    new_node_value = value

                #Alpha-beta prunning cuts: 
                #(if previous move was made by the engine)
                if (node_value != None and value < node_value and depth % 2 == 0):
                    self.board.pop()
                    break
                #(if previous move was made by the human player)
                elif (node_value != None and value > node_value and depth % 2 != 0):
                    self.board.pop()
                    break
                
                #Undo last move
                self.board.pop()

            #Return result
            if (depth>1):
                #return value of a move in the tree
                return new_node_value
            else:
                #return the move (only on first move)
                return move


'''
import chess
import random

class Engine:
    def __init__(self, board, max_depth, color): #color of engine
        self.board = board
        self.max_depth = max_depth
        self.color = color

    def getBestMove(self):
        return self.engine(None, 1)
    
    def evalFunct(self):
        compt = 0
        for i in range(64):
            compt+=self.squareResPoints(chess.SQUARES[i])
        compt+=self.mate_opportunity()+self.opening()+0.001*random.random()



    def opening(self):
        if (self.board.fullmove_number<10):
            if (self.board.turn == self.color):
                return 1/30 * self.board.legal_moves.count()
            else:
                return -1/30 * self.board.legal_moves.count()
        else:
            return 0
        
    #no moves left means potential checkmate
    def mate_opportunity(self):
        if (self.board.legal_moves.count()==0):
            if (self.board.turn == self.color):
                return -9999
            else:
                return 9999
        
        else: 
            return 0
        
    def squareResPoints(self, square):
        pieceValue = 0
        if(self.board.piece_type_at(square) == chess.PAWN):
            pieceValue = 1
        elif (self.board.piece_type_at(square) == chess.ROOK):
            pieceValue = 5.1
        elif (self.board.piece_type_at(square) == chess.BISHOP):
            pieceValue = 3.33
        elif (self.board.piece_type_at(square) == chess.KNIGHT):
            pieceValue = 3.2
        elif (self.board.piece_type_at(square) == chess.QUEEN):
            pieceValue = 8.8

        if (self.board.color_at(square)!=self.color):
            return -pieceValue
        else:
            return pieceValue



    def engine(self, candidate, depth):
        #base case for recurion:
        if (depth == self.max_depth or self.board.legal_moves.count()==0):
            return self.evalFunct()
        else:
            move_list = list(self.board.legal_moves)
            newCandidate=None
            if(depth % 2 !=0):
                newCandidate=float('-inf')
            else:
                newCandidate=float('-inf')

            for i in move_list:
                self.board.push(i)
                value = self.engine(newCandidate, depth+1)
                print("value is:")
                print(value)
                print("type is: ")
                    #minimize for engine's turn
                if (value>newCandidate and depth%2!=0):
                
                    if(depth==1):
                        move=i
                    newCandidate=value

                    #minimize for player's turn
                elif (value<newCandidate and depth%2==0):
                    newCandidate=value

                    #aplha-beta pruning, if previous move made by computer
                if (candidate != None and value<candidate and depth%2==0):
                    self.board.pop()
                    break

                    #aplha-beta pruning, if previous move made by human
                elif (candidate != None and value>candidate and depth%2!=0):
                    self.board.pop()
                    break                    

                #Undo last move
                self.board.pop()

            if (depth>1):
            #return value of a node in the tree
                return newCandidate
            else:
                return move
'''