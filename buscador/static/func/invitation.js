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
		idquery: $("#idfolder").val(),
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
	if (!$(this).hasClass('disabled'))
	{		
		inputconnect = 
		{
			url: "folder",
			type: "POST",
		};
		inputdata =
		{
			idquery: $("#idfolder").val(),
			email: $('#invitation').val()
		};
		ajaxPages(inputconnect, inputdata).promise().done(function(response)
		{
			console.log(response);		
			$("#invitation").prop('disabled', true);
			$("#check").addClass('disabled');
			modalFooter = $(".modal-footer").collapse('show');
			alert = modalFooter.find(".alert").removeClass("alert-success alert-info alert-warning");			
			if (response.check == 1)
			{
				$("#send").removeClass('disabled');
				alert.addClass("alert-success").html("Se sumará a " + response.name + " como colaborador. Presione aceptar para confirmar, o volver para probar con otro correo");
			}
			else if (response.check == 2)
			{
				$("#send").addClass('disabled');
				alert.addClass("alert-info").html("El correo corresponde a " + response.name + ". Pruebe con otro correo para continuar");
			}
			else if (response.check == -1)
			{
				$("#send").removeClass('disabled');
				alert.addClass("alert-warning").html("El correo no existe o no está registrado. Presione continuar para enviar una invitación.");
			}
			else
				alert("Error");
		});	
	}
});

$(document).on('click', "#back", function(e)
{
	$(".modal-footer").collapse('hide');
	$("#invitation").prop('disabled', false);
	$("#check").removeClass('disabled');
});

$(document).on('click', "#send", function(e)
{
	inputconnect = 
	{
		url: "folder",
		type: "POST",
	};
	inputdata =
	{
		idquery: $("#idfolder").val(),
		email: $('#invitation').val(),
		confirm: true,
	};
	ajaxPages(inputconnect, inputdata).promise().done(function(response)
	{
		if (response.check == 0)
			alert("El usuario no existe...\nAlgo mal estás haciendo.")
		else if (response.check == -1)
			alert("Error en solicitud")
		else if (response.check == 1)
			location.reload();
		else
			alert("Error");
	});	
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