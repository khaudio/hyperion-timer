#!/usr/bin/python3

from datetime import datetime, time
from time import sleep
import itertools
import json
import socket
import sys


defaults = {
    'colors': [(157, 124, 37)],
    'start': (17, 30),
    'stop': (23, 59, 59),
    'hosts': {'127.0.0.1:19444'},
    'port': 19444,
    'resolution': 8,
    'minimum': 0,
    'priority': 700,
    'clear': False,
    'pulse': False
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
            'priority': int(priority)
        }).encode('utf-8') + b'\n'


def encode_effect(effect):
    return json.dumps({
            'command': 'effect',
            'effect': {'name': effect},
            'priority': int(priority)
        }).encode('utf-8') + b'\n'


def clear_all(host):
    return wait_for_response(send(
            json.dumps({'command': 'clearall'}).encode('utf-8') + b'\n', host
        ))


def send(data, host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        address = list(host.split(':'))
        sock.connect((address[0], int(address[1])))
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
        if pulse:
            return
        response = sock.recv(8192)
    except socket.error:
        return False
    else:
        process_response(response)
    finally:
        sock.close()


def send_color(values, host):
    return wait_for_response(send(encode_color(*values), host))


def send_effect(effect, host):
    return wait_for_response(send(encode_effect(effect), host))


def run(values, force=None, sleepTime=4, **kwargs):
    on, off = time(*start), time(*stop)
    while True:
        now = datetime.time(datetime.now())
        values.extend(values[-1] for missing in range(len(hosts) - len(values)))
        for host, value in zip(hosts, values):
            if not (on < now < off) or (not force and force is not None):
                send_color((minimum for i in range(3)), host)
            elif (on < now < off) or force:
                send_effect(value, host) if isinstance(value, str) else send_color(value, host)
        force = not force if pulse else force
        sleep(pulse if pulse else sleepTime)


def parse_args():
    kwargs, explicitKey, port = {'colors': [], 'hosts': set()}, None, None
    for arg in sys.argv[1:]:
        values = arg.split(',')
        times = arg.split(':')
        addressPort = arg.partition(':')
        address = addressPort[0].split('.')
        if explicitKey:
            try:
                value = float(arg)
            except:
                value = arg.strip("'").strip('"')
            if explicitKey == 'effect' and isinstance(value, str):
                kwargs['colors'].append(value)
            kwargs[explicitKey] = value
            explicitKey = None
        if len(values) > 1:
            kwargs['colors'].append(tuple(int(digit) for digit in values))
        elif '.' in addressPort[0] and addressPort[2].isdigit():
            port = addressPort[2]
        elif len(times) > 1:
            if 'start' not in kwargs:
                kwargs['start'] = tuple(int(digit) for digit in times)
            elif 'stop' not in kwargs:
                kwargs['stop'] = tuple(int(digit) for digit in times)
        elif arg.startswith('--'):
            explicitKey = arg.lstrip('--')
            if any(command in explicitKey for command in ('clear', 'clearall')):
                kwargs['clear'] = True
        if len(address) == 4 and all(i.isdigit() for i in address):
            kwargs['hosts'].add('{}:{}'.format(addressPort[0], port if port else defaults['port']))
    return kwargs


if __name__ == '__main__':
    kwargs = parse_args()
    for key, default in defaults.items():
        if key in ('colors', 'hosts') and not kwargs[key]:
            kwargs.pop(key)
        globals()[key] = kwargs.pop(key) if key in kwargs else default
    if 'maximum' not in itertools.chain(kwargs, globals()):
        maximum = (2 ** resolution) - 1
    if clear:
        for host in hosts:
            clear_all(host)
    else:
        run(colors, **kwargs)
