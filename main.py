#!/usr/bin/python3

import socket
import json
from datetime import datetime, time
from time import sleep

on, off = time(17, 30), time(23, 59, 59)
color = 74, 0, 191
resolution = 8
minimum, maximum = 0, (2 ** resolution) - 1


def encode_color(red, green, blue, priority=700):
    if priority < 0:
        priority = 0
    for channel in (red, green, blue):
        if channel < minimum:
            channel = minimum
        elif channel > maximum:
            channel = maximum
    return json.dumps({
            'color': (red, green, blue),
            'command': 'color',
            'priority': priority
        }).encode('utf-8') + b'\n'


def clear_all():
    return json.dumps({'command': 'clearall'}).encode('utf-8') + b'\n'


def status():
    return json.dumps({'command': 'serverinfo'}).encode('utf-8') + b'\n'


def send(data, host='127.0.0.1'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, 19444))
    except:
        raise
    else:
        sock.send(data)
        return sock


def wait_for_response(sock):
    try:
        response = sock.recv(8192)
    except socket.error:
        return False
    else:
        return json.loads(response)


def process_response(decoded):
    keys = (decoded['info']['activeEffects'], decoded['info']['activeLedColor'])
    if (value is not None for value in keys):
        return True
    elif decoded['success']:
        return True
    else:
        return False


def run(host='127.0.0.1'):
    # active = process_response(wait_for_response(send(status(), host)))
    active = False
    while True:
        now = datetime.time(datetime.now())
        if (on < now < off) and not active:
            active = process_response(wait_for_response(send(encode_color(*color), host)))
        elif active and not (on < now < off):
            active = process_response(wait_for_response(send(clear_all(), host)))
        sleep(30)


def main():
    run()


if __name__ == '__main__':
    main()