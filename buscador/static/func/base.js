// Only enable if the document has a long scroll bar
// Note the window height + offset
if ( ($(window).height() + 132) < $(document).height() ) {
    $('#top-link-block').removeClass('hidden').affix({
        // how far to scroll down before link "slides" into view
        offset: {top:132}
    });
}

$(document).ready(function(){

	$('[data-toggle="tooltip"]').tooltip();  
});



var kkeys = [], konami = "38,38,40,40,37,39,37,39,66,65";

$(document).keydown(function(e) {

  kkeys.push( e.keyCode );

  if ( kkeys.toString().indexOf( konami ) >= 0 ) {

    $(document).unbind('keydown',arguments.callee);
    
    // do something awesome
    $("body").addClass("konami");
  
  }

});