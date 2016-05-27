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

 $("a[href='#download']").on('shown.bs.tab', function (e) {
 	divsource=this;
		inputconnect = 
		{
			url: "revisar",
			type: "GET",
		};
		inputdata =
		{
			idquery: $("#idquery").val(),
			download: true,
		};
		ajaxPages(inputconnect, inputdata).promise().done(function(response)
		{
			$("#download").empty().append(response);
			console.log("toggle");
		});  
});

$(document).ready(function(){
	$(".tab-pane.source").each(function()
	{
		divsource=this;
		inputconnect = 
		{
			url: "revisar",
			type: "GET",
		};
		inputdata =
		{
			source: $(divsource).attr("name"),
			page: 1,
			iddb: $(divsource).attr("id"),
			idquery: $("#idquery").val(),
		};
		ajaxPagesAUX(inputconnect, inputdata).promise().done(function(response)
		{
			console.log("toggle");
		});
	});
});

$(document).on('click', ".button-ok", function(){
	btn = this;
	inputconnect = 
	{
		url: "vote",
		type: "POST",
	};
	inputdata =
	{
		source: $(btn).parents(".source").attr("name"),
		rank: $(btn).parents(".well").attr("rank"),
		value: 0, 
		id: $(btn).parents(".source").attr("id"),
	};
	if ($(btn).hasClass('active')) 
	{
		inputdata.value = 0;
		ajaxPages(inputconnect, inputdata).promise().done(function(response)
		{
			if (response.remove)
			{
				$(btn).button('toggle');
				console.log("toggle ok from 1");
				updateCountVote (btn, response); 
			}
		});
	}
	else
	{
		inputdata.value = 1;
		ajaxPages(inputconnect, inputdata).promise().done(function(response)
		{
			if (response.add) 
			{
				$(btn).button('toggle');
				if ($(btn).parent().find(".button-remove").hasClass('active'))
					$(btn).parent().find(".button-remove").button('toggle');
				console.log("toggle ok from 0");
				updateCountVote (btn, response); 
			};
		});
	}
console.log("remove ok");
});

$(document).on('click', ".button-remove", function(){
	btn = this;
	inputconnect = 
	{
		url: "vote",
		type: "POST",
	};
	inputdata =
	{
		source: $(btn).parents(".source").attr("name"),
		rank: $(btn).parents(".well").attr("rank"),
		value: 0, 
		id: $(btn).parents(".source").attr("id"),
	};
	if ($(btn).hasClass('active')) 
	{
		inputdata.value = 0;
		ajaxPages(inputconnect, inputdata).promise().done(function(response)
		{
			if (response.remove)
			{
				$(btn).button('toggle');
				console.log("toggle end from -1");
				updateCountVote (btn, response); 
			}
		});
	}
	else
	{
		inputdata.value = -1;
		ajaxPages(inputconnect, inputdata).promise().done(function(response)
		{
			if (response.add) 
			{
				$(btn).button('toggle');
				if ($(btn).parent().find(".button-ok").hasClass('active'))
					$(btn).parent().find(".button-ok").button('toggle');
				console.log("toggle end from 0");
				updateCountVote (btn, response); 
			};
		});
	}
console.log("remove end");
});

function updateCountVote (btn, response) {
	$(btn).parent().find(".button-ok strong").html(" " + response.yes);
	$(btn).parent().find(".button-remove strong").html( " " + response.no);
	$(btn).parent().find(".button-comment strong").html( " " + response.comment);
};


$(document).on('click', ".buttonpagination", function(e){
	e.preventDefault();
	if (!$(this).hasClass('disabled'))
	{	
		btn = this;
		inputconnect = 
		{
			url: "revisar",
			type: "GET",
		};
		inputdata =
		{
			source: $(btn).parents(".source").attr("name"),
			iddb: $(btn).parents(".source").attr("id"),
			page: $(btn).val(),
			idquery: $("#idquery").val(),
		};
		ajaxPagesAUX(inputconnect, inputdata).promise().done(function(response)
		{
			console.log("toggle");
			$('html,body').animate({scrollTop:0},'slow');
		});
	};
});


$(document).on('click', "#ConfirmInfoComplete", function(e){
	//$('#ModalInfoComplete').modal('hide')
	inputconnect = 
	{
		url : "revisar",
	};

	inputconnect.type = "GET"; 
		inputdata =
		{

			source: $(".tab-pane.active").attr("name"),
			page: 1,
			iddb: $(".tab-pane.active").attr("id"),
			idquery: $("#idquery").val(),
		};
		ajaxPagesAUX(inputconnect, inputdata).promise().done(function(response)
		{
			console.log("toggle");
			$('html,body').animate({scrollTop:0},'slow');
		});


	inputconnect.type = "POST"; 
	inputdata =
	{
		query: $("#idquery").val(),
	};
	ajaxPages(inputconnect, inputdata).promise().done(function(response)
	{	
	 	location.reload();
	});
});

$(document).on('click', ".button-comment", function(e){
	btn = this;
	$("#ModalComment").attr("source", $(btn).parents(".source").attr("name"));
	$("#ModalComment").attr("rank", $(btn).parents(".well").attr("rank"));
	$("#ModalComment").attr("idpub", $(btn).parents(".source").attr("id"));	
	inputconnect = 
	{
		url: "comment",
		type: "GET",
	};
	inputdata =
	{
		source: $("#ModalComment").attr("source"),
		rank: $("#ModalComment").attr("rank"),
		id: $("#ModalComment").attr("idpub"),
	};
	ajaxPages(inputconnect, inputdata).promise().done(function(response)
	{
		console.log("llegado  comentarios");
		$(".modal-dialog").html(response);
		$('#ModalComment').modal('show');
	});	
	console.log("mostrado comentario");
});

