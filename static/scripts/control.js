var foon;

var distinct_files_uploaded = 0;
var selected_num = 0;
var selected;
var key;
var value;
var parcel = `<div class='parcel' hidden>
	<audio controls></audio>
	<div class='img_div'>
		<img/>
	</div>
	<div class='file_name'></div>
	<textarea class='file_textarea'></textarea>
</div>`;

$(document).on('blur', '.file_textarea', function(){
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

	instance = $(parcel).appendTo('#bottom').show();

	key = uploaded_file['name'];
	console.log('key from' + key);
	key = key.replace(/ /gi, "_");
	console.log('to ' + key);
	instance.children('.file_textarea').val(localStorage.getItem(key))

	var file_type = uploaded_file["type"];
	var image_types = ["image/gif", "image/jpeg", "image/png"];
	//if ($.inArray(file_type, image_types) < 0) {
	if (file_type == "image/gif"
	|| file_type == "image/jpeg"
	|| file_type == "image/png") {
		console.log('image: ' + file_type);
		/* this is an image */
		prev_audio = instance.children('audio');
		prev_audio.hide();
		
		instance.children().children('img').attr('src', URL.createObjectURL(uploaded_file));
		instance.children('.file_name').text(uploaded_file['name']);
		prev_selected = instance;
	} else {
		/* this is hopefully audio */
		console.log('audio: "' + file_type + '"');
		prev_img = instance.children('img');
		prev_img.hide();
		prev_audio = instance.children('audio');
		prev_audio.attr('src', URL.createObjectURL(uploaded_file));
		instance.children('.file_name').text(uploaded_file['name']);
		prev_selected = instance;
	}

	selected = instance;
	distinct_files_uploaded += 1;
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
			if (selected_num >= distinct_files_uploaded) {
				console.log(selected_num + " >= distinct_files_uploaded");
				return;
			}
			console.log(selected_num + " += 1");
			selected_num += 1;
		}

		temp_selected = $("#bottom .parcel:nth-of-type("+selected_num+")");

		console.log(temp_selected);

		selected = temp_selected;
		selected.css("background-color", "grey");
		if ($('audio').is(":hidden") == false) {
			selected.children('audio')[0].play();
   			selected.children('textarea').focus();
		}
	} else if(e.ctrlKey == false) {
		save_state($(':focus'));
		return;
	} else if (e.which == rightArrow) {
		if ($('audio').is(":hidden")) {
			//scroll down
			img_div = selected.children('.img_div');
			img_div.scrollTop(img_div.scrollTop() + 100);
		} else {
			selected.children('audio')[0].currentTime += 5;
			console.log('+5 to ' + prev_selected.children('.file_name').text());
		}
	} else if (e.which == leftArrow) {
		if ($('audio').is(":hidden")) {
			//scroll up
			img_div = selected.children('.img_div');
			img_div.scrollTop(img_div.scrollTop() - 100);
		} else {
			selected.children('audio')[0].currentTime -= 5;
			console.log('-5 to ' + prev_selected.children('.file_name').text());
		}
	}
});
