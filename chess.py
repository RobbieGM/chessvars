from bottle import route, request, response, redirect, Bottle, abort, Response
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
		<link rel='stylesheet' type='text/css' href='/main.css'/>
		<style>
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

terms_file = open("terms.txt", "r")
terms_and_conditions = terms_file.read()

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
main_css_file = open("main.css", "r")
main_css = main_css_file.read()
@app.route('/main.css')
def get_main_css():
	return Response(main_css, mimetype='text/css')
ipaddr = "localhost"
try:
	ipaddr = (subprocess.check_output("ipconfig getifaddr en1", shell=True))[:-1]
except:
	print "WiFi unavailable. Running on localhost."
server = WSGIServer((ipaddr, 8080), app, handler_class=WebSocketHandler)
click_allow_timer = Timer(0.25, click_allow)
click_allow_timer.start()
server.serve_forever()
