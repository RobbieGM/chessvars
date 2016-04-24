var darkSquareColor = localStorage.darkSquareColor;
var lightSquareColor = localStorage.lightSquareColor;
var animating = true; // for debugging
var CVLoadFen = function() {
	CVAlert("Error in game.js in trying to load the FEN (board model). Try reloading the page.", ["Dismiss"]);
};
var clipX = -5 + 131 * 3;
var clipY = 133 * 0;
var clipWidth = 133;
var clipHeight = 133;
var img = document.createElement('img');
img.src = '/resources/chess-set.png';
addEventListener('load', function() {
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

		for (var rank=0;rank<ranks.length;rank++) {
			for (var file=0;file<ranks[rank].length;file++) {
				if (ranks[rank][file] != '1') {
					c.drawImage(img, clipX, clipY, clipWidth, clipHeight, (file*canvasSize/8)-5, rank*canvasSize/8, 50, 50);
				}
			}
		}
	}
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

		}else{
			c.fillStyle = "black";
			c.textAlign = 'center';
			c.fillText('Loading...', canvasSize/2, canvasSize/2);
		}
		fc++;
		if (animating)
			requestAnimationFrame(animate);
	}
	animate();
});
