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
    'hosts': ['127.0.0.1:19444'],
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
    return encode_message(
            color=(red, green, blue),
            command='color',
            priority=int(priority)
        )


def encode_effect(effect):
    return encode_message(
            command='effect',
            effect={'name': effect},
            priority=int(priority)
        )


def clear_all(host):
    return wait_for_response(send(encode_message(command='clearall'), host))


def encode_message(message=None, **kwargs):
    if not message:
        message = kwargs
    else:
        message.update(kwargs)
    return json.dumps(message).encode('utf-8') + b'\n'


def send(data, host):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        address = host.split(':')
        sock.connect((address[0], int(address[1])))
    except:
        raise
    else:
        sock.send(data)
        return sock


def process_response(response):
    try:
        decoded = json.loads(response.decode().rstrip())
    except json.decoder.JSONDecodeError:
        return False
    try:
        successful = decoded['success']
    except KeyError:
        return False
    else:
        return successful, decoded


def wait_for_response(sock):
    try:
        if pulse:
            return
        response = sock.recv(8192)
    except socket.error:
        return False
    else:
        return process_response(response)
    finally:
        sock.close()


def send_color(values, host):
    successful, _ = wait_for_response(send(encode_color(*values), host))
    return successful


def send_effect(effect, host):
    successful, _ = wait_for_response(send(encode_effect(effect), host))
    return successful


def run(values, force=None, interval=4, **kwargs):
    on, off = time(*start), time(*stop)
    activity = {host: False for host in hosts}
    timer, initialized = 0, False
    while True:
        now = datetime.time(datetime.now())
        values.extend(values[-1] for missing in range(len(hosts) - len(values)))
        for host, value in zip(hosts, values):
            if (
                    (off < now < on)
                    and (activity[host] or not initialized or timer >= 10)
                    or (not force and force is not None)
                ):
                activity[host] = not send_color(tuple(minimum for i in range(3)), host)
            elif ((on < now < off) and not any((activity[host], initialized))) or force:
                if isinstance(value, str):
                    if not activity[host]:
                        activity[host] = send_effect(value, host)
                elif isinstance(value, tuple) and (not initialized or timer >= 10):
                    activity[host] = send_color(value, host)
        if timer > 10:
            timer = 0
        timer += interval
        force = not force if pulse else force
        sleep(pulse if pulse else interval)


def parse_args():
    kwargs, explicitKey, port = {'colors': [], 'hosts': []}, None, None
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
            kwargs['hosts'].append('{}:{}'.format(addressPort[0], port if port else defaults['port']))
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
