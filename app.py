import os
import csv
from flask import Flask, request, render_template, redirect, url_for, send_file
from crontab import CronTab
from model.sentiment import *
from stream import *
from config import *

# set Flask
app = Flask(__name__)

# set CNN model
global graph
graph = tf.get_default_graph()
vocab, tokenizer, max_length, model = load_variabels()
# text = 'terima kasih pak!'
# percent, conclusi = predict_sentiment(text, vocab, tokenizer,max_length, model)
# print(percent, conclusi)

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
            saveDirectory = dir_aplikasi + "/" +raw_file_directory
            begin_stream(duration, saveDirectory)

            # activate crontab 
            cron.remove_all()
            cron.write()
            duration = str(duration)
            job = cron.new(command= dir_python + ' ' + dir_aplikasi + '/streamArg.py ' + duration + ' ' + dir_aplikasi + "/" +raw_file_directory)
            duration = int(duration)
            job.minute.every(duration)
            cron.write()
    
    return redirect(url_for('index'))

# Download file route
@app.route("/download/<directory>/<filename>")
def download(directory, filename):
    if(directory == "raw"):
        return(send_file(dir_aplikasi + "/" + raw_file_directory + "/" +filename))
    else:
        return(send_file(dir_aplikasi + "/" + predict_file_directory + "/" +filename))

# Predict route using CNN Model
@app.route("/predict/<filename>")
def predict(filename):
    input_file = open(raw_file_directory + "/" + filename)
    csv_head = ['text', 'conclusi', 'percent']
    csv_body = []
    for line in input_file:
        with graph.as_default():
            percent, conclusion = predict_sentiment(line, vocab, tokenizer, max_length, model)
        csv_line = {}
        csv_line["text"] = line
        csv_line["conclusi"] = conclusion
        csv_line["percent"] = str(percent * 100)
        csv_body.append(csv_line)
    
    input_file.close()
    csv_name = filename + ".csv"
    try:
        with open(predict_file_directory + "/" + csv_name, 'w') as csv_name:
            writer = csv.DictWriter(csv_name, fieldnames=csv_head)
            writer.writeheader()
            for data in csv_body:
                writer.writerow(data)
    except IOError:
            print("I/O error")
    return redirect(url_for('index'))
