document.getElementById("bot-button-id").addEventListener("click", function() {
    sendGameMode("Bot button was clicked");
});

document.getElementById("friend-button-id").addEventListener("click", function() {
    sendGameMode("Friend button was clicked");
});

//sends which gamemode was clicked using ajax to flask app
function sendGameMode(data) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/botOrPlayer", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function() {
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        console.log('Sent')
      }
    };
    xhr.send(JSON.stringify(data));
    playMove("Reset board");
    var player1turn_div = document.getElementById("player1turn");
        player1turn_div.classList.remove('hide');
  }

  //reset board when button is clicked
  document.getElementById("reset").addEventListener("click", function() {
    playMove("Reset board");
});

  //when user clicks on a square to move
  document.getElementById("box1").addEventListener("click", function() {
    playMove(1);
});
document.getElementById("box2").addEventListener("click", function() {
    playMove(2);
});
document.getElementById("box3").addEventListener("click", function() {
    playMove(3);
});
document.getElementById("box4").addEventListener("click", function() {
    playMove(4);
});
document.getElementById("box5").addEventListener("click", function() {
    playMove(5);
});
document.getElementById("box6").addEventListener("click", function() {
    playMove(6);
});
document.getElementById("box7").addEventListener("click", function() {
    playMove(7);
});
document.getElementById("box8").addEventListener("click", function() {
    playMove(8);
});
document.getElementById("box9").addEventListener("click", function() {
    playMove(9);
});

//sends which box was clicked to flask app via an ajax request 
function playMove(move) {
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/movePlay", true);
    xhr.setRequestHeader("Content-Type", "application/json;charset=UTF-8");
    xhr.onreadystatechange = function() {
      if (this.readyState === XMLHttpRequest.DONE && this.status === 200) {
        var pencil_sound = document.getElementById("pencil-sound");
        var click_sound = document.getElementById("click-sound");
        //gets the boolean value from flask
        var player2turn = JSON.parse(xhr.responseText)[2];
        //Display whos turn it is
        var player2turn_div = document.getElementById("player2turn");
        var player1turn_div = document.getElementById("player1turn");
      if (player2turn){
        player2turn_div.classList.remove('hide');
        player1turn_div.classList.add('hide');
      }
      else{
        player1turn_div.classList.remove('hide');
        player2turn_div.classList.add('hide');
      }

        //display if anyone won, or if there is a draw
        //if x wins:
        var x_won = JSON.parse(xhr.responseText)['1'].x_won;
        var x_won_div = document.getElementById("x-won")
        //if o wins:
        var o_won = JSON.parse(xhr.responseText)['1'].o_won;
        var o_won_div = document.getElementById("o-won")
        //if draw:
        var draw = JSON.parse(xhr.responseText)['1'].draw;
        var draw_div = document.getElementById("draw")
        if (x_won) {
            x_won_div.classList.remove('hide');
            player2turn_div.classList.add('hide');
            click_sound.play();
        } 
        else if (o_won) {
            o_won_div.classList.remove('hide');
            player1turn_div.classList.add('hide');
            click_sound.play();
        }
        else if (draw) {
            draw_div.classList.remove('hide');
            player1turn_div.classList.add('hide');
            player2turn_div.classList.add('hide');
            click_sound.play();
        }
        else{
            x_won_div.classList.add('hide');
            o_won_div.classList.add('hide');
            draw_div.classList.add('hide');
            pencil_sound.play();
        }

        //update the page with the updated move
        var result = document.getElementById("1");
        var result2 = document.getElementById("2");
        var result3 = document.getElementById("3");
        var result4 = document.getElementById("4");
        var result5 = document.getElementById("5");
        var result6 = document.getElementById("6");
        var result7 = document.getElementById("7");
        var result8 = document.getElementById("8");
        var result9 = document.getElementById("9");
        result.innerHTML = JSON.parse(xhr.responseText)['0']['1'];
        result2.innerHTML = JSON.parse(xhr.responseText)['0']['2'];
        result3.innerHTML = JSON.parse(xhr.responseText)['0']['3'];
        result4.innerHTML = JSON.parse(xhr.responseText)['0']['4'];
        result5.innerHTML = JSON.parse(xhr.responseText)['0']['5'];
        result6.innerHTML = JSON.parse(xhr.responseText)['0']['6'];
        result7.innerHTML = JSON.parse(xhr.responseText)['0']['7'];
        result8.innerHTML = JSON.parse(xhr.responseText)['0']['8'];
        result9.innerHTML = JSON.parse(xhr.responseText)['0']['9'];
      }
    };
    xhr.send(JSON.stringify(move));
  }

const customize_button = document.querySelector(".customize-icon");
grid_boxes = document.querySelectorAll(".grid span")
let current_style = 1
customize_button.onclick = () => {
    if (current_style == 1){
    grid_boxes.forEach((grid_box) => {
        
      grid_box.classList.add("font2");
      
      console.log(current_style);
    });  
    current_style++;
    }
    
    else if (current_style == 2){
        grid_boxes.forEach((grid_box) => {
            grid_box.classList.remove("font2");
            grid_box.classList.add("shadow2");
          });
    document.body.style.background = "radial-gradient(#80FFDB, #5390D9)";
    current_style++;
    }
    else if (current_style == 3){
        grid_boxes.forEach((grid_box) => {
            grid_box.classList.add("font2");
          });
    current_style++;
  }
    else{
        grid_boxes.forEach((grid_box) => {
            grid_box.classList.remove("font2");
            grid_box.classList.remove("shadow2");
          });
          document.body.style.background = "radial-gradient(#f1ca91,#e8a948)";
          current_style = 1;
    }
};

//variable initializers
bot_button = document.querySelector(".bot-button");
friend_button = document.querySelector(".friend-button");
const box = document.querySelector(".box");
game = document.querySelector(".game")
icon_container = document.querySelector(".icon-container")
//when gamemode is chosen, hide the gamemode selector and show the game board and icons
window.onload = ()=>{
    bot_button.onclick = ()=>{
        box.classList.add("hide");
        game.classList.add("moveposition");
        setTimeout(function() {
            game.classList.add("show");
            icon_container.classList.add("show");
        }, 350);
        
    }
    friend_button.onclick = ()=>{
        box.classList.add("hide");
        game.classList.add("moveposition");
        setTimeout(function() {
            game.classList.add("show");
            icon_container.classList.add("show");
        }, 350);
    }
}
