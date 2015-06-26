import calendar
import datetime
import logging
import pickle
import sqlite3
from requests import HTTPError
import sys
import time

import get_todays_book
import pushover_notifications


logging.basicConfig(level=logging.INFO,
                    filename='packetpub_grabber.log',
                    format='%(asctime)s - %(levelname)s: %(message)s')


def get_tomorrow():
    return datetime.datetime.replace(datetime.datetime.utcnow() + datetime.timedelta(days=1),
                                     hour=0, minute=0, second=0)


def sleep_till_tomorrow():
    tomorrow = get_tomorrow()
    delta = tomorrow - datetime.datetime.utcnow()
    logging.info("Sleeping till {0}".format(tomorrow.ctime()))
    time.sleep(delta.seconds)
    return


def get_last_book():
    conn = sqlite3.connect('get_book.db')
    c = conn.cursor()
    try:
        sql_result = c.execute("SELECT * FROM last_book ORDER BY ID DESC LIMIT 1;")
        return sql_result.fetchone()
    except sqlite3.OperationalError:
        c.execute("CREATE TABLE last_book (id integer primary key autoincrement,nid integer, title text, date blob)")
        get_last_book()


def write_book_to_sql(book_data):
    with sqlite3.connect('get_book.db') as conn:
        c = conn.cursor()
        c.execute("INSERT INTO last_book (title, nid, date) VALUES (?, ?, ?)", (book_data['title'], book_data['nid'], pickle.dumps(datetime.datetime.utcnow().date())))
        conn.commit()
        logging.info("Grabbed {0} at {1}".format(book_data['title'], datetime.datetime.utcnow().ctime()))


def check_book_or_retry(book_sess, retrys=0):
    if retrys == 3:
        logging.error("Unbale to fetch book. We have reached max attempts. Bailing out.")
        try:
            pushover_notifications.make_pushover_call("Error getting today's book. Please check this out.")
        except HTTPError:
            logging.error("Pushover notificaion not working as expected.")
        sys.exit()
    my_last_book = get_todays_book.verify_todays_book(book_sess)
    if not my_last_book:
        logging.fatal("Email or Password appears invalid! Cannot continue. Exiting.")
        sys.exit()
    book_id, nid, title, date = get_last_book()
    if nid != int(my_last_book['nid']):
        logging.error("Book '{0}' with id {1} was not fetched on {2}. Trying again.".format(title, nid,
                                                                                            pickle.loads(date).ctime()))
        retrys += 1
        check_book_or_retry(book_sess, retrys=retrys)
    logging.info("Todays book '{0}' was verified".format(title))
    return True


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
    book_id, nid, title, date = last_book
    last_book_get = pickle.loads(date)
    # If todays book has already been grabbed
    if last_book_get == today_utc and todays_book['title'] == title:
        logging.info("Today's book \"{0}\", as already grabbed.".format(todays_book['title'].encode('utf-8', 'ignore'),))
        sleep_till_tomorrow()
    # If we have the date the same as the last grab, but the title is different, we try to grab the book
    elif last_book_get == today_utc and todays_book['title'] != title:
        logging.warning("We are seeing the same day, with differnt titles\n"
                        "Old Date:{0}\nNew Date:{1}".format(last_book_get, today_utc))
        book_get = get_todays_book.login_and_request_book(todays_book['url'])
        if not book_get:
            logging.log(logging.ERROR, "Error getting todays book!")
            return False
        write_book_to_sql(todays_book)
        check_book_or_retry(book_get)
        logging.info("{0} grabbed on {1}.".format(todays_book['title'], pickle.loads(date).ctime()))
        try:
            pushover_notifications.make_pushover_call("'{0}'. Enjoy!".format(todays_book['title']))
        except HTTPError:
            logging.error("Pushover notificaion not working as expected.")
        sleep_till_tomorrow()
    # This is where we should end up for everyday
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
        check_book_or_retry(book_get)
        logging.info("{0} grabbed on {1}.".format(todays_book['title'], pickle.loads(date).ctime()))
        try:
            pushover_notifications.make_pushover_call("'{0}'. Enjoy!".format(todays_book['title']))
        except HTTPError:
            logging.error("Pushover notificaion not working as expected.")
        sleep_till_tomorrow()


if __name__ == "__main__":
    check_last_book()