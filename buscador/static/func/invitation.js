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

$(document).on('click', ".acceptDemand", function(e){
	inputconnect = 
	{
		url: "folder",
		type: "POST",
	};
	inputdata =
	{
		idfolder: $("#idfolder").val(),
		iduser: $(this).attr("iduser"),		
	};
	ajaxPages(inputconnect, inputdata).promise().done(function(response)
	{
		console.log(response);
		if (response.check == 1)
			location.reload();
	});	
	console.log(" comentario enviado");
});


$(document).on('click', "#check", function(e)
{
	e.preventDefault();
	alert("hellow");
	inputconnect = 
	{
		url: "folder",
		type: "POST",
	};
	inputdata =
	{
		idfolder: $("#idfolder").val(),
		iduser: $(this).attr("iduser"),
	};
	//ajaxPages(inputconnect, inputdata).promise().done(function(response)
	//{
	//	console.log(response);
	//	if (response.check == 1)
	//		location.reload();
	//});	
	console.log(" comentario enviado");
});

function ajaxPages(inputconnect, inputdata)
{
	return $.ajax({
		url : inputconnect.url, // the endpoint
		type : inputconnect.type, // http method
		data : inputdata,// data sent with the post request
		// handle a successful response
		success : function(response)
		{
			return response;
		},
		// handle a non-successful response
		error : function(xhr,errmsg,err) {
		//$('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+" <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
		console.log("ERROR: " + xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
		}
	});
};