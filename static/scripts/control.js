var audio_files_uploaded = 0;
var selected = 0;
var last_selected;
var parcel = `<div class='parcel'>
	<audio controls></audio>
        <div class='audio_file_name'></div>
	<textarea class='audio_textarea' rows='3'></textarea>
</div>`;

//When a file gets selected, use it as audio source
$("input[type='file']").change(function() {
	uploaded_file = document.getElementsByTagName('input')[0].files[0];

	instance = $(parcel).appendTo('#bottom');

	last_audio = instance.children('audio');
	last_audio.attr('src', URL.createObjectURL(uploaded_file));
	instance.children('.audio_file_name').text(uploaded_file['name']);

	selected = audio_files_uploaded;
	audio_files_uploaded += 1;
});

$(document).on('keydown', function ( e ) {
	leftArrow = 37;
	upArrow = 38;
	rightArrow = 39;
	downArrow = 40;
	if (e.which == rightArrow) {
		$('audio')[0].currentTime += 5;
		console.log('+5');
	} else if (e.which == leftArrow) {
		$('audio')[0].currentTime -= 5;
		console.log('-5');
	} else if (e.which == upArrow || e.which == downArrow) {
		if (last_selected) {
			last_selected.css("background-color", "white");
		}

		if (e.which == upArrow) {
			selected -= 1;
		} else {
			selected += 1;
		}
		last_selected = $("#bottom .parcel:nth-of-type("+selected+")").css("background-color", "red")
	}
});
/*
$( ".audio_textarea" ).blur(function() {
  alert( "Handler for .blur() called." );
});
*/
