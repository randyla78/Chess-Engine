from flask import Flask, redirect, url_for, render_template, request, session, jsonify, request
import chess_engine as ce #python file
import chess as ch
import config

app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config['SECRET_KEY']

@app.route("/")
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template('about.html')

#CHESS GAME FUNCTIONS (tic tac toe game is below)
@app.route("/chess")
def chess():
    return render_template('/chess.html')

chess_game_running = True

class Main:
    def __init__(self, board=ch.Board):
        self.board = board

def playEngineMove(maxDepth, color):
    engine = ce.Engine(game.board, maxDepth, color)
    best_move = engine.get_best_move()
    return best_move

@app.route("/chess_settings", methods=['POST'])
def chess_settings():
    global chess_game_running
    global user_color
    global depth
    global with_engine
    global kings_moved
    global game
    global promoted_pawns
    chess_game_running = True
    kings_moved.clear()
    promoted_pawns.clear()
    #get game settings from ajax
    settings = request.get_json()
    user_color = settings["color_select"]
    depth = settings["difficulty"]
    with_engine = settings["with_engine"]
    #create a new board object
    newBoard = ch.Board()
    game = Main(newBoard)
    game.board.reset
    return "game start"

promoted_pawns = []
previous_move = {"previous_piece":"N/a", "from_square":"a1", "to_square":"a1"}

#receives from ajax the move the user tries to play
@app.route("/make_move", methods=["POST"])
def make_move():
    #get all variables from game settings
    global user_color
    global depth
    global with_engine
    global chess_game_running
    global previous_move
    castle_check=0
    #gets the move the user tried to play
    move_dict = request.get_json()
    if chess_game_running == False:
        return "game over"
    #try to play move
    try:
        selected_piece = move_dict['selected_piece']
        current_square = move_dict['current_square']
        to_square = move_dict['to_square']
        #convert move to proper chess library format
        current_square = ch.SQUARE_NAMES.index(current_square)
        to_square = ch.SQUARE_NAMES.index(to_square)
        #check if a pawn is promoting, then make the move
        if check_promote(selected_piece, move_dict["current_square"], move_dict["to_square"])==True and selected_piece not in promoted_pawns:
            #keep track of all pawns that promoted
            promoted_pawns.append(selected_piece)
            move = ch.Move.from_uci(ch.SQUARE_NAMES[current_square] + ch.SQUARE_NAMES[to_square] + "q")
            promoting = True
        else: 
            move = ch.Move.from_uci(ch.SQUARE_NAMES[current_square] + ch.SQUARE_NAMES[to_square])
            promoting = False
        #check if a pawn is doing en passant (by checking if the previous enemy move was a two square pawn advancement)
        is_en_passant = check_enpassant(previous_move, selected_piece, move_dict["current_square"], move_dict["to_square"])
        if game.board.is_legal(move):
            en_passant_capture = previous_move['previous_piece']
            previous_move = {"previous_piece":selected_piece, "from_square":move_dict["current_square"], "to_square":move_dict["to_square"]}
        if not game.board.is_legal(move):
            return "move was not played"  
        elif game.board.piece_at(to_square) is not None and game.board.piece_at(to_square).color == game.board.turn:
            return "cannot capture own piece"
        elif (game.board.piece_at(to_square) is not None and game.board.piece_at(to_square).color != game.board.turn) or is_en_passant:
            #this checks if there is an enemy piece on the to_square and if we can capture it. 
            game.board.push(move)
            #get current state of game (if there is a checkmate or draw)
            outcome = game.board.outcome()
            if outcome is not None:
                #checkmate or draw occured, turn off game return the outcome
                chess_game_running = False
                game_outcome = get_outcome()
                return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': True, 'chess_game_running': chess_game_running, 'outcome': game_outcome, 'castle': castle_check, "en_passant": False})
            #check if engine is playing
            if with_engine:
                if user_color == "black":
                    best_move = playEngineMove(int(depth), ch.WHITE)        
                else:
                    best_move = playEngineMove(int(depth), ch.BLACK)
                game.board.push(best_move)
                best_move_str = best_move.uci()
                #push engine move
                return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': True, 'chess_game_running': chess_game_running, 'outcome': "game_running", 'comp_move': best_move_str, 'castle': castle_check, 'promoting':promoting})    
            if is_en_passant:
                return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': True, 'chess_game_running': chess_game_running, 'castle': castle_check, 'en_passant': True, "capturing":en_passant_capture})
            #return the move that was played to javascript
            return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': True, 'chess_game_running': chess_game_running, 'outcome': "game_running", 'castle': castle_check, 'promoting':promoting, "en_passant": False})
        game.board.push(move)
        #check if game has ended
        outcome = game.board.outcome()
        if outcome is not None:
            chess_game_running = False
            game_outcome = get_outcome()
            return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': chess_game_running, 'chess_game_running': False, 'outcome': game_outcome, 'castle': castle_check, 'promoting':promoting})
        #return the move that was played
        if with_engine:
                if user_color == "black":
                    best_move = playEngineMove(int(depth), ch.WHITE)
                else:
                    best_move = playEngineMove(int(depth), ch.BLACK)
                game.board.push(best_move)
                best_move_str = best_move.uci()
                if selected_piece in ['w-king', 'b-king']:
                    castle_check = check_castle(selected_piece, move_dict["to_square"])
                outcome = game.board.outcome()
                if outcome is not None:
                    #checkmate or draw occured
                    chess_game_running = False
                    game_outcome = get_outcome()
                    return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': True, 'chess_game_running': chess_game_running, 'outcome': game_outcome, 'comp_move': best_move_str, 'castle': castle_check, "en_passant": False})
                if is_en_passant:
                    return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': False, 'chess_game_running': chess_game_running, 'outcome': "game_running", 'comp_move': best_move_str, 'castle': castle_check, 'promoting':promoting, 'en_passant': True, "capturing":en_passant_capture})    
                return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': False, 'chess_game_running': chess_game_running, 'outcome': "game_running", 'comp_move': best_move_str, 'castle': castle_check, 'promoting':promoting})    
        #if king move is played, check if king is trying to castle
        if selected_piece in ['w-king', 'b-king']:
            castle_check = check_castle(selected_piece, move_dict["to_square"])
        return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': False, 'chess_game_running': chess_game_running, 'outcome': "game_running", 'castle': castle_check, 'promoting':promoting})
    except:
        return "move was not played"