$(document).on('input propertychange paste', "#textComment", function(e){
	if ($("#textComment").val() != "")
		$("#sendComment").removeClass('disabled');
	else
		$("#sendComment").addClass('disabled');
});

$(document).on('click', "#sendComment", function(e){
	e.preventDefault();
	if ($(this).hasClass('disabled'))
		return null;
	inputconnect = 
	{
		url: "comment",
		type: "POST",
	};
	inputdata =
	{
		source: $("#ModalComment").attr("source"),
		rank: $("#ModalComment").attr("rank"),
		id: $("#ModalComment").attr("idpub"),
		comment: $("#textComment").val(),
	};
	$("#sendComment").addClass('disabled');
	ajaxPages(inputconnect, inputdata).promise().done(function(response)
	{
		console.log("llegado nuevos comentarios");
		$(".modal-dialog").html(response);
		$('#ModalComment').modal('show');
		updateButtonsValues();
	});		
	console.log(" comentario enviado");
});


$('#ModalComment').on('hidden.bs.modal', function () {
    updateButtonsValues();
})

function updateButtonsValues() {	
	inputconnect = 
	{
		url: "vote",
		type: "GET",
	};
    inputdata =
	{
		source: $("#ModalComment").attr("source"),
		rank: $("#ModalComment").attr("rank"),
		id: $("#ModalComment").attr("idpub"),
		update: true,
	};
	ajaxPages(inputconnect, inputdata).promise().done(function(response)
	{
		btn = $("[source='" + inputdata.source + "'][rank='" + inputdata.rank + "'][id='" + inputdata.id + "']").find(".button-comment");
		updateCountVote (btn, response); 
	});	
}

$(document).on('click', ".button-bookmark", function(){
	btn = this;
	inputconnect = 
	{
		url: "bookmark",
		type: "POST",
	};
	inputdata =
	{
		source: $(btn).parents(".source").attr("name"),
		rank: $(btn).parents(".well").attr("rank"),
		iddb: $(btn).parents(".source").attr("id"),
		idquery: $("#idquery").val(),
	};
	ajaxPages(inputconnect, inputdata).promise().done(function(response)
	{
		$(".panel-bookmark").removeClass("collapse");
		$(".panel-bookmark a").attr("iddb", inputdata.iddb).attr("rank", inputdata.rank).attr("source", inputdata.source);
		alert("Marcador guardado");
		console.log("bookmark check " +  response.modified);
	});
});

$(document).on('click', ".button-bookmarkGoTo", function(e){
	e.preventDefault()
	btn=this;
	inputconnect = 
	{
		url: "revisar",
		type: "GET",
	};
	inputdata =
	{
		source: $(btn).attr("source"),
		iddb: $(btn).attr("iddb"),
		idquery: $("#idquery").val(),
		page: parseInt((parseInt($(btn).attr("rank"))-1)/24)+1,
	};
	ajaxPagesAUX(inputconnect, inputdata).promise().done(function(response)
	{
		$('.nav-tabs a[href="#' + inputdata.iddb + '"]').tab('show');
		$('html,body').animate({
        scrollTop: $('#' + $(btn).attr("iddb")).find('[rank="' + $(btn).attr("rank") +  '"]').offset().top - 70},
        'slow');
        $('#' + $(btn).attr("iddb")).find('[rank="' + $(btn).attr("rank") +  '"]').effect( "highlight", {color:"#4080bf"}, 1000 );
	});
});

$(document).on('click', ".button-abstract", function(e){
	e.preventDefault()
	var objective = $($(this).attr("target"));
	if (objective.hasClass("empty") && !objective.hasClass("in") && "acm" == $(this).parents(".source").attr("name"))
	{
		inputconnect = 
		{
			url: "revisar",
			type: "POST",
		};
		inputdata =
		{
			getAbstract: true,
			source: $(this).parents(".source").attr("name"),
			rank: $(this).parents(".well").attr("rank"),
			iddb: $(this).parents(".source").attr("id"),
		};
		ajaxPages(inputconnect, inputdata).promise().done(function(response)
		{
			console.log(response);
			if (response.update)
			{
				objective.removeClass("empty");
				objective.empty().append("<p><b>Abstract: </b>" + response.abstract + "</p>");
			}
			else
			{
				objective.empty().append("<p><b>Error al obtener abstract. Intentelo más tarde...</b></p>");
			}
		});
	}
	objective.collapse("toggle");
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

function ajaxPagesAUX(inputconnect, inputdata)
{
	return $.ajax({
		url : inputconnect.url, // the endpoint
		type : inputconnect.type, // http method
		data : inputdata,// data sent with the post request
		// handle a successful response
		success : function(response)
		{
			console.log(inputdata.iddb);
			$("#" + inputdata.iddb).empty().append(response);
			return response;
		},
		// handle a non-successful response
		error : function(xhr,errmsg,err) {
		//$('#results').html("<div class='alert-box alert radius' data-alert>Oops! We have encountered an error: "+errmsg+" <a href='#' class='close'>&times;</a></div>"); // add the error to the dom
		console.log("ERROR: " + xhr.status + ": " + xhr.responseText); // provide a bit more info about the error to the console
		}
	});
};