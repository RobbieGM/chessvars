from bottle import route, request, response, redirect, Bottle, abort
from gevent_websocket.geventwebsocket import WebSocketError
from gevent_websocket.geventwebsocket.handler import WebSocketHandler
from gevent.pywsgi import WSGIServer
from threading import Timer
app = Bottle()
import os
import subprocess
from cgi import escape
def generate_session_token():
	ALLOWED_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890" # Shouldn't use: /&?%\;"':
	SESSION_TOKEN_LENGTH = 20
	session_token = ""
	for i in range(SESSION_TOKEN_LENGTH):
		session_token += choice(ALLOWED_CHARS)
	return session_token
def click_allow():
	os.system("cliclick c:1000,360")
def main_page_wrap(html, css=''):
	return '''<!DOCTYPE html>
	<html>
	<head>
		<title>Chessvars</title>
		<style>
		@import url(https://fonts.googleapis.com/css?family=Domine:400,700);
		@import url(https://fonts.googleapis.com/css?family=Montserrat:400,700);
		[material] {
			position: relative;
			overflow: hidden;
			text-align: center;
			border: none;
			background: none;
		}
		button[material], [material][button] {
			appearance: none;
			-webkit-appearance: none;
			padding: 8px;
			border-radius: 2px;
			font: bold 12px montserrat;
			height: 36px;
			line-height: 18px;
			box-sizing: border-box;
			margin-right: 8px;
			min-width: 64px;
		}
		[material][accent]:not([disabled]) {
			background: #FFD740;
		}
		[material][disabled] {
			background: rgb(234, 234, 234);
		}
		[material][primary] {
			background: #cecece;
			width: 56px;
			height: 56px;
			-webkit-clip-path: circle(32px at 32px 32px);
			clip-path: circle(32px at 32px 32px);
			line-height: 32px;
			border-radius: 50%;
			font-size: 24px;
		}
		[material][raised] {
			border-radius: 3px;
		}
		[material][raised]:not([disabled]) {
			box-shadow: 0 3px 3px rgba(0, 0, 0, 0.16), 0 3px 3px rgba(0, 0, 0, 0.23);
			transition: .3s all ease-in-out;
		}
		[material][raised]:not([colored]):not([accent]) {
			background: #dcdcdc;
		}
		[material][raised]:not([disabled]):hover,
		[material][raised]:not([disabled]):active {
			box-shadow: 0 14px 14px rgba(0, 0, 0, 0.25), 0 10px 5px rgba(0, 0, 0, 0.22);
			transform: translateY(-2px);
		}
		[material][raised][colored] {
			color: #fff;
			background: #3F51B5;
		}
		[material][secondary] {
			background: #cecece;
			width: 40px;
			height: 40px;
			-webkit-clip-path: circle(40px at 20px 20px);
			clip-path: circle(40px at 20px 20px);
			line-height: 16px;
			border-radius: 50%;
			font-size: 18px;
		}
		[material]:focus {
			outline: none;
		}
		[type="checkbox"]:not(:checked),
		[type="checkbox"]:checked {
			position: absolute;
			padding-left: -9999px;
			outline: none;
		}
		[type="checkbox"]:not(:checked) + label,
		[type="checkbox"]:checked + label {
			position: relative;
			padding-left: 25px;
			cursor: pointer;
		}
		[type="checkbox"]:not(:checked) + label:before,
		[type="checkbox"]:checked + label:before {
			content: '';
			position: absolute;
			left:0; top: 2px;
			width: 15px; height: 15px;
			box-sizing: border-box;
			border: 2px solid silver;
			background: #fafafa;
		}
		[type="checkbox"]:not(:checked) + label:after,
		[type="checkbox"]:checked + label:after {
			content: 'x';
			position: absolute;
			top: 0px; left: 4px;
			font-family: sans-serif;
			font-size: 16px;
			color: #FFD740;
			transition: all 0.3s;
		}
		@-moz-document url-prefix() {
			[type="checkbox"]:not(:checked) + label:after,
			[type="checkbox"]:checked + label:after {
				content: 'x';
				position: absolute;
				top: 0px; left: 4px;
				font-family: sans-serif;
				font-size: 20px;
				color: #FFD740;
				transition: all 0.3s;
			}
			[type="checkbox"]:not(:checked) + label:before,
			[type="checkbox"]:checked + label:before {
				content: '';
				position: absolute;
				left:0; top: 2px;
				width: 17px; height: 17px;
				box-sizing: border-box;
				border: 2px solid silver;
				background: #fafafa;
			}
		}
		[type="checkbox"]:not(:checked) + label:after {
			opacity: 0;
		}
		[type="checkbox"]:checked + label:after {
			opacity: 1;
		}
		/* disabled checkbox */
		[type="checkbox"]:disabled:not(:checked) + label:before,
		[type="checkbox"]:disabled:checked + label:before {
			box-shadow: none;
			border-color: #bbb;
			background-color: #ddd;
		}
		[type="checkbox"]:disabled:checked + label:after {
			color: #999;
		}
		[type="checkbox"]:disabled + label {
			color: #aaa;
		}
		[type="checkbox"]:disabled + label:hover:before, [type="checkbox"]:disabled:focus + label:before {
			border: 1px solid gray !important;
		}
		[type="checkbox"]:not(:disabled) + label:hover:before, [type="checkbox"]:not(:disabled):focus + label:before {
			border: 2px solid #FFD740 !important;
		}
		html, body {
			margin: 0;
			padding: 0;
			font-family: domine;
			background: #FAFAFA;
		}
		h1 {
			background: #3F51B5;
			margin: 0;
			padding: 1em;
			color: white;
			border-bottom: 10px solid #303F9F;
		}
		h1, h2, h3, h4, h5, h6 {
			font-family: montserrat;
		}
		#main {
			margin: 5%;
			font-family: domine;
		}
		a {
			color: #FFAB00;
		}
		[type="text"], [type="password"] {
			padding: 8px;
			outline: none;
			font: 15px montserrat;
			border: 2px solid silver;
			transition-duration: 0.3s;
		}
		[type="text"]:focus, [type="password"]:focus {
			border: 2px solid #FFD740;
		}
		form input {
			margin-top: 5px;
			margin-bottom: 5px;
		}
		#modal-dialog {
			z-index: 1000;
			opacity: 0;
			visibility: hidden;
			transition-duration: 0.3s;
			position: absolute;
			display: block;
			left: 50%;
			top: 50%;
			transform: translate(-50%, -30%);
			-webkit-transform: translate(-50%, -30%);
			-ms-transform: translate(-50%, -30%);
			background: #3F51B5;
			width: 50%;
			height: 50%;
			transition-duration: 0.3s;
			border-radius: 5px 5px 10px 10px;
			box-sizing: border-box;
			padding: 0;
			max-height: 500px;
			overflow: hidden;
			transform-origin: center;
			-webkit-transform-origin: center;
			-ms-transform-origin: center;
		}
		#modal-dialog.active {
			visibility: visible;
			opacity: 1;
			transform: translate(-50%, -50%);
			-webkit-transform: translate(-50%, -50%);
			-ms-transform: translate(-50%, -50%);
		}
		#modal-overlay {
			position: absolute;
			display: block;
			visibility: hidden;
			opacity: 0;
			top: 0;
			left: 0;
			right: 0;
			bottom: 0;
			width:100%;
			height:100%;
			z-index: 999;
			background: rgba(83, 97, 79, 0.35);
			opacity: 0;
			transition-duration: 0.3s;
		}
		#modal-overlay.active {
			visibility: visible;
			opacity: 1;
		}
		#modal-dialog-content {
			width: 100%;
			height: 70%;
			overflow-y: auto;
			margin: 0;
			padding: 10px;
			box-sizing: border-box;
		}
		#modal-dialog-content::-webkit-scrollbar {
			display:none;
		}
		#modal-dialog-dismiss-buttons {
			width: 100%;
			height: 30%;
			max-height: 60px;
			font-weight: bold;
			font-family: Montserrat;
			padding: 0;
			position: absolute;
			bottom: 0;
			border-spacing: 0;
		}
		#modal-dialog-dismiss-row { width: 100%; }
		#modal-dialog-dismiss-row td {
			line-height: 100%;
			text-align: center;
			margin: 0;
			cursor: pointer;
			background: rgba(255, 255, 255, 0.2);
			transition-duration: 0.3s;
		}
		#modal-dialog-dismiss-row td:hover {
			background: rgba(255, 255, 255, 0.3);
		}
		#modal-dialog-wrapper {
			position: relative;
			height: 100%;
			width: 100%;
			padding: 0;
			margin: 0;
		}
		#modal-overlay:active + #modal-dialog {
			animation: anim-grab-attention 0.15s linear;
			-webkit-animation: anim-grab-attention 0.15s linear;
		}
		h1 a {
			text-decoration: none;
			color: white;
		}
		.hidden_password {
			display: block;
			visibility: hidden;
			opacity: 0;
			transition-duration: 0.3s;
			transform: scaleY(0);
			-webkit-transform: scaleY(0);
			transform-origin: 0 0;
			-webkit-transform-origin: 0 0;
			padding-top: 0;
			padding-bottom: 0;
			height: 0;
			margin-top: 0;
			margin-bottom: 0;
		}
		.hidden_password.show {
			height: auto;
			margin-top: 5px;
			margin-bottom: 5px;
			padding-top: 8px;
			padding-bottom: 8px;
			transform: scaleY(1);
			-webkit-transform: scaleY(1);
			visibility: visible;
			opacity: 1;
		}
		'''+css+'''
		</style>
	</head>
	<body>
		<h1><a href="/">Chess<span style="color:#FFD740">vars</span></a></h1>
		<div id="main">
		'''+html+'''
		</div>

		<script>
		function CVAlert(content, buttons) {
			if (!buttons || buttons.length === 0) { buttons = ["OK"]; }
			document.getElementById("modal-dialog").className = "active";
			document.getElementById("modal-overlay").className = "active";
			document.getElementById("modal-dialog-content").innerHTML = content;
			document.getElementById("modal-dialog-dismiss-row").innerHTML = "<td>"+(buttons.join("</td><td>"))+"</td>";
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
		var onAlertDismiss = function() { console.log("No action taken on alert dismiss. (default)"); };
		var socket = new WebSocket("ws://"+location.host+"/socket");
		socket.onmessage = function(data) {
			var msg = data.data;
			if (msg == "ping") {
				socket.send("echo"); // Warning user: if you change this, the server with think you're not online and kick you off! :-D
			}
		};
		</script>

		<div id="modal-overlay" class="inactive"></div>
		<div id="modal-dialog" class="inactive"><div id="modal-dialog-wrapper">
			<div id="modal-dialog-content"></div>
			<table id="modal-dialog-dismiss-buttons"><tbody><tr id="modal-dialog-dismiss-row"><td>OK</td></tr></tbody></table>
		</div>
		</div>
	</body>
	</html>'''
