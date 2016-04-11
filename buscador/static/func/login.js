function csrfSafeMethod(method) {
	// these HTTP methods do not require CSRF protection
	return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
$.ajaxSetup({
	beforeSend: function(xhr, settings) {
		if (!csrfSafeMethod(settings.type) && !this.crossDomain) {
			xhr.setRequestHeader("X-CSRFToken", csrftoken = $.cookie("csrftoken"));
		}
	}

});

$(document).on('click', "#send", function(e)
{
	e.preventDefault();
	var jsonOut = {};
	$("input").each(function()
	{	
		if ($(this).attr("name")=="password")
			jsonOut[$(this).attr("name")] = $.md5($(this).val());
		else if ($(this).attr("name")=="email")
			jsonOut[$(this).attr("name")] = $(this).val().toLowerCase();
		else
			jsonOut[$(this).attr("name")] = $(this).val(); 

	});
	console.log(jsonOut);			
	ajaxComplete(jsonOut).promise().done(function(response)
	{
		if (response.check < 1) 
		{
			console.log("send");
		}
		else 
		{
			response.check
			$.cookie("head", response.check[0], { expires: 360 });
			$.cookie("body", response.check[1], { expires: 360 });
			$.cookie("usr", response.check[2]), { expires: 360 };
			self.location="/";
		}
		
	});
});

function ajaxComplete(jsonOut)
{
	return $.ajax({
		url : "login", // the endpoint
		type : "POST", // http method
		data : jsonOut,// data sent with the post request
		// handle a successful response
		success : function(response)
		{
			console.log(response);
			return response;
		},
		// handle a non-successful response
		error : function(xhr,errmsg,err) {
		//$('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+" <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
		console.log("ERROR: " + xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
		}
	});
};