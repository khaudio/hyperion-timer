import getpass
import os
import subprocess

installService = True
username = getpass.getuser()
service = """
[Unit]
Description=hyperion-timer

[Service]
User={}
Type=simple
ExecStart=/usr/bin/python3 -m hyperion-timer 157,124,37 17:30, 23:59:59
StandardOutput=syslog
StandardError=syslog

[Install]
After=hyperion.service
WantedBy=default.target
""".format(username)

try:
    from setuptools import setup, find_packages
except ImportError:
    if username == 'pi':
        subprocess.run('sudo apt install -y python3-setuptools'.split())

setup(
        name='hyperion-timer',
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

if installService and os.path.exists('/etc/systemd'):
    print('Installing service')
    with open('/tmp/hyperion-timer.service', 'w') as temp:
        temp.write(service)
    commands = (
            'systemctl stop hyperion-timer',
            'cp /tmp/hyperion-timer.service /etc/systemd/system/hyperion-timer.service',
            'systemctl daemon-reload',
            'systemctl enable hyperion-timer',
            'systemctl start hyperion-timer',
        )
    for command in commands:
        split = command.split()
        split.insert(0, 'sudo')
        process = subprocess.run(split)
        if process.returncode is not 0:
            print('Error:', process.args)
    print('Installed and enabled hyperion-timer.service')
