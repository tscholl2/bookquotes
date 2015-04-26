import tornado.websocket
import tornado.ioloop
import socket #to get IP address
import sys #for user input
import threading #needed to run tornado server and console
import sqlite3 #for database access
import json #to send data back and forth neatly


#exec(open('server.py').read())

exec(open('databasecommands.py').read())
exec(open('protocol.py').read())
exec(open('client.py').read())

SERVER_PORT = 8888;



application = tornado.web.Application([
	(r'/database', ClientHandler,{"arg":'websocket initliazed!'}),
])

def beginTornadoThread():
	tornado.ioloop.IOLoop.instance().start()
	server_thread = threading.Thread(target = beginTornadoThread)

server_thread = threading.Thread(target = beginTornadoThread)

def start():
	try:
		application.listen(SERVER_PORT)
	except socket.error:
		print("Port {0} already open".format(SERVER_PORT))
		return
	#start tornado in a new thread
	server_thread.start()
	print("server listening, ip is---> {0}:{1}".format(socket.gethostbyname(socket.gethostname()),SERVER_PORT))

def exit():
	#stop tornado
	tornado.ioloop.IOLoop.instance().stop()
	server_thread.join()

#FOR CMD CONSOLE (helps if running as python program along not in shell)
if __name__ == "__main__":
	try:
		start()
		input('press enter to shutdown server\n')
	finally:
		exit()