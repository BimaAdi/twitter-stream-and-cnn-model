import os
from flask import Flask, request, render_template, redirect, url_for, send_file
from crontab import CronTab
from stream import *
from config import *

app = Flask(__name__)

# Set crontab
cron = CronTab(user=curr_username)
cron.remove_all()
cron.write()

# index route
@app.route("/")
def index():
    raw_file = os.listdir(raw_file_directory)
    predict_file = os.listdir(predict_file_directory)
    return render_template('index.html', raw_file=raw_file, predict_file=predict_file)

# twitter stream route
@app.route("/start_stream", methods=["GET", "POST"])
def start_stream():
    params = request.form
    if(params == None):
        params = flask.request.args
    if(params != None):
        if(params.get("menit") != ""):
            # activate stream 
            duration = int(params.get("menit"))
            saveDirectory = dir_aplikasi + raw_file_directory
            begin_stream(duration, saveDirectory)

            # activate crontab 
            cron.remove_all()
            cron.write()
            duration = str(duration)
            job = cron.new(command= dir_python + ' ' + dir_aplikasi + '/streamArg.py ' + duration + ' ' + dir_aplikasi + raw_file_directory)
            duration = int(duration)
            job.minute.every(duration)
            cron.write()
    
    return redirect(url_for('index'))

# Download file route
@app.route("/download/<filename>")
def download(filename):
    print(filename)
    # return redirect(url_for('index'))
    return(send_file(dir_aplikasi + raw_file_directory + filename))

@app.route("/predict/<filename>")
def predict(filename):
    return redirect(url_for('index'))
