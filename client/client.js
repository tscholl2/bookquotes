/**
STATES or HANDLERS
**/
/*
NOT_CONNECTED = -1;
CONNECTED = 0;
LOGGED_OUT = 1;
LOGGING_IN = 2; //sent credentials, waiting for response
MAKING_NEW_UN = 2.5;
LOGGED_IN = 3;
*/


not_connected_handler = function (msg) {
	if (!msg) {
		if (ws != null) {
			ws.close()
			ws = null;
		}
		if (ScreenHolder.current[0] != $('#connect_screen')[0])
			ScreenHolder.swap($('#connect_screen'));
		MenuHolder.current = '0';
		$('.menu').hide();
		$('#menu0').show();
	
	} else if (msg == 'Hello World') {
		CURRENT_STATE = connected_handler;
		log('STATE = connected');
		MessageHolder.add('Connected!','success');
		connected_handler();
	};
};

connected_handler = function(msg) {
	if (!msg) {
		ScreenHolder.swap($('#login_screen'));
	} else {
		switch(msg.type) {
			case TYPE_ERROR_INPUT:
				MessageHolder.add('Something is wrong with the input.','danger');
				break;
			case TYPE_NO_USERNAME:
				MessageHolder.add('No such username found.','danger');
				break;
			case TYPE_ALREADY_USERNAME:
				MessageHolder.add('That username already exists.','danger');
				break;
			case TYPE_ALREADY_LOGGEDIN:
				MessageHolder.add('That user is already logged in.','danger');
				break;
			case TYPE_INVALID_PASSWORD:
				MessageHolder.add('Invalid password.','danger');
				//ScreenHolder.swap($('connect_screen'));
				break;
			case TYPE_LOGGED_IN:
				log('successfully logged in!')
				MessageHolder.add('Logged in as '+$('#un_input').val()+'.','success');
				CURRENT_STATE = logged_in_handler;
				log('STATE = logged in')
				logged_in_handler()
				break;
			default:
				//to-do?
		};
	}
};

logged_in_handler = function(msg) {
	if (!msg) {
		ScreenHolder.swap($('#logged_in_screen'));
	} else {
		switch(msg.type) {
			case TYPE_MESSAGE:
				log(msg.msg);
				ChatHolder.add(msg.msg,msg.by);
				//log-message
				break;
			case TYPE_DATA_RESPONSE:
				data = msg.r;
				if (data == null) {
					log('EMPTY QUERY');
					//to-do
					//show an alert thing on the page
					break;
				}
				$('#response_output').empty();
				switch(data.type) {
					case RESPONSE_BOOKS:
						//books:[{id:id#,t:title,a:author,i:isbn}]}
						//hides current results and then replaces them after hiding is done
						if (data.books.length > 0) {
							MessageHolder.add('Found '+data.books.length+' matches.','info');
							ResultsHolder.showBooks(data.books,function () {MessageHolder.add('Recieved search query.','success')});
						}
						else
							MessageHolder.add('No matches found.','info');
						break;
						
					case RESPONSE_QUOTES:
						if (data.quotes.length > 0) {
							MessageHolder.add('Found '+data.quotes.length+' matches.','info');
							ResultsHolder.showQuotes(data.quotes,function() {MessageHolder.add('Recieved search query.','success')});
						}
						else
							MessageHolder.add('No matches found.','info');
						break;
					default:
						//to-do?
				}
				break;
			case TYPE_SUBMISSION_RESPONSE:
				log('submission was successfule? ' + msg.b);
				if (msg.b) {
					MessageHolder.add('Submission successful','success');
					MenuHolder.clearInputs();
				}
				else
					MessageHolder.add('Submission failed','danger');
				break;
			default:
				//to-do?
		};
	}
};

/**
VARIOUS FUNCTIONS
**/

