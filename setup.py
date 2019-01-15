from setuptools import setup, find_packages
import getpass
import os
import subprocess
import sys

installService, ensurePath = True, True
username = getpass.getuser()
service = """
[Unit]
Description=Hyperion Timer

[Service]
User={}
Type=simple
ExecStart=/usr/bin/python3 -m hyperiontimer 157,124,37 17:30, 23:59:59
StandardOutput=syslog
StandardError=syslog

[Install]
After=hyperion.service
WantedBy=default.target
""".format(username)

setup(
        name='hyperiontimer',
        version='0.1.0',
        description='Starts and stops hyperion-based lighting on a timer.',
        long_description='Periodically sends json messgaes to local or remote hyperion instance to illuminate based on current time.',
        url='https://github.com/khaudio/hyperion-timer',
        author='Kyle Hughes',
        author_email='kyle@kylehughesaudio.com',
        packages=find_packages(exclude=[]),
        install_requires=[],
        classifiers=[
                'Programming Language :: Python :: 3.5.3'
                'Programming Language :: Python :: 3.7.0'
            ]
    )

def get_filename():
    for filename in ('.bashrc', '.bash_profile'):
        path = os.path.expanduser('~' + os.sep + filename)
        if os.path.exists(path):
            return path

def python_path_set():
    for path in sys.path:
        if path and path in os.environ['PATH']:
            for scanned in os.scandir(path):
                if os.path.expanduser('~') in scanned.path:
                    return True

def set_env():
    if not python_path_set():
        filename = get_filename()
        if filename:
            path = os.path.expanduser(os.path.join('~', '.local'))
            with open(filename, 'r') as profile:
                for line in profile:
                    if path in line:
                        return
            with open(filename, 'a') as profile:
                profile.write('export PATH=$PATH:{}\n'.format(path))
                print('Added {} to $PATH'.format(path))

if installService and os.path.exists('/etc/systemd'):
    print('Installing service')
    if ensurePath:
        set_env()
    with open('/tmp/hyperiontimer.service', 'w') as temp:
        temp.write(service)
    commands = (
            'systemctl stop hyperiontimer',
            'cp /tmp/hyperiontimer.service /etc/systemd/system/hyperiontimer.service',
            'systemctl daemon-reload',
            'systemctl enable hyperiontimer',
            'systemctl start hyperiontimer',
        )
    for command in commands:
        split = command.split()
        split.insert(0, 'sudo')
        process = subprocess.run(split)
        if process.returncode is not 0:
            print('Error:', process.args)
    print('Installed and enabled hyperiontimer.service')
