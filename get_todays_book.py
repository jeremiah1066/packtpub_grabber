import BeautifulSoup
import json
import requests
import sys

try:
    with open('config.json', 'r') as config_file:
        config = json.load(config_file)
except IOError:
    print "'config.json' does not appear to exist! Exiting"
    sys.exit()
try:
    config['email'] and config['password']
except KeyError:
    print "'config.json' Does not appear to have the proper items. Exiting"
    sys.exit()


class login_invalid(Exception):
    pass

headers = {
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
"Accept-Encoding":"gzip, deflate, sdch",
"Accept-Language": "en-US,en;q=0.8",
"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36",
"content-type": "application/x-www-form-urlencoded"
}


def get_todays_title():
    pckpub = requests.get("https://www.packtpub.com/packt/offers/free-learning", headers=headers)
    if pckpub.status_code == 200:
        soup = BeautifulSoup.BeautifulSoup(pckpub.text)
        todays_title = soup.find("div", {"class": "dotd-title"}).text
        countdown_to = soup.find("span", {"class": "packt-js-countdown"}).get('data-countdown-to')
        get_url = soup.find("a", {"class": "twelve-days-claim"}).get('href')
        return dict(title=todays_title, epoch=int(countdown_to), url=get_url)
    else:
        raise Exception("Unable to fetch todays title")


def login_and_request_book(get_url):
    sess = requests.Session()
    payload = {
        "email": "spam1066spam1066@yahoo.com",#config['email'],
        "password": "buddy17",#config['password'],
        "op": "Login",
        "form_id": "packt_user_login_form",
        "form_build_id": ""
    }
    r = sess.post("https://www.packtpub.com/packt/offers/free-learning",
                      data=payload, headers=headers)
    soup = BeautifulSoup.BeautifulSoup(r.text)
    if soup.find("div", {"class": "messages error"}):
            raise login_invalid("Login Issue. Username or password incorrect.")
    get_url = soup.find("a", {"class": "twelve-days-claim"}).get('href')
    get_book_url = "https://www.packtpub.com" + get_url
    get_da_book = sess.get(get_book_url, headers=headers, allow_redirects=False)
    if get_da_book.status_code == 302:
        return True
    else:
        return False




