import shlex
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from joblib import Parallel, delayed
from functools import cmp_to_key

chrome_options = Options()
chrome_options.add_argument('--headless')
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
chrome_options.add_argument('log-level=3')
chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
chrome_options.add_argument('--no-sandbox')
chrome_options.add_argument('--ignore-certificate-errors')
chrome_options.add_argument('--disable-dev-shm-usage')

class Player:
    def __init__(self, id64, name, rate):
        self.kpd = None
        self.id64 = id64
        self.name = name
        self.rate = rate

    def get_kpd(self):
        driver = webdriver.Chrome(options=chrome_options)
        url = "https://csgostats.gg/player/" + self.id64
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        kpd_div = soup.find(id="kpd")
        if kpd_div != None:
            self.kpd = float(kpd_div.find('span').get_text())
        else:
            self.kpd = "Unknown"

        driver.close()

def get_states(p):
    p.get_kpd()
    return p

def compare(p1, p2):
    if p1.kpd == "Unknown":
        return -1
    if p2.kpd == "Unknown":
        return 1
    if p1.kpd < p2.kpd:
        return 1
    return -1

print("Waiting for input...")
players = []
while True:
    try:
        line = input()
    except EOFError:
        break
    fields = shlex.split(line)
    if fields[0] == "#end":
        break
    if fields[1] == "userid":
        continue
    if fields[2] != "BOT":
        a,b,userid,name,steam32id,connected,ping,loss,state,rate = fields
        X,Y,Z = steam32id.split(":")
        id64 = int(Z) * 2
        id64 = id64 + 76561197960265728
        id64 = id64 + int(Y)
        players.append(Player(str(id64), name, rate))

players = Parallel(n_jobs=-1)(delayed(get_states)(p) for p in players)
players.sort(key=cmp_to_key(compare))
for p in players:
    if p.kpd == "Unknown":
        print(p.kpd, p.name)
    else:
        print('{0:.2f}'.format(p.kpd), p.name)
