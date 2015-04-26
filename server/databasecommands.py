import sqlite3
import hashlib
import re
import html

class DataBase:
	rePlainText = re.compile(r'[^a-z0-9]')
	rePlainNumbers = re.compile(r'[^0-9]')
	reAuthor = re.compile(r'[^a-zA-Z0-9. ]')
	reTag = re.compile(r'[^a-zA-Z0-9.!#@$%&*? ]')
	
	def __init__(self,name):
		self.name = name
		self.conn = sqlite3.connect(self.name)
		self.c = self.conn.cursor()
		
	
	def close(self):
		self.conn.close()
		self.conn = None
		self.c = None
	
	
	def isValidPlainText(self,text):
		return text == DataBase.rePlainText.sub('',text)
	
	def isValidPlainNumbers(self,text):
		return text == DataBase.rePlainNumbers.sub('',text)

	def hash(self,text):
		return hashlib.sha256(text.encode()).hexdigest()
		
	def isValidTitle(self,title):
		return type(title) is str and len(title) < 255
	
	def isValidAuthor(self,author):
		return type(author) is str and author == DataBase.reAuthor.sub('',author) and len(author) < 255
		
	def isValidISBN(self,isbn):
		return type(isbn) is str and self.isValidPlainNumbers(isbn) and len(isbn) < 14 and len(isbn) > 8
		
	def isValidTag(self,tag):
		return type(tag) is str and tag == DataBase.reTag.sub('',tag) and len(tag) < 120
		
	def isValidQuote(self,quote):
		return type(quote) is str
	
	def isValidID(self,id):
		return type(id) is int
		
	def isValidPage(self,page):
		return type(page) is int
		
	def isValidUsername(self,un):
		return type(un) is str and self.isValidPlainText(un) and len(un) < 25 and len(un) > 4
		
	def isValidPassword(self,pw):
		return type(pw) is str and self.isValidPlainText(pw) and len(pw) < 100 and len(pw) > 4

	'''SEARCH COMMANDS'''

	###INPUT###
	#self.DB.searchBooks(id=q['id'],title=q['t'],author=q['a'],isbn=q['i'])
	###OUTPUT###
	#{type:#,books:[{id:id#,t:title,a:author,i:isbn}]}
	#return [{'id':row[0],'t':row[1],'a':row[2],'i':row[3]} for row in array_of_books]
	def searchBooks(self,id=None,title=None,author=None,isbn=None):
		results = self.getAllBooks()
		try:
			if id is not None:
				results = [r for r in results if r[0] == id]
			if title is not None:
				results = [r for r in results if title.lower() in r[1].lower()]
			if author is not None:
				results = [r for r in results if author.lower() in r[2].lower()]
			if isbn is not None:
				results = [r for r in results if r[3] == isbn]
			return results
		except Exception as e: #only triggered if given query terms are not of required form e.g. tags is a number then len(tags) excepts
			print('error with search query %s'%e)
			return []
	
	
	###INPUT###
	#self.DB.searchQuotes(id=q['id'],txt=q['txt'],username=q['un'],date=q['d'],book_id=q['bid'],author=q['a'],isbn=q['i'],tags=q['tags'].split(','))
	###OUTPUT###
	#{type:#,quotes:[{id:quoteid#,txt:quotetext, b:{id:bookid#,t:title,a:author,i:isbn},p:page#,un:usersubmitter,d:datestring,tags:[tag1,tag2,...]}]}
	#return [{'id':row[0],'txt':row[1],'b':row[2],'p':row[3],'un':row[4],'d':row[5],'tags':row[6]} for row in array_of_quotes]
	def searchQuotes(self,id=None,txt=None,username=None,datebefore=None,dateafter=None,book_id=None,title=None,author=None,isbn=None,page=None,tags=None):	
		results = [(q[0],q[1],self.formatBook(int(q[2])),q[3],q[4],q[5],[t[1] for t in self.getAllTagsForQuote(q[0])]) for q in self.getAllQuotes()]
		try:
			if id is not None:
				results = [r for r in results if r[0] == id]
			if txt is not None:
				results = [r for r in results if txt.lower() in r[1].lower()]
			if username is not None:
				results = [r for r in results if r[4] == username]
			if datebefore is not None:
				results = [r for r in results if r[5][:10] >= datebefore]
			if dateafter is not None:
				results = [r for r in results if r[5][:10] <= dateafter]
			if book_id is not None:
				results = [r for r in results if int(r[2]['id']) == int(book_id)]
			if title is not None:
				results = [r for r in results if title.lower() in r[2]['t'].lower()]
			if author is not None:
				results = [r for r in results if author.lower() in r[2]['a'].lower()]
			if isbn is not None:
				results = [r for r in results if r[2]['i'] == isbn]
			if page is not None:
				results = [r for r in results if int(r[3]) == int(page)]
			if tags is not None:
				results = [r for r in results if not False in [t in r[6] for t in tags]]
			return results
		except Exception as e: #only triggered if given query terms are not of required form e.g. tags is a number then len(tags) excepts
			print('error with search query %s'%e)
			return []
		
	def formatBook(self,id):
		row = self.getBook(id)
		return {'id':row[0],'t':row[1],'a':row[2],'i':row[3]}
	
	'''BOOKS'''
	
	#Title: as on book
	#Author: as on book
	#isbn: as txt no hyphans
	def addBook(self,title,author,isbn):
		try:
			if not (self.isValidTitle(title) and self.isValidAuthor(author) and self.isValidISBN(isbn)):
				return False
			self.c.execute('INSERT INTO books VALUES (?,?,?,?)',(None,title,author,isbn))
			self.conn.commit()
			return True
		except sqlite3.IntegrityError:
			return False
			
			#
			#
			#
			#
			#
			#
		#CHECK FOR EXCEPTIONS!!!
		#
		#
		#
		#
		#
	def editBook(self,bid,title=None,author=None,isbn=None):
		if ((title != None and not self.isValidTitle(title)) or \
		(author != None and not self.isValidAuthor(author)) or\
		(isbn != None and self.isValidISBN(isbn))):
			return False
		self.c.execute('SELECT title,author,isbn FROM books WHERE id=?',(bid,))
		b = self.c.fetchone()
		if title is None:
			title = b[0]
		if author is None:
			author = b[1]
		if isbn is None:
			isbn = b[2]
		self.c.execute('UPDATE books SET title=?,author=?,isbn=? WHERE id=?',(title,author,isbn,bid))
		self.conn.commit()
		return True
		
	def removeBook(self,bid):
		self.c.execute('DELETE FROM books WHERE bid=?',(bid,))
		self.c.conn.commit()
	
	def getBook(self,id):
		self.c.execute('SELECT * FROM books WHERE id=?',(id,))
		return self.c.fetchone()
	
	#returns a list of book ideas matching search criterion
	def getBookId(self,title = None,author = None,isbn = None):
		matches = None
		if title != None:
			title_matches = set([row[0] for row in self.c.execute('SELECT * FROM books WHERE title=(?)',(title,))])
			if matches is None:
				matches = title_matches
			else:
				matches = matches.intersection(title_matches)
		if author != None:
			author_matches = set([row[0] for row in self.c.execute('SELECT * FROM books WHERE author=(?)',(author,))])
			if matches is None:
				matches = author_matches
			else:
				matches = matches.intersection(author_matches)
		if isbn != None:
			isbn_matches = set([row[0] for row in self.c.execute('SELECT * FROM books WHERE isbn=(?)',(isbn,))])
			if matches is None:
				matches = isbn_matches
			else:
				matches = matches.intersection(isbn_matches)
		return list(matches)
	
	def getBookSearchByTitle(self,partial_title):
		return [row for row in self.c.execute('SELECT * FROM books WHERE title LIKE (?)',('%'+partial_title+'%',))]
		
	def getBookSearchByAuthor(self,partial_author):
		return [row for row in self.c.execute('SELECT * FROM books WHERE author LIKE (?)',('%'+partial_author+'%',))]
	
	def getAllBooks(self):
		return [row for row in self.c.execute('SELECT * FROM books')]
	
	'''QUOTES'''
	
	
	def getAllQuotes(self):
		return [row for row in self.c.execute('SELECT * FROM quotes')]
	
	#NOT USER INPUT#id: auto generated just add null
	#quote: actual text from the quote
	#book_id: id of the book used, see books table below
	#page: page number of quote
	#user: name of user who submitted quote
	#NOT USER INPUT#date: YYYY-MM-DD HH:MM:SS
	def addQuote(self,quote,book_id,page,user,tags = []):
		if not (\
			self.isValidQuote(quote) and \
			self.isValidID(book_id) and \
			self.isValidPage(page) and \
			self.isValidUsername(user) and \
			[self.isValidTag(t) for t in tags].count(False) is 0 \
			):
			return False
		self.c.execute('SELECT datetime(strftime("%s","now"),"unixepoch","localtime")')
		date = self.c.fetchone()[0]
		self.c.execute('INSERT INTO quotes VALUES (?,?,?,?,?,?)',(None,html.escape(quote),book_id,page,user,date))
		quote_id = self.c.lastrowid
		self.c.executemany('INSERT OR IGNORE INTO Tags VALUES (NULL,?)',[(t,) for t in tags]); #add tags even if already exist
		for t in tags:
			self.c.execute('SELECT id FROM Tags WHERE tag=(?)',(t,)) #have to look up each tag anyways...
			tag_id = self.c.fetchone()[0]
			self.c.execute('INSERT INTO quote_tag VALUES (?,?)',(quote_id,tag_id))
		#remember to commit changes so we don't lock the db!
		self.conn.commit()
		return True
		
	def removeQuote(self,quote_id):
		self.c.execute('DELETE FROM quotes WHERE id=?',(quote_id,))
		self.conn.commit()
		
	def getQuote(self,id):
		return [row for row in self.c.execute('SELECT * FROM quotes WHERE id=(?)',(id,))]
	
	def getAllQuotesForTag(self,tag_id):
		return [row for row in self.c.execute('SELECT quotes.* FROM quotes JOIN quote_tag ON quotes.id = quote_tag.quote_id WHERE quote_tag.tag_id = (?)',(tag_id,))]
	
	def getAllQuotesForBook(self,book_id):
		return [row for row in self.c.execute('SELECT quotes.*,books.* FROM quotes JOIN books ON quotes.book_id = books.id WHERE books.id = (?)',(book_id,))]
	
	'''TAGS'''
	
	def getTagId(self,tag):
		try:
			self.c.execute('SELECT id FROM Tags WHERE tag=(?)',(tag,))
			return self.c.fetchone()[0]
		except:
			return None
	
	def getAllTags(self):
		return [row for row in self.c.execute('SELECT * FROM Tags')]
		
	def getAllTagsForQuote(self,quote_id):
		return [row for row in self.c.execute('SELECT Tags.* FROM Tags JOIN quote_tag ON Tags.id = tag_id WHERE quote_tag.quote_id = (?)',(quote_id,))]
	
	def getTagCloud(self):
		return [row for row in self.c.execute('SELECT Tags.tag, count(*) FROM Tags JOIN quote_tag ON Tags.id = quote_tag.tag_id GROUP BY Tag.tag')]
	
	#NOT USER INPUT#id: unique identifier for tag
	#tag: actual tag, no more than 255 characters
	def addTag(self,tag):
		if self.isValidTag(tag):
			self.c.execute('INSERT OR IGNORE INTO Tags VALUES (?,?)',(None,tag))
			self.conn.commit()
			return True
		else:
			return False
	
	def addTagToQuote(self,quote_id,tag):
		self.addTag(tag)
		tag_id = self.getTagId(tag)
		self.addTagIdToQuote(quote_id,tag_id)
		
	def removeTagFromQuote(self,quote_id,tag_id):
		self.c.execute('DELETE FROM quote_tag WHERE quote_id=? AND tag_id=?',(quote_id,tag_id))
		self.conn.commit()
		
	def addTagIdToQuote(self,quote_id,tag_id):
		self.c.execute("SELECT EXISTS(SELECT 1 FROM quote_tag WHERE quote_id=? AND tag_id=?)",(quote_id,tag_id))
		if self.c.fetchone()[0] == 0:
			self.c.execute('INSERT INTO quote_tag VALUES (?,?)',(quote_id,tag_id))
			self.conn.commit()
			
			
	'''quote_tag'''
	
	
	def getAllQuoteTags(self):
		return [row for row in self.c.execute('SELECT * FROM quote_tag')]
	
	
	'''
	USER COMMANDS
	'''
	
	#requires password in PLAIN TEXT - we have no security till here?
	# -1 means user exists/database error
	# -2 means invalid username/password
	# 1 means worked fine
	def addUser(self,un,pw):
		#check input
		if not (self.isValidUsername(un) and self.isValidPassword(pw)):
			return -2
		else:
			values = (un,self.hash(pw))
			try:
				self.c.execute("INSERT INTO Users VALUES (?,?)",values)
			except sqlite3.IntegrityError as e:
				print('error adding user:\n\t%s' %e)
				return -1
			finally:
				self.conn.commit()
		return 1
	

	#returns true if user exists
	def userExists(self,un):
		return len([row for row in self.c.execute('SELECT * FROM Users WHERE username=?',(un,))])>0
	
	def getUser(self,un):
		self.c.execute("SELECT * FROM Users WHERE username=?",(un,))
		val = self.c.fetchone()
		if val is None:
			return None
		else:
			return (val[0],val[1])
		
	#returns true if given correct pw for un
	#requires pw to be string
	def checkPassword(self,un,pw):
		val = self.getUser(un)
		if val is None:
			return False
		else:
			return val[1] == self.hash(pw)
	
	def removeUser(self,un):
		self.c.execute("DELETE FROM Users WHERE username=?",(un,))
		self.conn.commit()
	
	def getAllUsers(self):
		return [row[0] for row in self.c.execute('SELECT * FROM Users')]
	
	def listAllUsers(self):
		return [row for row in self.c.execute('SELECT * FROM Users')]
	'''
	
	GENERAL TABLE COMMANDS
	
	'''
	
	
	#returns true if table exists
	def tableExists(self,table_name):
		self.c.execute('SELECT count(*) FROM sqlite_master WHERE type="table" AND name=?;',(table_name,))
		return not self.c.fetchone()[0] is 0
	
	
	#builds table if doesn't already exist
	#-a little sketchy
	def createTable(self,table_data):
		if self.tableExists(table_data):
			return False
		else:
			self.c.execute('CREATE TABLE %s;' % table_data)
			self.conn.commit()
			return True

	
	#drops table
	#-a little sketchy
	def dropTable(self,table_name):
		if self.tableExists(table_name):
			self.c.execute('DROP TABLE %s' % table_name)
			self.conn.commit()
			return True
		else:
			return False