var foon;

var audio_files_uploaded = 0;
var selected_num = 0;
var selected;
var key;
var value;
var parcel = `<div class='parcel'>
	<audio controls></audio>
        <div class='audio_file_name'></div>
	<textarea class='audio_textarea' rows='3' onblur="blur()"></textarea>
</div>`;

$(document).on('blur', '.audio_textarea', function(){
	save_state(this);
});

function save_state(state) {
	console.log("Handler for .blur() has been called.");
	val = $(state).val();
	key = $(state).prev().text();
	
	console.log('key from' + key);
	key = key.replace(/ /gi, "_");
	console.log('to ' + key);

	if(typeof(Storage) !== "undefined") {
		localStorage.setItem(key, val);
	}
}

//When a file gets selected, use it as audio source
$("input[type='file']").change(function() {
	uploaded_file = document.getElementsByTagName('input')[0].files[0];

	instance = $(parcel).appendTo('#bottom');

	prev_audio = instance.children('audio');
	prev_audio.attr('src', URL.createObjectURL(uploaded_file));
	instance.children('.audio_file_name').text(uploaded_file['name']);
	prev_selected = instance;

	key = uploaded_file['name'];
	console.log('key from' + key);
	key = key.replace(/ /gi, "_");
	console.log('to ' + key);
	instance.children('.audio_textarea').val(localStorage.getItem(key))

	selected = instance;
	audio_files_uploaded += 1;
});

$(document).on('keydown', function (e) {
	leftArrow = 37;
	upArrow = 38;
	rightArrow = 39;
	downArrow = 40;

	if (e.which == upArrow || e.which == downArrow) {
		$.each($('audio'), function () {
			this.pause();
		});
		$(".parcel").css("background-color", "white");

		if (e.which == upArrow) {
			if (selected_num <= 0) {
				console.log(selected_num + " <= 0");
				return;
			}
			console.log(selected_num + " -= 1");
			selected_num -= 1;
		} else {
			if (selected_num >= audio_files_uploaded) {
				console.log(selected_num + " >= audio_files_uploaded");
				return;
			}
			console.log(selected_num + " += 1");
			selected_num += 1;
		}

		temp_selected = $("#bottom .parcel:nth-of-type("+selected_num+")");

		console.log(temp_selected);

		selected = temp_selected;
		selected.css("background-color", "red");
		selected.children('audio')[0].play();
   		selected.children('textarea').focus();
	} else if(e.ctrlKey == false) {
		save_state($(':focus'));
		return;
	} else if (e.which == rightArrow) {
		selected.children('audio')[0].currentTime += 5;
		console.log('+5 to ' + prev_selected.children('.audio_file_name').text());
	} else if (e.which == leftArrow) {
		selected.children('audio')[0].currentTime -= 5;
		console.log('-5 to ' + prev_selected.children('.audio_file_name').text());
	}
});
