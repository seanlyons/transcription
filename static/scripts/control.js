//When a file gets selected, use it as audio source
$("input[type='file']").change(function() {
    $('audio').attr('src', URL.createObjectURL(document.getElementsByTagName('input')[0].files[0]));
});

$(document).on('keydown', function ( e ) {
	// You may replace `c` with whatever key you want
	rightArrow = 39;
	leftArrow = 37;
	console.log(e.which +'; '+ String.fromCharCode(e.which).toLowerCase() +'; ' + rightArrow);
	if (e.which == rightArrow) {
		$('audio')[0].currentTime += 5;
		console.log('+5');
	} else if (e.which == leftArrow) {
		$('audio')[0].currentTime -= 5;
		console.log('-5');
	}
});
