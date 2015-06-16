$('#myTab a').click(function (e) 
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

var sol = {};

$(document).ready(function(){
	$(".button-ok").click(function(){
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
					sol = btn;
				};
			});
		}
	console.log("remove ok");
	});

	$(".button-remove").click(function(){
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
		console.log(xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
		}
	});
};