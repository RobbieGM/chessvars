// JavaScript Safari bug to fix! [material] buttons won't press unless held or double-clicked.
console.log("%cCaution", "font: bold 35pt sans-serif; color: red;");
console.log("%cEven though we use a temporary username system and there is not much to lose (e.g., account passwords), pasting text here may give scammers or hackers access \
to your Chessvars in-browser settings or worse your session id. Your session id could give them the ability to play your games or send messages as 'you'.",
	"font: 12pt georgia, serif;");
(function initLocalStorage() {
	var idealLocalStorage = {
		darkSquareColor: "#555555",
		lightSquareColor: "#EEEEEE"
	};
	for (key in idealLocalStorage) {
		if (localStorage[key] === undefined || localStorage[key] === null) {
			localStorage[key] = idealLocalStorage[key];
		}
	}
})();
function activateMaterial() {
	var addMultiListener = function(el, events, callback) {
		var e = events.split(' ');
		Array.prototype.forEach.call(el, function(element, i) {
			Array.prototype.forEach.call(e, function(event, i) {
				element.addEventListener(event, callback, false);
			});
		});
	};
	addMultiListener(document.querySelectorAll('[material]'), 'mousedown touchstart', function(e) {
		var ripple = this.querySelector('.ripple');
		var eventType = e.type;
		if (ripple == null) {
			ripple = document.createElement('span');
			ripple.classList.add('ripple');
			this.insertBefore(ripple, this.firstChild);
			if (!ripple.offsetHeight && !ripple.offsetWidth) {
				var size = Math.max(e.target.offsetWidth, e.target.offsetHeight);
				ripple.style.width = size + 'px';
				ripple.style.height = size + 'px';
			}
		}
		ripple.classList.remove('animate');
		if (eventType == 'mousedown') {
			var x = e.pageX;
			var y = e.pageY;
		} else if (eventType == 'touchstart') {
			var x = e.changedTouches[0].pageX;
			var y = e.changedTouches[0].pageY;
		}
		var cRect = this.getBoundingClientRect();
		x = e.clientX - cRect.left - ripple.offsetWidth / 2;
		y = e.clientY - cRect.top - ripple.offsetHeight / 2;
		ripple.style.top = y + 'px';
		ripple.style.left = x + 'px';
		ripple.classList.add('animate');
	});
}
addEventListener('load', function() {
	try {
	document.getElementById("is_admin").onchange = function() {
		if (this.checked) {
			document.getElementById("password").classList.add("show");
			document.getElementById("choose_username").value = "LOG IN";
		}else{
			document.getElementById("password").classList.remove("show");
			document.getElementById("choose_username").value = "PICK USERNAME";
		}
	};
	}catch(err) {
		// not the login page, but whatever.
	}
	try {
		document.getElementById("option-icon-container").onclick = function() {
			for (var i = this.children.length - 1; i >= 0; i--) {
				if (this.children[i].classList.toString().indexOf("t-icon") !== -1) {
					this.children[i].classList.toggle("open");
				}
			}
			var options = 3;
			for (var i=1;i<=options;i++) {
				document.getElementById("option-"+i).classList.toggle("open");
			}
		};
	}catch(err) {
		// no option-icon-container present
	}
	activateMaterial();
	document.body.addEventListener("keyup", function(evt) {
		if (evt.keyCode == 27) {
			CVDismissAlert();
		}
	});
	// End onload
});
function CVAlert(content, buttons, defaultButton) {
	if (!buttons || buttons.length === 0) { buttons = ["OK"]; defaultButton = "OK";}
	document.getElementById("modal-dialog").className = "active";
	document.getElementById("modal-overlay").className = "active";
	document.getElementById("modal-dialog-content").innerHTML = content;
	var html = "";
	for (var i=0;i<buttons.length;i++) {
		html += "<td "+(defaultButton==buttons[i]?" class='default-button'":"")+">"+buttons[i]+"</td>"
	}
	document.getElementById("modal-dialog-dismiss-row").innerHTML = html;
	var CVAlertButtons = document.getElementById("modal-dialog-dismiss-row").childNodes;
	for (var i=0;i<CVAlertButtons.length;i++) {
		CVAlertButtons[i].onclick = function() {
			CVDismissAlert(this.innerHTML);
		}
	}
	activateMaterial();
}
function CVDismissAlert(result) {
	document.getElementById("modal-dialog").className = "inactive";
	document.getElementById("modal-overlay").className = "inactive";
	var noClear = onAlertDismiss(result);
	if (!noClear) { onAlertDismiss = function(){}; }
}
function CVCreateGame() {
	var text = "\
	<!--div style='width: 100%; text-align: center'-->\
	<form>\
	<h3>Variant</h3>\
	<select id='variant'>\
		<option value='normal'>Standard</option>\
		<option value='atomic'>Atomic</option>\
		<option value='race-kings'>Racing Kings</option>\
		<option value='fischer-random'>Fischer random</option>\
		<option value='crazyhouse'>Crazyhouse</option>\
		<option value='suicide'>Suicide</option>\
		<option value='sniper'>Sniper chess</option>\
		<option value='koth'>King of the Hill</option>\
		<option value='three-check'>Three-check</option>\
		<option value='cheshire-cat'>Cheshire cat</option>\
		<option value='annihilation'>Annihilation</option>\
		<option value='gryphon'>Gryphon chess</option>\
		<option value='cornerless'>Cornerless</option>\
		<option value='mutation'>Mutation</option>\
		<option value='bomb'>Bomb chess</option>\
	</select>\
	<h3>Variant description</h3>\
	<p>Standard chess: normal chess rules.</p>\
	<h3>Time control</h3>\
	<table>\
	<tr><td>Minutes:</td><td><input id='minutes' value='5' type='range' min='1' max='60'/></td><td id='display-minutes'>5min</td></tr>\
	<tr><td>Delay:</td><td><input id='delay' value='8' type='range' min='0' max='30'/></td><td id='display-seconds'>8sec</td></tr>\
	</table>\
	<h3>Play as</h3>\
	<input type='radio' name='play-as' value='random' checked /> Random color<br/>\
	<input type='radio' name='play-as' value='white' /> White<br/>\
	<input type='radio' name='play-as' value='black' /> Black<br/>\
	</form>\
	<!--/div-->";
	CVAlert(text, ["Cancel", "Create Game"], "Create Game");
	onAlertDismiss = function(result) {
		if (result == "Create Game") {
			var variant = document.getElementById("variant").value;
			var minutes = document.getElementById("minutes").value;
			var delay   = document.getElementById("delay").value;
			var playAs  = "random";
			var radioButtons = document.getElementsByName("play-as");
			for (var i=0;i<radioButtons.length; i++) {
				if (radioButtons[i].checked == true) {
					playAs = radioButtons[i].value;
				}
			}
			socket.send("creategame:"+variant+":"+minutes+":"+delay+":"+playAs);
		}
	};
	setTimeout(function() {
		document.getElementById("delay").oninput = function() { document.getElementById("display-seconds").innerHTML = this.value+"sec"; };
		document.getElementById("delay").onchange = function() { document.getElementById("display-seconds").innerHTML = this.value+"sec"; };
		document.getElementById("minutes").oninput = function() { document.getElementById("display-minutes").innerHTML = this.value+"min"; };
		document.getElementById("minutes").onchange = function() { document.getElementById("display-minutes").innerHTML = this.value+"min"; };
	}, 200);
}
var suppressOfflineMessages = false;
setInterval(function() {
	if (!navigator.onLine && !suppressOfflineMessages) {
		CVAlert("<h3>Network Error</h3><p>We are unable to connect to the Chessvars server. Please check your internet connection.</p>")
		onAlertDismiss = function() {
			suppressOfflineMessages = true;
		};
	}
}, 2000);
function CVAcceptGame(gameId) {
	socket.send("acceptgame:"+gameId)
}
var onAlertDismiss = function() { console.log("No action taken on alert dismiss. (default)"); };
var socket = new WebSocket("ws://"+location.host+"/socket");
var socketSend = socket.send;
socket.send = function() {
	socketSend.apply(this, arguments);
};
socket.onmessage = function(received) {
	function switch_bw(c) {
		if (c == "white") return "black";
		if (c == "black") return "white";
		return c;
	}
	var msg = received.data;
	console.log("Received WS data: "+msg);
	var msgargs = msg.split(":");
	if (msgargs[0] == "newgame") {
		var word = (msgargs[7] == "owned") ? "Withdraw" : "Accept";
		var playAs = (msgargs[7] == "owned") ? switch_bw(msgargs[5]) : msgargs[5];
		document.getElementById("games-tbody").innerHTML += "<tr id='game-id-"+msgargs[6]+"'></td><td>"+msgargs[1]+"</td><td>"+msgargs[2]+"</td><td>"+msgargs[3]+"min + "+msgargs[4]+"sec</td><td>"+playAs+"</td><td><button raised material button onclick='CVAcceptGame(\""+msgargs[6]+"\")'>"+word+" Game</button></td></tr>";
		activateMaterial();
	}
	if (msgargs[0] == "withdrawgame") {
		try {
			var elt = document.getElementById("game-id-"+msgargs[1]);
			elt.parentNode.removeChild(elt);
		}catch(err) {}
	}
	if (msgargs[0] == "showmessage") {
		CVAlert(msgargs[1])
	}
	if (msgargs[0] == "gameaccepted" || msgargs[0] == "gameready") {
		location.replace( "/g/"+msgargs[1] );
	}
	if (msgargs[0] == "fen") {
		try {
			CVLoadFen(msgargs[1], msgargs[2])
		}catch(err) {/* Not /g/8Ad2blahdeblah8sC page */}
	}
	if (msgargs[0] == "gamemessage") {
		try {
			var gameMessage = msg.split(':').slice(2, msgargs.length).join(':');
			console.log(gameMessage);
			CVGameMessage(msgargs[1], gameMessage);
		}catch(err) {
			console.log(err);
			console.log('CVGameMessage not defined');
		}
	}
};
