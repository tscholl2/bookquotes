import sqlite3
import hashlib

#execfile('databasecommands.py')
exec(open('databasecommands.py').read())

DB = DataBase('stuff.db')

#
#SET UP INITIAL TABLES
#

#check if user table is inputted
if not DB.tableExists('users'):
	print('no table "users"... making one now...')
	DB.createTable('users (username VARCHAR(25) UNIQUE, password VARCHAR(100))')
	#add default admin
	print('adding default admin user...')
	DB.addUser('admin','admin')
else:
	print('already "users" table')

#QUOTE TABLE
	
if not DB.tableExists('quotes'):
	print('no table "quotes"... making one now...')
	#id: auto generated just add null
	#quote: actual text from the quote
	#book_id: id of the book used, see Books table below
	#page: page number of quote
	#user: name of user who submitted quote
	#date: YYYY-MM-DD HH:MM:SS
	DB.createTable('quotes (id INTEGER PRIMARY KEY AUTOINCREMENT, quote TEXT, book_id INTEGER, page INTEGER, user VARCHAR(25), date TEXT)')
else:
	print('already "quotes" table')

#TAG TABLE	

if not DB.tableExists('tags'):
	print('no table "tags"... making one now...')
	#id: unique identifier for tag
	#tag: actual tag, no more than 120 characters
	DB.createTable('tags (id INTEGER PRIMARY KEY AUTOINCREMENT, tag VARCHAR(120) UNIQUE)')
else:
	print('already "tags" table')

#QUOTE TAG MAP TABLE

if not DB.tableExists('quote_tag'):
	print('no table "quote_tag"... making one now...')
	#quote_id: id corresponding to quote
	#tag_id: id corresponding to tag
	DB.createTable('quote_tag (quote_id INTEGER, tag_id INTEGER)')
else:
	print('already "quote_tag" table')

#BOOK TABLE

if not DB.tableExists('books'):
	print('no table "books"... making one now...')
	#Title: Book title #as spelled on  book
	#Author: as appears on book
	#isbn: as txt no hyphans
	DB.createTable('books (id INTEGER PRIMARY KEY AUTOINCREMENT, title VARCHAR(255), author VARCHAR(255), isbn VARCHAR(13) UNIQUE)')
else:
	print('already "quote_tag" table')
	
print('adding test data...')
if DB.getQuote(1):
	print('already quotes')
else:
	#def addBook(self,title,author,isbn10,isbn13):
	DB.addBook("Harry Potter and the Philosopher's Stone",'J. K. Rowling','9780590353427')
	DB.addBook('Brave New World','Aldous Huxley','0060809833')
	DB.addBook('Catch 22','Paul Bacon','0684833395')
	#def getBookId(self,title = None,author = None,isbn10 = None,isbn13 = None):
	bookid = DB.getBookId(title='Catch 22',author='Paul Bacon',isbn='0684833395')[0]
	#addQuote(self,quote,book_id,page,user,date,tags = []):
	DB.addQuote('This is a quote',bookid,397,'admin',['catch22','tag2'])
	
def _resetDB():
	DB.dropTable('users')
	DB.dropTable('quotes')
	DB.dropTable('tags')
	DB.dropTable('quote_tag')
	DB.dropTable('books')
	DB.close()