connect = function() {
	if (ws != null)
		return false;
	//var host = "192.168.0.150";
	var host = $("#ip_input").val()
	var port = "8888";
	var uri = "/database";
	ws = new WebSocket("ws://" + host + ":" + port + uri);
	ws.onmessage = function(evt) {
		log("message received: " + evt.data);
		var msg = JSON.parse(evt.data);
		//deal with messages that happen in every state
		try { 
			switch(msg.type) {
				case TYPE_NEW_CLIENT:
					CONNECTED_CLIENTS[msg.un] = true;
					MessageHolder.add(msg.un+' logged in.','info');
					//do something?
					break;
				case TYPE_CLIENT_LEFT:
					delete CONNECTED_CLIENTS[msg.un];
					MessageHolder.add(msg.un+' logged out.','info');
					//do something?
					break;
				default:
					//call current state's handler
					CURRENT_STATE(msg);
			};
		} catch(e) { 
			log('ERROR DOING SOMETHING???: \n\t' + e);
		};
	};
	ws.onclose = function(evt) {
		log("Connection close");
		MessageHolder.add('Disconnected from server.','danger');
		disconnect();
	};
	ws.onopen = function(evt) {
		log("Connection open");
	};
};

disconnect = function() {
	if (ws != null)
		ws.close();
	ws = null;
	CURRENT_STATE = not_connected_handler;
	log('STATE = not connected');
	not_connected_handler();
};

/**
UI
**/

/* CHATS */

ChatHolder = new Object();
ChatHolder.count = 0;
ChatHolder.add = function(message,author) {
	this.count += 1;
/*
<tr>
	<td style='width:70px;'>
		User:
	</td>
	<td>
		Message goes here
	</td>
</tr>
*/
	$('#chat-table').append("<tr><td>"+author+": </td>"+"<td>"+message+"</td></tr>\n");
	var $target = $('#chat-window'); 
	$target.scrollTop($target[0].scrollHeight);
	
	if (this.count > 10)
		$($('#chat-table').children()[0]).children()[1].remove();
}

/* SCREENS */

ScreenHolder = new Object();
ScreenHolder.swap = function(next) {
	swapFocusInWrapper(
		$('#screen-wrapper'),
		ScreenHolder.current,
		next,
		function() {
			ScreenHolder.current = next;
		}
	);
}
ScreenHolder.current = null; //needs to be set later

/* MENUS */

MenuHolder = new Object();
MenuHolder.current = '0';
MenuHolder.previous = ['0'];
MenuHolder.swap = function(i,jump) {
	var next_menu;
	if (jump != null) {
		next_menu = $('#menu'+jump);
	} else {
		next_menu = $('#menu'+(i >= 0 ? (this.current+i) : (this.previous.pop())));
	}
	swapFocusInWrapper($('#menu-wrapper'),$('#menu'+this.current),next_menu,function() {

		if (i >= 0 && next_menu.attr('id').slice(4) != MenuHolder.current)
			MenuHolder.previous.push(MenuHolder.current);
		MenuHolder.current = next_menu.attr('id').slice(4);
		ResultsHolder.hide();
	});
}
MenuHolder.clearInputs = function() {
	var inputs = $('#menu'+this.current+' input');
	for (var i=0;i<inputs.length;i++) {
		if (inputs[i].type != 'hidden')
			$(inputs[i]).val('');
	}
}

/* MESSAGES */


MessageHolder = new Object();
MessageHolder.id = 0;
MessageHolder.add = function(text,type,duration) {
	if (duration == null)
		duration = 5000;
	if (type == null)
		type = 'success';
	var i = (this.id+=1);
	var msg = document.createElement('div');
	msg.setAttribute("id", "message"+i);
	/*
		<div class="alert alert-block alert-warning">  
			<a class="close" data-dismiss="alert">&times</a>  
			<strong>Warning!</strong> Best check yo self, you're not looking too good.  
		</div>
	*/
	$(msg).addClass('alert alert-block alert-'+type);
	$(msg).addClass('custom-alert');
	$(msg).html("<a class='close' onclick='MessageHolder.delete("+i+");'>&times</a>"+text);
	setTimeout("MessageHolder.delete("+i+")",duration);
	$(msg).hide();
	$('#message-wrapper').append($(msg));
	$(msg).show('medium');
}
MessageHolder.delete = function(i) {
	var msg = $('#message'+i);
	if (msg.len != 0)
		msg.hide('slide',function(){msg.remove()});
}

