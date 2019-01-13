import getpass
import os
import subprocess

installService = True
installPath = '/etc/hyperion-timer'
username = getpass.getuser()
service = """
[Unit]
Description=hyperion-timer

[Service]
User={}
Type=simple
ExecStart=/usr/bin/python3 {}
StandardOutput=syslog
StandardError=syslog

[Install]
After=hyperion.service
WantedBy=default.target
""".format(username, installPath + '/main.py')

if installService and os.path.exists('/etc/systemd'):
    commands = (
            'mkdir -p {}'.format(installPath),
            'cp main.py {}'.format(installPath),
            'cp /tmp/hyperion-timer.service /etc/systemd/system/hyperion-timer.service',
            'chown {} {}/main.py'.format(username, installPath),
            'chmod +x {}/main.py'.format(installPath),
            'systemctl daemon-reload',
            'systemctl enable hyperion-timer',
            'systemctl start hyperion-timer',
        )
    for i, command in enumerate(commands):
        if i == 1:
            with open('/tmp/hyperion-timer.service', 'w') as temp:
                temp.write(service)
        split = command.split()
        split.insert(0, 'sudo')
        subprocess.run(split)


try:
    from setuptools import setup, find_packages
except ImportError:
    if username == 'pi':
        subprocess.run('sudo apt install -y python3-setuptools'.split())

setup(
        name='Hyperion Timer',
        version='0.1.0',
        description='Starts and stops hyperion-based lighting on a timer.',
        long_description='Periodically sends json messgaes to local or remote hyperion instance to illuminate based on current time.',
        url='https://github.com/khaudio/hyperion-timer',
        author='Kyle Hughes',
        author_email='kyle@kylehughesaudio.com',
        packages=find_packages(exclude=[]),
        install_requires=['datetime', 'json', 'socket', 'time'],
        classifiers=[
                'Programming Language :: Python :: 3.5.3'
                'Programming Language :: Python :: 3.7.0'
            ]
    )