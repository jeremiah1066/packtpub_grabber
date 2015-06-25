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
    config['pushover_token'] and config['pushover_user']
    push_over = True
except KeyError:
    push_over = False


def make_pushover_call(message, title="Today's Packet Pub book:"):
    if not push_over:
        return False
    data = {
        "token": config['pushover_token'],
        "user": config['pushover_user'],
        "device": config.get('pushover_device', None),
        "message": str(message),
        "title": title
    }
    pushover_push = requests.post("https://api.pushover.net/1/messages.json", data=data)
    pushover_push.raise_for_status()
    return True