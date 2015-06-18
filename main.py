# -*- coding: utf-8 -*-
import calendar
import datetime
import logging
import pickle
import sqlite3
import os
import sys
import time

import get_todays_book



logging.basicConfig(level=logging.INFO,
                    filename='packetpub_grabber.log',
                    format='%(asctime)s - %(levelname)s: %(message)s')


def get_tomorrow():
    return datetime.datetime.replace(datetime.datetime.utcnow() + datetime.timedelta(days=1),
                                                hour=0, minute=0, second=0)


def sleep_till_tomorrow():
    tomorrow = get_tomorrow()
    delta = tomorrow - datetime.datetime.utcnow()
    time.sleep(delta.seconds)
    return


def get_last_book():
    conn = sqlite3.connect('get_book.db')
    c = conn.cursor()
    try:
        sql_result = c.execute("SELECT * FROM last_book ORDER BY ID DESC LIMIT 1;")
        return sql_result.fetchone()
    except sqlite3.OperationalError:
        c.execute("CREATE TABLE last_book (id integer primary key autoincrement, title text, date blob)")
        get_last_book()


def write_book_to_sql(book_data):
    with sqlite3.connect('get_book.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO last_book (title, date) VALUES (?, ?)", (book_data['title'], pickle.dumps(datetime.datetime.utcnow().date())))
        conn.commit()
        logging.info("Grabbed {0} at {1}".format(book_data['title'], datetime.datetime.utcnow().ctime()))


def check_last_book():
    last_book = get_last_book()
    todays_book = get_todays_book.get_todays_title()

    if not last_book:
        book_get = get_todays_book.login_and_request_book(todays_book['url'])
        if not book_get:
            logging.log(logging.ERROR, "Error getting todays book!")
            return False
        write_book_to_sql(todays_book)
        sleep_till_tomorrow()

    today_utc = datetime.datetime.utcnow().date()
    id, title, date = last_book
    last_book_get = pickle.loads(date)
    if last_book_get == today_utc and todays_book['title'] == title:
        logging.info("Today's book \"{0}\", as already grabbed. "
                     "Sleeping till {1}".format(todays_book['title'].encode('utf-8', 'ignore'),
                     str(get_tomorrow().ctime())))
        sleep_till_tomorrow()
    elif last_book_get == today_utc and todays_book['title'] != title:
        book_get = get_todays_book.login_and_request_book(todays_book['url'])
        if not book_get:
            logging.log(logging.ERROR, "Error getting todays book!")
            return False
        write_book_to_sql(todays_book)
        sleep_till_tomorrow()
    else:
        try:
            book_get = get_todays_book.login_and_request_book(todays_book['url'])
        except get_todays_book.login_invalid:
            logging.fatal("Email or Password appears invalid! Cannot continue. Exiting.")
            sys.exit()
        if not book_get:
            logging.error("Error getting todays book!")
            return False
        write_book_to_sql(todays_book)
        sleep_till_tomorrow()

if __name__ == "__main__":
    check_last_book()