terms_and_conditions = '''<h3>Terms and Conditions (\\"Terms\\")</h3>\\
Last updated: February 22, 2016<br/>\\
Please read these Terms and Conditions (\\"Terms\\", \\"Terms and Conditions\\") carefully before using the chessvars.com website (the \\"Service\\") operated by Chessvars (\\"us\\", \\"we\\", or \\"our\\").<br/>\\
Your access to and use of the Service is conditioned on your acceptance of and compliance with these Terms. These Terms apply to all visitors, users and others who access or use the Service.<br/>\\
By accessing or using the Service you agree to be bound by these Terms. If you disagree with any part of the terms then you may not access the Service.<br/>\\
<h3>Links To Other Web Sites</h3>\\
Our Service may contain links to third-party web sites or services that are not owned or controlled by Chessvars.<br/>\\
Chessvars has no control over, and assumes no responsibility for, the content, privacy policies, or practices of any third party web sites or services. You further acknowledge and agree that Chessvars shall not be responsible or liable, directly or indirectly, for any damage or loss caused or alleged to be caused by or in connection with use of or reliance on any such content, goods or services available on or through any such web sites or services.<br/>\\
We strongly advise you to read the terms and conditions and privacy policies of any third-party web sites or services that you visit.<br/>\\
<h3>Termination</h3>\\
We may terminate or suspend access to our Service immediately, without prior notice or liability, for any reason whatsoever, including without limitation if you breach the Terms.<br/>\\
All provisions of the Terms which by their nature should survive termination shall survive termination, including, without limitation, ownership provisions, warranty disclaimers, indemnity and limitations of liability.<br/>\\
<h3>Governing Law</h3>\\
These Terms shall be governed and construed in accordance with the laws of Michigan, United States, without regard to its conflict of law provisions.<br/>\\
Our failure to enforce any right or provision of these Terms will not be considered a waiver of those rights. If any provision of these Terms is held to be invalid or unenforceable by a court, the remaining provisions of these Terms will remain in effect. These Terms constitute the entire agreement between us regarding our Service, and supersede and replace any prior agreements we might have between us regarding the Service.<br/>\\
<h3>Changes</h3>\\
We reserve the right, at our sole discretion, to modify or replace these Terms at any time. If a revision is material we will try to provide at least 30 days notice prior to any new terms taking effect. What constitutes a material change will be determined at our sole discretion.<br/>\\
By continuing to access or use our Service after those revisions become effective, you agree to be bound by the revised terms. If you do not agree to the new terms, please stop using the Service.<br/>\\
<h3>Contact Us</h3>\\
If you have any questions about these Terms, please contact us.'''

