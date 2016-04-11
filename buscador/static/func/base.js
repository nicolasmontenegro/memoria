$(document).ready(function(){
	$('[data-toggle="tooltip"]').tooltip();  
});

var kkeys = [], konami = "38,38,40,40,37,39,37,39,66,65";

$(document).keydown(function(e) {

  kkeys.push( e.keyCode );

  if ( kkeys.toString().indexOf( konami ) >= 0 ) {

    $(document).unbind('keydown',arguments.callee);
    
    // do something awesome
    //$("body").addClass("konami");
    alert("Roses are #ff0000\nViolets are #0000ff\nThe thesis are Null")
  }

});