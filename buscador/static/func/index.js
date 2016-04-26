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

//$(document).ready(function(){
//
//	$('#searchButton').click(function (event) 
//	{
//		if ($('#searchText').val().length > 0 )
//			$(location).attr('href', 'revisar?query='+$('#searchText').val());
//			/*$.get( 
//				"revisar", 
//				{query: $('#searchText').val()}
//			);*/
//		else
//			alert("no hay na!");
//	});
//});


//function ajaxPages(inputconnect, inputdata)
//{
//	return $.ajax({
//		url : inputconnect.url, // the endpoint
//		type : inputconnect.type, // http method
//		data : inputdata,// data sent with the post request
//		// handle a successful response
//		success : function(response)
//		{
//			return response;
//		},
//		// handle a non-successful response
//		error : function(xhr,errmsg,err) {
//		//$('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+" <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
//		console.log("ERROR: " + xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
//		}
//	});
//};