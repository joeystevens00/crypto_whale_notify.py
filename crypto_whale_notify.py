import requests
import time
import redis
import json
import notify2
import os
dirname = os.path.dirname(__file__)

try:
    config_file = open(os.path.join(dirname,'config.json'), 'r')
    config = json.load(config_file)
    config_file.close()
except FileNotFoundError:
    config = {'api_key':os.getenv('WHALE_ALERT_API_KEY')}

# initialise the d-bus connection
notify2.init("Whale Alert")
ICON_PATH = os.path.join(dirname, 'whale.png')
# create Notification object
n = notify2.Notification(None, icon = ICON_PATH)
# set urgency level
n.set_urgency(notify2.URGENCY_NORMAL)

# set timeout for a notification
n.set_timeout(10000)

def popupAlert(s):
    # update notification data for Notification object
    n.update('Whale Alert', s)

    # show notification on screen
    n.show()

if not config.get("redis"):
    config["redis"] = {}
redis_db = config["redis"].get("db") or 0
redis_host = config["redis"].get("host") or "localhost"
redis_port = config["redis"].get('port') or 6379
r = redis.Redis(host=redis_host, port=redis_port, db=redis_db)

API_KEY = config['api_key']
ENDPOINT = 'https://api.whale-alert.io/v1/'


# attribution_string(transaction, direction)
# extracts owner info from transaction and returns as string
def attribution_string(transaction, direction='from'):
    owner = transaction[direction]
    attr_str = ""
    if owner['owner_type'] == "unknown":
        attr_str += "unknown wallet"
    else:
        attr_str += owner['owner'] + " (" + owner['owner_type'] + ")"
    return attr_str

def format_number(number, prefix='$'):
    return prefix+'{:,.2f}'.format(float(number))

# notify(transaction)
# notifies and prints to STDOUT the transaction
def notify(transaction):
    alert_msg_components = [
        format_number(transaction['amount'], prefix=''),
        transaction['symbol'].upper(),
        "(" + format_number(transaction['amount_usd']) + ")",
        transaction['transaction_type'],
        "from",
        attribution_string(transaction),
        "to",
        attribution_string(transaction, direction='to')
    ]
    alert_msg = " ".join(alert_msg_components)
    popupAlert(alert_msg)
    print (alert_msg)

current_time = int(time.time())
seek_seconds = int(config.get('seek_seconds') or 1500)
min_value = int(config.get('min_dollars') or 500000)
notify_delay = int(config.get('notify_delay') or 15)
transaction_args = {'api_key': API_KEY, "min_value": min_value, "start":current_time-seek_seconds}
res = requests.get(ENDPOINT + "transactions" , params=transaction_args)
response = res.json()

# If have transactions
if response.get('count'):
    for transaction in response['transactions']:
        notification_key = 'whalealert:' + transaction['id']
        notification_history = r.get(notification_key)
        # If transaction is new
        if not notification_history:
            r.set(notification_key, json.dumps(transaction))
            notify(transaction)
            r.expire(notification_key, seek_seconds+1)
            time.sleep(notify_delay)
