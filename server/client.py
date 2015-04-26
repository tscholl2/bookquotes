import tornado.websocket
import threading
import html

exec(open('databasecommands.py').read())
exec(open('various.py').read())
exec(open('protocol.py').read())


class InvalidInputException(Exception):
	pass
class AlreadyLoggedInException(Exception):
	pass
class UsernameAlreadyExistsException(Exception):
	pass
class WrongPasswordException(Exception):
	pass
class NoUsernameFoundException(Exception):
	pass
class ProtocalException(Exception):
	pass
	
class ClientHandler(tornado.websocket.WebSocketHandler):
	CLIENTS = SafeList()
	LOCK = threading.Lock()

	def check_origin(self, origin):
		return True

	def initialize(self,arg):
		self.name = ''
		self.ip = self.request.remote_ip
		self.DB = DataBase('stuff.db')
		self.state = self.state_connected
		print(arg)
		
	def open(self):
		print('new connection from %s' %self.ip)
		self.send(json.dumps("Hello World"))
	
	#should only be called when attempting to log in for first time.
	#so client should NOT have a name and NOT be in the list of clients until
	#that happens here
	def login(self,un,pw):
		try:
			print('attempting to log in as "%s"/"%s" from %s'%(un,pw,self.ip))
			with ClientHandler.LOCK:
				if not self.DB.userExists(un):
					raise NoUsernameFoundException('no such username found "%s":"%s"'%(un,pw))
				if not self.DB.checkPassword(un,pw):
					raise WrongPasswordException('invalid password attempt! "%s":"%s"'%(un,pw))
				if True in [c.name == un for c in ClientHandler.CLIENTS]:
					raise AlreadyLoggedInException('user "%s" is already logged in'%un)
				#actually log in
				self.name = un
				self.state = self.state_logged_in
				self.sendToAll(json.dumps({'type':TYPE_NEW_CLIENT,'un':un}))
				ClientHandler.CLIENTS.append(self)
				self.send(json.dumps({'type':TYPE_LOGGED_IN}))
		#handle exceptions
		except NoUsernameFoundException as e:
			print('Known exception in login process:\n\t%s'%e)
			self.send(json.dumps({'type':TYPE_NO_USERNAME}))
			self.on_close_wrapper()
		except WrongPasswordException as e:
			print('Known exception in login process:\n\t%s'%e)
			self.send(json.dumps({'type':TYPE_INVALID_PASSWORD}))
			self.on_close_wrapper()
		except AlreadyLoggedInException as e:
			print('Known exception in login process:\n\t%s'%e)
			self.send(json.dumps({'type':TYPE_ALREADY_LOGGEDIN}))
			self.on_close_wrapper()
		except Exception as e:
			print('unkown error in login process:\n\t%s'%e)
			self.send(json.dumps({'type':TYPE_ERROR_INPUT}))
			self.on_close_wrapper()
	
	########
	#STATES#
	########
	def state_connected(self,type,data):
		#
		#regular login
		#
		if type is TYPE_LOGIN:
			try:
				un = data['un']
				pw = data['pw']
				#actual login
				self.login(un,pw)
			except KeyError as e:
				self.send(json.dumps({'type':TYPE_ERROR_INPUT}))
				self.on_close_wrapper()
		#
		#new username
		#
		# -1 means user exists/database error
		# -2 means invalid username/password
		# 1 means worked fine
		elif type is TYPE_NEW_USERNAME:
			try:
				un = data['un']
				pw = data['pw']
				response = self.DB.addUser(un,pw)
				if response is -1:
					raise UsernameAlreadyExistsException('username exists in db')
				elif response is -2:
					raise InvalidInputException('username and/or password is invalid: "%s"/"%s"' %(un,pw))
				#actual login
				self.login(un,pw)	
			except KeyError as e:
				print('Bad input, no key name = \n\t"%s"' %e)
				self.send(json.dumps({'type':TYPE_ERROR_INPUT}))
				self.on_close_wrapper()
			except UsernameAlreadyExistsException as e:
				print('Exception:\n\t%s' %e)
				self.send(json.dumps({'type':TYPE_ALREADY_USERNAME}))
				self.on_close_wrapper()
			except InvalidInputException as e:
				print('Exception:\n\t%s' %e)
				self.send(json.dumps({'type':TYPE_ERROR_INPUT}))
				self.on_close_wrapper()
		else:
			print('illeagle protocol type from %s:\n\t:%s' %(self.ip,data))
			self.send(json.dumps({'type':TYPE_ERROR_INPUT}))
			self.on_close_wrapper()
	
	def state_logged_in(self,type,data):
		#
		#chat
		#
		if type is TYPE_MESSAGE:
			if self.name == '':
				print('%s not logged in!' % self.name)
				self.on_close_wrapper()
			else:
				if data['msg'] and data['msg'] != '':
					self.sendToAll(json.dumps({'type':TYPE_MESSAGE,'by':self.name,'msg':html.escape(data['msg'])}))
		#
		#data request
		#
		elif type is TYPE_DATA_QUERY:
			try:
				q = data['q']
				response = self.dataQuery(data['q'])
				self.send(json.dumps({'type':TYPE_DATA_RESPONSE,'r':response}))
			except KeyError as e:
				print('no query given, intolerable behaviour! by "%s":\n\t%s'%(self.un,data))
				self.send(json.dumps({'type':TYPE_ERROR_INPUT}))
				self.on_close_wrapper()
		#
		#book submission request
		#
		elif type is TYPE_SUBMIT_BOOK:
			#{type:#,t:title,a:author,i:isbn} ##ALL must be non-empty and valid!
			#addBook(self,title,author,isbn):
			try:
				t = data['t']
				a = data['a']
				i = data['i']
				if (self.DB.addBook(title=t,author=a,isbn=i)):
					self.send(json.dumps({'type':TYPE_SUBMISSION_RESPONSE,'b':True}))
				else:
					print('invalid book submission check types\n\t:%s'%data)
					self.send(json.dumps({'type':TYPE_SUBMISSION_RESPONSE,'b':False}))
			except KeyError as e:
				print("Couldn't do it: %s" % e)
				self.send(json.dumps({'type':TYPE_SUBMISSION_RESPONSE,'b':False}))
		#
		#quote submission request
		#
		elif type is TYPE_SUBMIT_QUOTE:
			#{type:#,txt:quotetext,bid:bookid#,p:page#,tags:[tag1,tag2,...]}
			#addQuote(self,quote,book_id,page,user,tags = []):
			try:
				txt = data['txt']
				bid = data['bid']
				p = data['p']
				try:
					tags = data['tags']
				except KeyError:
					print('no tags given in quote submission, thats ok though')
					tags = None
				if (self.DB.addQuote(quote=txt,book_id=bid,page=p,user=self.name,tags=tags)):
					self.send(json.dumps({'type':TYPE_SUBMISSION_RESPONSE,'b':True}))
				else:
					print("Couldn't add quote, check types:\n\t%s" %data)
					self.send(json.dumps({'type':TYPE_SUBMISSION_RESPONSE,'b':False}))
			except KeyError as e:
				print("missing submission parameters: %s" % e)
				self.send(json.dumps({'type':TYPE_SUBMISSION_RESPONSE,'b':False}))
			
		
				
				
