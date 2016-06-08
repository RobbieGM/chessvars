#!/usr/bin/python

# TODO (3):
# ACTUALLY GET TO PLAY CHESS!
# Fix browser bugs
# Game conclusion

DEBUG = False
NORMAL = 0
CHECK = 1
CHECKMATE = 2
STALEMATE = 3
from sys import argv
from time import sleep
import Chessnut
from bottle import request, response, redirect, Bottle, abort, static_file, debug
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
	<html lang="en">
	<head>
		<link rel="stylesheet" type="text/css" href="/main.css"/>
		<title>Chessvars</title>
		<script src="/main.js"></script>
		<link rel="shortcut icon" type="image/x-icon" href="/favicon.ico?v=2"/>
		<link rel="icon" type="image/x-icon" href="/favicon.ico?v=2"/>
		<meta charset="utf-8"/>
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
game_page_file = open("game.html", "r")
game_page = game_page_file.read()
terms_file = open("terms.txt", "r")
terms_and_conditions = terms_file.read()
LEGAL_VARIANT_LIST = ['normal', 'atomic', 'race-kings', 'fischer-random', 'crazyhouse', 'suicide', 'sniper', 'koth', 'three-check', 'cheshire-cat', 'annihilation', 'gryphon', 'cornerless', 'mutation', 'bomb']
class Admin:
	def __init__(self, uname, pswd):
		self.uname = uname
		self.pswd = pswd
admins = [Admin("RobbieM", "utf8"), Admin("KatieM", "Percy2014"), Admin("ParkerS", "capjacksparrow45"), Admin("JosephW", "Arman@2003")] # user-pass admin list
admin_usernames = ["RobbieM"] # quick-scan list of admin usernames
logged_in_users = {} # logged in users list, these represent username/session-token pairs. These are deleted when a ping request is not met with an echo.
game_offers = []
games = {}
def session_exists(token):
	if not token:
		return False
	return token in logged_in_users
def username_required(func):
	def wrapper(**args):
		if session_exists(request.get_cookie("session_token")):
			return func(**args)
		else:
			redirect("/choose_username")
	return wrapper
def token_has_socket(session_token, socket):
	for i in range(len(logged_in_users[session_token].sockets)):
		if logged_in_users[session_token].sockets[i] is socket:
			return True
	return False
class GameOffer:
	def __init__(self, offered_by, variant, minutes, delay, play_as, game_id, offered_by_session):
		self.offered_by = offered_by
		self.variant = variant
		self.minutes = minutes
		self.delay = delay
		self.play_as = play_as
		self.game_id = game_id
		self.offered_by_session = offered_by_session
class Game:
	def __init__(self, white_player, black_player, variant, minutes, delay, game_id):
		self.white_player = white_player
		self.black_player = black_player
		self.variant = variant
		self.minutes = minutes
		self.delay = delay
		self.game_id = game_id
		self.cn_game = Chessnut.Game()
		self.msgs = []
		self.moves = []
	def terminate(self):
		if self.game_id in games:
			winner = 'draw'
			white_token = get_token_by_username(self.white_player)
			black_token = get_token_by_username(self.black_player)
			'''if logged_in_users[white_token]:
				broadcast_to('gameconclusion:')
			else:
				pass # No white player?
			if logged_in_users[black_token]:
				logged_in_users[black_token]
			else:
				pass # No black player?'''
			del games[self.game_id]
		else:
			print 'Game.terminate(): property `game_id` (equal to ', self.game_id, ') was not found in the games dict.'
class LoggedInUser:
	def __init__(self, username, session_token):
		self.username = username
		self.sockets = []
		self.session_token = session_token # for quick reference by logged_in_users[self.session_token]
		self.game_id = None
	def logout(self, force=True):
		if force or len(self.sockets) == 0:
			if self.game_id in games:
				games[self.game_id].terminate()
			print 'User logged out.'
			for i in xrange(len(game_offers)-1, -1, -1):
				if game_offers[i].offered_by == self.username:
					del game_offers[i]
			try:
				del logged_in_users[self.session_token]
			except:
				pass # user already deleted
	def start_logout_timer(self):
		self.logout_timer = Timer(5, self.logout, [False])
		self.logout_timer.daemon = True
		self.logout_timer.start()
	def on_socket_close(self):
		print 'Socket closed.'
		if len(self.sockets) == 0:
			self.start_logout_timer()
	def execute_js(self):
		pass # which socket(s)?
