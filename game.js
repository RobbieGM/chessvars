var darkSquareColor = localStorage.darkSquareColor;
var lightSquareColor = localStorage.lightSquareColor;
var animating = true; // for debugging
var CVLoadFen = function() {
	CVAlert("Error in game.js in trying to load the FEN (board model). Try reloading the page.", ["Dismiss"]);
};
var pieceToClipXMap = {
	'R': 0,
	'r': 0,
	'N': 1,
	'n': 1,
	'B': 2,
	'b': 2,
	'Q': 3,
	'q': 3,
	'K': 4,
	'k': 4,
	'P': 5,
	'p': 5
}
function getClipXY(piece) {
	return [Math.min(132 * pieceToClipXMap[piece.toLowerCase()], 659), 131 * (piece.toLowerCase() == piece ? 1 : 0)]
}
var clipX = 131 * 0;
var clipY = 133 * 0;
var clipWidth = 133;
var clipHeight = 133;
var img = document.createElement('img');
img.src = '/resources/chess-set.png';
var chessBoard, getClipXY, getSquareByCursorPosition, getPieceByCursorPosition, getAlgebraicSquareBySquare, getSquareByAlgebraicSquare, rotateSquare;
addEventListener('load', function() {
	var whitePlayer 	 = document.getElementById('white-player').innerHTML;
	var blackPlayer 	 = document.getElementById('black-player').innerHTML;
	var username 		 = document.getElementById('username').innerHTML;
	var opponentUsername = document.getElementById('opponent-username').innerHTML;
	var chessBoard = document.getElementById('chess-board');
	chessBoard.width = parseInt(getComputedStyle(chessBoard.parentNode).width) + 2;
	chessBoard.height = chessBoard.width;
	var chessBoardContext = chessBoard.getContext('2d');
	var c = chessBoardContext;
	window.requestAnimationFrame = ( function() {
		return window.requestAnimationFrame ||
		window.webkitRequestAnimationFrame ||
		window.mozRequestAnimationFrame ||
		window.oRequestAnimationFrame ||
		window.msRequestAnimationFrame ||
		function( /* function FrameRequestCallback */ callback, /* DOMElement Element */ element ) {
			window.setTimeout( callback, 1000 / 60 );
		};
	} )();
	var canvasSize = chessBoard.width;
	addEventListener('resize', function() {
		chessBoard.width = parseInt(getComputedStyle(chessBoard.parentNode).width) + 2;
		chessBoard.height = chessBoard.width;
		canvasSize = chessBoard.width;
	});
	var fc = 0;
	var loaded = false;
	var currentRanksArray = []; // No need to keep track of FEN, server will authorize castling/en-passant
	var playerToMove = 'w';
	CVLoadFen = function(fen, lastMove) {
		loaded = true;
		console.log('FEN: '+fen);
		console.log('lastMove: '+lastMove);
		var board = fen.split(' ')[0];
		board = board.replace(/2/g, '11');
		board = board.replace(/3/g, '111');
		board = board.replace(/4/g, '1111');
		board = board.replace(/5/g, '11111');
		board = board.replace(/6/g, '111111');
		board = board.replace(/7/g, '1111111');
		board = board.replace(/8/g, '11111111');
		var ranks = board.split('/');
		currentRanksArray = ranks;
		playerToMove = fen.split(' ')[1];
	};
	function getSquareByCursorPosition(e) {
		var cursorX = e.clientX, cursorY = e.clientY;
		var rect = chessBoard.getBoundingClientRect();
		cursorX -= rect.left;
		cursorY -= rect.top;
		var indexX = Math.floor(cursorX * 8 / canvasSize);
		var indexY = Math.floor(cursorY * 8 / canvasSize);
		return [indexX, indexY];
	}
	function rotateSquare(square) {
		var re = /[abcdefgh]/g;
		var isAlgebraic = re.test(square);
		var sqToReturn;
		if (isAlgebraic) {
			sqToReturn = getSquareByAlgebraicSquare(square);
		}
		sqToReturn =  [7-square[0], 7-square[1]];
		if (isAlgebraic) {
			sqToReturn = getAlgebraicSquareBySquare(sqToReturn);
		}
		return sqToReturn;
	}
	function getAlgebraicSquareBySquare(square) {
		if (square[0] == -1 || square[1] == -1) return null;
		else{
			var letters = 'abcdefgh';
			return letters[square[0]]+(8-square[1]);
		}
	}
	function getSquareByAlgebraicSquare(algebraicSquare) {
		var map = {
			'a': 0,
			'b': 1,
			'c': 2,
			'd': 3,
			'e': 4,
			'f': 5,
			'g': 6,
			'h': 7
		};
		return [map[algebraicSquare[0]], 8-algebraicSquare[1]];
	}
	function getPieceByCursorPosition(e) {
		var square = getSquareByCursorPosition(e);
		var indexX = square[0];
		var indexY = square[1];
		if (indexX == -1 || indexY == -1) {
			return null;
		}else{
			return currentRanksArray[indexY][indexX];
		}
	}
	var playerColor = (whitePlayer == username ? 'w' : 'b');
	var mouseDown = false;
	chessBoard.onmousedown = function() {
		mouseDown = true;
	};
	chessBoard.onmouseup = function() {
		mouseDown = false;
	};
	var mouseX = 1, mouseY = 1;
	var clientPosition = [];
	var rotated = true;
	document.getElementById('rotate-board').onclick = function() {
		rotated = !rotated;
	};
	chessBoard.onmousemove = function(e) {
		var cursorX = e.clientX, cursorY = e.clientY;
		var rect = chessBoard.getBoundingClientRect();
		clientPosition = [cursorX, cursorY];
		cursorX -= rect.left;
		cursorY -= rect.top;
		mouseX = cursorX;
		mouseY = cursorY;
		if (!loaded) return;
		var pieceByCursor = getPieceByCursorPosition(e);
		if (mouseDown && pieceByCursor && (((pieceByCursor == pieceByCursor.toUpperCase() && playerColor == 'w') || (pieceByCursor == pieceByCursor.toLowerCase() && playerColor == 'b')) && isNaN(parseInt(pieceByCursor)) && playerToMove == playerColor)) {
			CVAlert('<h3>Click, don\'t drag</h3>Enter moves by tapping, not dragging.');
			mouseDown = false;
		}
		if (pieceByCursor) {
			if (((pieceByCursor == pieceByCursor.toUpperCase() && playerColor == 'w') || (pieceByCursor == pieceByCursor.toLowerCase() && playerColor == 'b')) && isNaN(parseInt(pieceByCursor)) && playerToMove == playerColor) {
				chessBoard.style.cursor = 'pointer';
			}else{
				chessBoard.style.cursor = 'default';
			}
		}else{
			chessBoard.style.cursor = 'default';
		}
	};
	var fromAlgebraicSquare;
	var fromSquare;
	canvasBlur = function() {
		fromSquare = undefined;
		fromSquare = undefined;
	};
	function visualSquare(square) {
		return (rotated ? rotateSquare(square) : square);
	}
	chessBoard.onclick = function(e) {
		// Time to move the pieces
		var pieceByCursor = getPieceByCursorPosition(e);
		if (playerToMove == playerColor) {
			if ( ((pieceByCursor == pieceByCursor.toUpperCase() && playerColor == 'w') || (pieceByCursor == pieceByCursor.toLowerCase() && playerColor == 'b')) && isNaN(parseInt(pieceByCursor)) ) {
				fromSquare = getSquareByCursorPosition(e);
				fromAlgebraicSquare = getAlgebraicSquareBySquare(fromSquare);
			}else if (fromAlgebraicSquare && fromSquare) {
				var toAlgebraicSquare = getAlgebraicSquareBySquare(getSquareByCursorPosition(e));
				socket.send('game:move:'+fromAlgebraicSquare+toAlgebraicSquare);
				fromAlgebraicSquare = undefined;
				fromSquare = undefined;
			}
		}
	};
	function animate() {
		c.fillStyle = "#AAAAAA";
		c.fillRect(0, 0, canvasSize+1, canvasSize+1);
		for (var x=0;x<=7;x++) {
			for (var y=0;y<=7;y++) {
				var squareColor = (x + y) % 2 ? darkSquareColor : lightSquareColor;
				c.fillStyle = squareColor;
				c.fillRect(x*canvasSize/8, y*canvasSize/8, canvasSize/8, canvasSize/8);
			}
		}
		if (loaded) {
			if (fromAlgebraicSquare) {
				c.globalAlpha = 0.5;
				c.fillStyle = '#FFAB00'; // #FFD740?
				c.fillRect(fromSquare[0]*canvasSize/8, fromSquare[1]*canvasSize/8, canvasSize/8, canvasSize/8);
				c.globalAlpha = 1;
			}
			var sq;
			for (var rank=0;rank<currentRanksArray.length;rank++) {
				for (var file=0;file<currentRanksArray[rank].length;file++) {
					sq = rotateSquare([rank, file]);
					if (rank == 7 && fc % 50 == 0) {
						console.log(sq);
						console.log([rank, file]);
					}
					if (currentRanksArray[sq[0]][sq[1]] != '1') {
						var clipXY = getClipXY(currentRanksArray[sq[0]][sq[1]]);
						c.drawImage(img, clipXY[0], clipXY[1], clipWidth, clipHeight, sq[1]*canvasSize/8, sq[0]*canvasSize/8, canvasSize/8, canvasSize/8);
					}
				}
			}
			if (fromAlgebraicSquare) {
				c.globalAlpha = 0.5;
				var clipXY = getClipXY(currentRanksArray[fromSquare[1]][fromSquare[0]]);
				c.fillStyle = '#FFAB00';
				var square = getSquareByCursorPosition({clientX: clientPosition[0], clientY: clientPosition[1]});
				c.fillRect(square[0]*canvasSize/8, square[1]*canvasSize/8, canvasSize/8, canvasSize/8);
				c.drawImage(img, clipXY[0], clipXY[1], clipWidth, clipHeight, mouseX-canvasSize/16, mouseY-canvasSize/16, canvasSize/8, canvasSize/8);
				c.globalAlpha = 1;
			}
		}else{
			c.fillStyle = 'black';
			c.textAlign = 'center';
			c.textBaseline = 'middle';
			c.font = 'bold 15px montserrat';
			c.fillText('Loading...', canvasSize/2, canvasSize/2);
			c.lineWidth = '10';
			c.beginPath();
			c.arc(canvasSize/2, canvasSize/2, 100, fc/10, fc/10+(1/3) * 2 * Math.PI);
			c.stroke();
		}
		fc++;
		if (animating)
			requestAnimationFrame(animate);
	}
	animate();
});
