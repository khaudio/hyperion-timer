#!/usr/bin/python3

import socket
import json
from datetime import datetime, time
from time import sleep

color = 157, 124, 37
on, off = time(17, 30), time(23, 59, 59)
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


def process_response(response):
    try:
        decoded = json.loads(response.decode())
    except json.decoder.JSONDecodeError:
        return False
    try:
        successful = decoded['success']
    except KeyError:
        return False
    else:
        return successful


def wait_for_response(sock):
    try:
        response = sock.recv(8192)
    except socket.error:
        return False
    else:
        return process_response(response)


def send_color(values, host):
    return wait_for_response(send(encode_color(*values), host))


def run(values, host='127.0.0.1', force=False, sleepTime=4):
    while True:
        now = datetime.time(datetime.now())
        if (on < now < off) or force:
            send_color(values, host)
        elif not (on < now < off):
            send_color((0, 0, 0), host)
        sleep(sleepTime)


if __name__ == '__main__':
    run(color)