@app.route("/play_initial_move", methods=["POST"])
def play_initial_move():
  global depth
  best_move = playEngineMove(3, ch.WHITE)
  game.board.push(best_move)
  best_move_str = best_move.uci()
  return jsonify({'comp_move': best_move_str})    
        
def check_enpassant(previous_move_dict, piece, current_square, to_square):
        #get how far the previous pawn moved vertically (to check if it advanced two squares)
        diff = abs(int(previous_move['to_square'][1])-int(previous_move['from_square'][1]))
        #get how far the current pawn moved horizontally (check if it is capturing)
        diff1 = abs(ord(to_square[0])-ord(current_square[0]))
        #if previous pawn moved 2 vertically, 
        #and current pawn moved 1 horizontally, and if both pieces are pawns
        #then an en passant is occuring
        if diff==2 and diff1==1 and previous_move_dict['previous_piece'][2] == 'p' and piece[2]=='p':
            return True
        return False

def check_promote(piece, current_square, to_square):
    #if white pawn reaches 8th rank or if black pawn reaches first rank, then pawn promotes
    ch_current_square = ch.SQUARE_NAMES.index(current_square)
    ch_to_square = ch.SQUARE_NAMES.index(to_square)
    check_move = ch.Move.from_uci(ch.SQUARE_NAMES[ch_current_square] + ch.SQUARE_NAMES[ch_to_square] + "q")
    if piece[:3] == "w-p" and to_square[1] == "8" and game.board.is_legal(check_move):
        return True
    elif piece[:3] == "b-p" and to_square[1] == "1" and game.board.is_legal(check_move):
        return True
    else:
        return False
    
