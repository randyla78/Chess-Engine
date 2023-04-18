//Select gamemode animations
const icon_container = document.querySelector(".icon-container")
const white_select = document.querySelector('.white-select');
const white_select_box = document.querySelector('.piece-label-white');
white_select_box.addEventListener('mouseover', () => {
  white_select.classList.add('fa-bounce');
});
white_select_box.addEventListener('mouseout', () => {
  white_select.classList.remove('fa-bounce');
});

const black_select = document.querySelector('.black-select');
const black_select_box = document.querySelector('.piece-label-black');
black_select_box.addEventListener('mouseover', () => {
  black_select.classList.add('fa-bounce');
});
black_select_box.addEventListener('mouseout', () => {
  black_select.classList.remove('fa-bounce');
});

//Select gamemode form
const form = document.getElementById('chess-settings-form');
const submit_btn = document.getElementById('submit-btn');
const select_box = document.querySelector(".select-box");
const board = document.querySelector(".board");
let with_engine=true;
let difficulty = null;
let color_select = null
  submit_btn.addEventListener('click', (event) => {
    event.preventDefault();
    color_select = form.querySelector('input[name="color-select"]:checked').value;
    difficulty = form.querySelector('#fader').value;
    with_engine = true;
    const settings = { color_select, difficulty, with_engine };
    send_settings(settings);
    //Play the first engine move if user selects black
    if(color_select=="black"){
      play_initial_move();
    }
    select_box.classList.add('hide');
    setTimeout(function() {
      board.classList.add('show');
    }, 300);
    white_turn.classList.add('show');
    icon_container.classList.add("show");
  });

//If user selects no engine
const no_engine_btn = document.getElementById('no-engine-btn');
no_engine_btn.addEventListener('click', (event) => {
    event.preventDefault();
    color_select = "white";
    difficulty = "2";
    with_engine = false;
    const settings = { color_select, difficulty, with_engine };
    send_settings(settings)
    select_box.classList.add('hide');
    setTimeout(function() {
        board.classList.add('show');
    }, 300);
    white_turn.classList.add('show');
    icon_container.classList.add("show");
    });

  function send_settings(settings) {
      var xhr = new XMLHttpRequest();
      xhr.open("POST", "/chess_settings", true);
      xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
      xhr.onreadystatechange = function() {
        if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
          console.log('Settings Sent Successfully')
        }
      };
      xhr.send(JSON.stringify(settings));
    }

  //create variables for each square in the format of (a1, a2, a3... h6, h7, h8)
  for (let row = 1; row <= 8; row++) {
    for (let col = 1; col <= 8; col++) {
      //starting at 96+1 is the ASCII code for the letter 'a', which then loops to 'b', etc
      let boxId = String.fromCharCode(96 + col) + row;
      let boxElement = document.getElementById(boxId);
      window[boxId] = boxElement;
    }
  }

    
const thinking_msg = document.querySelector(".thinking-msg");
const white_turn = document.querySelector(".white-turn");
const black_turn = document.querySelector(".black-turn");
let turn="w";
var temp = null;
  capture_piece = false;
  var piece_to_capture = null;
  current_piece_square = null;
  const pieces = document.querySelectorAll('.pieces');

