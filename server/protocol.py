##start prototcal*/

'''
NOTE: all transmissions are json encoded with descriptions given
EX:
{type:#,msg:string}
this means the encoded object has field called 'type' with value some number
and a field called 'msg' with value some string like
{
	type:7
	msg:'hello world'
}
'''

'''
#client <-> server
'''

##time request returned
##server->client: {type:#,t:servertime}
##client->server: {type:#}
TYPE_TIME_REQUEST=5;

'''
#client -> server
'''

##asking for data, queryinfo is dictionary example q.type,q.title,q.tags,q.author, etc.
##{type:#,q:dataquery}
TYPE_DATA_QUERY=23;

##asking to submit book
##{type:#,t:title,a:author,i:isbn} ##ALL must be non-empty and valid!
TYPE_SUBMIT_BOOK=25;

##asking to submit quote
##{type:#,txt:quotetext,bid:bookid#,p:page#,tags:[tag1,tag2,...]}
TYPE_SUBMIT_QUOTE=26;

##asking to make a new user name/password
##{type:#,un:username,pw:password}
TYPE_NEW_USERNAME=21;

##login message 
##{type:#,un:username,pw:password}
TYPE_LOGIN=4;

##chat message 
##{type:#,msg:string}
TYPE_MESSAGE=17;

'''
#server -> client
'''

##responds wheather a submission was successful or not
##{type:#,b:boolean}
TYPE_SUBMISSION_RESPONSE=27;

##data query response
##{type:#,r:dictionary_of_data}
TYPE_DATA_RESPONSE=24;

##chat message 
##{type:#,by:authorname,msg:string}
TYPE_MESSAGE=17;

##error in input
##{type:#}
TYPE_ERROR_INPUT = 12;

##no such user name exists
##{type:#}
TYPE_NO_USERNAME=13;

##if asked to create user name, and it exists
##{type:#}
TYPE_ALREADY_USERNAME=14;

##already logged in
##{type:#}
TYPE_ALREADY_LOGGEDIN=15;

##wrong passowrd
##{type:#}
TYPE_INVALID_PASSWORD=18;

##new player enters
##{type:#,un:username}
TYPE_NEW_CLIENT=3;

##when client correctly logs in
##{type:#}
TYPE_LOGGED_IN=20;

##if a player leaves
##{type:#,un:username}
TYPE_CLIENT_LEFT=19;


##end protocal*/
##start  data-protocal*/

##
#queries
##

##search books using given parameters. If left blank a wild card is substituted
##so if all blank returns all books
##{type:#,id:bookid#,t:title,a:author,i:isbn#}
QUERY_BOOKS = 1;

#search quotes using given parameters. If left blank a wild card is substituted
#so if all blank returns all quotes
##note tags is a separated list by commas
##{type:#,id:id#,txt:searchtext,un:username,d1:beforethisdate,d2:afterthisdate,bid:bookid#,t:booktitle,a:bookauthor,i:bookisbn,,p:page,tags:[tag1,tag2,...]}
QUERY_QUOTES = 2;


##
#responses
##

##return all books satisfying given search parameters
##{type:#,books:[{id:id#,t:title,a:author,i:isbn}]}
RESPONSE_BOOKS=1;

##list all quotes satisfying search parameters
##{type:#,quotes:[{id:quoteid#,txt:quotetext,b:{id:bookid#,t:title,a:author,i:isbn},p:page#,un:usersubmitter,d:datestring,tags:[tag1,tag2,...]}]}
RESPONSE_QUOTES = 2;


##end    data-protocal*/