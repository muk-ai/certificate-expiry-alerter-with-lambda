import os
import datetime
import ssl
import socket
import json
import logging
import urllib.request

'''
Please set the following environment variables

SLACK_URL: incomming webhook url
FQDN_LIST: comma-separated values
DAYS: threshold
'''

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def ssl_expiry_datetime(host, port=443):
    ssl_date_fmt = r'%b %d %H:%M:%S %Y %Z'
    context = ssl.create_default_context()
    conn = context.wrap_socket(
        socket.socket(socket.AF_INET),
        server_hostname=host,
    )
    conn.settimeout(5)
    res = None
    try:
        conn.connect((host, port))
        ssl_info = conn.getpeercert()
        res = datetime.datetime.strptime(ssl_info['notAfter'], ssl_date_fmt)
    except socket.error:
        logger.error('socket error')

    return res

def post_slack(fqdn, expiry_date, remaining_days):
    url = os.environ['SLACK_URL']
    slack_message = {
        'icon_emoji': ':eye-in-speech-bubble:',
        'text': '証明書の期限が迫っていますが自動更新が失敗しているようです',
        'attachments': [{
            'fallback': 'fallback text',
            'fields': [
                {
                    'title': 'FQDN',
                    'value': fqdn,
                    'short': True
                },
                {
                    'title': 'expiry date',
                    'value': expiry_date.strftime('%Y-%m-%d'),
                    'short': True
                },
                {
                    'title': '残り',
                    'value': '{}日'.format(remaining_days),
                    'short': True
                },
            ],
            'color': 'warning'
        }]
    }
    data = "payload=" + json.dumps(slack_message)
    request = urllib.request.Request(url, data.encode('utf-8'))
    try:
        with urllib.request.urlopen(request) as response:
            _response_body = response.read().decode('utf-8')
    except urllib.request.HTTPError as e:
        logger.error('Request failed: {} {}'.format(e.code, e.reason))
    except urllib.request.URLError as e:
        logger.error('Server connection failed: {}'.format(e.reason))

def lambda_handler(event, context):
    fqdn_list = os.environ['FQDN_LIST'].split(',')
    threshold_days = int(os.environ['DAYS'])
    target_list = []
    for fqdn in fqdn_list:
        expiry_date = ssl_expiry_datetime(fqdn)
        if expiry_date is None:
            continue
        delta = expiry_date - datetime.datetime.now()
        if delta.days < threshold_days:
            target_list.append((fqdn, expiry_date, delta.days))

    for fqdn, expiry_date, remaining_days  in target_list:
        post_slack(fqdn, expiry_date, remaining_days)