/* RESULTS */

ResultsHolder = new Object();
ResultsHolder.books = [];
ResultsHolder.quotes = [];

ResultsHolder.empty = function() {
	while ($('#accordion').length > 0)
		$('#accordion').remove();
}
ResultsHolder.hasResults = function() {
	return $('#accordion').length > 0;
}
ResultsHolder.isVisible = function() {
	return this.hasResults() && $('#output-wrapper').is(":visible");
}
ResultsHolder.hide = function(callback) {
	$('#output-wrapper').hide('slow',callback);
}
ResultsHolder.show = function(callback) {
	$('#output-wrapper').show('slow',callback);
}

ResultsHolder.showResults = function(callback) {
	ResultsHolder.showResults.children = [];
	var arr = $('#accordion').children();
	for (var i=0;i<arr.length;i++)
		ResultsHolder.showResults.children.push(arr[i]);
	ResultsHolder.showResults_helper(callback);
}
ResultsHolder.showResults_helper = function(callback) {
	if (ResultsHolder.showResults.children.length > 0) {
		c = ResultsHolder.showResults.children.pop();
		$(c).show('slide',function() {ResultsHolder.showResults_helper(callback);});
	} else {
		if ($.isFunction(callback)) {
			callback();	
		}
	}
}

ResultsHolder.hideResults = function(callback) {
	if (!$('#output-wrapper').is(':visible')) {
		var arr = $('#accordion').children();
		for (var i=0;i<arr.length;i++)
			$(arr[i]).hide();
	}
	else {
		ResultsHolder.hideResults.children = [];
		var arr = $('#accordion').children();
		for (var i=0;i<arr.length;i++)
			ResultsHolder.hideResults.children.push(arr[i]);
		ResultsHolder.hideResults_helper(callback);
	}
}
ResultsHolder.hideResults.children = [];
ResultsHolder.hideResults_helper = function(callback) {
	if (ResultsHolder.hideResults.children.length > 0) {
		c = ResultsHolder.hideResults.children.pop();
		$(c).hide('slide',function() {ResultsHolder.hideResults_helper(callback);});
	} else {
		if ($.isFunction(callback)) {
			callback();	
		}
	}
}


/* DISPLAYING BOOKS */


