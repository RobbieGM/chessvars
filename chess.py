#!/usr/bin/python
DEBUG = False

from bottle import route, request, response, redirect, Bottle, abort, static_file
from random import choice
import re
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
	os.system("cliclick c:1000,375")
def main_page_wrap(html, css=''):
	return '''<!DOCTYPE html>
	<html>
	<head>
		<link rel="stylesheet" type="text/css" href="/main.css"/>
		<title>Chessvars</title>
		<script src="/main.js"></script>
		<style>
		'''+css+'''
		</style>
	</head>
	<body>
		<h1><a tabindex="-1" href="/" tabindex="-1">Chess<span style="color:#FFD740">vars</span></a></h1>
		<div id="main">
		'''+html+'''
		</div>

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

admins = [Admin("RobbieM", "utf8")] # user-pass admin list
admin_usernames = ["RobbieM"] # quick-scan list of admin usernames
logged_in_users = {} # logged in users list, these represent username/session-token pairs. These are deleted when a ping request is not met with an echo.
game_offers = []
def session_exists(token):
	if not token:
		return False
	return token in logged_in_users
def username_required(func):
	def wrapper():
		if session_exists(request.get_cookie("session_token")):
			return func()
		else:
			redirect("/choose_username")
	return wrapper
def token_has_socket(session_token, socket):
	for i in range(len(logged_in_users[session_token].sockets)):
		if logged_in_users[session_token].sockets[i] is socket:
			return True
	return False
class GameOffer:
	def __init__(self, offered_by, variant, minutes, delay, play_as, game_id):
		self.offered_by = offered_by
		self.variant = variant
		self.minutes = minutes
		self.delay = delay
		self.play_as = play_as
		self.game_id = game_id
class LoggedInUser:
	def __init__(self, username):
		self.username = username
		self.sockets = []

def tablify_game_offers():
	rows = ""
	def switch_bw(c):
		if c == "white":
			return "black"
		if c == "black":
			return "white"
		return c
	for i in range(len(game_offers)):
		rows += "<tr><td>"+game_offers[i].offered_by+"</td><td>"+game_offers[i].variant+"</td><td>"+game_offers[i].minutes+"min + "+game_offers[i].delay+"sec</td><td>"+switch_bw(game_offers[i].play_as)+"</td><td><button material raised>Accept Game</button></td></tr>"
	return rows
def get_token_by_socket(socket):
	for token in logged_in_users:
		if token_has_socket(token, socket):
			return token
	return None
def broadcast_to(message, recipients):
	for session_token in logged_in_users:
		if session_token in recipients or recipients == "all":
			for i in range(len(logged_in_users[session_token].sockets)):
				logged_in_users[session_token].sockets[i].send(message)
def get_token_by_username(username):
	for token in logged_in_users:
		if logged_in_users[token].username == username:
			return token
	return None
ICON_SIZE = str(40)
@app.route('/')
@username_required
def index():
	uname = logged_in_users[request.get_cookie("session_token")].username
	return main_page_wrap('''
		<table class="splitter-table"><tbody><tr>
		<td>
			<h2>Welcome, '''+uname+'''</h2>
			<p>Don't like your current username? <a href="/choose_username">Repick it</a></p>
			
		</td>
		<td>
			<h2>Open Games</h2>
			<table class="cv-table"><thead>
			<th>
			<tr><td>Player</td><td>Variant</td><td>Time Control</td><td>Play as</td><td>Action</td></tr>
			</th></thead>
			<tbody id="games-tbody">
			'''+str(tablify_game_offers())+'''
			</tbody>
			<tfoot>
			<tr><td colspan="5"><button raised material button onclick="CVCreateGame()">Create a Game...</button></td></tr>
			</tfoot>
			</table>
		</td>
		</tr></tbody></table>
		<div material raised id="option-icon-container" class="option">
			<a class="navicon-button x t-icon"><div class="navicon"></div></a>
		</div>
		<a href="/settings"><div material class="option" id="option-1" raised>
			<img src="/resources/ic_settings_black_24px.svg" width="'''+ICON_SIZE+'''px" height="'''+ICON_SIZE+'''px"/>
		</div></a>
		<a href="/people"><div material class="option" id="option-2" raised>
			<img src="/resources/ic_people_black_24px.svg" width="'''+ICON_SIZE+'''px" height="'''+ICON_SIZE+'''px"/>
		</div></a>
		<a href="/choose_username"><div material class="option" id="option-3" raised>
			<img src="/resources/ic_undo_black_24px.svg" width="'''+ICON_SIZE+'''px" height="'''+ICON_SIZE+'''px"/>
		</div></a>
		''')
@app.route('/settings')
def settings():
	return main_page_wrap('''
		<script src="http://yui.yahooapis.com/2.9.0/build/utilities/utilities.js" ></script>
		<script src="http://yui.yahooapis.com/2.9.0/build/slider/slider-min.js" ></script>
		<link rel="stylesheet" type="text/css" href="http://yui.yahooapis.com/2.9.0/build/colorpicker/assets/skins/sam/colorpicker.css" />
		<script src="http://yui.yahooapis.com/2.9.0/build/colorpicker/colorpicker-min.js" ></script>
		<script>
		var picker = new YAHOO.widget.ColorPicker("white-squares", {
			showhsvcontrols: true,
			showhexcontrols: true/*,
			images: {
				PICKER_THUMB: "https://lh3.googleusercontent.com/-7TryPunxCTQ/Vt4J1Xp5uEI/AAAAAAAABek/CIHY4EC6VIM/s506/circle.png",
				HUE_THUMB: "https://lh3.googleusercontent.com/-7TryPunxCTQ/Vt4J1Xp5uEI/AAAAAAAABek/CIHY4EC6VIM/s506/circle.png"
			}*/
		});
		</script>
		<h2>Settings</h2>
		<p>These are in-browser settings and do not apply to your username. If you choose a different username, these settings will still apply.</p>
		<h3>Board</h3>
		<p>Light square color:</p>
		<div id="white-squares" style="position: relative"></div>
		<p>Dark square color:</p>
		<div id="black-squares" style="position: relative"></div>
		<h3>Pieces</h3>
		''')
@app.route('/choose_username')
def choose_uname():
	return main_page_wrap('''<h2>Choose your temporary username to play</h2>
		<form action="/choose_username" method="POST">
			<input type="text" name="username" autofocus required placeholder="johndoe123" maxlength="20"/><br/>

			<input type="password" name="password" id="password" class="hidden_password" placeholder="aDm1n-p@s$w0RD"/>
			<input type="checkbox" name="is_admin" id="is_admin"/><label for="is_admin">Log in as admin</label><br/>

			<button material colored raised button type="submit" id="choose_username">PICK USERNAME</button
			><button material raised button type="button" onclick='CVAlert("'''+terms_and_conditions+'''");'>TERMS & CONDITIONS</button>
		</form>''')