def switch_bw(c):
		if c == "white":
			return "black"
		if c == "black":
			return "white"
		return c
def tablify_game_offers(username):
	rows = ""
	for i in range(len(game_offers)):
		word = "Withdraw" if username == game_offers[i].offered_by else "Accept"
		clr = game_offers[i].play_as if username == game_offers[i].offered_by else switch_bw(game_offers[i].play_as)
		rows += "<tr id='game-id-"+game_offers[i].game_id+"'><td>"+game_offers[i].offered_by+"</td><td>"+game_offers[i].variant+"</td><td>"+game_offers[i].minutes+"min + "+game_offers[i].delay+"sec</td><td>"+clr+"</td><td><button material raised onclick=\"CVAcceptGame('"+game_offers[i].game_id+"')\">"+word+" Game</button></td></tr>"
	return rows
def get_token_by_socket(socket):
	for token in logged_in_users:
		if token_has_socket(token, socket):
			return token
	return None
def broadcast_to(message, recipients, from_token='FROM_SERVER', signify_owned=False):
	if DEBUG:
		print "from_token: "+from_token
		print "message: "+message
		print "recipients: "+recipients
		print "signify_owned: "+str(signify_owned)
	for session_token in logged_in_users:
		if session_token in recipients or recipients == "all":
			for i in range(len(logged_in_users[session_token].sockets)):
				is_owned = from_token == session_token
				extra = None
				if signify_owned:
					extra = ":owned" if is_owned else ":foreign"
				else:
					extra = ""
				logged_in_users[session_token].sockets[i].send(message+extra)
def get_token_by_username(username):
	for token in logged_in_users:
		if logged_in_users[token].username == username:
			return token
	return None
def delete_game(game_id):
	broadcast_to("withdrawgame:"+game_id, "all", "FROM_SERVER")
	for i in xrange(len(game_offers)-1, -1, -1):
		if game_offers[i].game_id == game_id:
			del game_offers[i]
def string_is_int(s):
	return False
def permaban(session_token):
	pass # Well, you sent some suspicious data. A little too suspicious.
