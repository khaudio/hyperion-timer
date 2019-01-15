#!/usr/bin/python3

import json
import socket
import sys
from itertools import chain
from datetime import datetime, time
from time import sleep


defaults = {
    'color': (157, 124, 37),
    'start': (17, 30),
    'stop': (23, 59, 59),
    'host': '127.0.0.1',
    'port': 19444,
    'resolution': 8,
    'minimum': 0,
    'effect': None,
    'priority': 700,
    'clear': False
}


def limit(channel):
    if channel < minimum:
        channel = minimum
    elif channel > maximum:
        channel = maximum
    return channel


def encode_color(red, green, blue):
    global priority
    if priority < 0:
        priority = 0
    red, green, blue = (limit(channel) for channel in (red, green, blue))
    return json.dumps({
            'color': (red, green, blue),
            'command': 'color',
            'priority': priority
        }).encode('utf-8') + b'\n'


def encode_effect(effect):
    return json.dumps({
            'command': 'effect',
            'effect': {'name': effect},
            'priority': priority
        }).encode('utf-8') + b'\n'


def clear_all():
    return wait_for_response(send(
            json.dumps({'command': 'clearall'}).encode('utf-8') + b'\n'
        ))


def send(data):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((host, port))
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


def send_color(values):
    return wait_for_response(send(encode_color(*values)))


def send_effect(effect):
    return wait_for_response(send(encode_effect(effect)))


def run(color, force=False, sleepTime=4, **kwargs):
    on, off = time(*start), time(*stop)
    while True:
        now = datetime.time(datetime.now())
        if (on < now < off) or force:
            send_color(color) if not effect else send_effect(effect)
        elif not (on < now < off):
            send_color((minimum for i in range(3)), host)
        sleep(sleepTime)


def parse_args():
    kwargs, explicitKey = {}, None
    for arg in sys.argv[1:]:
        values = arg.split(',')
        times = arg.split(':')
        address = arg.split('.')
        if explicitKey:
            try:
                value = int(arg)
            except:
                value = arg
            kwargs[explicitKey] = value
            explicitKey = None
        if len(values) > 1:
            kwargs['color'] = tuple(int(digit) for digit in values)
        elif len(times) > 1:
            if 'start' not in kwargs:
                kwargs['start'] = tuple(int(digit) for digit in times)
            elif 'stop' not in kwargs:
                kwargs['stop'] = tuple(int(digit) for digit in times)
        elif len(address) == 4 and all(i.isdigit() for i in address):
            kwargs['host'] = arg
        elif arg.startswith('--'):
            explicitKey = arg.lstrip('--')
            if any(command in explicitKey for command in ('clear', 'clearall')):
                kwargs['clear'] = True
    return kwargs


if __name__ == '__main__':
    kwargs = parse_args()
    for key, default in defaults.items():
        globals()[key] = kwargs.pop(key) if key in kwargs else default
    if 'maximum' not in chain(kwargs, globals()):
        maximum = (2 ** resolution) - 1
    if clear:
        clear_all()
    else:
        run(color, **kwargs)