ResultsHolder.showBooks = function(books,callback) {
	//store the given books
	this.books = books;
	//empty current output and then start populating again
	if (this.isVisible())
		this.hideResults(function() {
			ResultsHolder.empty();
			ResultsHolder.showBooks_step1(callback)
		})
	else {
		this.empty();
		this.show(function() {
			ResultsHolder.showBooks_step1(callback);
		});
	}
}
ResultsHolder.showBooks.children = [];
ResultsHolder.showBooks_step1 = function(callback) {

/* STYLE OF BOOK PANELS
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title">
        <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion" href="#collapseOne">
          Collapsible Group Item #1
        </a>
      </h4>
    </div>
    <div id="collapseOne" class="panel-collapse collapse in">
      <div class="panel-body">
        table, raw denim aesthetic synth nesciunt you probably haven't heard of them accusamus labore sustainable VHS.
      </div>
    </div>
  </div>
*/
	
	//build div to hold new output
	var panels = document.createElement('div');
	$(panels).addClass('panel-group');
	$(panels).attr({
		id: 'accordion'
	});
	$(panels).css({'margin':'auto'});
	
	//add panels
	$('#request_output').append(panels);
	
	for (var k=0;k<this.books.length;k++) {
		var b = this.books[k];
		//setup div container
		var div = document.createElement('div');
		$(div).attr({
			id: 'bookdiv'+b.id
		});
		$(div).addClass('panel panel-default');
		
		//set up heading
		var heading = document.createElement('div');
		$(heading).addClass('panel-heading book-panel-heading');
		$(heading).attr({
			'data-toggle':'collapse',
			'data-parent':'accordion',
			'href':'#collapse'+b.id
		});
		var h4 = document.createElement('h4');
		$(h4).addClass('panel-title book-panel-title');
		$(h4).html(b.t);
		
		$(heading).append(h4);
		$(div).append(heading);
		
		//setup collapsable
		
		var collapsable = document.createElement('div');
		$(collapsable).addClass('panel-collapse collapse');
		$(collapsable).attr({
			'id':'collapse'+b.id
		});
		var cbody = document.createElement('div');
		$(cbody).addClass('panel-body book-extra-info');
		$(cbody).html('<ul class="list-group" style="text-align:left">'
			+'<li class="list-group-item"><strong>Author:</strong> '+b.a
			+'</li><li class="list-group-item">'+'<strong>ISBN:</strong> '+b.i+'</li></ul>');
		
		var quotebtn = document.createElement('button');
		$(quotebtn).addClass('btn btn-info btn-sm');
		$(quotebtn).attr('id','linkbtn'+b.id);
		$(quotebtn).attr('onclick','MenuHolder.swap(0,"022");'
			+'$("#submit_quote_bid").val('+b.id+')'
		);
		$(quotebtn).html('Submit Quote');
		
		$(cbody).append(quotebtn);
		$(collapsable).append(cbody);
		$(div).append(collapsable);

		
		//attach
		$(panels).append(div);
		$(div).hide();
	}
	var arr=$('#accordion').children();
	for (var i=0;i<arr.length;i++)
		this.showBooks.children.push(arr[i]);
	if (this.showBooks.children.length > 0)
		this.showBooks_step1_helper(callback);
}
ResultsHolder.showBooks_step1_helper = function(callback) {
	if (ResultsHolder.showBooks.children.length > 1)
		$(ResultsHolder.showBooks.children.pop()).show('medium',function() {
			ResultsHolder.showBooks_step1_helper(callback);
		});
	if (ResultsHolder.showBooks.children.length == 1)
		$(ResultsHolder.showBooks.children.pop()).show('medium',callback);
}



/* DISPLAYING QUOTES */



ResultsHolder.showQuotes = function(quotes,callback) {
	//store the given books
	this.quotes = quotes;
	//empty current output and then start populating again
	if (this.isVisible())
		this.hideResults(function() {
			ResultsHolder.empty();
			ResultsHolder.showQuotes_step1(callback)
		})
	else {
		this.empty();
		this.show(function() {
			ResultsHolder.showQuotes_step1(callback);
		});
	}
}
ResultsHolder.showQuotes.children = [];