//ajax function to send the attempted move to flask backend
  function make_move(move_dict) {
    if(parseInt(difficulty)>3){
      black_turn.classList.add('show');
      white_turn.classList.remove('show');
      thinking_msg.classList.add('show');
    }
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/make_move", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function() {
      if(parseInt(difficulty)>3){
        black_turn.classList.remove('show');
        white_turn.classList.add('show');
        thinking_msg.classList.remove('show');
      }
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        // get all data from flask stored in response variable
        var response = JSON.parse(xhr.responseText);
        if (response.selected_piece==="move was not played"){
          return
        }
        
        //first check if either side is castling
        if (response.castle==1){
          move_piece(document.getElementById("w-rook2"), "f1")
        }
        else if (response.castle==2){
          move_piece(document.getElementById("w-rook1"), "d1")
        }
        else if (response.castle==3){
          move_piece(document.getElementById("b-rook2"), "f8")
        }
        else if (response.castle==4){
          move_piece(document.getElementById("b-rook1"), "d8")
        }
        //then check if either side is promoting 
        if (response.promoting==true){
          var pawn = document.getElementById(move_dict.selected_piece);
          if(move_dict.selected_piece.charAt(0) === "b")
          pawn.src = "/static/images/black_queen.png";
          else{
            pawn.src = "/static/images/white_queen.png";
          }
        }

        capture_piece = response.capturing_piece;
        var current_piece = document.getElementById(response.selected_piece);
        move_piece(current_piece, response.to_square);
        //if not with engine, switch who's turn it is
        if (!with_engine && turn==="w"){
          turn = "b"
          black_turn.classList.add('show');
          white_turn.classList.remove('show');
        }
        else if (!with_engine && turn==="b"){
          turn = "w"
          black_turn.classList.remove('show');
          white_turn.classList.add('show');
        }
        //if either side is capturing a piece, check if it is an en passant then remove the captured piece
        if (capture_piece==true){
          if(response.en_passant == true){
            var piece_to_capture = document.getElementById(response.capturing);
          }
          else{
            var piece_to_capture = document.getElementById(temp);
          }
          piece_to_capture.style.opacity = "0";
          piece_to_capture.style.bottom = "calc((100% / 8)*0)";
          piece_to_capture.style.zIndex = `-5`;
          capture_piece = false
        }
        //get the computer's best move from flask
        if(with_engine===true){
          comp_move = response.comp_move;
          comp_from_square = comp_move.substring(0,2);
          comp_to_square = comp_move.slice(-2);
          comp_piece = getPieceOnSquare(comp_from_square);
          //check if piece is already on comp_to_square. If so, capture (erase) it.
          const remove_piece = getPieceOnSquare(comp_to_square);
          if(response.en_passant == true){
            remove_piece = document.getElementById(response.capturing);
          }
          if(remove_piece!=null){
            remove_piece.style.bottom = "calc((100% / 8)*0)";
            remove_piece.style.zIndex = `-5`;
          }
          move_piece(comp_piece, comp_to_square);
      }

              //if game is no longer running
              if (!response.chess_game_running) {
                //display the game outcome
                document.getElementById("game-outcome").innerHTML = response.outcome + "!";
                black_turn.classList.remove('show');
                white_turn.classList.remove('show');
                return
              }
      }
    };
    xhr.send(JSON.stringify(move_dict));
  }


  //to visually move pieces on the board
  function move_piece(piece, position) {
    const [col, row] = position.split('');
    //convert the column/file into a number (e.g. 'a' -> 1, 'b' -> 2, etc.)
    const colNum = col.charCodeAt(0) - 96;
    //set the piece's position using the row and column numbers
    piece.style.left = `calc((100% / 8)*${colNum-1})`;
    piece.style.bottom = `calc((100% / 8)*${row-1})`;
    unhighlight_all();
  }

  function unhighlight_all(){
    var lightSquares = document.querySelectorAll('.light');
    for (var i = 0; i < lightSquares.length; i++) {
        lightSquares[i].style.backgroundColor = 'white';
    }
    var darkSquares = document.querySelectorAll('.dark');
    for (var i = 0; i < darkSquares.length; i++) {
      if(blue_board===true){
        darkSquares[i].style.backgroundColor = '#5485ab';
      }
      else{    
        darkSquares[i].style.backgroundColor = 'gray';
      }
    }
  }

  

  pieces.forEach(piece => {
    piece.addEventListener('click', () => {
      const poop = getPieceOnSquare("e8");
      console.log("piece on e8 is");
      console.log(poop);
      //get the current square of the clicked piece (using the fact that each piece and square is 1/8 of the board)
      const squareWidth = piece.offsetWidth;
      const squareHeight = piece.offsetHeight;
      const x = piece.offsetLeft + (squareWidth / 2);
      const y = piece.offsetTop + (squareHeight / 2);
      const col = Math.floor(x / squareWidth);
      const row = Math.floor(y / squareHeight);
      const letter = String.fromCharCode(97 + col);
      const number = 8 - row;
      const square = letter + number;
      const id = piece.getAttribute("id"); //get the ID of the clicked piece
       get_legal_moves(square);
      //to test if we can capture the piece we just clicked:
      var move_dict = {selected_piece: temp, 
        current_square: current_piece_square, 
        to_square: square};
        make_move(move_dict);
        piece_to_capture = temp;
        temp = piece.getAttribute("id");
        //update the selected piece square
        current_piece_square = square;
    });
  });