kings_moved=[]
def check_castle(king, to_square):
    global kings_moved
    if king in kings_moved:
        return 0
    if king=='w-king':
        kings_moved.append(king)
    elif king=='b-king':
        kings_moved.append(king)
    if to_square=='g1':   
        return 1 #white short castle
    elif to_square=='c1':
        return 2 #white long castle
    elif to_square=='g8':
        return 3 #black short castle
    elif to_square=='c8':
        return 4 #black long castle
    return 0
    

def get_outcome():
    outcome = game.board.outcome()
    if outcome is not None:
        if outcome.winner is not None:
            if outcome.winner == True:
                return "White wins by " + outcome.termination.name.lower()
            else:
                return "Black wins by " + outcome.termination.name.lower()
        else:
            return "Draw by " + outcome.termination.name.lower()
    else:
        print("Game is still in progress")


#takes a square as a parameter from ajax and returns all legal moves for the piece on that square
@app.route("/get_legal_moves_for_piece", methods=["POST"])
def get_legal_moves_for_piece():
    data = request.get_json()
    square = data["selected_square"]
    legal_squares = legal_moves_for_piece(game.board, square)
    return legal_squares

def legal_moves_for_piece(board, square_name):
    square = ch.parse_square(square_name)
    piece = board.piece_at(square)
    if piece is None:
        return []
    legal_moves = []
    for move in board.legal_moves:
        if move.from_square == square:
            if board.is_capture(move) or board.is_en_passant(move) or board.is_pseudo_legal(move):
                if board.is_legal(move):
                    legal_moves.append(move.to_square)
    return [ch.square_name(square) for square in legal_moves]




#Everything below is tictactoe

@app.route("/tictactoe")
def tictactoe():
    return render_template('tictactoe.html')

#receives ajax request from js, puts gamemode to vs player or vs bot depending on ajax request
@app.route("/botOrPlayer", methods=["POST"])
def botOrPlayer():
    global gameRunning
    global withComputer
    global withFriend
    gameRunning = True
    if request.method == 'POST':
        data = request.get_json()
        if data == "Bot button was clicked":
            withComputer = True
        elif data == "Friend button was clicked":
            withFriend = True
            withComputer = False
        print(data)
        updated_data = {'message': 'X'}
        return jsonify(updated_data)

#receives ajax request with the current board and which box the user clicked.
#depending on gamemode and whose turn, call the proper functions to make
#a move then send the new board via jsonify to javascript file
@app.route("/movePlay", methods=["POST"])
def movePlay():
    global player2turn
    global gameRunning
    if request.method == 'POST':
        data = request.get_json()
        if data == "Reset board":
            clearGrid(grid)
            gameUpdate['x_won'] = False
            gameUpdate['o_won'] = False
            gameUpdate['draw'] = False
            gameRunning = True
            player2turn = False
            if withComputer:
                grid[1] = 'X'
                player2turn = True
                return jsonify(grid, gameUpdate, player2turn)
            return jsonify(grid, gameUpdate, player2turn)
        if gameRunning == False:
            print('game not running')
            return jsonify(grid, gameUpdate, player2turn)
        if player2turn == True:
            playMove('O', data)
            player2turn = False
            if withComputer:
                compMove()
                player2turn = True
        elif player2turn == False:
            if withFriend:
                playMove('X', data)
            player2turn = True
        return jsonify(grid, gameUpdate, player2turn)

#initialize tic tac toe board
grid = {1: ' ', 2: ' ', 3: ' ',
         4: ' ', 5: ' ', 6: ' ',
         7: ' ', 8: ' ', 9: ' '}
gameRunning = False
player2 = 'O'
computer = 'X'
player2turn = False

#clear grid to reset game
def clearGrid(grid):
    for key in grid:
        grid[key] = ' '
    
