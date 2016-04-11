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
					firstname: "required",
					lastname: "required",
					password: {
						required: true,
						minlength: 8
					},
					confirm_password: {
						required: true,
						equalTo: "#password"
					},
					email: {
						email: true
					},
					topic: {
						required: "#newsletter:checked",
						minlength: 2
					},
					agree: "required"
				},
				messages: {
					firstname: "Ingresa al menos tu primer nombre",
					lastname: "Ingresa al menos tu primer apellido",
					password: {
						required: "Por favor ingresa una contraseña",
						minlength: "Tu contraseña debe tener al menos 8 caracteres"
					},
					confirm_password: {
						required: "Por favor ingresa una contraseña",
						minlength: "Tu contraseña debe tener al menos 8 caracteres",
						equalTo: "Escribe la misma contraseña de arriba"
					},
					email: "Por favor ingrese un mail válido",
					agree: "<b>Acepte el acuerdo...</b>"
				}
			});
});


$(document).on('click', "#send", function(e)
{
	e.preventDefault();
	if($("#signupForm").valid())
	{
		var jsonOut = {};
		$("input").each(function()
		{
			if ($(this).attr("name")=="password")
				jsonOut[$(this).attr("name")] = $.md5($(this).val());
			else if ($(this).attr("name")!="confirm_password")
				jsonOut[$(this).attr("name")] = $(this).val(); 
		});
		console.log(jsonOut);
		ajaxComplete(jsonOut).promise().done(function(response)
		{
			if (response.check == 1) 
			{
				//alert("guardado");
				self.location="/login?new=true";
			}//location.reload();};
			else if (response.check == 0) 
			{
				alert("El correo ya ha sido ocupado");
				console.log("send");
			}
			else if (response.check == -1) 
			{
				alert("error");
			}
		});
	};
});

function ajaxComplete(jsonOut)
{
	return $.ajax({
		url : "signup", // the endpoint
		type : "POST", // http method
		data : jsonOut,// data sent with the post request
		// handle a successful response
		success : function(response)
		{
			//console.log(response);
			return response;
		},
		// handle a non-successful response
		error : function(xhr,errmsg,err) {
		//$('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+" <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
		console.log("ERROR: " + xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
		}
	});
};