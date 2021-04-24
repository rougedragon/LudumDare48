from selenium import webdriver
import time
import random
import json
from urllib.parse import unquote

driver = webdriver.Chrome(executable_path="chromedriver.exe")
url = 'https://en.wikipedia.org/wiki/Special:Random'

levels = []

with open('betaLevels.json') as json_file:
    levels = json.load(json_file)


for _ in range(5):
    step = random.randint(2, 3)
    canceled = False
    driver.get(url)
    time.sleep(3)
    current_url = unquote(driver.current_url)
    start = current_url[30:]
    for i in range(step):
        current_url = unquote(driver.current_url)
        while unquote(driver.current_url) == current_url:
            time.sleep(1)
        if unquote(driver.current_url) == "https://en.wikipedia.org/wiki/Main_Page":
            canceled = True
            break
    if not canceled:
        end = unquote(driver.current_url)[30:]
        level = {
            "start": start,
            "end": end,
            "step": step
        }
        print(level)
        levels.append(level)

with open('betaLevels.json', 'w') as outfile:
    json.dump(levels, outfile)