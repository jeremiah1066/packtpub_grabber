import BeautifulSoup
import bs4
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


def create_session():
    s = requests.Session()
    s.headers.update({
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Encoding":"gzip, deflate, sdch",
        "Accept-Language": "en-US,en;q=0.8",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36",
        "content-type": "application/x-www-form-urlencoded"
    })


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
        return dict(title=todays_title, epoch=int(countdown_to), url=get_url, nid=get_url.split('/')[-2:-1][0])
    else:
        raise Exception("Unable to fetch todays title")


def login_and_request_book(get_url):
    sess = requests.Session()
    payload = {
        "email": config['email'],
        "password": config['password'],
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
        return sess
    else:
        return False


def verify_todays_book(prev_session):
    my_ebooks = prev_session.get('https://www.packtpub.com/account/my-ebooks', headers=headers, allow_redirects=False)
    #TODO fix this
    if my_ebooks.status_code == 302:
        return False
    soup = bs4.BeautifulSoup(my_ebooks.text)
    book_list = soup.find_all("div", class_="product-line unseen")
    last_book = book_list[0]
    nid = last_book.get('nid')
    title = last_book.get('title')
    return {'nid': nid, 'title': title}