##############################################




##################################################
				
				
				
				

	#read messages and send to current state
	def on_message(self,message):
		print('message received from "%s":\n\t%s' %(self.name,message))
		try:
			data = json.loads(message)
			type = data['type']
		except KeyError as e:
			print('Error reading input message from "%s"@%s'%(self.name,self.ip))
			self.send(json.dumps({'type':TYPE_ERROR_INPUT}))
			self.on_close_wrappper()
		#send message to current state
		self.state(type,data)
	

	#
	#REQUEST FUNCTIONS
	#

	def dataQuery(self,q):
		response = {};
		#
		#BOOK QUERY
		#
		if q['type'] is QUERY_BOOKS:
			#q = {type:#,id:bookid#,t:title,a:author,i:isbn#}
			try:
				id=q['id']
			except KeyError:
				id=None
			try:
				t=q['t']
			except KeyError:
				t=None
			try:
				a=q['a']
			except KeyError:
				a=None
			try:
				i=q['i']
			except KeyError:
				i=None
			response = {'type':RESPONSE_BOOKS,'books':self.formatBookResponse( \
			self.DB.searchBooks(id=id,title=t,author=a,isbn=i))}
		#
		#QUOTE QUERY
		#
		elif q['type'] is QUERY_QUOTES:
			#q = {type:#,id:id#,un:username,d1:beforethisdate,d2:afterthisdate,bid:bookid#,t:booktitle,a:bookauthor,i:bookisbn,p:page,tags:[tag1,tag2,...]}
			try:
				id = int(q['id'])
			except KeyError:
				id = None
			except TypeError:
				id = None
			try:
				un = q['un']
			except KeyError:
				un = None
			try:
				d1 = q['d1']
			except KeyError:
				d1 = None
			try:
				d2 = q['d2']
			except KeyError:
				d2 = None
			try:
				bid = int(q['bid'])
			except KeyError:
				bid = None
			except TypeError:
				bid = None
			try:
				t = q['t']
			except KeyError:
				t = None
			try:
				a = q['a']
			except KeyError:
				a = None
			try:
				i = q['i']
			except KeyError:
				i = None
			try:
				p = int(q['p'])
			except KeyError:
				p = None
			except TypeError:
				p = None
			try:
				tags = q['tags']
			except KeyError:
				tags = None
			try:
				txt = q['txt']
			except KeyError:
				txt = None
			response = {'type':RESPONSE_QUOTES,'quotes':self.formatQuoteResponse( \
			self.DB.searchQuotes(id=id,txt=txt,username=un,datebefore=d1,dateafter=d2,book_id=bid,title=t,author=a,isbn=i,page=p,tags=tags))}		
		return response
	
	#given array of books straight from the database
	#{type:#,books:[{id:id#,t:title,a:author,i:isbn}]}
	def formatBookResponse(self,array_of_books):
		return [{'id':row[0],'t':row[1],'a':row[2],'i':row[3]} for row in array_of_books]
	
	#given array of quotes straight from database
	#{type:#,quotes:[{id:quoteid#,txt:quotetext,b:{id:bookid#,t:title,a:author,i:isbn},p:page#,un:usersubmitter,d:datestring,tags:[tag1,tag2,...]}]}
	def formatQuoteResponse(self,array_of_quotes):
		return [{'id':row[0],'txt':row[1],'b':row[2],'p':row[3],'un':row[4],'d':row[5],'tags':row[6]} for row in array_of_quotes]
	
	#
	#SENDING FUNCTIONS
	#
	
	def sendToAll(self,msg):
		for c in ClientHandler.CLIENTS:
			try:
				c.send(msg)
			except Exception as e:
				print('"%s" had error sending msg to %s, probably disconnected:\n\t%s' %(self.name,c.name,e))
	
	def send(self,text):
		try:
			self.write_message(str(text))
		except Exception as e:
			print('"%s"@%s: exception while sending msg to self:\n\t%s'%(self.name,self.ip,e))
	
	def on_close(self):
		print('connection to "%s"@%s closed'%(self.name,self.ip))
		if self.name != '':
			ClientHandler.CLIENTS.remove(self)
			self.sendToAll(json.dumps({'type':TYPE_CLIENT_LEFT,'un':self.name}))
			self.name = ''
			self.state = self.state_connected #not necessary
		self.DB.close()
		
	def on_close_wrapper(self):
		self.close()
		self.on_close()