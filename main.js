console.log("%cCaution", "font: bold 35pt sans-serif; color: red;");
console.log("%cEven though we use a temporary username system and there is not much to lose (e.g., account passwords), pasting text here may give scammers or hackers access \
to your Chessvars in-browser settings or worse your session id. Your session id could give them the ability to play your games or send messages as 'you'.",
	"font: 12pt georgia, serif;");

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
	x = x - this.offsetLeft - ripple.offsetWidth / 2;
	y = y - this.offsetTop - ripple.offsetHeight / 2;
	ripple.style.top = y + 'px';
	ripple.style.left = x + 'px';
	ripple.classList.add('animate');
});
document.body.addEventListener("keyup", function(evt) {
	if (evt.keyCode == 27) {
		CVDismissAlert();
	}
});
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
			var playAs  = document.forms[0]['play-as'].value;
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
function CVAcceptGame(gameId) {
	console.log("Accepted game with ID "+gameId);	
}
var onAlertDismiss = function() { console.log("No action taken on alert dismiss. (default)"); };
var socket = new WebSocket("ws://"+location.host+"/socket");
socket.onmessage = function(received) {
	var msg = received.data;
	console.log("Received WS data: "+msg);
	if (msg == "ping") {
		socket.send("echo"); // Warning user: if you change this, the server may think you're not online and kick you off! :-D
	}
	var msgargs = msg.split(":");
	if (msgargs[0] == "newgame") {
		document.getElementById("games-tbody").innerHTML = "<tr></td><td>"+msgargs[1]+"</td><td>"+msgargs[2]+"</td><td>"+msgargs[3]+"min + "+msgargs[4]+"sec</td><td>"+msgargs[5]+"</td><td><button raised material button onclick='CVAcceptGame(\""+msgargs[6]+"\")'>Accept Game</button></td></tr>";
	}
};
