from flask import Flask
from flask import render_template
from flask import request
from flask import send_from_directory

app = Flask(__name__)

''' v.0.1
if you upload a new file, spawn a new audioplayer+textarea at the bottom, and bind the filename to it.
up/down keybinds allow you to iterate through the audioplayers vertically.
left/right keybinds allow you to iterate through that audioplayer's +/-5s.
all textareas have a losefocus event which saves their contents to localstorage, using the bound filename as the key.
if you upload a file whose filename exists in localstorage, load the previous contents from localstorage.
add a button next to the uploader which copies the catted contents of all textareas into the OS buffer. '''

@app.route('/')
def transcribe():
    return render_template('transcribe.html')


