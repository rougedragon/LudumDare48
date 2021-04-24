from flask import Flask, session, redirect, render_template
import bs4
import requests
import random
import string
import json

app = Flask(__name__)
app.secret_key = "YOUR SECRET KEY HERE"

indexHtml = open("index.html", "r").read()

allLevels = []
with open('levels.json') as json_file:
    allLevels = json.load(json_file)


def getWikipage(wikipage, target):
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

    searchBar = soup.find(id='simpleSearch')
    searchBar.decompose()

    extraSoup = bs4.BeautifulSoup('<div id="mw-head" style="color:red;text-align:center;font-size:xx-large;">TARGET: ' + target + '<br>SCORE: 15</div>')
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
    return indexHtml


@app.route('/menu')
def menu():
    if not "info" in session:
        session["info"] = {
                "id": create_player_id(),
                "level": {},
                "levelNb": 0,
                "stepDone": 0
            }
        return redirect("/0")
    else:
        print(session["info"])
        session["info"] = {
            "id": session["info"]["id"],
            "level": session["info"]["level"],
            "stepDone": session["info"]["stepDone"],
            "levelNb": session["info"]["levelNb"] + 1,
        }
        print(session["info"]["levelNb"])
        return redirect("/" + str(session["info"]["levelNb"]))

@app.route('/<int:level>')
def level(level):
    level = level - 1
    session["info"] = {
        "id": session["info"]["id"],
        "level": allLevels[level],
        "stepDone": 0,
        "levelNb": session["info"]["levelNb"],
    }
    session["info"]["level"] = allLevels[level]
    return '<p>You start at ' + session["info"]["level"]["start"] + ' and you end at ' + session["info"]["level"]["end"] + '. You have a maximum of ' + str(session["info"]["level"]["step"]) + ' link to click.</p> <a href="/wiki/' + session["info"]["level"]["start"] + '">START</a>'


@app.route('/wiki/<wikipage>')
def wikipage(wikipage):
    if "info" in session and session["info"]["level"] != {}:
        session["info"] = {
            "id": session["info"]["id"],
            "level": session["info"]["level"],
            "levelNb": session["info"]["levelNb"],
            "stepDone": session["info"]["stepDone"] + 1
        }
        if session["info"]["level"]["end"] == wikipage:
            session["info"]["level"] = {}
            return 'You win. Click <a href="/menu">here</a> to start a new level'

        else:
            if session["info"]["stepDone"] > session["info"]["level"]["step"]:
                return 'You loose this level. You have made too many step. Go back to the <a href="/menu">menu</a> to start a new level'
            return getWikipage(wikipage, session["info"]["level"]["end"])
    else:
        return "You need to start a level before"


if __name__ == "__main__":
    app.run(debug=True, port=10001)
