from flask import Flask
import bs4
import requests
import random
import string

app = Flask(__name__)

indexHtml = open("index.html", "r").read()
menuHtml = open("menu.html", "r").read()

def getWikipage(wikipage):
    print(wikipage)
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
    
    return str(soup)

@app.route('/')
def index():
    return indexHtml

@app.route('/menu')
def menu():
    return menuHtml

@app.route('/<int:level>')
def level(level):
    return "this is the level number " + str(level)

@app.route('/wiki/<wikipage>')
def wikipage(wikipage):
    return getWikipage(wikipage)

if __name__ == "__main__":
    app.run(debug=True)