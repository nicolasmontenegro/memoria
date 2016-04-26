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

$().ready(function() {	
	$("#signupForm").validate({
				rules: {
					password: {
						required: true,
						minlength: 8
					},
					confirm_password: {
						required: true,
						equalTo: "#password"
					},
				},
				messages: {
					password: {
						required: "Por favor ingresa una contraseña",
						minlength: "Tu contraseña debe tener al menos 8 caracteres"
					},
					confirm_password: {
						required: "Por favor ingresa una contraseña",
						minlength: "Tu contraseña debe tener al menos 8 caracteres",
						equalTo: "Escribe la misma contraseña de arriba"
					},
				}
			});
});


$(document).on('click', "#send", function(e)
{
	e.preventDefault();
	if($("#signupForm").valid())
	{
		inputconnect = 
		{
			url: "recoverpassword",
			type: "POST",
		};
		inputdata =
		{
			password: $.md5($("input[name='password']").val()),
			idRecover: $("#idRecover").val(),
		};
		console.log(inputdata)
		ajaxPages(inputconnect, inputdata).promise().done(function(response)
		{
			if (response.check == 1) 
			{
				self.location="/login?recover=true";
			}
			else if (response.check == 0) 
			{
				alert("El tiempo de recuperación expiró");
				self.location="/recoverpassword";
			}
			else if (response.check == -1) 
			{
				alert("error");
			}
		});
	};
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