@app.route('/choose_username', method="POST")
def save_uname():
	temp_uname = escape(request.forms.get("username"))
	admin_pass = request.forms.get("password")
	admin_login_attempt = request.forms.get("is_admin")
	offensive_language = ["666", "69", "ass", "bitch", "balls", "biotch", "bollock", "biatch", "biutch", "boob", "cunt", "dick", "dieck", "damn", "fuck", "hell", "intercourse", "nigger", "nigga", "pussy", "penis", "piss", "shit", "shiat", "shait", "shiut", "sex", "slag", "vagina", "wanker"]
	if len(temp_uname) > 20:
		return main_page_wrap('''<h2>Could not choose username</h2><p>The username is you have chosen is too long.
			<strong><em>Having fun with the 'inspect element' feature in your browser? Remember, hacking will get you banned!</em></strong>''')
	if True in [liu.username == temp_uname for liu in logged_in_users.values()]: # another user already has this username
		return main_page_wrap("<h2>Could not choose username</h2><p>A user has already chosen this username. <a href='/choose_username'>Repick</a></p>")
	if temp_uname in admin_usernames and not admin_login_attempt: # user tried admin username but thought it was ok
		return main_page_wrap("<h2>Could not choose username</h2><p>This is an administrator username, which has been reserved. <a href='/choose_username'>Repick</a></p>")
	for obscenity in offensive_language:
		if obscenity in temp_uname.lower():
			return main_page_wrap("<h2>Could not choose username</h2><p>This username is offensive or vulgar. <a href='/choose_username'>Repick</a></p>")
	if re.search("<script>", temp_uname) or re.search("<\w+?>.*?<\/\w+?>", temp_uname):
		return main_page_wrap('''<h2>Could not choose username</h2><p>Username must only contain letters, numbers, dashes, and spaces.
			<strong><em>Testing for Cross-Site Scripting? Remember, hacking will get you banned!</em></strong></p>''')
	try:
		temp_uname.decode('ascii')
		if not re.match("^[a-zA-Z\d\s_\-]+$", temp_uname):
			raise Exception
		if temp_uname.isspace():
			raise Exception
		if not temp_uname:
			raise Exception
	except:
		return main_page_wrap("<h2>Could not choose username</h2><p>Username must contain only letters, numbers, dashes, and spaces.</p>")
	if admin_login_attempt:
		credentials_correct = False
		for i in range(len(admins)):
			if admins[i].uname == temp_uname and admins[i].pswd == admin_pass:
				credentials_correct = True
		if not credentials_correct:
			return main_page_wrap("<h2>Could not log in</h2><p>Administrator login credentials are incorrect.<a href='/choose_username'>Repick</a></p>")
	random_session_token = generate_session_token()
	response.set_cookie("session_token", random_session_token)
	logged_in_users[random_session_token] = LoggedInUser(temp_uname)
	redirect("/")