ResultsHolder.showQuotes_step1 = function(callback) {
//quotes:[{id:quoteid#,txt:quotetext,b:{id:bookid#,t:title,a:author,i:isbn},p:page#,un:usersubmitter,d:datestring,tags:[tag1,tag2,...]}]}

/* STYLE OF BOOK PANELS
  <div class="panel panel-default">
    <div class="panel-heading">
      <h4 class="panel-title">
        <a class="accordion-toggle" data-toggle="collapse" data-parent="#accordion" href="#collapseOne">
          Collapsible Group Item #1
        </a>
      </h4>
    </div>
    <div id="collapseOne" class="panel-collapse collapse in">
      <div class="panel-body">
        table, raw denim aesthetic synth nesciunt you probably haven't heard of them accusamus labore sustainable VHS.
      </div>
    </div>
  </div>
*/
	
	//build div to hold new output
	var panels = document.createElement('div');
	$(panels).addClass('panel-group');
	$(panels).attr({
		id: 'accordion'
	});
	$(panels).css({'margin':'auto'});
	
	//add panels
	$('#request_output').append(panels);
	
	for (var k=0;k<this.quotes.length;k++) {
		var q = this.quotes[k];
		//q looks like this:
/*
{id:quoteid#,
txt:quotetext,
b:{id:bookid#,t:title,a:author,i:isbn},
p:page#,
un:usersubmitter,
d:datestring,
tags:[tag1,tag2,...]}
*/

		//setup div container
		var div = document.createElement('div');
		$(div).attr({
			id: 'quotediv'+q.id
		});
		$(div).addClass('panel panel-default');
		
		//set up heading
		var heading = document.createElement('div');
		$(heading).addClass('panel-heading book-panel-heading');
		$(heading).attr({
			'data-toggle':'collapse',
			'data-parent':'accordion',
			'href':'#collapse'+q.id
		});
		$(heading).on({ 'touchend' : $(heading).click});
		var h4 = document.createElement('h4');
		$(h4).addClass('panel-title book-panel-title');
		$(h4).html(q.b.t+', p.'+q.p);
		
		$(heading).append(h4);
		$(div).append(heading);
		
		//setup collapsable
		
		var collapsable = document.createElement('div');
		$(collapsable).addClass('panel-collapse collapse');
		$(collapsable).attr({
			'id':'collapse'+q.id
		});
		var cbody = document.createElement('div');
		$(cbody).addClass('panel-body book-extra-info');
		$(cbody).html(
			'<ul class="list-group" style="text-align:left">'
			+'<li class="list-group-item"><strong>Author:</strong> '+q.b.a+'</li>'
			+'<li class="list-group-item">'+'<strong>Quote:</strong> '+q.txt+'</li>'
			+'<li class="list-group-item"><strong>User:</strong> '+q.un+'</li>'
			+'<li class="list-group-item">'+'<strong>Date:</strong> '+q.d+'</li>'
			+'<li class="list-group-item">'+'<strong>Tags:</strong> '+q.tags.join(', ')+'</li>'
			+'</ul>'
			);
		
		$(collapsable).append(cbody);
		$(div).append(collapsable);

		
		//attach
		$(div).hide();
		$(panels).append(div);
	}
	var arr=$('#accordion').children();
	for (var i=0;i<arr.length;i++)
		this.showQuotes.children.push(arr[i]);
	if (this.showQuotes.children.length > 0)
		this.showQuotes_step1_helper(callback);
	
}
ResultsHolder.showQuotes_step1_helper = function(callback) {
	if (ResultsHolder.showQuotes.children.length > 1)
		$(ResultsHolder.showQuotes.children.pop()).show('medium',function() {
			ResultsHolder.showQuotes_step1_helper(callback);
		});
	if (ResultsHolder.showQuotes.children.length == 1)
		$(ResultsHolder.showQuotes.children.pop()).show('medium',callback);
}



/**
TOOLS
**/

swapFocusInWrapper = function(wrapper,current,next,callback) {
	var cur_size = {
		width:	current.width()+'px',
		height:	current.height()+'px'
	};

	var next_size = {
		width: next.width()+'px',
		height: next.height()+'px'
	};

	//fix current settings (while fadeout)
	wrapper.css(cur_size);
	//hide current screen
	current.fadeOut('fast',function () {
		//hide current thing - make sure stays hidden
		current.hide();
		//animate to next size
		wrapper.animate(next_size, 'medium', function() {
			//fade in new screen
			next.fadeIn('fast',callback());
			//clear fixed width/height so other elements can move this if necessary
			wrapper.css({width:'',height:''});
		});
	});
}


log = function(text) {
	//$('#log').append('<br/>'+text)
	//$('#log').scrollTop($('#log')[0].scrollHeight);
	console.log(text);
};