class Admin:
	def __init__(self, uname, pswd):
		self.uname = uname
		self.pswd = pswd
class LoggedInUser:
	def __init__(self, username, session_token, socket):
		self.username = username
		self.session_token = session_token
		self.socket = socket
admins = [Admin("RobbieM", "utf8")] # user-pass admin list
admin_usernames = ["RobbieM"] # quick-scan of admin usernames
logged_in_users = [] # logged in users list
def get_user_by_socket(socket_obj):
	for i in range(len(logged_in_users)):
		if logged_in_users[i].socket is socket_obj:
			return logged_in_users[i]
	return None
def get_user_by_token(session_token):
	for i in range(len(logged_in_uesrs)):
		if logged_in_users[i].session_token == session_token:
			return logged_in_users[i]
@app.route('/')
def index():
	if request.get_cookie("username"):
		print "Cookie exists on /"
		return main_page_wrap('''
			<h2>Welcome, '''+request.get_cookie("username")+'''</h2>
			<p>Don't like your current username? <a href="/choose_username">Repick it</a></p>
			''')
	else:
		redirect("/choose_username")
@app.route('/choose_username')
def choose_uname():
	return main_page_wrap('''<h2>Choose your temporary username to play</h2>
		<form action="/choose_username" method="POST">
			<input type="text" name="username" placeholder="johndoe123"/><br/>

			<input type="password" name="password" id="password" class="hidden_password" placeholder="aDm1n-p@s$w0RD"/>
			<input type="checkbox" name="is_admin" id="is_admin"/><label for="is_admin">Log in as admin</label><br/>

			<input material colored raised button type="submit" id="choose_username" value="PICK USERNAME"
			/><button material raised button type="button" onclick='CVAlert("'''+terms_and_conditions+'''");'>TERMS & CONDITIONS</button>
			<script>
			document.getElementById("is_admin").onchange = function() {
				if (this.checked) {
					document.getElementById("password").classList.add("show");
					document.getElementById("choose_username").value = "LOG IN";
				}else{
					document.getElementById("password").classList.remove("show");
					document.getElementById("choose_username").value = "PICK USERNAME";
				}
			}
			</script>
		</form>''')
