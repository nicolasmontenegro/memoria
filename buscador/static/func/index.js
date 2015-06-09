$(document).ready(function(){

	$('#searchButton').click(function (event) 
	{
		if ($('#searchText').val().length > 0 )
			$(location).attr('href', 'revisar?query='+$('#searchText').val());
			/*$.get( 
				"revisar", 
				{query: $('#searchText').val()}
			);*/
		else
			alert("no hay na!");
	});
});