/**
BUTTON LINKING
**/

$(function() { //needs to be wrapped because code is called before buttons actually loaded
	$("#conn_btn").click(function() {
		connect();
	});

	$("#login_btn").click(function() {
		var msg = {
			type:TYPE_LOGIN,
			un:$('#un_input').val(),
			pw:$('#pwd_input').val()
		};
		ws.send(JSON.stringify(msg));
	});

	$("#newuser_btn").click(function() {
		var msg = {
			type:TYPE_NEW_USERNAME,
			un:$('#un_input').val(),
			pw:$('#pwd_input').val()
		};
		ws.send(JSON.stringify(msg));
	});
	
	$("#search_book_btn").click(function() {
		//{type:#,id:bookid#,t:title,a:author,i:isbn#}
		var q = {type:QUERY_BOOKS}
		if ($('#search_book_title').val() != '')
			q.t = $('#search_book_title').val();
		if ($('#search_book_author').val() != '')
			q.a = $('#search_book_author').val();
		if ($('#search_book_isbn').val() != '')
			q.i = $('#search_book_isbn').val();
		var msg = {
			type:TYPE_DATA_QUERY,
			q:q
		};
		ws.send(JSON.stringify(msg));
	});
	
	
	$("#search_quote_btn").click(function() {
//{type:#,txt:searchtext,un:username,d1:beforethisdate,d2:afterthisdate,bid:bookid#,t:booktitle,a:bookauthor,i:bookisbn,p:page,tags:tag1,tag2}
		tag_data = $('#search_quote_tags').val().split(',');
		for (var i=0;i<tag_data.length;i++) {
			tag_data[i] = tag_data[i].trim();
		}
		var q = {type:QUERY_QUOTES}
		if ($('#search_quote_p').val() != '')
			q.p = parseInt($('#search_quote_p').val());
		if ($('#search_quote_title').val() != '')
			q.t = $('#search_quote_title').val();
		if ($('#search_quote_author').val() != '')
			q.a = $('#search_quote_author').val();
		if ($('#search_quote_un').val() != '')
			q.un = $('#search_quote_un').val();
		if ($('#search_quote_d1').val() != '')
			q.d1 = $('#search_quote_d1').val();
		if ($('#search_quote_d2').val() != '')
			q.d2 = $('#search_quote_d2').val();
		if ($('#search_quote_txt').val() != '')
			q.txt = $('#search_quote_txt').val();
		if ($('#search_quote_tags').val() != '')
			q.tags = tag_data;
		var msg = {
			type:TYPE_DATA_QUERY,
			q:q
		};
		ws.send(JSON.stringify(msg));
	});
	
	$("#submit_book_btn").click(function() {
//{type:#,t:title,a:author,i:isbn}
		var msg = {
			type:TYPE_SUBMIT_BOOK,
			t:$('#submit_book_title').val(),
			a:$('#submit_book_author').val(),
			i:$('#submit_book_isbn').val()
		};
		ws.send(JSON.stringify(msg));
	});
	
	$("#submit_quote_btn").click(function() {
//{type:#,txt:quotetext,bid:bookid#,p:page#,tags:[tag1,tag2,...]}
		tag_data = $('#search_quote_tags').val().split(',');
		for (var i=0;i<tag_data.length;i++) {
			tag_data[i] = tag_data[i].trim();
		}
		var msg = {
			type:TYPE_SUBMIT_QUOTE,
			txt:$('#submit_quote_txt').val(),
			bid:parseInt($('#submit_quote_bid').val()),
			p:parseInt($('#submit_quote_p').val()),
			tags:$('#submit_quote_tags').val().split(',')
		};
		ws.send(JSON.stringify(msg));
	});
	
	$("#send_message_button").click(function(){
		if ($('#message_input').val() != '')
			ws.send(JSON.stringify({
				'type':TYPE_MESSAGE,
				'msg':$('#message_input').val()
			}));
		$('#message_input').val('');
	});
	
	/* BOOK SORTING */
	
	$('#sort_book_title_button').click(function() {
		ResultsHolder.books.sort(function(a,b){
			if (a.t.toLowerCase() == b.t.toLowerCase())
				return 0
			if (a.t.toLowerCase() < b.t.toLowerCase())
				return -1
			else
				return 1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showBooks(ResultsHolder.books)});
	});
	
	$('#sort_book_author_button').click(function() {
		ResultsHolder.books.sort(function(a,b){
			if (a.a.toLowerCase() == b.a.toLowerCase())
				return 0
			if (a.a.toLowerCase() < b.a.toLowerCase())
				return -1
			else
				return 1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showBooks(ResultsHolder.books)});
	});
	
	$('#sort_book_isbn_button').click(function() {
		ResultsHolder.books.sort(function(a,b){
			if (a.i == b.i)
				return 0
			if (a.i<b.i)
				return -1
			else
				return 1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showBooks(ResultsHolder.books)});
	});
	
	/* QUOTE SORTING */
	
	$('#sort_quote_tags_button').click(function() {
		ResultsHolder.quotes.sort(function(a,b){
			if (a.tags.join(' ').toLowerCase() == b.tags.join(' ').toLowerCase())
				return 0
			if (a.tags.join(' ').toLowerCase()<b.tags.join(' ').toLowerCase())
				return -1
			else
				return 1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showQuotes(ResultsHolder.quotes)});
	});
	
	$('#sort_quote_txt_button').click(function() {
		ResultsHolder.quotes.sort(function(a,b){
			if (a.txt.toLowerCase() == b.txt.toLowerCase())
				return 0
			if (a.txt.toLowerCase()<b.txt.toLowerCase())
				return -1
			else
				return 1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showQuotes(ResultsHolder.quotes)});
	});
	
	$('#sort_quote_d2_button').click(function() {
		ResultsHolder.quotes.sort(function(a,b){
			if (a.d == b.d)
				return 0
			if (a.d<b.d)
				return 1
			else
				return -1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showQuotes(ResultsHolder.quotes)});
	});
	
	$('#sort_quote_d1_button').click(function() {
		ResultsHolder.quotes.sort(function(a,b){
			if (a.d == b.d)
				return 0
			if (a.d<b.d)
				return -1
			else
				return 1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showQuotes(ResultsHolder.quotes)});
	});
	
	$('#sort_quote_un_button').click(function() {
		ResultsHolder.quotes.sort(function(a,b){
			if (a.un == b.un)
				return 0
			if (a.un<b.un)
				return -1
			else
				return 1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showQuotes(ResultsHolder.quotes)});
	});
	
	$('#sort_quote_author_button').click(function() {
		ResultsHolder.quotes.sort(function(a,b){
			if (a.b.a.toLowerCase() == b.b.a.toLowerCase())
				return 0
			if (a.b.a.toLowerCase() < b.b.a.toLowerCase())
				return -1
			else
				return 1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showQuotes(ResultsHolder.quotes)});
	});
	
	$('#sort_quote_title_button').click(function() {
		ResultsHolder.quotes.sort(function(a,b){
			if (a.b.t.toLowerCase() == b.b.t.toLowerCase())
				return 0
			if (a.b.t.toLowerCase() < b.b.t.toLowerCase())
				return -1
			else
				return 1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showQuotes(ResultsHolder.quotes)});
	});
	
	$('#sort_quote_page_button').click(function() {
		ResultsHolder.quotes.sort(function(a,b){
			if (a.p == b.p)
				return 0
			if (a.p < b.p)
				return -1
			else
				return 1
		});
		ResultsHolder.hideResults(function() {ResultsHolder.showQuotes(ResultsHolder.quotes)});
	});
});