@app.route('/choose_username', method="POST")
def save_uname():
	temp_uname = escape(request.forms.get("username"))
	admin_pass = request.forms.get("password")
	admin_login_attempt = request.forms.get("is_admin")
	if temp_uname in logged_in_users: # another user already has this username
		return main_page_wrap("<h2>Could not choose username</h2><p>A user has already been assigned this username. <a href='/choose_username'>Repick</a></p>")
	if temp_uname in admin_usernames and not admin_login_attempt: # user tried admin username but thought it was ok
		return main_page_wrap("<h2>Could not choose username</h2><p>This is an administrator username, which has been reserved. <a href='/choose_username'>Repick</a></p>")
	if admin_login_attempt:
		credentials_correct = False
		for i in range(len(admins)):
			if admins[i].uname == temp_uname and admins[i].pswd == admin_pass:
				credentials_correct = True
				response.set_cookie("admin_session", generate_session_token(), httponly="on")
		if not credentials_correct:
			return main_page_wrap("<h2>Could not log in</h2><p>Administrator login credentials are incorrect.<a href='/choose_username'>Repick</a></p>")
	response.set_cookie("username", temp_uname)
	logged_in_users.append(temp_uname)
	redirect("/")
@app.route('/socket')
def socket():
	socket = request.environ.get('wsgi.websocket')
	if not socket:
		abort(400, "Expected WebSocket request.")
	while True:
		try:
			msg = socket.receive()
			print msg
			if msg == "ping":
				socket.send("echo")
		except Exception as e:
			if str(e) == "Connection is already closed":
				abort(400, "Connection terminated.")
			else:
				print "WebSocketError: "+str(e)
ipaddr = "localhost"
try:
	ipaddr = (subprocess.check_output("ipconfig getifaddr en1", shell=True))[:-1]
except:
	print "WiFi unavailable. Running on localhost."
server = WSGIServer((ipaddr, 8080), app, handler_class=WebSocketHandler)
click_allow_timer = Timer(0.25, click_allow)
click_allow_timer.start()
server.serve_forever()