#check if box is empty
def freeSpace(position):
    if grid[position] == ' ':
        return True
    else:
        return False


def playMove(letter, position):
    global gameRunning
    if freeSpace(position) == True:
        grid[position] = letter
        if CheckWin(): #after every move, check if anyone won
            if letter == "X":
                print("X wins!")
                gameRunning = False
                gameUpdate['x_won'] = True
            else:
                print('O wins!')
                gameRunning = False
                gameUpdate['o_won'] = True
        if checkDraw(): #after every move, check for draw
            print("Draw") 
            gameRunning = False
            gameUpdate['draw'] = True
        return
    else:
        playMove(letter, position)
        return

def CheckWin():
    if (grid[1] != ' ' and grid[1] == grid[2] and grid[1] == grid[3]):
        return True
    elif (grid[4] != ' ' and grid[4] == grid[5] and grid[4] == grid[6]):
        return True
    elif (grid[7] != ' ' and grid[7] == grid[8] and grid[7] == grid[9]):
        return True
    elif (grid[1] != ' ' and grid[1] == grid[4] and grid[1] == grid[7]):
        return True
    elif (grid[2] != ' ' and grid[2] == grid[5] and grid[2] == grid[8]):
        return True
    elif (grid[3] != ' ' and grid[3] == grid[6] and grid[3] == grid[9]):
        return True
    elif (grid[1] != ' ' and grid[1] == grid[5] and grid[1] == grid[9]):
        return True
    elif (grid[7] != ' ' and grid[7] == grid[5] and grid[7] == grid[3]):
        return True
    else:
        return False

def checkDraw():
    for key in grid.keys():
        if grid[key] == ' ':
            return False
    return True

def player2Move():
    position = int(input("Enter a position for 'O': "))
    playMove(player2, position)
    return

def compMove():
    best_score = -800
    bestMove = 0
    for key in grid.keys():
        if grid[key] == ' ':
            grid[key] = computer
            score = minimax(grid, False) #call minimax function to find best move
            grid[key] = ' ' #check move, then revert back to original state
            if score > best_score:
                best_score = score
                bestMove = key
    playMove(computer, bestMove)
    return

#minimax function finds best possible move by playing a possible move, checks score, undoes the move then repeat
def minimax(grid, maximize):
    if checkWinner(computer):
        return 1
    elif checkWinner(player2):
        return -1
    elif checkDraw():
        return 0
    if maximize == True:
        best_score = -800
        for key in grid.keys():
            if grid[key] == ' ':
                grid[key] = computer
                score = minimax(grid, False)
                grid[key] = ' '
                if score > best_score:
                    best_score = score
        return best_score
    else: #minimizing
        best_score = 800
        for key in grid.keys():
            if grid[key] == ' ':
                grid[key] = player2
                score = minimax(grid, True)
                grid[key] = ' '
                if score < best_score:
                    best_score = score
        return best_score

def checkWinner(current_move):
    if (grid[1] == current_move and grid[1] == grid[2] and grid[1] == grid[3]):
        return True
    elif (grid[4] == current_move and grid[4] == grid[5] and grid[4] == grid[6]):
        return True
    elif (grid[7] == current_move and grid[7] == grid[8] and grid[7] == grid[9]):
        return True
    elif (grid[1] == current_move and grid[1] == grid[4] and grid[1] == grid[7]):
        return True
    elif (grid[2] == current_move and grid[2] == grid[5] and grid[2] == grid[8]):
        return True
    elif (grid[3] == current_move and grid[3] == grid[6] and grid[3] == grid[9]):
        return True
    elif (grid[1] == current_move and grid[1] == grid[5] and grid[1] == grid[9]):
        return True
    elif (grid[7] == current_move and grid[7] == grid[5] and grid[7] == grid[3]):
        return True
    else:
        return False

gameUpdate = {'x_won': False, 'o_won': False, 'draw': False, 'player2turn': player2turn}

if __name__ == "__main__":
    app.run(debug=True)