ICON_SIZE = str(40)
hamburger_menu = '''
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
'''
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
			'''+str(tablify_game_offers(uname))+'''
			</tbody>
			<tfoot>
			<tr><td colspan="5"><button raised material button onclick="CVCreateGame()">Create a Game...</button></td></tr>
			</tfoot>
			</table>
		</td>
		</tr></tbody></table>
		'''+hamburger_menu)
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
	orig_session_token = request.get_cookie('session_token')
	response.delete_cookie('session_token')
	try:
		current_user = logged_in_users[request.get_cookie('session_token')]
		current_user.logout(current_user, force=True)
	except:
		pass
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
	orig_temp_uname = request.forms.get("username")
	temp_uname = escape(orig_temp_uname)
	admin_pass = request.forms.get("password")
	admin_login_attempt = request.forms.get("is_admin")
	offensive_language = ["666", "69", "a55", "bitch", "balls", "biotch", "bollock", "biatch", "biutch", "boob", "cunt", "dick", "dieck", "damn", "fuck", "hell", "intercourse", "nigger", "nigga", "pussy", "penis", "piss", "shit", "shiat", "shait", "shiut", "sex", "slag", "vagina", "wanker", "faggot", "fagget", "fagg0t"]
	if len(orig_temp_uname) > 20:
		return main_page_wrap('''<h2>Could not choose username</h2><p>The username is you have chosen is too long.
			<strong><em>Having fun with the 'inspect element' feature in your browser? Remember, hacking will get you banned!</em></strong>''')
	if True in [liu.username == temp_uname for liu in logged_in_users.values()]: # another user already has this username
		return main_page_wrap("<h2>Could not choose username</h2><p>A user has already chosen this username. <a href='/choose_username'>Repick</a></p>")
	if temp_uname in admin_usernames and not admin_login_attempt: # user tried admin username but thought it was ok
		return main_page_wrap("<h2>Could not choose username</h2><p>This is an administrator username, which has been reserved. <a href='/choose_username'>Repick</a></p>")
	for obscenity in offensive_language:
		if obscenity in temp_uname.lower():
			return main_page_wrap("<h2>Could not choose username</h2><p>This username is offensive or vulgar. <a href='/choose_username'>Repick</a></p>")
	if re.search("<script>", orig_temp_uname) or re.search("<\w+?>.*?<\/\w+?>", orig_temp_uname):
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
	response.set_cookie("session_token", random_session_token, httponly="on")
	logged_in_users[random_session_token] = LoggedInUser(temp_uname, random_session_token)
	print 'New user: '+temp_uname
	redirect("/")
@app.route('/people')
@username_required
def view_people():
	return main_page_wrap('''
		<h2>People online</h2>
		<h4>Keep in mind that the temporary username system allows usernames to be picked and chosen at each session, so one person you saw earlier may have a different username now.</h4>
		'''+hamburger_menu)
@app.route('/blankpage')
def blank_page():
	return main_page_wrap('''
		<h2>Blank testing page</h2>
		<div style='position: relative; background: #CACACA; width: 500px; height; 350px'>
			<div style='position: absolute; top: 50px; bottom: 100px; right: 70px; left: 50px;'>
				<button material raised>Button</button>
			</div>
		</div>
		''')
@app.route('/socket')
@username_required
def socket():
	socket = request.environ.get('wsgi.websocket')
	if not socket:
		abort(400, "Expected WebSocket request.")
	initial_session_token = request.get_cookie("session_token")
	logged_in_users[initial_session_token].sockets.append(socket)
	if logged_in_users[initial_session_token].game_id in games:
		cn_game = games[logged_in_users[initial_session_token].game_id].cn_game
		def send_fen():
			socket.send("fen:"+cn_game.fen_history[-1:][0]+":newboard") # fen:rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR:newboard
		Timer(0.3, send_fen).start()
	while True:
		try:
			msg = socket.receive()
			new_session_token = get_token_by_socket(socket)
			if new_session_token != initial_session_token:
				print "Session token linked to a socket changed."
			# if msg == None, then connection terminated
			if not msg:
				print 'No message, socket close assumed.'
				for i in xrange(len(logged_in_users[new_session_token].sockets)-1, -1, -1):
					if logged_in_users[new_session_token].sockets[i] is socket:
						del logged_in_users[new_session_token].sockets[i]
				logged_in_users[new_session_token].on_socket_close()
				abort(400, "Connection closed.")
			msg_args = msg.split(":")
			print msg_args
			if msg_args[0] == 'creategame' and msg_args[1] in LEGAL_VARIANT_LIST:
				if logged_in_users[new_session_token].game_id in games:
					socket.send('showmessage:<h3>You are already in a game</h3><p>Please finish the game you are in before you accept another game.</p>')
				else:
					if session_exists(new_session_token):
						game_id = generate_session_token()
						game_offers.append(GameOffer(logged_in_users[new_session_token].username, msg_args[1], msg_args[2], msg_args[3], msg_args[4], game_id, new_session_token))
						broadcast_to("newgame:"+logged_in_users[new_session_token].username+":"+msg_args[1]+":"+msg_args[2]+":"+msg_args[3]+":"+switch_bw(msg_args[4])+":"+game_id, "all", new_session_token, signify_owned=True)
					else:
						print "weird error."
			if msg_args[0] == 'acceptgame': # Remember, acceptgame means withdraw game if game is 'accepted' by creator of that game!
				if logged_in_users[new_session_token].game_id in games:
					socket.send('showmessage:<h3>You are already in a game</h3><p>Please finish the game you are in before you accept another game.</p>')
				else:
					found = False
					for i in xrange(len(game_offers)-1, -1, -1):
						if game_offers[i].game_id == msg_args[1]:
							found = True
							# this is the game you are looking for
							if game_offers[i].offered_by == logged_in_users[new_session_token].username:
								# Withdraw, not accept (that would be weird to accept your own game.)
								delete_game(game_offers[i].game_id)
							else:
								# Accept game
								logged_in_users[new_session_token].game_id = game_offers[i].game_id
								logged_in_users[game_offers[i].offered_by_session].game_id = game_offers[i].game_id
								socket.send('gameready:'+game_offers[i].game_id)
								broadcast_to('gameaccepted:'+game_offers[i].game_id, game_offers[i].offered_by_session)
								offered_by  = game_offers[i].offered_by
								accepted_by = logged_in_users[new_session_token].username
								if game_offers[i].play_as != "white" and game_offers[i].play_as != "black":
									game_offers[i].play_as = choice(["white", "black"]) 
								white_player = offered_by if game_offers[i].play_as == "white" else accepted_by
								black_player = offered_by if game_offers[i].play_as == "black" else accepted_by
								games[game_offers[i].game_id] = Game(white_player, black_player, game_offers[i].variant, game_offers[i].minutes, game_offers[i].delay, game_offers[i].game_id)
								delete_game(game_offers[i].game_id)
					if not found:
						socket.send('showmessage:<h3>Game Unavailable</h3><p>Sorry, this game is no longer available. This could be caused by a slow internet connection or by a bug in our server.</p>')
			if msg_args[0] == 'game':
				if logged_in_users[new_session_token].game_id in games:
					# There's a game here for sure
					game = games[logged_in_users[new_session_token].game_id]
					if msg_args[1] == 'move':
						try:
							if not msg_args[2] in game.cn_game.get_moves():
								raise Chessnut.game.InvalidMove
							if (game.cn_game.state.player == 'w' and logged_in_users[new_session_token].username == game.white_player) or (game.cn_game.state.player == 'b' and logged_in_users[new_session_token].username == game.black_player):
								game.cn_game.apply_move(msg_args[2])
							else:
								raise Chessnut.game.OpponentsTurn
						except Chessnut.game.InvalidMove:
							socket.send('illegalmove')
						except Chessnut.game.OpponentsTurn:
							socket.send('opponentsturn')
						else:
							socket.send("fen:"+cn_game.fen_history[-1:][0]+":newboard")
							if logged_in_users[new_session_token].username == game.white_player:
								broadcast_to('fen:'+cn_game.fen_history[-1:][0]+':newboard', get_token_by_username(game.black_player))
							elif logged_in_users[new_session_token].username == game.black_player:
								broadcast_to('fen:'+cn_game.fen_history[-1:][0]+':newboard', get_token_by_username(game.white_player))
							else:
								pass # Player is in a game but not white or black? Weird. Possibly hacking
					elif msg_args[1] == 'message' and (msg_args[2] or msg_args[3]): # Emojis like ':-)' when split will return ['', '-)']
						msg_content = ':'.join(msg.split(':')[2:])
						msg_content = escape(msg_content) # XSS protection
						msg_sender = logged_in_users[new_session_token].username
						game = games[logged_in_users[new_session_token].game_id]
						game.msgs.append('<article><span style="color: #FFAB00;">['+msg_sender+']</span> '+msg_content+'</article>')
						socket.send('gamemessage:'+msg_sender+':'+msg_content)
						if logged_in_users[new_session_token].username == game.white_player:
							broadcast_to('gamemessage:'+msg_sender+':'+msg_content, get_token_by_username(game.black_player))
						elif logged_in_users[new_session_token].username == game.black_player:
							broadcast_to('gamemessage:'+msg_sender+':'+msg_content, get_token_by_username(game.white_player))
						else:
							pass # Player is in a game but not white or black? Weird. Possibly hacking
					elif msg_args[1] == 'resign':
						game_id = logged_in_users[new_session_token].game_id
						game = games[game_id]
						opponent = 'draw'
						if logged_in_users[new_session_token].username == game.white_player:
							opponent = game.black_player
						elif logged_in_users[new_session_token].username == game.black_player:
							opponent = game.white_player
						else:
							pass # Player is in a game but not white or black? Weird. Possibly hacking
						socket.send('gameconclusion:'+opponent)
						broadcast_to('gameconclusion:'+opponent, get_token_by_username(opponent))
					elif msg_args[1] == 'takeback':
						game_id = logged_in_users[new_session_token].game_id
						game = games[game_id]
						print game.cn_game.fen_history
						if len(game.cn_game.fen_history) > 1:
							game.cn_game.fen_history.pop()
							game.cn_game.set_fen(game.cn_game.fen_history.pop())
							socket.send("fen:"+cn_game.fen_history[-1:][0]+":newboard")
							if logged_in_users[new_session_token].username == game.white_player:
								broadcast_to('fen:'+cn_game.fen_history[-1:][0]+':newboard', get_token_by_username(game.black_player))
							elif logged_in_users[new_session_token].username == game.black_player:
								broadcast_to('fen:'+cn_game.fen_history[-1:][0]+':newboard', get_token_by_username(game.white_player))
							else:
								pass # Player is in a game but not white or black? Weird. Possibly hacking
				else:
					pass # They're sending game moves without a game. Suspicious? Maybe, but possibly just a laggy internet or glitch.
			session_token = request.get_cookie("session_token")
		except WebSocketError as e:
			for i in xrange(len(logged_in_users[new_session_token].sockets)-1, -1, -1):
				if logged_in_users[new_session_token].sockets[i] is socket:
					del logged_in_users[new_session_token].sockets[i]
			logged_in_users[new_session_token].on_socket_close()
			abort(400, "Connection closed.")
@app.route('/g/<game_id>')
@username_required
def game_page_func(game_id):
	try:
		game = games[game_id]
		current_user = logged_in_users[request.get_cookie('session_token')]
		spectating = current_user.game_id != game_id
		if spectating:
			return main_page_wrap('''
				<h2>Game in progress</h2>
				<p>This game is already being played. Spectating functionality is not implemented right now.</p>
				''')
		opponent = 'Error in lines 426-430 in finding opponent username'
		if game.white_player == current_user.username:
			opponent = game.black_player
		if game.black_player == current_user.username:
			opponent = game.white_player
		msgs = ''.join(game.msgs)
		return main_page_wrap(game_page.format(white_player=game.white_player, black_player=game.black_player, username=current_user.username, opponent_username=opponent, variant=game.variant, msgs=msgs, hamburger_menu=hamburger_menu))
	except KeyError:
		return main_page_wrap('''
			<h2>Game unavailable</h2>
			<p>Sorry, this game is no longer available. This could be caused by a slow internet connection or by a bug in our server.</p>
			''')
@app.route('/favicon.ico')
def get_favicon():
	return static_file("cv-favicon.ico", root="/Users/rmoore/code/resources")
@app.route('/main.css')
def get_main_css():
	return static_file("main.css", root="/Users/rmoore/code")
@app.route('/main.js')
def get_main_js():
	return static_file("main.js", root="/Users/rmoore/code")
@app.route('/game.js')
def get_game_js():
	return static_file("game.js", root="/Users/rmoore/code")
@app.route('/resources/<resource>')
def get_resource(resource):
	return static_file(resource, root="/Users/rmoore/code/resources")
@app.error(404)
def error_404(error):
	return main_page_wrap('''
		<h2>Page not found (404)</h2>
		<p>This page was not found (it may have moved). Sorry.</p>
		''')
@app.error(500)
def error_500(error):
	return main_page_wrap('''
		<h2>Internal server error (500)</h2>
		''')
def debug_manually():
	print "-----------------------------------"
	for session_token in logged_in_users:
		print "debug: "+str(logged_in_users[session_token].__dict__)
	d = Timer(5, debug_manually)
	d.daemon = True
	d.start()
if DEBUG:
	debug_manually()
	debug(True)
ipaddr = "localhost"
try:
	ipaddr = (subprocess.check_output("ipconfig getifaddr en1", shell=True))[:-1]
except:
	print "WiFi unavailable. Running on localhost."
port = 8080
if len(argv) > 1 and argv[1]:
	port = int(argv[1])
print 'http://'+ipaddr+':'+str(port)+'/'
server = WSGIServer((ipaddr, port), app, handler_class=WebSocketHandler)
click_allow_timer = Timer(0.25, click_allow)
click_allow_timer.start()
server.serve_forever()