@app.route('/people')
@username_required
def view_people():
	return main_page_wrap('''
		<h2>People online</h2>
		<h4>Keep in mind that the temporary username system allows usernames to be picked and chosen at each session, so one person you saw earlier may have a different username now.</h4>
		''')
@app.route('/socket')
@username_required
def socket():
	socket = request.environ.get('wsgi.websocket')
	if not socket:
		abort(400, "Expected WebSocket request.")
	initial_session_token = request.get_cookie("session_token")
	'''def ping():
		print "ping request functionality unavailable."
		Timer(30, ping).start()
	ping()'''
	logged_in_users[initial_session_token].sockets.append(socket)
	def ping_socket():
		try:
			socket.send("testsocket")
		except Exception as e:
			num_user_sockets = len(logged_in_users[initial_session_token].sockets)
			for i in xrange(num_user_sockets-1, -1, -1):
				print "found user socket"
				if logged_in_users[initial_session_token].sockets[i] is socket:
					del logged_in_users[initial_session_token].sockets[i]
					print "deleted dead socket(s)"
					if len(logged_in_users[initial_session_token].sockets) == 0:
						print "user closed final socket, deleting user"
						for i in xrange(len(game_offers), -1, -1):
							if game_offers[i].offered_by == logged_in_users[initial_session_token].username:
								print "deleted user game offer (user logged out)"
								del game_offers[i]
						del logged_in_users[initial_session_token]
		else:
			t = Timer(5, ping_socket)
			t.daemon = True
			t.start()
	ping_socket()
	while True:
		try:
			msg = socket.receive()
			# if msg == None, there was no message. If error, the connection was terminated.
			if not msg:
				return
			msg_args = msg.split(":")
			print msg_args
			if msg_args[0] == 'creategame':
				if session_exists(get_token_by_socket(socket)):
					game_id = generate_session_token()
					game_offers.append(GameOffer(logged_in_users[get_token_by_socket(socket)].username, msg_args[1], msg_args[2], msg_args[3], msg_args[4], game_id))
					broadcast_to("newgame:"+logged_in_users[get_token_by_socket(socket)].username+":"+msg_args[1]+":"+msg_args[2]+":"+msg_args[3]+":"+msg_args[4]+":"+game_id, "all")
				else:
					print "weird error."
			session_token = request.get_cookie("session_token")
		except Exception as e:
			print e
			if str(e) == "Connection is already closed":
				for i in range(len(logged_in_users[initial_session_token].sockets)):
					if logged_in_users[initial_session_token].sockets[i] is socket:
						del logged_in_users[initial_session_token].sockets[i]
				abort(400, "Connection terminated.")
			else:
				print "WebSocketError: "+str(e)
@app.route('/main.css')
def get_main_css():
	return static_file("main.css", root="/Users/rmoore/code")
@app.route('/main.js')
def get_main_js():
	return static_file("main.js", root="/Users/rmoore/code")
@app.route('/resources/<resource>')
def get_resource(resource):
	return static_file(resource, root="/Users/rmoore/code/resources")
from pprint import pprint
def debug():
	for session_token in logged_in_users:
		print "debug: "+str(logged_in_users[session_token].__dict__)
	d = Timer(5, debug)
	d.daemon = True
	d.start()
if DEBUG:
	debug()
ipaddr = "localhost"
try:
	ipaddr = (subprocess.check_output("ipconfig getifaddr en1", shell=True))[:-1]
except:
	print "WiFi unavailable. Running on localhost."
server = WSGIServer((ipaddr, 8080), app, handler_class=WebSocketHandler)
click_allow_timer = Timer(0.25, click_allow)
click_allow_timer.start()
server.serve_forever()
