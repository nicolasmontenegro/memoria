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
			alertBox = modalFooter.find(".alert").removeClass("alert-success alert-info alert-warning");			
			if (response.check == 1)
			{
				$("#send").removeClass('disabled');
				alertBox.addClass("alert-success").html("Se sumará a <b>" + response.name + "</b> como colaborador.<br>Presione aceptar para confirmar, o volver para probar con otro correo");
			}
			else if (response.check == 2)
			{
				$("#send").addClass('disabled');
				alertBox.addClass("alert-info").html("El correo corresponde a <b>" + response.name + "</b> quien ya es colaborador.<br>Pruebe con otro correo para continuar");
			}
			else if (response.check == 0)
			{
				$("#send").addClass('disabled');
				alertBox.addClass("alert-warning").html("<b>El correo no existe o no está registrado.</b>");
			}
			else
				alarm("Error");
		});	
	}
});

$(document).on('click', "#back", function(e)
{
	e.preventDefault();
	$(".modal-footer").collapse('hide');
	$("#invitation").prop('disabled', false);
	$("#check").removeClass('disabled');
});

$(document).on('click', "#send", function(e)
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
			{
				$(".modal-footer").collapse('hide');
				$("#invitation").prop('disabled', false);
				$("#check").removeClass('disabled');
				location.reload();
			}
			else
				alert("Error");
		});	
	}
});

$(document).ready(function(){
	$("#serach").submit(function(e){
		$("#whenSearchQuery").append("\"" + $("#query").val() +  "\"");
		$(".row").addClass("collapse in").collapse("hide");
		$("#whenSearch").collapse("show");
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