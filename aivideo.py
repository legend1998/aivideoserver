from flask import Flask, request, jsonify, Response, send_file
from threading import Thread
import csv
import random
import requests
import subprocess
import requests
import json
import re
import os
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


def generateId():
    randoms = "aAbBcCDdEeFfGgHhIiJjKkLlMmNnOoPp1234567890"
    id = ""
    for i in range(16):
        id += random.choice(randoms)
    return id


def generateAiText(brand, query):
    colors = [
        "#" + "".join([random.choice("0123456789ABCDEF") for j in range(6)])
        for i in range(10)
    ]
    print(colors)
    # colors = [
    #     "#fa0a7a",
    #     "#fa64be",
    #     "#fa647d",
    #     "#7d64fa",
    #     "#64cafa",
    #     "#64fab9",
    #     "#64fa7d",
    #     "#a5fa64",
    #     "#a5fa64",
    #     "#a5fa64",
    # ]
    docs = requests.post(
        "https://openai-zscu3untuq-as.a.run.app/generate-text",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "prompt": "my brand is {}. {}. write title and 5 one liner of 10 words".format(
                brand, query
            ),
        },
    )
    docs = json.loads(docs.text)
    response = docs["data"]
    with open("readme.txt", "w") as f:
        f.write(response)
    lineBreak = 30
    clearText = []
    texts = response.split(".")

    title = texts[0]
    texts = texts[1:]

    title = title.replace("Title", "")
    title = re.sub("[^a-zA-Z ]", "", title)
    title = re.sub(" +", " ", title)
    title = title.strip()
    temptitle = title.split(" ")

    if len(temptitle) > 5:
        temptitle.insert(5, "\f")
        title = " ".join(temptitle)
    title = "drawtext=fontfile=d:/WorkingProjects/watermarkJob/roboto.ttf:enable='between(t,0\,3)':text='{}':fontcolor=white:fontsize=24:x=(main_w-text_w)/2:y=(main_h-text_h)/2:box=1:boxborderw=12:boxcolor={}".format(
        title, colors[0]
    )
    colors = colors[1:]

    with open("readme.txt", "w") as f:
        f.write(title)

    for sentence in texts:
        if len(clearText) > 4:
            break
        sentence = re.sub("[^a-zA-Z ]", "", sentence)
        sentence = sentence.strip()

        lines = 1
        while len(sentence) > (lineBreak * lines):
            nextspace = lineBreak * lines
            print("finding next space")
            abort = False
            while sentence[nextspace] != " ":
                try:
                    sentence[nextspace + 1]
                    nextspace += 1
                except IndexError:
                    abort = True
                    break
            if abort:
                break
            sentence = sentence[:nextspace] + "\f" + sentence[nextspace:]
            lines += 1

        if len(sentence) > 3:
            clearText.append(sentence)

    texts = clearText

    drawtext = []
    height = 0
    time = 2
    counter = 0

    drawtext.append(title)
    for option in texts:
        height += 120
        time += 2
        opt = "drawtext=fontfile=d:/WorkingProjects/watermarkJob/roboto.ttf:enable='between(t,{}\,20)':text='{}':fontcolor=white:fontsize=22:x=(main_w-text_w)/2:y={}:box=1:boxborderw=8:boxcolor={}".format(
            time, option, height, colors[counter]
        )
        drawtext.append(opt)
        counter += 1

    return ",".join(drawtext)


def getVideoName(videoType):
    choice = random.choice(range(1, 3))
    return "vids/" + videoType + str(choice) + ".mp4"


def getAudioName(audioType):
    choice = random.choice(range(1, 6))
    return "bgmc/soothing" + str(choice) + ".mp3"


def clearDesk(currentId):
    os.remove(currentId + ".mp4")


def mergeAll(listOfOptions, videoName, audioName, projectId):
    p = subprocess.Popen(
        [
            "ffmpeg",
            "-i",
            videoName,
            "-i",
            audioName,
            "-c:v",
            "copy",
            "-c:a",
            "aac",
            "-t",
            "20",
            projectId + ".mp4",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    stdout, stderr = p.communicate(input="y\n".encode())
    p = subprocess.Popen(
        [
            "ffmpeg",
            "-i",
            projectId + ".mp4",
            "-vf",
            listOfOptions,
            "output/" + projectId + "output.mp4",
        ],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )
    stdout, stderr = p.communicate(input="y\n".encode())
    p.kill()


def generateVideo(brand, query, videoType, audioType, projectId):
    print("------GETTING RESPONSE FROM AI--------")
    listOfOptions = generateAiText(brand, query)
    print("------GENERATED--------")
    print("------SELECTING VIDEO--------")
    videoName = getVideoName(videoType)
    print("------SELECTED--------")
    print("------SELECTING AUDIO--------")
    audioName = getAudioName(audioType)
    print("------SELECTED--------")
    print("------FINALIZING--------")
    mergeAll(listOfOptions, videoName, audioName, projectId)
    clearDesk(projectId)
    print("------DONE--------")
    return projectId


@app.route("/generateAiVideo", methods=["POST"])
def handle_post():
    try:
        if request.method == "POST":
            print("data laoding")
            print(request.headers.get("Content-Type"))
            print(request.is_json)
            data = request.get_json(True)
            print(data)
            query = data.get("query")
            videoType = data.get("videoType")
            audioType = data.get("audioType")
            brand = data.get("brand")
            projectId = data.get("projectId")
            print(query, videoType, audioType, brand)
            currenttaskId = generateVideo(brand, query, videoType, audioType, projectId)
            print("----------THIS IS NOT REACHING HERE I THINK----------------")
            return jsonify({"success": True, "id": currenttaskId})
        else:
            print("----------THIS IS ALSO NOT REACHING HERE I THINK----------------")
            return Response(
                jsonify({"success": False, "data": "invalid Request method"}),
                status=403,
                mimetype="application/json",
            )
    except:
        print("----------THIS CAN'T BE AN ERROR----------------")
        return Response(
            jsonify({"success": False, "data": "some error occured"}),
            status=500,
            mimetype="application/json",
        )


@app.route("/")
def hello_world():
    return "HEllo"


@app.route("/task/<id>", methods=["GET"])
def getVideoFile(id):
    print(id)
    return send_file("output/" + id + "output.mp4")


@app.route("/deleteProject/<id>", methods=["GET"])
def deleteProject(id):
    print(id)
    os.remove("output/" + id + ".mp4")
    return jsonify({"success": True})


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
