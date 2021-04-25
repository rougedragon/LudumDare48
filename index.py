from flask import Flask, session, redirect, render_template, send_file
import bs4
import requests
import random
import string
import json
from datetime import datetime, timedelta

app = Flask(__name__, static_folder="static")
app.secret_key = "YOUR SECRET KEY HERE"

allLevels = []
with open('levels.json') as json_file:
    allLevels = json.load(json_file)


def getWikipage(wikipage, target, score, link_left, time_left):
    r = requests.get('https://en.wikipedia.org/wiki/' + wikipage)
    txt = r.text
    soup = bs4.BeautifulSoup(txt)

    # Removing the default steelsheet
    for link in soup.findAll("link"):
        if link["rel"] == ["stylesheet"]:
            link.decompose()

    

    # Adding the style sheet
    style = open("wikipediaStyle.css", "r").read()
    styleTag = soup.new_tag('style')
    styleTag.insert(0, style)
    soup.head.append(styleTag)

    link0 = bs4.BeautifulSoup('<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Gloria Hallelujah">')
    link1 = bs4.BeautifulSoup('<link rel="stylesheet" href="https://fonts.googleapis.com/css?family=Roboto Condensed">')
    link2 = bs4.BeautifulSoup('<link rel="stylesheet" href="static/stylesheet.css">')
    link3 = bs4.BeautifulSoup('<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.5.1/jquery.min.js"></script>')
    soup.head.append(link0)
    soup.head.append(link1)
    soup.head.append(link2)
    soup.head.append(link3)

    searchBar = soup.find(id='simpleSearch')
    searchBar.decompose()

    extraSoup = bs4.BeautifulSoup('<div id="mw-head" class="card card-normal font-normal" style="text-align: center;"><p class="font-normal">TARGET:</p> ' + target + '<br><p class="font-normal">LINK LEFT:</p> ' + str(link_left) + '<br>' + open("templates/timer.html", "r").read().replace("M:SS", time_left, 1) + '</div>')
    
    soup.find(id='mw-head').replace_with(extraSoup)
    #targetElt.insert(0, "TARGET: " + target)

    return str(soup)


def create_player_id():
    random_number = random.randrange(1, 20)
    letter_count, digit_count = random_number, 20 - random_number
    str1 = ''.join((random.choice(string.ascii_letters)
                    for x in range(letter_count)))
    str1 += ''.join((random.choice(string.digits) for x in range(digit_count)))

    sam_list = list(str1)  # it converts the string to list.
    # It uses a random.shuffle() function to shuffle the string.
    random.shuffle(sam_list)
    final_string = ''.join(sam_list)
    return final_string


@app.route('/')
def index():
    return render_template("index.html")

@app.route('/menu')
def menu():
    if not "info" in session:
        session["info"] = {
                "id": create_player_id(),
                "level": {},
                "levelNb": 0,
                "stepDone": 0,
                "score": 0
            }
        return redirect("/0")
    else:
        print(session["info"])
        session["info"] = {
            "id": session["info"]["id"],
            "level": session["info"]["level"],
            "stepDone": session["info"]["stepDone"],
            "levelNb": session["info"]["levelNb"] + 1,
            "score": session["info"]["score"]
        }
        print(session["info"]["levelNb"])
        return redirect("/" + str(session["info"]["levelNb"]))

@app.route('/<int:level>')
def level(level):
    if level >= len(allLevels):
        #The player win
        score = session["info"]["score"]
        session.clear()
        return render_template("winGame.html", score=score)
    levelToDo = allLevels[level]
    levelToDo["levelStarted"] = False
    session["info"] = {
        "id": session["info"]["id"],
        "level": allLevels[level],
        "stepDone": 0,
        "levelNb": session["info"]["levelNb"],
        "score": session["info"]["score"]
    }
    session["info"]["level"] = allLevels[level]
    return render_template("levelStart.html", start=session["info"]["level"]["start"], end=session["info"]["level"]["end"], maxStep=str(session["info"]["level"]["maxStep"]), minStep=str(session["info"]["level"]["minStep"]), href='/wiki/' + session["info"]["level"]["start"], level=level + 1)


@app.route('/wiki/<wikipage>')
def wikipage(wikipage):
    if "info" in session and session["info"]["level"] != {}:
        session["info"] = {
            "id": session["info"]["id"],
            "level": session["info"]["level"],
            "levelNb": session["info"]["levelNb"],
            "stepDone": session["info"]["stepDone"] + 1,
            "score": session["info"]["score"]
        }
        if session["info"]["level"]["start"] == wikipage and not session["info"]["level"]["levelStarted"]:
            #The player start a new round
            now = datetime.now()
            session["info"] = {
            "id": session["info"]["id"],
            "level": {
                "start":session["info"]["level"]["start"],
                "end":session["info"]["level"]["end"],
                "minStep":session["info"]["level"]["minStep"],
                "maxStep":session["info"]["level"]["maxStep"],
                "startTime": now,
                "levelStarted": True
            },
            "levelNb": session["info"]["levelNb"],
            "stepDone": session["info"]["stepDone"],
            "score": session["info"]["score"]
        }

        if session["info"]["level"]["end"] == wikipage:
            scoreToWin = abs(session["info"]["stepDone"] - session["info"]["level"]["maxStep"])
            session["info"] = {
                "id": session["info"]["id"],
                "level": session["info"]["level"],
                "levelNb": session["info"]["levelNb"],
                "stepDone": session["info"]["stepDone"],
                "score": session["info"]["score"] + scoreToWin
            }
            session["info"]["level"] = {}
            return render_template("win.html", scoreEarn=scoreToWin, score=session["info"]["score"])

        else:
            if session["info"]["stepDone"] > session["info"]["level"]["maxStep"] or session["info"]["level"]["startTime"] + timedelta(minutes = 1, seconds=58) <= datetime.now():
                session.clear()
                return render_template("gameover.html")
            timeTimer = (session["info"]["level"]["startTime"] + timedelta(minutes = 2)) - datetime.now()
            return getWikipage(wikipage, session["info"]["level"]["end"], session["info"]["score"], (session["info"]["level"]["maxStep"] - session["info"]["stepDone"]) + 1, str(timeTimer)[3:7])
    else:
        return "This is an error message: You need to start a level before"


if __name__ == "__main__":
    app.run(debug=True, port=10001)
