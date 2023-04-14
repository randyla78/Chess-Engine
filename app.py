from flask import Flask, redirect, url_for, render_template, request, session, jsonify, request
import chess_engine as ce #python file
import chess as ch
import config


app = Flask(__name__)
app.config.from_object(config)
app.secret_key = app.config['SECRET_KEY']

#flask app starts
@app.route("/")
def home():
    return render_template("index.html")

@app.route('/about')
def about():
    return render_template('about.html')

#CHESS GAME FUNCTIONS (tic tac toe game is below)
#Chess functions (tictactoe below)
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
    chess_game_running = True
    #get game settings from ajax
    settings = request.get_json()
    #settings["color_select"] gives prints white or black
    #settings["difficulty"] gives max depth as an int
    #settings["with_engine"] gives boolean value
    global user_color
    user_color = settings["color_select"]
    global depth
    depth = settings["difficulty"]
    global with_engine
    with_engine = settings["with_engine"]
    #create a new board object
    newBoard = ch.Board()
    global game
    game = Main(newBoard)
    print(game.board)
    
    game.board.reset
    return "works"

#receives from ajax the move the user tries to play
@app.route("/make_move", methods=["POST"])
def make_move():
    #get all variables from game settings
    global user_color
    global depth
    global with_engine
    global chess_game_running
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
        #play move
        move = ch.Move.from_uci(ch.SQUARE_NAMES[current_square] + ch.SQUARE_NAMES[to_square])
        if not game.board.is_legal(move):
            print("move was not played")
            return "move was not played"  
        elif game.board.piece_at(to_square) is not None and game.board.piece_at(to_square).color == game.board.turn:
            print("You cannot capture your own pieces")
            return "Error: You cannot capture your own pieces"
        elif game.board.piece_at(to_square) is not None and game.board.piece_at(to_square).color != game.board.turn:
            #this checks if there is an enemy piece on the to_square and if we can capture it. 
            game.board.push(move)
            print(game.board)
            print('piece captured')
            #get current state of game (if there is a checkmate or draw)
            outcome = game.board.outcome()
            if outcome is not None:
                #checkmate or draw occured, turn off game return the outcome
                chess_game_running = False
                game_outcome = get_outcome()
                return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': True, 'chess_game_running': chess_game_running, 'outcome': game_outcome})
            #here, check if engine is playing
            if with_engine:
                best_move = playEngineMove(int(depth), ch.BLACK)        
                game.board.push(best_move)
                best_move_str = best_move.uci()
                #push engine move
                return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': True, 'chess_game_running': chess_game_running, 'outcome': "game_running", 'comp_move': best_move_str})    
            #return the move that was played to javascript
            return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': True, 'chess_game_running': chess_game_running, 'outcome': "game_running"})
        game.board.push(move)
        #check if game has ended
        outcome = game.board.outcome()
        if outcome is not None:
            print("GAME IS OVER")
            chess_game_running = False
            game_outcome = get_outcome()
            print(game_outcome)
            return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': chess_game_running, 'chess_game_running': False, 'outcome': game_outcome})
        print(game.board)
        #return the move that was played
        if with_engine:
                #push engine move
                print('playing best move...')
                best_move = playEngineMove(int(depth), ch.BLACK)
                print('best move:')
                game.board.push(best_move)
                best_move_str = best_move.uci()
                return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': False, 'chess_game_running': chess_game_running, 'outcome': "game_running", 'comp_move': best_move_str})    
        return jsonify({'selected_piece': selected_piece, 'to_square':move_dict["to_square"], 'capturing_piece': False, 'chess_game_running': chess_game_running, 'outcome': "game_running"})
    except:
        print("move was not played")
        return "move was not played"


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


#def get_legal_moves(square)
@app.route("/get_legal_moves_for_piece", methods=["POST"])
def get_legal_moves_for_piece():
    #get square from ajax
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
#depending on gamemode and whose turn, this calls appropiate functions to make
#a move then sends the new board via jsonify to javascript file
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
    bestScore = -800
    bestMove = 0
    for key in grid.keys():
        if grid[key] == ' ':
            grid[key] = computer
            score = minimax(grid, False) #call minimax function to find best move
            grid[key] = ' ' #check move, then revert back to original state
            if score > bestScore:
                bestScore = score
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
        bestScore = -800
        for key in grid.keys():
            if grid[key] == ' ':
                grid[key] = computer
                score = minimax(grid, False)
                grid[key] = ' '
                if score > bestScore:
                    bestScore = score
        return bestScore
    else: #minimizing
        bestScore = 800
        for key in grid.keys():
            if grid[key] == ' ':
                grid[key] = player2
                score = minimax(grid, True)
                grid[key] = ' '
                if score < bestScore:
                    bestScore = score
        return bestScore

def checkWinner(currentMove):
    if (grid[1] == currentMove and grid[1] == grid[2] and grid[1] == grid[3]):
        return True
    elif (grid[4] == currentMove and grid[4] == grid[5] and grid[4] == grid[6]):
        return True
    elif (grid[7] == currentMove and grid[7] == grid[8] and grid[7] == grid[9]):
        return True
    elif (grid[1] == currentMove and grid[1] == grid[4] and grid[1] == grid[7]):
        return True
    elif (grid[2] == currentMove and grid[2] == grid[5] and grid[2] == grid[8]):
        return True
    elif (grid[3] == currentMove and grid[3] == grid[6] and grid[3] == grid[9]):
        return True
    elif (grid[1] == currentMove and grid[1] == grid[5] and grid[1] == grid[9]):
        return True
    elif (grid[7] == currentMove and grid[7] == grid[5] and grid[7] == grid[3]):
        return True
    else:
        return False

gameUpdate = {'x_won': False, 'o_won': False, 'draw': False, 'player2turn': player2turn}

if __name__ == "__main__":
    app.run(debug=True)