//get all legal moves for a specific piece to highlight squares
function get_legal_moves(square) {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/get_legal_moves_for_piece", true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.onreadystatechange = function() {
  if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
    unhighlight_all();
    var square_element = document.getElementById(square);
    square_element.style.backgroundColor = "red";
    //get all legal squares that a specific piece can move to from flask
    var response = JSON.parse(xhr.responseText);
        //loop through each square and highlight it
        for (var i = 0; i < response.legal_moves.length; i++) {
          var square_id = response.legal_moves[i];
          var square_elem = document.getElementById(square_id);
          square_elem.style.backgroundColor = "orange"; 
        }
      }
    };
    const square_dict = {selected_square: square};
    xhr.send(JSON.stringify(square_dict));
  }

var selectedPiece = null;
$(".pieces").on("click", selectPiece);
function selectPiece(event) {
  if (selectedPiece != null) {
  //unselect the previously selected piece
  selectedPiece.classList.remove("selected");
  }
  // select the clicked piece
  selectedPiece = event.target;
  selectedPiece.classList.add("selected");
  }


function getPieceOnSquare(square) {
    const pieces = document.querySelectorAll('.pieces');
    for (let i = 0; i < pieces.length; i++) {
      const piece = pieces[i];
      const styles = getComputedStyle(piece);
      const left = parseFloat(styles.getPropertyValue('left'));
      const bottom = parseFloat(styles.getPropertyValue('bottom'));
      const file = Math.floor(left / 50); // calculate file (column) from left position
      const rank = Math.floor(bottom / 50); // calculate rank (row) from bottom position
      const pieceSquare = String.fromCharCode('a'.charCodeAt(0) + file) + (rank + 1);
      if (pieceSquare === square) {
        return piece;
      }
    }
    //return null if no piece is on square
    return null;
  }


function play_initial_move() {
  var xhr = new XMLHttpRequest();
  xhr.open("POST", "/play_initial_move", true);
  xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
  xhr.onreadystatechange = function() {
  if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
    var response = JSON.parse(xhr.responseText);
    comp_move = response.comp_move;
    comp_from_square = comp_move.substring(0,2);
    comp_to_square = comp_move.slice(-2);
    comp_piece = getPieceOnSquare(comp_from_square);
    move_piece(comp_piece, comp_to_square);
  }
  };
    xhr.send(JSON.stringify({}));
  };

// if a square is clicked, attempt to play that move
$(".dark, .light").on("click", function(event) {
  if (selectedPiece != null) {
    unhighlight_all();
    var move_dict = {selected_piece: selectedPiece.id, 
      current_square: current_piece_square, 
      to_square: event.target.id}
      make_move(move_dict);
    selectedPiece = null;
  }
});

function refresh() {
  location.reload();
}

//when customize btn is clicked, change color of board
const customize_board_btn = document.querySelector('.circle-chess-icon');
let blue_board = false;
customize_board_btn.addEventListener('click', (event) => {
  event.preventDefault();
  if (blue_board === false){
    blue_board = true;
    var dark_squares = document.querySelectorAll('.dark');
    for (var i = 0; i < dark_squares.length; i++) {
      dark_squares[i].style.backgroundColor = '#5485ab';
  }
  }
  else{
    blue_board = false;
    var dark_squares = document.querySelectorAll('.dark');
    for (var i = 0; i < dark_squares.length; i++) {
      dark_squares[i].style.backgroundColor = 'gray';
  }
  }
});
