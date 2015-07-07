$('#nav-tabs').click(function (e) 
{
	e.preventDefault()
	$(this).tab('show')
})

var csrftoken = $("#csrfmiddlewaretoken").val();

function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
	beforeSend: function(xhr, settings) {
		if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken);
		}
	}

});

$(document).ready(function(){
	$(".tab-pane.source").each(function()
	{
		divsource=this;
		ajaxPage($(divsource).attr("name"), 1, $(divsource).attr("id")).promise().done(function(response)
		{
			console.log("toggle");
		});
	});
});

$(document).on('click', ".button-ok", function(){
	btn = this;
	if ($(btn).hasClass('active')) 
	{
		ajaxVote(0, btn).promise().done(function(json)
		{
			if (json.modified)
			{
				$(btn).button('toggle');
				console.log("toggle ok from 1");
			}
		});
	}
	else
	{
		ajaxVote(1, btn).promise().done(function(json)
		{
			if (json.modified) 
			{
				$(btn).button('toggle');
				if ($(btn).parent().find(".button-remove").hasClass('active'))
					$(btn).parent().find(".button-remove").button('toggle');
				console.log("toggle ok from 0");
			};
		});
	}
console.log("remove ok");
});

$(document).on('click', ".button-remove", function(){
	btn = this;
	if ($(btn).hasClass('active')) 
	{
		ajaxVote(0, btn).promise().done(function(json)
		{
			if (json.modified)
			{
				$(btn).button('toggle');
				console.log("toggle end from -1");
			}
		});
	}
	else
	{
		ajaxVote(-1, btn).promise().done(function(json)
		{
			if (json.modified) 
			{
				$(btn).button('toggle');
				if ($(btn).parent().find(".button-ok").hasClass('active'))
					$(btn).parent().find(".button-ok").button('toggle');
				console.log("toggle end from 0");
				sol = btn;
			};
		});
	}
console.log("remove end");
});


$(document).on('click', ".buttonpagination", function(e){
	e.preventDefault();
	if (!$(this).hasClass('disabled'))
	{	
		btn = this;
		ajaxPage($(".tab-pane.active").attr("name"), $(btn).val(), $(".tab-pane.active").attr("id")).promise().done(function(response)
		{
			console.log("toggle");
			$('html,body').animate({scrollTop:0},'slow');
		});
	};
});


$(document).on('click', "#ConfirmInfoComplete", function(e){
	$('#ModalInfoComplete').modal('hide')
	ajaxPage($(".tab-pane.active").attr("name"), 1, $(".tab-pane.active").attr("id")).promise().done(function(response)
	{
		console.log("toggle");
		$('html,body').animate({scrollTop:0},'slow');
	});
	ajaxComplete($("#idquery").val()).promise().done(function(response)
	{	
	 	location.reload();
	});
});


function ajaxVote(valueVote, button)
{
	return $.ajax({
		url : "vote", // the endpoint
		type : "POST", // http method
		data : 
			{
				source: $(button).parent().attr("source"),
				rank: $(button).parent().attr("rank"),
				value: valueVote, 
				id: $(button).parent().attr("id"),
			},// data sent with the post request

		// handle a successful response
		success : function(json)
		{
			return json;
		},

		// handle a non-successful response
		error : function(xhr,errmsg,err) {
		$('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+" <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
		console.log("ERROR: " + xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
		}
	});
};


function ajaxPage(source_, page_, iddb_)
{
	return $.ajax({
		url : "revisar", // the endpoint
		type : "GET", // http method
		data : 
			{
				source: source_,
				page: page_,
				iddb: iddb_,
				idquery: $("#idquery").val(),
			},// data sent with the post request

		// handle a successful response
		success : function(response)
		{
			console.log(iddb_);
			$("#" + iddb_).empty().append(response);
			return response;
		},

		// handle a non-successful response
		error : function(xhr,errmsg,err) {
		//$('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+" <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
		console.log("ERROR: " + xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
		}
	});
};

function ajaxComplete(query_)
{
	return $.ajax({
		url : "revisar", // the endpoint
		type : "POST", // http method
		data : 
			{
				query: query_,
			},// data sent with the post request
		// handle a successful response
		success : function(response)
		{
			console.log(response);
		},
		// handle a non-successful response
		error : function(xhr,errmsg,err) {
		//$('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+" <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
		console.log("ERROR: " + xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
		}
	});
};